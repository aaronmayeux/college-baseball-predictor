"""Offline BB/recorded-PA challenger; closed candidates and app stay unchanged."""
import argparse
from datetime import date, datetime
import math
from pathlib import Path
import team_components as components
from team_components import (common, ROOT, State, frozen, load_games, metric,
    overlay, seeds, regional, group_probabilities, lock, probability, scored)

OUT = ROOT / 'walk_rate_output'
CANDIDATES = {'walk_rate': ['walk_rate']}
PROTOCOL = dict(version=1, train=[2021, 2022], select=2023, validate=2024,
    refit=[2021, 2022, 2023], mode='conference_inclusive', ridge=.01,
    candidates=CANDIDATES, denominator='AB+BB+HBP+SF+SH; interference unavailable',
    qualification='unchanged team_components preparation',
    selection='improve both log_loss and brier, otherwise Elo',
    sensitivity=['flagged_matchups_to_elo', 'same_candidate_without_2021'])


def fingerprints(evidence):
    result = components.fingerprints(evidence)
    result['historical/walk_rate.py'] = common.digest(Path(__file__))
    result['historical/team_components.py'] = common.digest(Path(components.__file__))
    result['walk_rate_protocol'] = common.fingerprint(
        (ROOT.parent / 'docs/Walk_Rate_Experiment.md').read_text().split('\n## Results', 1)[0])
    return result


def row_features(bat):
    if bat is None:
        return None, ['missing_report_row']
    keys = ('AB', 'BB', 'HBP', 'SF', 'SH')
    if any(type(bat.get(k)) is not int or bat[k] < 0 for k in keys):
        return None, ['invalid_or_missing_walk_count']
    pa = sum(bat[k] for k in keys)
    if pa <= 0:
        return None, ['invalid_denominator']
    return dict(walk_rate=bat['BB']/pa), []


def build_row(a, b, elo, features, **extra):
    covered = all(features[t]['values'] is not None for t in (a, b))
    return dict(extra, elo=elo, covered=covered,
        flagged=bool(features[a]['flags'] or features[b]['flags']),
        differences={'walk_rate': features[a]['values']['walk_rate'] -
            features[b]['values']['walk_rate']} if covered else {})


def prepare(evidence):
    before = fingerprints(evidence)
    components.prepare(evidence)  # Qualification only; no closed-candidate scoring.
    source = common.read(components.OUT / 'prepared.json')
    if source['inputs'] != components.fingerprints(evidence):
        raise ValueError('Stale qualified inputs')
    features = []
    for year, (folder, day) in components.SNAPSHOTS.items():
        rows, _ = components.parse_report(
            (evidence / folder / f'{year}_obp.response').read_text(),
            'obp', year, date.fromisoformat(day))
        table = {r['Name']: r for r in rows}
        for old in source['features']:
            if old['season'] != year:
                continue
            bat = table.get(old['ncaa_name'])
            values, reasons = row_features(bat)
            reasons = sorted(set(old['reasons'] + reasons))
            features.append(dict(old, values=None if reasons else values, reasons=reasons,
                counts={k: bat[k] for k in ('AB','BB','HBP','SF','SH')} if bat else None))
    samples, coverage = [], []
    for year in components.SNAPSHOTS:
        field = {r['team_id']: r for r in features if r['season'] == year}
        for old in source['samples']:
            if old['season'] != year:
                continue
            row = {k:v for k,v in old.items() if k not in ('elo','covered','flagged','differences')}
            samples.append(build_row(row['team_a_id'], row['team_b_id'], old['elo'], field, **row))
        previous = next(r for r in source['coverage'] if r['season'] == year)
        coverage.append(dict(previous,
            usable_teams=sum(r['values'] is not None for r in field.values()),
            covered_games=sum(r['covered'] for r in samples if r['season']==year),
            fallback_teams=[dict(name=r['name'], reasons=r['reasons'])
                for r in field.values() if r['values'] is None]))
    if before != fingerprints(evidence):
        raise ValueError('Inputs changed during preparation')
    lock(OUT / 'prepared.json', dict(protocol=PROTOCOL, inputs=before,
        features=features, samples=samples, coverage=coverage))


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
