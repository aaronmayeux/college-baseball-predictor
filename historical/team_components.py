"""Locked, offline NCAA OBP/ERA experiment; baseline and app remain unchanged."""
import argparse
from collections import Counter
from datetime import date, datetime
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT.parent / 'scripts'), str(ROOT / 'validation_v2'), str(ROOT.parent)]
import team_runs as common
from audit_ncaa_archive import audit, parse_report
from baseline import State, frozen, load_games, metric
from eligibility import reject
from reconcile import internal
from reconcile_ncaa_archive import totals, ncaa_totals, differences
from validation_v2.evidence import overlay
from validation_v2 import seeds
import regional_validation as regional
from tournament.engine import group_probabilities

OUT = ROOT / 'team_component_output'
CANDIDATES = {'obp': ['obp'], 'era': ['era'], 'both': ['obp', 'era']}
SNAPSHOTS = {2021: ('weekly', '2021-05-23'), 2022: ('previous', '2022-05-25'),
             2023: ('raw', '2023-05-28'), 2024: ('raw', '2024-05-26')}
PROTOCOL = dict(version=1, train=[2021, 2022], select=2023, validate=2024,
    refit=[2021, 2022, 2023], mode='conference_inclusive', ridge=.01,
    candidates=CANDIDATES, snapshots=SNAPSHOTS, min_games=20, max_age_days=14,
    max_record_delta=2, max_runs_delta=10,
    selection='improve both log_loss and brier; order log_loss,brier,name',
    sensitivity=['flagged_matchups_to_elo', 'same_candidate_without_2021'])


def fingerprints(evidence):
    result = common.inputs()
    paths = [Path(__file__), ROOT / 'regional_validation.py',
             ROOT.parent / 'tournament/engine.py',
             ROOT / 'validation_v2/seeds.py']
    paths += [ROOT.parent / 'scripts' / n for n in ('audit_ncaa_archive.py', 'reconcile_ncaa_archive.py')]
    for year, (folder, _) in SNAPSHOTS.items():
        paths += [ROOT / f'{year}/{n}.json' for n in ('teams', 'excluded_observations')]
        paths += sorted((evidence / folder).glob(f'{year}_*'))
    for year in (2023, 2024):
        path = ROOT / 'research/raw' / f'ncaa_{year}.pdf'
        if common.read(path.with_name(path.name + '.meta.json'))['sha256'] != common.digest(path):
            raise ValueError('Manual evidence changed')
        paths += [path, path.with_name(path.name + '.meta.json')]
    # Portable relative keys for evidence; source metadata holds exact URLs/timestamps.
    for p in paths:
        key = ('ncaa/' + str(p.relative_to(evidence))) if p.is_relative_to(evidence) else str(p.relative_to(ROOT.parent))
        result[key] = common.digest(p)
    protocol_text = (ROOT.parent / 'docs/Team_Component_Experiment.md').read_text().split('\n## Results', 1)[0]
    result['experiment_protocol'] = common.fingerprint(protocol_text)
    return result


def lock(path, value):
    if path.exists() and common.fingerprint(common.read(path)) != common.fingerprint(value):
        raise ValueError('Existing lock differs: ' + str(path))
    common.write(path, value)


def source_mapping(year, tables, selected):
    """Exact names and previously reviewed NCAA aliases only; ambiguity falls back."""
    roster = common.read(ROOT / f'{year}/teams.json')
    lookup = {r['name'].replace('’', "'"): internal(r['slug']) for r in roster}
    valid = {internal(r['slug']) for r in roster}
    for name, slug in seeds.ALIASES.items():
        if internal(slug) in valid:
            lookup[name.replace('’', "'")] = internal(slug)
    for r in selected:
        if r['season'] == year:
            lookup[r['source_name'].replace('’', "'")] = r['team_id']
    found = {}
    for name in set(tables['obp']) | set(tables['era']):
        team = lookup.get(name.replace('’', "'"))
        if team:
            found.setdefault(team, []).append(name)
    return {team: names[0] for team, names in found.items() if len(names) == 1}


