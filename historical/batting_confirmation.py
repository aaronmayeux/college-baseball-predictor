"""Frozen 2025 development confirmation; no fitting or app mutation."""
import argparse
from collections import Counter
from datetime import date, datetime
from pathlib import Path
import re
import guillen
import walk_rate
import team_components as c
from team_components import common, ROOT, regional, seeds, overlay, load_games, State
from audit_ncaa_archive import selected_date, parse_report
from ncaa_style_inputs import parse as parse_style
from collect_ncaa_archive import fetch, URL
from schedule_components import update_through

OUT = ROOT / 'batting_confirmation_output'
MODE = 'conference_inclusive'
MODELS = {
    'guillen': dict(candidate='guillen', keys=['guillen'], scale=[0.10032947177598207],
                    beta=[0.25322391361463914], n=403, training_seasons=[2021,2022,2023]),
    'walk_rate': dict(candidate='walk_rate', keys=['walk_rate'], scale=[0.022077761145654972],
                     beta=[0.16776241190324512], n=403, training_seasons=[2021,2022,2023])}
MODULES = {'guillen': guillen, 'walk_rate': walk_rate}
STATS = {'obp':'589','era':'211','hr':'513','runs':'486'}
PROTOCOL = dict(version=1, season=2025, mode=MODE, models=MODELS,
    sensitivity='flagged_matchups_to_elo', promoted=False,
    snapshot='latest eligible non-final menu date', min_games=20, max_age_days=14,
    max_record_delta=2, max_runs_delta=10, bootstrap_samples=5000, bootstrap_seed=20240926)


def scope(raw):
    contract = common.read(ROOT/'cutoffs.json')
    cutoff = datetime.fromisoformat(contract['seasons']['2025']['forecast_cutoff'])
    day, report = selected_date(raw, 2025, cutoff)
    menu = (raw/'2025_menu.html').read_text().split('id="LIST2"',1)[1].split('</select>',1)[0]
    forms = {}
    for kind, stat in STATS.items():
        if not re.search(r'<option value="'+stat+r'">[^<]+\(Team\)</option>',menu):
            raise ValueError('Statistic absent from retained menu')
        forms[kind] = [('sportCode','MBA'),('academicYear','2025'),('rptType','CSV'),
            ('doWhat','showrankings'),('div','1'),('rptWeeks',report)] + [
            ('statSeq',v) for v in ('-1','-1',stat,'-1')]
    return contract, cutoff, day, forms


def collect(raw):
    raw.mkdir(parents=True,exist_ok=True)
    fetch(raw,'2025_menu','.html',dict(sportCode='MBA',academicYear='2025',doWhat='display',year='2025'))
    _,_,day,forms = scope(raw)
    for kind,form in forms.items():
        fetch(raw,'2025_'+kind,'.response',form,requested_season=2025,
              requested_through_date=day.isoformat(),statistic=kind)


def tables(raw):
    _,cutoff,day,forms = scope(raw)
    if not 2 <= (cutoff.date()-day).days <= PROTOCOL['max_age_days']:
        raise ValueError('Snapshot age outside locked range')
    result, issues = {}, {}
    for kind,form in forms.items():
        path = raw/f'2025_{kind}.response'
        meta = common.read(raw/f'2025_{kind}.json')
        if (meta.get('status')!=200 or meta.get('url')!=URL or meta.get('method')!='POST'
            or meta.get('form')!=[list(r) for r in form] or meta.get('requested_season')!=2025
            or meta.get('requested_through_date')!=day.isoformat() or meta.get('statistic')!=kind
            or meta.get('sha256')!=common.digest(path)):
            raise ValueError('Invalid report provenance')
        if kind in ('obp','era'):
            rows, problems = parse_report(path.read_text(),kind,2025,day)
            result[kind] = {r['Name']:r for r in rows}
            for name,problem in problems:
                issues.setdefault(name,[]).append(problem)
        else:
            result[kind] = parse_style(path.read_text(),kind,2025,day.isoformat())
    return day, result, issues


