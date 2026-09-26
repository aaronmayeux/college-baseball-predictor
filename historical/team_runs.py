"""Offline, versioned team scoring experiment; never modifies baseline or app."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

from baseline import ROOT, load_games, metric
from eligibility import reject
from validation_v2.evidence import overlay, verify_timing

OUT = ROOT / 'team_run_output'
CANDIDATES = ('net', 'offense', 'prevention')
PROTOCOL = dict(version=1, seasons=[2021, 2022, 2023, 2024], train=[2021, 2022],
                select=2023, validate=2024, ridge=0.01, candidates=CANDIDATES,
                selection='strictly improve log_loss and brier; order log_loss,brier,name',
                primary='regular_only', scaling='training matchup RMS; no centering',
                refit=[2021, 2022, 2023], minimum_field_teams=64)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def inputs():
    paths = [ROOT / f'{y}/games.json' for y in PROTOCOL['seasons']]
    paths += [ROOT / name for name in ('cutoffs.json', 'coverage_validation.json',
        'correction_evidence_checks.json', 'team_crosswalk.json', 'team_runs.py',
        'baseline.py', 'eligibility.py', 'reconcile.py', 'validation_v2/evidence.py')]
    paths += [ROOT / 'validation_v2/output' / (name + '.json') for name in
              ('summary', 'frozen_predictions', 'seed_comparison', 'seeds', 'official_checks')]
    return {str(p.relative_to(ROOT)): digest(p) for p in paths}


def gates():
    coverage = read(ROOT / 'coverage_validation.json')
    if {r['season'] for r in coverage} != set(range(2021, 2026)) or not all(r['pass'] for r in coverage):
        raise ValueError('Coverage gate failed')
    if not read(ROOT / 'correction_evidence_checks.json')['pass']:
        raise ValueError('Correction gate failed')
    summary = read(ROOT / 'validation_v2/output/summary.json')
    if not summary['baseline_unchanged']:
        raise ValueError('v2 preservation gate failed')
    for name, sha in summary['baseline_sha256'].items():
        if digest(ROOT / name) != sha:
            raise ValueError('Baseline differs from verified v2: ' + name)
    checks = read(ROOT / 'validation_v2/output/official_checks.json')
    if any(r['status'] == 'review' for r in checks):
        raise ValueError('Independent checks unresolved')
    return verify_timing()


def aggregate(games, cutoff, stages):
    """Totals from qualified D1 game rows; every exclusion retains its reason."""
    totals = collections.defaultdict(lambda: dict(games=0, runs_for=0, runs_against=0, game_ids=[]))
    eligibility, seen = [], set()
    for g in games:
        if g['game_id'] in seen:
            raise ValueError('Duplicate game ID')
        seen.add(g['game_id'])
        reason = reject(g, cutoff, stages)
        eligibility.append(dict(game_id=g['game_id'], reason=reason))
        if reason:
            continue
        if g['a'] == g['b'] or any(type(g[k]) is not int or g[k] < 0 for k in ('runs_a', 'runs_b')):
            raise ValueError('Invalid team or score')
        for team, scored, allowed in ((g['a'], g['runs_a'], g['runs_b']),
                                     (g['b'], g['runs_b'], g['runs_a'])):
            row = totals[team]
            row['games'] += 1
            row['runs_for'] += scored
            row['runs_against'] += allowed
            row['game_ids'].append(g['game_id'])
    if sum(r['runs_for'] for r in totals.values()) != sum(r['runs_against'] for r in totals.values()):
        raise ValueError('Run conservation failed')
    for row in totals.values():
        row['offense'] = row['runs_for'] / row['games']
        row['prevention'] = -row['runs_against'] / row['games']
        row['net'] = row['offense'] + row['prevention']
        row['game_ids'].sort()
    return dict(totals), eligibility


def prepare():
    refs = gates()
    before = inputs()
    contract = read(ROOT / 'cutoffs.json')
    predictions = read(ROOT / 'validation_v2/output/frozen_predictions.json')
    seeds = read(ROOT / 'validation_v2/output/seed_comparison.json')
    seed_index = {(r['season'], r['mode'], r['game_id']): r['seed'] for r in seeds}
    regions = {(r['season'], r['team_id']): r['regional']
               for r in read(ROOT / 'validation_v2/output/seeds.json')}
    crosswalk = {(r['season'], r['internal_team_id']): r
                 for r in read(ROOT / 'team_crosswalk.json')}
    data = dict(protocol=PROTOCOL, inputs=before, features=[], eligibility=[], samples=[], coverage=[])
    for year in PROTOCOL['seasons']:
        games = overlay(load_games(year), refs)
        for mode, stages in contract['modes'].items():
            cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
            totals, eligibility = aggregate(games, cutoff, stages)
            data['eligibility'].extend(dict(season=year, mode=mode, **r) for r in eligibility)
            rows = [r for r in predictions if r['season'] == year and r['mode'] == mode and not r['tie']]
            teams = {r[k] for r in rows for k in ('team_a_id', 'team_b_id')}
            if len(teams) != 64 or not teams <= totals.keys():
                raise ValueError(f'Incomplete field: {year} {mode}')
            if len({r['game_id'] for r in rows}) != len(rows):
                raise ValueError('Duplicate evaluation matchup')
            for team in sorted(teams):
                identity = crosswalk[year, team]
                data['features'].append(dict(season=year, mode=mode, team_id=team,
                    provider_id=identity['provider_id'], name=identity['provider_name'],
                    conference=identity['source_conference'], **totals[team]))
            for row in rows:
                a, b = row['team_a_id'], row['team_b_id']
                group = row['stage']
                if group == 'regional' and year > 2021:
                    if regions[year, a] != regions[year, b]:
                        raise ValueError('Regional identity mismatch')
                    group += ':' + regions[year, a]
                result = dict(row, group=group,
                              differences={k: totals[a][k] - totals[b][k] for k in CANDIDATES})
                if year > 2021:
                    result['seed'] = seed_index[year, mode, row['game_id']]
                data['samples'].append(result)
            data['coverage'].append(dict(season=year, mode=mode, teams=len(teams),
                games=len(rows), excluded_ncaa_ties=sum(r['season'] == year and r['mode'] == mode and r['tie'] for r in predictions),
                missing_feature_games=0, seed_games=sum('seed' in r for r in data['samples'] if r['season'] == year and r['mode'] == mode),
                conferences=dict(collections.Counter(crosswalk[year, t]['source_conference'] for t in teams)),
                feature_game_count_range=[min(totals[t]['games'] for t in teams), max(totals[t]['games'] for t in teams)],
                input_exclusions=dict(collections.Counter(r['reason'] for r in eligibility if r['reason']))))
    if inputs() != before:
        raise ValueError('Input changed during prepare')
    write(OUT / 'prepared.json', data)
    print(json.dumps(data['coverage'], indent=2))


def sigmoid(x):
    return 1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))


def probability(row, model):
    if model['candidate'] == 'elo':
        return row['elo']
    p = row['elo']
    return sigmoid(math.log(p / (1-p)) + model['beta'] * row['differences'][model['candidate']] / model['scale'])


def fit(rows, candidate):
    if not rows or any(r['tie'] for r in rows):
        raise ValueError('Empty or nonbinary training sample')
    scale = math.sqrt(sum(r['differences'][candidate] ** 2 for r in rows) / len(rows))
    if not scale:
        raise ValueError('No training variation')
    xs = [r['differences'][candidate] / scale for r in rows]
    offsets = [math.log(r['elo'] / (1-r['elo'])) for r in rows]
    # Strictly convex one-dimensional ridge objective. Bracket its derivative.
    def gradient(beta):
        return sum((sigmoid(o + beta*x) - r['outcome'])*x for o,x,r in zip(offsets,xs,rows))/len(rows) + PROTOCOL['ridge']*beta
    lo, hi = -1., 1.
    while gradient(lo) > 0:
        lo *= 2
    while gradient(hi) < 0:
        hi *= 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if gradient(mid) > 0:
            hi = mid
        else:
            lo = mid
    return dict(candidate=candidate, beta=(lo+hi)/2, scale=scale,
                training_seasons=sorted({r['season'] for r in rows}), n=len(rows))


def scored(rows, model):
    return [dict(r, challenger=probability(r, model)) for r in rows]


def select(rows, models):
    baseline = metric(rows, 'elo')
    metrics = {k: metric(scored(rows, v), 'challenger') for k,v in models.items()}
    qualifying = [k for k,v in metrics.items() if v['log_loss'] < baseline['log_loss'] and v['brier'] < baseline['brier']]
    winner = min(qualifying, key=lambda k: (metrics[k]['log_loss'], metrics[k]['brier'], k)) if qualifying else 'elo'
    return winner, dict(elo=baseline, candidates=metrics)


def summarize(rows):
    models = ('elo', 'challenger', 'seed') if all('seed' in r for r in rows) else ('elo', 'challenger')
    metrics = {k: metric(rows, k) for k in models}
    calibration = {}
    for key in models:
        bins = []
        for i in range(10):
            sample = [r for r in rows if i/10 <= r[key] < (i+1)/10]
            if sample:
                bins.append(dict(lower=i/10, n=len(sample), mean_probability=sum(r[key] for r in sample)/len(sample),
                                 observed=sum(r['outcome'] for r in sample)/len(sample)))
        calibration[key] = bins
    return dict(metrics=metrics, paired_delta={k: metrics['challenger'][k]-metrics['elo'][k] for k in ('log_loss','brier','accuracy')},
                calibration=calibration)


def evaluate():
    gates()
    data = read(OUT / 'prepared.json')
    if data['inputs'] != inputs() or fingerprint(data['protocol']) != fingerprint(PROTOCOL):
        raise ValueError('Stale preparation; explicitly prepare the new version')
    before = inputs()
    rows = data['samples']
    primary = [r for r in rows if r['mode'] == 'regular_only']
    training = [r for r in primary if r['season'] in PROTOCOL['train']]
    models = {k: fit(training, k) for k in CANDIDATES}
    winner, selection = select([r for r in primary if r['season'] == 2023], models)
    chosen = fit([r for r in primary if r['season'] <= 2023], winner) if winner != 'elo' else dict(candidate='elo')
    lock = dict(preparation_sha256=digest(OUT / 'prepared.json'), protocol=PROTOCOL,
                training_models=models, selection=selection, winner=winner, refitted_model=chosen)
    lock_path = OUT / 'selection_lock.json'
    if lock_path.exists() and fingerprint(read(lock_path)) != fingerprint(lock):
        raise ValueError('Selection lock differs; do not overwrite a previous experiment')
    write(lock_path, lock)  # Selection persisted before any 2024 candidate metrics.
    report = dict(lock=lock, coverage=data['coverage'], results=[], tournament_groups=[],
                  uncertainty='One retrospective validation season; no credible season-cluster CI or independent-game significance claim.',
                  promoted=False)
    predictions = []
    for year in (2023, 2024):
        model = (models[winner] if winner != 'elo' else chosen) if year == 2023 else chosen
        for mode in ('regular_only', 'conference_inclusive'):
            sample = scored([r for r in rows if r['season'] == year and r['mode'] == mode], model)
            predictions.extend(sample)
            for stage in ('all_ncaa', 'regional', 'super_regional', 'omaha', 'championship_series'):
                subset = [r for r in sample if stage == 'all_ncaa' or r['stage'] == stage]
                if subset:
                    report['results'].append(dict(season=year, mode=mode, stage=stage, **summarize(subset)))
            for group in sorted({r['group'] for r in sample}):
                report['tournament_groups'].append(dict(season=year, mode=mode, group=group,
                    **summarize([r for r in sample if r['group'] == group])))
    if before != inputs():
        raise ValueError('Preserved inputs changed')
    report['preserved_inputs_unchanged'] = True
    write(OUT / 'predictions.json', predictions)
    write(OUT / 'report.json', report)
    print(json.dumps(dict(winner=winner, model=chosen, results=[r for r in report['results'] if r['stage'] == 'all_ncaa']), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'evaluate'))
    args = parser.parse_args()
    (prepare if args.action == 'prepare' else evaluate)()