def row_features(bat, pitch, issues):
    reasons = list(issues)
    if bat is None or pitch is None:
        return None, reasons + ['missing_report_row']
    if bat['reclassifying'] or pitch['reclassifying']:
        reasons.append('reclassifying_identity')
    if any(bat[k] != pitch[k] for k in ('G', 'W-L')):
        reasons.append('cross_table_record_mismatch')
    denominator = bat['AB'] + bat['BB'] + bat['HBP'] + bat['SF']
    if denominator <= 0 or pitch['outs'] <= 0:
        reasons.append('invalid_denominator')
    if bat['G'] < PROTOCOL['min_games']:
        reasons.append('small_sample')
    if reasons:
        return None, sorted(set(reasons))
    return dict(obp=(bat['H']+bat['BB']+bat['HBP']) / denominator,
                era=-27*pitch['ER']/pitch['outs']), []


def build_row(a, b, elo, features, **extra):
    covered = features[a]['values'] is not None and features[b]['values'] is not None
    return dict(extra, elo=elo, covered=covered,
        flagged=bool(features[a]['flags'] or features[b]['flags']),
        differences={k: features[a]['values'][k]-features[b]['values'][k] for k in ('obp','era')} if covered else {})


def prepare(evidence):
    refs = common.gates()
    before = fingerprints(evidence)
    contract = common.read(ROOT / 'cutoffs.json')
    selected = seeds.load(contract)
    predictions = common.read(ROOT / 'validation_v2/output/frozen_predictions.json')
    seed_probs = {(r['season'], r['game_id']): r['seed'] for r in common.read(ROOT / 'validation_v2/output/seed_comparison.json') if r['mode']==PROTOCOL['mode']}
    identities = {(r['season'],r['internal_team_id']):r for r in common.read(ROOT / 'team_crosswalk.json')}
    result = dict(protocol=PROTOCOL, inputs=before, features=[], samples=[], coverage=[])
    for year, (folder, day) in SNAPSHOTS.items():
        raw, through = evidence / folder, date.fromisoformat(day)
        check = audit(raw, year, through)
        if not check['national_tables_populated']:
            raise ValueError('Snapshot is empty')
        tables, issues = {}, {}
        for kind in ('obp','era'):
            rows, problems = parse_report((raw / f'{year}_{kind}.response').read_text(), kind, year, through)
            tables[kind] = {r['Name']: r for r in rows}
            for name, issue in problems:
                issues.setdefault(name, []).append(issue)
        mapped = source_mapping(year, tables, selected)
        games = overlay(load_games(year), refs)
        sample = [r for r in predictions if r['season']==year and r['mode']==PROTOCOL['mode'] and not r['tie']]
        field = {r[k] for r in sample for k in ('team_a_id','team_b_id')}
        if len(field)!=64 or len({r['game_id'] for r in sample})!=len(sample):
            raise ValueError('Incomplete field or duplicate games')
        if year > 2021 and field != {r['team_id'] for r in selected if r['season']==year}:
            raise ValueError('Selection field mismatch')
        cutoff = datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        excluded = common.read(ROOT / f'{year}/excluded_observations.json')
        features = {}
        for team in sorted(field):
            identity = identities[year,team]
            name = mapped.get(team)
            bat, pitch = tables['obp'].get(name), tables['era'].get(name)
            values, reasons = row_features(bat, pitch, issues.get(name, []))
            if name is None:
                reasons = ['unresolved_report_identity']
            tg = [g for g in games if team in (g['a'],g['b'])]
            eligible = [g for g in tg if reject(g, cutoff, contract['modes'][PROTOCOL['mode']]) is None]
            included = [g for g in tg if g.get('game_date') and g['game_date'] <= day]
            if any(g not in eligible for g in included) or any(not g.get('game_date') for g in tg):
                reasons.append('ineligible_or_unknown_date_in_snapshot')
            age = (cutoff.date()-through).days
            if not 2 <= age <= PROTOCOL['max_age_days']:
                reasons.append('snapshot_age')
            omitted = [g['game_id'] for g in eligible if g['game_date'] > day]
            nd = [r for r in excluded if r['team_id']==identity['provider_id'] and r['non_d1_explicit'] and r['status']=='completed' and r.get('game_date') and r['game_date']<=day]
            for r in nd:
                if r['timing_review'] or common.digest(ROOT / str(year) / r['raw_path']) != r['raw_sha256']:
                    raise ValueError('Non-D1 evidence invalid')
            expected = totals([(g['runs_a'],g['runs_b']) if g['a']==team else (g['runs_b'],g['runs_a']) for g in included] + [(r['runs_for'],r['runs_against']) for r in nd])
            delta = differences(ncaa_totals(pitch), expected) if pitch else None
            if delta and (any(abs(delta[k])>PROTOCOL['max_record_delta'] for k in ('G','W','L','T')) or abs(delta['R'])>PROTOCOL['max_runs_delta']):
                reasons.append('material_count_discrepancy')
            flags = (['omitted_eligible_games'] if omitted else []) + (['known_non_d1'] if nd else []) + (['count_discrepancy'] if delta and any(delta.values()) else [])
            features[team] = dict(season=year, team_id=team, name=identity['provider_name'], ncaa_name=name,
                identity_basis='exact_roster_or_reviewed_selection_alias', through=day, age_days=age,
                values=None if reasons else values, reasons=sorted(set(reasons)), flags=flags,
                delta=delta, source_games=bat['G'] if bat else None,
                omitted_game_ids=omitted, known_non_d1_games=len(nd),
                source_hashes={k:v['source_sha256'] for k,v in check['tables'].items()})
        result['features'].extend(features.values())
        for row in sample:
            row = dict(row)
            if year > 2021:
                row['seed'] = seed_probs[year,row['game_id']]
            result['samples'].append(build_row(row['team_a_id'],row['team_b_id'],row.pop('elo'),features,**row))
        result['coverage'].append(dict(season=year, through=day, age_days=age, teams=64,
            usable_teams=sum(r['values'] is not None for r in features.values()), games=len(sample),
            covered_games=sum(r['covered'] for r in result['samples'] if r['season']==year),
            fallback_teams=[dict(name=r['name'],reasons=r['reasons']) for r in features.values() if r['values'] is None],
            flags=dict(Counter(f for r in features.values() for f in r['flags'])),
            omitted_games_per_team_range=[min(len(r['omitted_game_ids']) for r in features.values()),max(len(r['omitted_game_ids']) for r in features.values())],
            discrepancies=[dict(name=r['name'],delta=r['delta']) for r in features.values() if r['delta'] and any(r['delta'].values())]))
    if before != fingerprints(evidence):
        raise ValueError('Inputs changed')
    lock(OUT / 'prepared.json', result)
    print(__import__('json').dumps(result['coverage'], indent=2))


