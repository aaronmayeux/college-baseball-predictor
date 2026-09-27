"""Locked Nolan schedule-only correction; 2025 development, no app mutation."""
import argparse
from collections import Counter
from datetime import datetime
import math
from pathlib import Path

import schedule_components as schedule
from schedule_components import components, common, regional, seeds, State, load_games, overlay, reject, group_probabilities

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'schedule_only_output'
PROTOCOL = dict(version=1, train=[2021, 2022, 2023], evaluate=2025,
    mode='conference_inclusive', ridge=.01, min_schedule_games=20,
    candidate='schedule_only', keys=['schedule'], scale='training matchup RMS',
    sensitivity='drop one latest eligible appearance per team; fixed ratings and fit')


def fingerprints():
    result = common.inputs()
    paths = [Path(__file__), ROOT/'schedule_components.py', ROOT/'team_components.py',
             ROOT/'regional_validation.py', ROOT/'validation_v2/seeds.py',
             ROOT.parent/'tournament/engine.py', ROOT/'2025/games.json',
             ROOT/'research/raw/ncaa_di_selections_2025.html',
             ROOT/'research/raw/ncaa_di_selections_2025.html.meta.json']
    for year in range(2021, 2026):
        paths += [ROOT/f'{year}/teams.json']
    for path in paths:
        result[str(path.relative_to(ROOT.parent))] = common.digest(path)
    protocol = (ROOT.parent/'docs/Schedule_Only_Development.md').read_text().split('\n## Results', 1)[0]
    result['protocol_text'] = common.fingerprint(protocol)
    return result


def feature(team, games, state, drop_latest=False):
    games = [g for g in games if team in (g['a'], g['b'])]
    if drop_latest and games:
        # ID breaks equal-date ties only for this deletion diagnostic, never Elo updates.
        latest = max(games, key=lambda g: (g['game_date'], g['game_id']))
        games = [g for g in games if g['game_id'] != latest['game_id']]
    return schedule.schedule_feature(team, games, state)


def pair(a, b, elo, features, **extra):
    covered = all(features[t]['value'] is not None for t in (a, b))
    return dict(extra, elo=elo, covered=covered, flagged=False,
        differences={'schedule':features[a]['value']-features[b]['value']} if covered else {})


def fit(rows):
    if not rows or any(r['season'] not in PROTOCOL['train'] for r in rows):
        raise ValueError('Only locked 2021–2023 training seasons allowed')
    return schedule.fit(rows, ['schedule'], 'schedule_only')


def prepare():
    refs = common.gates()
    before = fingerprints()
    contract = common.read(ROOT/'cutoffs.json')
    selected = seeds.load(contract)
    frozen = common.read(ROOT/'validation_v2/output/frozen_predictions.json')
    seed_index = {(r['season'], r['mode'], r['game_id']):r['seed'] for r in
                  common.read(ROOT/'validation_v2/output/seed_comparison.json')}
    data = dict(protocol=PROTOCOL, inputs=before, features=[], samples=[], coverage=[],
                exclusions=[], ratings={}, sensitivity_features={})
    state = State()
    for year in range(2021, 2026):
        if year > 2021:
            state.regress()
        games = overlay(load_games(year), refs)
        cutoff = datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        stages = contract['modes'][PROTOCOL['mode']]
        state, eligible = schedule.update_through(state, games, cutoff, stages, cutoff.date().isoformat())
        data['exclusions'].extend(dict(season=year, game_id=g['game_id'], reason=reject(g, cutoff, stages))
                                  for g in games if reject(g, cutoff, stages))
        if year == 2024:
            continue  # Carry eligible Elo state only; no 2024 fitting or scoring.
        rows = [r for r in frozen if r['season']==year and r['mode']==PROTOCOL['mode'] and not r['tie']]
        teams = ({r['team_id'] for r in selected if r['season']==year} if year==2025 else
                 {r[k] for r in rows for k in ('team_a_id', 'team_b_id')})
        if len(teams)!=64 or any(not state.n.get(t) for t in teams):
            raise ValueError('Incomplete field or missing current-season Elo history')
        features = {t:feature(t, eligible, state) for t in sorted(teams)}
        data['features'].extend(dict(season=year, team_id=t, **f) for t,f in features.items())
        data['ratings'][str(year)] = {t:state.r[t] for t in sorted(teams)}
        if year==2025:
            data['sensitivity_features'] = {t:feature(t, eligible, state, True) for t in sorted(teams)}
        if len({r['game_id'] for r in rows})!=len(rows):
            raise ValueError('Duplicate evaluation game')
        for row in rows:
            a,b = row['team_a_id'],row['team_b_id']
            if a not in teams or b not in teams or abs(state.p(a,b)-row['elo'])>1e-14:
                raise ValueError('Frozen baseline or field mismatch')
            extra = {k:v for k,v in row.items() if k!='elo'}
            if year>2021:
                extra['seed'] = seed_index[year, PROTOCOL['mode'], row['game_id']]
            data['samples'].append(pair(a,b,row['elo'],features,**extra))
        data['coverage'].append(dict(season=year, teams=len(teams),
            usable_teams=sum(f['value'] is not None for f in features.values()),
            games=len(rows), covered_games=sum(r['covered'] for r in data['samples'] if r['season']==year),
            schedule_game_range=[min(f['games'] for f in features.values()),max(f['games'] for f in features.values())],
            fallback_teams={t:f['reasons'] for t,f in features.items() if f['reasons']},
            exclusions=dict(Counter(r['reason'] for r in data['exclusions'] if r['season']==year))))
    if before!=fingerprints():
        raise ValueError('Inputs changed during preparation')
    components.lock(OUT/'prepared.json',data)
    model = fit([r for r in data['samples'] if r['season'] in PROTOCOL['train']])
    components.lock(OUT/'model_lock.json',dict(prepared_sha256=common.digest(OUT/'prepared.json'),model=model))
    features = {r['team_id']:r for r in data['features'] if r['season']==2025}
    ratings = data['ratings']['2025']
    def probability(a,b,key,region):
        if key=='seed':
            return seeds.probability(region['seeds'][a],region['seeds'][b])
        elo = 1/(1+10**((ratings[b]-ratings[a])/400))
        if key=='elo':
            return elo
        fs = data['sensitivity_features'] if key=='drop_latest' else features
        return components.probability(pair(a,b,elo,fs),model)
    forecasts = []
    for region in regional.regions(selected,2025):
        probabilities = {k:group_probabilities(region['teams'],lambda a,b:probability(a,b,k,region))
                         for k in ('elo','challenger','seed','drop_latest')}
        forecasts.append(dict(**region,probabilities=probabilities))
    if before!=fingerprints():
        raise ValueError('Inputs changed during forecasting')
    components.lock(OUT/'forecast_lock.json',dict(model_sha256=common.digest(OUT/'model_lock.json'),forecasts=forecasts))
    print('Locked model and 16 regional forecasts before 2025 scoring.')
    print(model)
    print(data['coverage'])