def fingerprints(raw):
    result = common.inputs()
    paths = [Path(__file__), ROOT/'guillen.py', ROOT/'walk_rate.py', ROOT/'team_components.py',
        ROOT/'schedule_components.py', ROOT/'regional_validation.py', ROOT/'validation_v2/seeds.py',
        ROOT.parent/'tournament/engine.py', ROOT.parent/'scripts/audit_ncaa_archive.py',
        ROOT.parent/'scripts/ncaa_style_inputs.py', ROOT.parent/'scripts/collect_ncaa_archive.py',
        ROOT.parent/'scripts/reconcile_ncaa_archive.py', ROOT/'2025/games.json',
        ROOT/'2025/teams.json', ROOT/'2025/excluded_observations.json',
        ROOT/'research/raw/ncaa_di_selections_2025.html',
        ROOT/'research/raw/ncaa_di_selections_2025.html.meta.json']
    for p in paths:
        result[str(p.relative_to(ROOT.parent))] = common.digest(p)
    for p in sorted(raw.glob('2025_*')):
        result['source/'+p.name] = common.digest(p)
    result['protocol'] = common.fingerprint(PROTOCOL)
    result['protocol_text'] = common.fingerprint((ROOT.parent/'docs/Batting_Confirmation_2025.md').read_text().split('\n## Results',1)[0])
    return result


def qualify(raw, refs, selected):
    day, ts, issues = tables(raw)
    contract,cutoff,_,_ = scope(raw)
    mapped = c.source_mapping(2025,ts,selected)
    field = {r['team_id'] for r in selected if r['season']==2025}
    if len(field)!=64:
        raise ValueError('Incomplete selected field')
    identities = {r['internal_team_id']:r for r in common.read(ROOT/'team_crosswalk.json') if r['season']==2025}
    games = overlay(load_games(2025),refs)
    excluded = common.read(ROOT/'2025/excluded_observations.json')
    features = {k:{} for k in MODELS}
    for team in sorted(field):
        ident,name = identities[team],mapped.get(team)
        bat,pitch = ts['obp'].get(name),ts['era'].get(name)
        _,reasons = c.row_features(bat,pitch,issues.get(name,[]))
        if name is None: reasons.append('unresolved_report_identity')
        tg = [g for g in games if team in (g['a'],g['b'])]
        eligible = [g for g in tg if c.reject(g,cutoff,contract['modes'][MODE]) is None]
        included = [g for g in tg if g.get('game_date') and g['game_date']<=day.isoformat()]
        if any(g not in eligible for g in included) or any(not g.get('game_date') for g in tg):
            reasons.append('ineligible_or_unknown_date_in_snapshot')
        nd = [r for r in excluded if r['team_id']==ident['provider_id'] and r['non_d1_explicit']
              and r['status']=='completed' and r.get('game_date') and r['game_date']<=day.isoformat()]
        for r in nd:
            if (r.get('timing_review') or r['stage'] not in contract['modes'][MODE]
                or common.digest(ROOT/'2025'/r['raw_path'])!=r['raw_sha256']):
                raise ValueError('Non-D1 evidence invalid')
        scores = [(g['runs_a'],g['runs_b']) if g['a']==team else (g['runs_b'],g['runs_a']) for g in included]
        scores += [(r['runs_for'],r['runs_against']) for r in nd]
        expected = c.totals(scores)
        delta = c.differences(c.ncaa_totals(pitch),expected) if pitch else None
        if delta and (any(abs(delta[k])>2 for k in ('G','W','L','T')) or abs(delta['R'])>10):
            reasons.append('material_count_discrepancy')
        omitted = [g['game_id'] for g in eligible if g['game_date']>day.isoformat()]
        flags = (['omitted_eligible_games'] if omitted else []) + (['known_non_d1'] if nd else []) + (['count_discrepancy'] if delta and any(delta.values()) else [])
        hr,runs = ts['hr'].get(name),ts['runs'].get(name)
        for key,module in MODULES.items():
            value,extra = module.row_features(hr,runs,bat) if key=='guillen' else module.row_features(bat)
            rs,fs = reasons+extra,list(flags)
            run_delta = runs['R']-sum(a for a,b in scores) if key=='guillen' and runs else None
            if run_delta:
                fs.append('runs_scored_discrepancy')
                if abs(run_delta)>10: rs.append('material_runs_scored_discrepancy')
            features[key][team] = dict(team_id=team,name=ident['provider_name'],ncaa_name=name,
                values=None if rs else value,reasons=sorted(set(rs)),flags=sorted(set(fs)),
                delta=delta,runs_scored_delta=run_delta,through=day.isoformat(),
                age_days=(cutoff.date()-day).days,omitted_game_ids=omitted,known_non_d1_games=len(nd),
                counts={k:bat[k] for k in ('G','W-L','AB','BB','HBP','SF','SH')} if bat else None,
                style_counts={'HR':hr['HR'],'R':runs['R']} if hr and runs else None)
    return features