def probability(row, model, strict=False):
    if model['candidate']=='elo' or not row['covered'] or (strict and row['flagged']):
        return row['elo']
    p = row['elo']
    return common.sigmoid(math.log(p/(1-p)) + sum(b*row['differences'][k]/s for k,b,s in zip(model['keys'],model['beta'],model['scale'])))


def fit(rows, candidate):
    if candidate=='elo':
        return dict(candidate='elo')
    if any(r.get('tie') or r['season'] not in (2021,2022,2023) for r in rows):
        raise ValueError('Invalid training season/outcome')
    rows = [r for r in rows if r['covered']]
    if not rows:
        raise ValueError('No covered training games')
    keys = CANDIDATES[candidate]
    scales = [math.sqrt(sum(r['differences'][k]**2 for r in rows)/len(rows)) for k in keys]
    if any(s<=0 or not math.isfinite(s) for s in scales):
        raise ValueError('No valid training variation')
    xs = [[r['differences'][k]/s for k,s in zip(keys,scales)] for r in rows]
    offsets = [math.log(r['elo']/(1-r['elo'])) for r in rows]
    beta = [0.]*len(keys)
    # Convex ridge logistic regression, cyclic exact coordinate minimization.
    for iteration in range(1000):
        old = beta[:]
        for j in range(len(keys)):
            def grad(b):
                return sum((common.sigmoid(o + sum((b if k==j else beta[k])*x[k] for k in range(len(keys))))-r['outcome'])*x[j] for o,x,r in zip(offsets,xs,rows))/len(rows)+PROTOCOL['ridge']*b
            lo,hi=-1.,1.
            while grad(lo)>0: lo*=2
            while grad(hi)<0: hi*=2
            for _ in range(55):
                mid=(lo+hi)/2
                if grad(mid)>0: hi=mid
                else: lo=mid
            beta[j]=(lo+hi)/2
        if max(abs(a-b) for a,b in zip(old,beta))<1e-12:
            break
    else:
        raise ValueError('Fit did not converge')
    return dict(candidate=candidate, keys=keys, scale=scales, beta=beta, n=len(rows), training_seasons=sorted({r['season'] for r in rows}))


