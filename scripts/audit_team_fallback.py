"""Validate all-field fallback mechanics against the preserved v2 evaluation.

Offline only. Outputs belong outside Git; no player features or source totals
enter ratings. The original baseline and v2 files are read, never rewritten.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO/'historical'), str(REPO/'historical/validation_v2')]
from baseline import load_games, metric
from evidence import overlay, verify_timing
from team_fallback import MODES, reconstruct, snapshot, matchup
from validation_v2 import run as validation
import independent
import seeds


def audit(field):
    before = validation.hashes()
    coverage = json.loads((REPO/'historical/coverage_validation.json').read_text())
    if {r['season'] for r in coverage} != set(range(2021, 2026)) or not all(r['pass'] for r in coverage):
        raise ValueError('Baseline coverage gate failed')
    if not json.loads((REPO/'historical/correction_evidence_checks.json').read_text())['pass']:
        raise ValueError('Correction gate failed')
    refs = verify_timing()
    if any(r['status'] == 'review' for r in independent.run()):
        raise ValueError('Independent comparison gate failed')
    contract = json.loads((REPO/'historical/cutoffs.json').read_text())
    selected = seeds.load(contract)
    if any(r['status'] != 'pass' for r in validation.opening_checks(selected, contract)):
        raise ValueError('Opening game/phase gate failed')
    expected = {r['team_id'] for r in selected if r['season'] == 2025}
    if {t['stable_team_id'] for t in field['teams']} != expected:
        raise ValueError('Field differs from independent NCAA selection')
    from reconcile import internal
    if any(internal(t['team_id'].removeprefix('wn:')) != t['stable_team_id'] for t in field['teams']):
        raise ValueError('Provider/stable identity mismatch')
    games = {y: overlay(load_games(y), refs) for y in range(2021, 2026)}
    reference, _, _ = validation.evaluate(contract, refs)
    modes = {}
    for mode in MODES:
        state, history = reconstruct(games, contract, 2025, mode)
        teams = snapshot(field, state, mode)
        by_id = {t['stable_team_id']: t for t in teams}
        pairs = []
        for a, b in itertools.combinations(teams, 2):
            result = matchup(a, b)
            if result['probability_a'] is not None:
                reverse = matchup(b, a)['probability_a']
                if not 0 < result['probability_a'] < 1 or abs(result['probability_a'] + reverse - 1) > 1e-12:
                    raise ValueError('Invalid/complementary matchup probability')
            pairs.append(dict(team_a_id=a['team_id'], team_b_id=b['team_id'], **result))
        sample = [r for r in reference if r['season'] == 2025 and r['mode'] == mode]
        if not sample or any(r['team_a_id'] not in by_id or r['team_b_id'] not in by_id for r in sample):
            raise ValueError('Missing observed tournament matchup')
        errors = []
        for row in sample:
            p = matchup(by_id[row['team_a_id']], by_id[row['team_b_id']])['probability_a']
            if p is None:
                raise ValueError('Blocked observed tournament matchup')
            errors.append(abs(p - row['elo']))
        if max(errors) > 1e-12:
            raise ValueError('Fallback diverged from fixed v2 Elo')
        modes[mode] = dict(teams=teams, matchups=pairs, history=history,
            summary=dict(teams=len(teams), fallback_status=dict(Counter(t['fallback_status'] for t in teams)),
                unique_matchups=len(pairs), available_matchups=sum(p['probability_a'] is not None for p in pairs),
                observed_ncaa_games=len(sample), maximum_v2_probability_difference=max(errors),
                retrospective_game_metrics={k: metric(sample, k) for k in ('elo', 'win_rate', 'coin')}))
    if validation.hashes() != before:
        raise ValueError('Baseline changed')
    return dict(schema_version=1, season=2025, development_only=True, model='fixed_neutral_elo_timing_v2',
        complete_bracket_ready=False, production_fallback_validated=False, requests_performed=0,
        baseline_sha256=before, modes=modes,
        limitations=['Matchup mechanics only; no tournament engine or advancement validation.',
            'Unknown player availability remains unmodeled; no calibrated uncertainty interval or rest claim.',
            'Historical cutoff reconstruction, not point-in-time certification; 2025 development, no 2026 use.'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--field-audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = audit(json.loads(args.field_audit.read_text()))
    result['input_sha256'] = {args.field_audit.name: hashlib.sha256(args.field_audit.read_bytes()).hexdigest(),
        'cutoffs.json': hashlib.sha256((REPO/'historical/cutoffs.json').read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({m: v['summary'] for m, v in result['modes'].items()}, indent=2))