def evaluate():
    refs = common.gates()
    before = fingerprints()
    data = common.read(OUT/'prepared.json')
    locked = common.read(OUT/'model_lock.json')
    forecasts = common.read(OUT/'forecast_lock.json')
    if (data['inputs']!=before or data['protocol']!=PROTOCOL or
        locked['prepared_sha256']!=common.digest(OUT/'prepared.json') or
        forecasts['model_sha256']!=common.digest(OUT/'model_lock.json')):
        raise ValueError('Stale inputs or model/forecast lock')
    model = locked['model']
    rows = [r for r in data['samples'] if r['season']==2025]
    predictions = components.scored(rows,model)
    sensitivity = components.scored([pair(r['team_a_id'],r['team_b_id'],r['elo'],data['sensitivity_features'],
        **{k:v for k,v in r.items() if k not in ('elo','covered','flagged','differences')}) for r in rows],model)
    report = dict(protocol=PROTOCOL,model=model,coverage=data['coverage'],games=[],regionals=[],game_groups=[],
        promoted=False, equivalence_checks=0, uncertainty='2025 development; no untouched or future-season claim')
    for variant,rs in [('primary',predictions),('drop_latest',sensitivity)]:
        for subset in ['all','adjusted','fallback',*sorted({r['stage'] for r in rs})]:
            sample = [r for r in rs if subset=='all' or (subset=='adjusted' and r['covered']) or
                      (subset=='fallback' and not r['covered']) or r['stage']==subset]
            if sample:
                report['games'].append(dict(variant=variant,subset=subset,**common.summarize(sample)))
    ratings = data['ratings']['2025']
    features = {r['team_id']:r for r in data['features'] if r['season']==2025}
    for r in predictions:
        a,b = r['team_a_id'],r['team_b_id']
        p = 1/(1+10**((ratings[b]-ratings[a])/400))
        if abs(p-r['elo'])>1e-14 or abs(components.probability(pair(a,b,p,features),model)-r['challenger'])>1e-14:
            raise ValueError('Observed/hypothetical probability mismatch')
        report['equivalence_checks'] += 1
    games = overlay(load_games(2025),refs)
    covered=set(); winners=set()
    for forecast in forecasts['forecasts']:
        match=[g for g in games if g['stage']=='regional' and g['a'] in forecast['teams'] and g['b'] in forecast['teams']]
        outcome=regional.champion(forecast['teams'],match)
        covered.update(g['game_id'] for g in match); winners.add(outcome['winner'])
        report['regionals'].append(dict(**forecast,**outcome,
            scores={k:regional.score(p,outcome['winner']) for k,p in forecast['probabilities'].items()}))
        sample=[r for r in predictions if r['stage']=='regional' and r['team_a_id'] in forecast['teams'] and r['team_b_id'] in forecast['teams']]
        report['game_groups'].append(dict(regional=forecast['name'],**common.summarize(sample)))
    if covered!={g['game_id'] for g in games if g['stage']=='regional'} or winners!={g[t] for g in games if g['stage']=='super_regional' for t in ('a','b')}:
        raise ValueError('Regional outcomes mismatch')
    report['advancement']=regional.summary(report['regionals'])
    diagnostic=[dict(r,scores=dict(r['scores'],challenger=r['scores']['drop_latest']),
        probabilities=dict(r['probabilities'],challenger=r['probabilities']['drop_latest'])) for r in report['regionals']]
    report['sensitivity_advancement']=regional.summary(diagnostic)
    report['passes_probability_screen']=all(report['games'][0]['paired_delta'][k]<0 and
        report['advancement']['paired_delta'][k]<0 for k in ('log_loss','brier'))
    if before!=fingerprints():
        raise ValueError('Protected inputs changed')
    report['preserved_inputs_unchanged']=True
    common.write(OUT/'predictions.json',predictions)
    common.write(OUT/'report.json',report)
    print({k:report[k] for k in ('passes_probability_screen','equivalence_checks','advancement','sensitivity_advancement')})
    print([r for r in report['games'] if r['subset']=='all'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','evaluate'))
    args=parser.parse_args()
    (prepare if args.action=='prepare' else evaluate)()