def scored(rows, model, strict=False):
    return [dict(r, challenger=probability(r,model,strict)) for r in rows]


def evaluate(evidence):
    refs = common.gates()
    data = common.read(OUT / 'prepared.json')
    before = fingerprints(evidence)
    if data['inputs']!=before or common.fingerprint(data['protocol'])!=common.fingerprint(PROTOCOL):
        raise ValueError('Stale preparation')
    rows = data['samples']
    train = [r for r in rows if r['season'] in PROTOCOL['train']]
    selection_rows = [r for r in rows if r['season']==2023]
    models = {k:fit(train,k) for k in CANDIDATES}
    base = metric(selection_rows,'elo')
    selection = {k:metric(scored(selection_rows,m),'challenger') for k,m in models.items()}
    qualified = [k for k,v in selection.items() if v['log_loss']<base['log_loss'] and v['brier']<base['brier']]
    winner = min(qualified,key=lambda k:(selection[k]['log_loss'],selection[k]['brier'],k)) if qualified else 'elo'
    refit = fit([r for r in rows if r['season']<=2023],winner)
    selection_lock = dict(protocol=PROTOCOL, prepared_sha256=common.digest(OUT/'prepared.json'),
        training_models=models, selection=dict(elo=base,candidates=selection), winner=winner, refitted_model=refit)
    lock(OUT/'selection_lock.json', selection_lock)  # Before any 2024 candidate scoring.
    chosen = {2023:models.get(winner,dict(candidate='elo')),2024:refit}
    sensitivity = {y:fit([r for r in rows if 2022<=r['season']<y],winner) for y in (2023,2024)}
    # Freeze every hypothetical regional matchup before evaluating advancement.
    contract = common.read(ROOT/'cutoffs.json')
    selected = seeds.load(contract)
    forecasts, equivalence = [], 0
    state = State()
    for year in range(2021,2025):
        if year>2021: state.regress()
        games = overlay(load_games(year),refs)
        frozen(games,state,PROTOCOL['mode'],datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff']),contract['modes'][PROTOCOL['mode']])
        if year<2023: continue
        features = {r['team_id']:r for r in data['features'] if r['season']==year}
        def pair(a,b):
            if not state.n.get(a) or not state.n.get(b): raise ValueError('Missing Elo history')
            return build_row(a,b,state.p(a,b),features)
        for r in rows:
            if r['season']==year:
                p=pair(r['team_a_id'],r['team_b_id'])
                if abs(p['elo']-r['elo'])>1e-14 or abs(probability(p,chosen[year])-probability(r,chosen[year]))>1e-14:
                    raise ValueError('Observed/hypothetical probability mismatch')
                equivalence+=1
        for region in regional.regions(selected,year):
            probabilities={}
            for key in ('elo','challenger','seed','strict','without_2021'):
                def p(a,b):
                    row=pair(a,b)
                    if key=='elo': return row['elo']
                    if key=='seed': return seeds.probability(region['seeds'][a],region['seeds'][b])
                    return probability(row,sensitivity[year] if key=='without_2021' else chosen[year],key=='strict')
                probabilities[key]=group_probabilities(region['teams'],p)
            forecasts.append(dict(season=year,**region,probabilities=probabilities))
    lock(OUT/'forecast_lock.json',dict(selection_sha256=common.digest(OUT/'selection_lock.json'),forecasts=forecasts))
    report = dict(selection=selection_lock,coverage=data['coverage'],games=[],regionals=[],advancement=[],
        sensitivity_models=sensitivity,equivalence_checks=equivalence,promoted=False,game_groups=[])
    predictions=[]
    for year in (2023,2024):
        sample=[r for r in rows if r['season']==year]
        for variant in ('primary','strict','without_2021'):
            scored_rows=scored(sample,sensitivity[year] if variant=='without_2021' else chosen[year],variant=='strict')
            if variant=='primary': predictions.extend(scored_rows)
            subsets={'all':scored_rows,'covered':[r for r in scored_rows if r['covered']], 'fallback':[r for r in scored_rows if not r['covered']]}
            if variant=='primary':
                subsets.update({s:[r for r in scored_rows if r['stage']==s] for s in sorted({r['stage'] for r in scored_rows})})
            for subset,rs in subsets.items():
                if rs: report['games'].append(dict(season=year,variant=variant,subset=subset,n=len(rs),**common.summarize(rs)))
        games=overlay(load_games(year),refs)
        covered=set(); winners=set(); regional_rows=[]
        for forecast in [f for f in forecasts if f['season']==year]:
            match=[g for g in games if g['stage']=='regional' and g['a'] in forecast['teams'] and g['b'] in forecast['teams']]
            outcome=regional.champion(forecast['teams'],match)
            covered.update(g['game_id'] for g in match); winners.add(outcome['winner'])
            regional_rows.append(dict(**forecast,**outcome,scores={k:regional.score(v,outcome['winner']) for k,v in forecast['probabilities'].items()}))
        if covered!={g['game_id'] for g in games if g['stage']=='regional'} or winners!={g[t] for g in games if g['stage']=='super_regional' for t in ('a','b')}:
            raise ValueError('Regional outcome coverage mismatch')
        report['regionals'].extend(regional_rows)
        for region in regional_rows:
            rs = [r for r in predictions if r['season']==year and r['stage']=='regional'
                  and r['team_a_id'] in region['teams'] and r['team_b_id'] in region['teams']]
            report['game_groups'].append(dict(season=year,regional=region['name'],n=len(rs),**common.summarize(rs)))
        for variant,key in (('primary','challenger'),('strict','strict'),('without_2021','without_2021')):
            adjusted=[dict(r,scores=dict(r['scores'],challenger=r['scores'][key]),probabilities=dict(r['probabilities'],challenger=r['probabilities'][key])) for r in regional_rows]
            report['advancement'].append(dict(season=year,variant=variant,**regional.summary(adjusted)))
    if before!=fingerprints(evidence): raise ValueError('Preserved inputs changed')
    report['preserved_inputs_unchanged']=True
    common.write(OUT/'predictions.json',predictions)
    common.write(OUT/'report.json',report)
    print(__import__('json').dumps(dict(winner=winner,model=refit,games=[r for r in report['games'] if r['subset']=='all'],advancement=report['advancement']),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','evaluate'))
    parser.add_argument('--evidence-dir',type=Path,required=True)
    args=parser.parse_args()
    (prepare if args.action=='prepare' else evaluate)(args.evidence_dir.resolve())
