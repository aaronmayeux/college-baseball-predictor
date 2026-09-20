"""Separate validation/seed evaluation. Run the original cached pipeline first."""
import collections
import csv
import datetime as dt
import hashlib
import json
from evidence import ROOT, OUT, SOURCES, TIMING, overlay, verify_timing, read_source, article_text
import independent
import seeds
from baseline import State, frozen, load_games, metric
from eligibility import reject

PRESERVED = ['predictions.csv', 'baseline_metrics.json', 'calibration.json', 'forecast_eligibility.csv',
             'cutoff_summary.json', 'coverage_validation.json'] + [f'{y}/games.json' for y in range(2021, 2026)]

def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PRESERVED}

def evaluate(contract, refs):
    states = {mode: State() for mode in contract['modes']}
    predictions, eligibility, corrected = [], [], []
    for year in range(2021, 2026):
        games = overlay(load_games(year), refs)
        corrected.extend(g for g in games if g['game_id'] in TIMING)
        for mode, state in states.items():
            if year > 2021:
                state.regress()
            cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
            stages = contract['modes'][mode]
            predictions.extend(frozen(games, state, mode, cutoff, stages))
            for game in games:
                reason = reject(game, cutoff, stages)
                eligibility.append(dict(season=year, game_id=game['game_id'], mode=mode,
                    eligible=reason is None, exclusion_reason=reason, forecast_cutoff=cutoff.isoformat()))
    if {g['game_id'] for g in corrected} != set(TIMING):
        raise ValueError('Missing timing correction target')
    return predictions, eligibility, corrected

def read_baseline():
    with (ROOT / 'predictions.csv').open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row['season'] = int(row['season'])
        row['tie'] = row['tie'] == 'True'
        for key in ('outcome', 'elo', 'win_rate', 'coin'):
            row[key] = float(row[key])
    return rows

def benchmark(predictions, baseline, seed_rows):
    seed_index = {(r['season'], r['team_id']): r for r in seed_rows}
    old = {(r['season'], r['mode'], r['game_id']): r for r in baseline}
    joined, excluded = [], []
    for row in predictions:
        a = seed_index.get((row['season'], row['team_a_id']))
        b = seed_index.get((row['season'], row['team_b_id']))
        cutoff = dt.datetime.fromisoformat(row['forecast_cutoff'])
        if not a or not b or not seeds.eligible(a, cutoff) or not seeds.eligible(b, cutoff):
            excluded.append(dict(season=row['season'], game_id=row['game_id'], mode=row['mode'],
                reason='missing_seed_season' if row['season'] not in seeds.SEASONS else 'missing_or_late_seed'))
            continue
        original = old[(row['season'], row['mode'], row['game_id'])]
        if original['outcome'] != row['outcome'] or original['tie'] != row['tie']:
            raise ValueError('Evaluation outcomes changed')
        joined.append(dict(row, seed=seeds.probability(a['regional_seed'], b['regional_seed']),
            seed_a=a['regional_seed'], seed_b=b['regional_seed'], baseline_elo=original['elo']))
    metrics = []
    for year in seeds.SEASONS:
        for mode in ('regular_only', 'conference_inclusive'):
            sample = [r for r in joined if r['season'] == year and r['mode'] == mode]
            for stage in ('all_ncaa', 'regional', 'super_regional', 'omaha', 'championship_series'):
                subset = [r for r in sample if stage == 'all_ncaa' or r['stage'] == stage]
                metrics.append(dict(season=year, mode=mode, stage=stage,
                    role='development' if year == 2025 else 'chronological_validation_fixed_parameters',
                    equal_seed_games=sum(r['seed_a'] == r['seed_b'] for r in subset),
                    **{key: metric(subset, key) for key in ('baseline_elo', 'elo', 'seed', 'win_rate', 'coin')}))
    if any(r['reason'] != 'missing_seed_season' for r in excluded):
        raise ValueError('Incomplete seed coverage within supported season')
    return joined, excluded, metrics