def pair(a,b,ratings,features,key,variant='primary'):
    p = 1/(1+10**((ratings[b]-ratings[a])/400))
    row = MODULES[key].build_row(a,b,p,features)
    return p if variant=='elo' else c.probability(row,MODELS[key],strict=variant=='strict')


def prepare(raw):
    refs = common.gates()
    before = fingerprints(raw)
    contract = common.read(ROOT/'cutoffs.json')
    selected = seeds.load(contract)
    features = qualify(raw,refs,selected)
    state = State()
    for year in range(2021,2026):
        if year>2021: state.regress()
        cutoff = datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        state,_ = update_through(state,overlay(load_games(year),refs),cutoff,
                                 contract['modes'][MODE],cutoff.date().isoformat())
    teams = set(features['guillen'])
    if any(not state.n.get(t) for t in teams):
        raise ValueError('Missing current-season Elo history')
    ratings = {t:state.r[t] for t in sorted(teams)}
    forecasts = {key:[] for key in MODELS}
    for group in regional.regions(selected,2025):
        for key in MODELS:
            probs = {variant:c.group_probabilities(group['teams'],
                lambda a,b:c.seeds.probability(group['seeds'][a],group['seeds'][b]) if variant=='seed'
                else pair(a,b,ratings,features[key],key,variant)) for variant in ('elo','primary','seed','strict')}
            forecasts[key].append(dict(**group,probabilities=probs))
    if before!=fingerprints(raw): raise ValueError('Inputs changed')
    c.lock(OUT/'forecast_lock.json',dict(protocol=PROTOCOL,inputs=before,features=features,
                                       ratings=ratings,forecasts=forecasts))
    print('Locked models, 64-team features and regional forecasts before scoring.')