def opening_checks(seed_rows, contract):
    checks = []
    for year in seeds.SEASONS:
        games = load_games(year)
        groups = collections.defaultdict(list)
        for row in seed_rows:
            if row['season'] == year:
                groups[row['regional']].append(row)
        for name, group in sorted(groups.items()):
            by_seed = {r['regional_seed']: r['team_id'] for r in group}
            for a, b in ((1, 4), (2, 3)):
                matches = [g for g in games if {g['a'], g['b']} == {by_seed[a], by_seed[b]}
                    and g['stage'] == 'regional' and g['game_date'] == contract['seasons'][str(year)]['ncaa_opening_date']]
                evidence = []
                planned_date = contract['seasons'][str(year)]['ncaa_opening_date']
                if not matches:
                    # Explicit independently checked completion exceptions; no broad date tolerance.
                    delayed = {'wn:2022:42024': ('canisius_2022.html', 'wn:Canisius', 'Miami (FL)'),
                        'wn:2022:42026': ('arizona_2022.html', 'wn:Arizona', 'Ole Miss'),
                        'wn:2022:42056': ('uncg_2022.html', 'wn:UNCG', 'Georgia Southern'),
                        'wn:2024:48060': ('latech_recap_20240601.html', 'wn:Louisiana-Tech', 'Kansas State')}
                    for game in games:
                        if game['game_id'] not in delayed or {game['a'], game['b']} != {by_seed[a], by_seed[b]}:
                            continue
                        source, school, opponent = delayed[game['game_id']]
                        html, ref = read_source(source)
                        if source == 'latech_recap_20240601.html':
                            body = article_text(html)
                            valid = (all(v in body for v in ('19-4', '13-hour weather delay', 'Saturday morning', 'Kansas State'))
                                and game['game_date'] == '2024-06-01' and {game['runs_a'], game['runs_b']} == {4, 19})
                        else:
                            try:
                                rows = independent.extract(ROOT / 'research/raw' / source)
                            except ValueError:
                                rows = independent.legacy(html)
                            score = (game['runs_a'], game['runs_b']) if game['team_a_id'] == school else (game['runs_b'], game['runs_a'])
                            valid = sum(r['date'] == game['game_date'] and
                                independent.name_key(r['opponent'], school) == opponent and
                                (r['team_score'], r['opponent_score']) == score for r in rows) == 1
                        if valid and game['stage'] == 'regional':
                            matches.append(game)
                            evidence.append(ref)
                checks.append(dict(season=year, regional=name, seeds=[a, b],
                    planned_date=planned_date, actual_completion_dates=[g['game_date'] for g in matches],
                    completion_exception_evidence=evidence,
                    game_ids=[g['game_id'] for g in matches], status='pass' if len(matches) == 1 else 'review'))
    return checks

def run():
    before = hashes()
    audit = json.loads((ROOT / 'coverage_validation.json').read_text())
    if len(audit) != 5 or not all(r['pass'] for r in audit):
        raise ValueError('Baseline coverage gate failed')
    if not json.loads((ROOT / 'correction_evidence_checks.json').read_text())['pass']:
        raise ValueError('Baseline correction gate failed')
    refs = verify_timing()
    checks = independent.run()
    if any(r['status'] == 'review' for r in checks):
        raise ValueError('Unresolved independent schedule check')
    contract = json.loads((ROOT / 'cutoffs.json').read_text())
    seed_rows = seeds.load(contract)
    openings = opening_checks(seed_rows, contract)
    if any(r['status'] != 'pass' for r in openings):
        raise ValueError('NCAA opening date/phase check failed: ' + str([r for r in openings if r['status'] != 'pass']))
    predictions, eligibility, corrected = evaluate(contract, refs)
    joined, excluded, metrics = benchmark(predictions, read_baseline(), seed_rows)
    phase_counts = collections.Counter(r['official_phase'] for c in checks for r in c.get('rows', []) if r['phase_status'] == 'pass')
    summary = dict(dataset_version='timing_seed_v2', baseline_unchanged=before == hashes(), baseline_sha256=before,
        resolved_game_ids=sorted(TIMING), official_school_seasons=sum(c['status'] == 'pass' for c in checks),
        official_scored_observations=sum(c['scored_rows'] for c in checks if c['status'] == 'pass'),
        independent_scored_observations=sum(r['independent_from_result_source'] for c in checks for r in c.get('rows', [])),
        reused_supplement_observations=sum(not r['independent_from_result_source'] for c in checks for r in c.get('rows', [])),
        independent_unique_d1_games=len({(c['season'], r['matches'][0]) for c in checks for r in c.get('rows', [])
            if r['independent_from_result_source'] and not r['non_d1']}),
        independently_verified_phase_observations=dict(phase_counts), ncaa_opening_date_phase_checks=len(openings),
        seed_team_seasons=len(seed_rows), seed_seasons=seeds.SEASONS,
        seed_contract='Regional 1–4 seeds only; odds double per seed step; equal seeds 0.5; no tuning; national seeds unused.',
        unavailable_school_seasons=[{k:v for k,v in c.items() if k != 'rows'} for c in checks if c['status'] != 'pass'],
        limitations=['Retrospective publisher-dated evidence, not archived point-in-time certification.',
            'School sample is targeted, not a random national coverage estimate.',
            'Unlabeled schedule rows do not independently verify regular-season phase.',
            'No 2021 seed evidence; 2021 remains initialization only.',
            'No daily-updated v2 forecasts; suspended-game start and completion need separate daily event handling.',
            '2025 remains development; no 2026 modeling; no untouched holdout; no bracket simulation.'])
    if not summary['baseline_unchanged']:
        raise ValueError('Preserved baseline changed')
    OUT.mkdir(parents=True, exist_ok=True)
    for name, value in dict(summary=summary, official_checks=checks, timing_resolutions=corrected,
            seeds=seed_rows, opening_checks=openings, forecast_eligibility=eligibility,
            frozen_predictions=predictions, seed_comparison=joined, seed_exclusions=excluded, metrics=metrics).items():
        (OUT / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    for row in metrics:
        if row['stage'] == 'all_ncaa' and row['mode'] == 'regular_only':
            print(row['season'], {k:row[k] for k in ('baseline_elo', 'elo', 'seed')})

if __name__ == '__main__':
    run()