def evaluate(raw):
    refs = common.gates()
    before = fingerprints(raw)
    data = common.read(OUT/'forecast_lock.json')
    if data['inputs']!=before or data['protocol']!=PROTOCOL:
        raise ValueError('Stale forecast lock')
    rows = [r for r in common.read(ROOT/'validation_v2/output/frozen_predictions.json')
            if r['season']==2025 and r['mode']==MODE and not r['tie']]
    if len({r['game_id'] for r in rows})!=len(rows): raise ValueError('Duplicate evaluation game')
    seed_index = {r['game_id']:r['seed'] for r in common.read(ROOT/'validation_v2/output/seed_comparison.json')
                  if r['season']==2025 and r['mode']==MODE}
    games = overlay(load_games(2025),refs)
    report = dict(protocol=PROTOCOL,forecast_sha256=common.digest(OUT/'forecast_lock.json'),candidates={})
    predictions = {}
    for key,module in MODULES.items():
        fs = data['features'][key]
        sample = [module.build_row(r['team_a_id'],r['team_b_id'],r['elo'],fs,
            **{k:v for k,v in r.items() if k!='elo'},seed=seed_index[r['game_id']]) for r in rows]
        variants = {v:c.scored(sample,MODELS[key],strict=v=='strict') for v in ('primary','strict')}
        for variant,rs in variants.items():
            for r in rs:
                a,b = r['team_a_id'],r['team_b_id']
                if (abs(pair(a,b,data['ratings'],fs,key,'elo')-r['elo'])>1e-14 or
                    abs(pair(a,b,data['ratings'],fs,key,variant)-r['challenger'])>1e-14):
                    raise ValueError('Observed/hypothetical mismatch')
        result = dict(usable_teams=sum(r['values'] is not None for r in fs.values()),
            covered_games=sum(r['covered'] for r in sample),games=len(sample),
            fallback_teams=[dict(name=r['name'],reasons=r['reasons']) for r in fs.values() if r['values'] is None],
            flags=dict(Counter(f for r in fs.values() for f in r['flags'])),game_scores=[],regionals=[],advancement={},game_groups=[])
        for variant,rs in variants.items():
            for subset in ('all','covered','fallback',*sorted({r['stage'] for r in rs})):
                selected = [r for r in rs if subset=='all' or (subset=='covered' and r['covered']) or
                            (subset=='fallback' and not r['covered']) or r['stage']==subset]
                if selected: result['game_scores'].append(dict(variant=variant,subset=subset,**common.summarize(selected)))
        covered,winners = set(),set()
        for group in data['forecasts'][key]:
            match = [g for g in games if g['stage']=='regional' and g['a'] in group['teams'] and g['b'] in group['teams']]
            outcome = regional.champion(group['teams'],match)
            covered.update(g['game_id'] for g in match); winners.add(outcome['winner'])
            result['regionals'].append(dict(**group,**outcome,scores={v:regional.score(p,outcome['winner']) for v,p in group['probabilities'].items()}))
            for variant,rs in variants.items():
                group_rows = [r for r in rs if r['stage']=='regional' and r['team_a_id'] in group['teams'] and r['team_b_id'] in group['teams']]
                result['game_groups'].append(dict(variant=variant,regional=group['name'],**common.summarize(group_rows)))
        if covered!={g['game_id'] for g in games if g['stage']=='regional'} or winners!={g[t] for g in games if g['stage']=='super_regional' for t in ('a','b')}:
            raise ValueError('Regional outcomes mismatch')
        for variant in variants:
            adapted = [dict(r,scores=dict(r['scores'],challenger=r['scores'][variant]),
                probabilities=dict(r['probabilities'],challenger=r['probabilities'][variant])) for r in result['regionals']]
            result['advancement'][variant] = regional.summary(adapted)
        result['passes_probability_screen'] = bool(result['covered_games']) and all(
            result['game_scores'][0]['paired_delta'][m]<0 and result['advancement']['primary']['paired_delta'][m]<0 for m in ('log_loss','brier'))
        result['equivalence_checks'] = len(rows)*len(variants)
        report['candidates'][key] = result
        predictions[key] = variants
    if before!=fingerprints(raw): raise ValueError('Protected inputs changed')
    report['preserved_inputs_unchanged'] = True
    common.write(OUT/'predictions.json',predictions)
    common.write(OUT/'report.json',report)
    print({k:dict(passes=v['passes_probability_screen'],teams=v['usable_teams'],covered=v['covered_games'],
                 game=v['game_scores'][0]['paired_delta'],regional=v['advancement']['primary']['paired_delta']) for k,v in report['candidates'].items()})


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('collect','prepare','evaluate'))
    parser.add_argument('--raw-dir',required=True,type=Path)
    args = parser.parse_args()
    globals()[args.action](args.raw_dir)
