"""Offline development export from the existing audited baseline and v2 evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'historical'), str(ROOT/'historical/validation_v2')]
from baseline import load_games
from evidence import overlay, verify_timing
from team_fallback import MODES, reconstruct
from validation_v2 import run as validation
from reconcile import internal
import independent
import seeds
from tournament.engine import forecast, probability
from tournament.field import build_regions


def build():
    before = validation.hashes()
    audit = json.loads((ROOT/'historical/coverage_validation.json').read_text())
    if len(audit) != 5 or {r['season'] for r in audit} != set(range(2021, 2026)) or not all(r['pass'] for r in audit):
        raise ValueError('Baseline coverage gate failed')
    if not json.loads((ROOT/'historical/correction_evidence_checks.json').read_text())['pass']:
        raise ValueError('Baseline correction gate failed')
    refs = verify_timing()
    if any(r['status'] == 'review' for r in independent.run()):
        raise ValueError('Independent schedule check failed')
    contract = json.loads((ROOT/'historical/cutoffs.json').read_text())
    selections = seeds.load(contract)
    if any(r['status'] != 'pass' for r in validation.opening_checks(selections, contract)):
        raise ValueError('Opening matchup check failed')
    selected = [r for r in selections if r['season'] == 2025]
    regions = build_regions(selected, internal)
    games = {y: overlay(load_games(y), refs) for y in range(2021, 2026)}
    reference, _, _ = validation.evaluate(contract, refs)
    modes = {}
    for mode in MODES:
        state, history = reconstruct(games, contract, 2025, mode)
        ratings = {r['team_id']: state.r.get(r['team_id']) for r in selected}
        if any(state.n.get(t, 0) <= 0 or rating is None for t, rating in ratings.items()):
            raise ValueError('Field team missing eligible current-season results')
        sample = [r for r in reference if r['season'] == 2025 and r['mode'] == mode]
        if not sample:
            raise ValueError('Missing v2 comparison sample')
        error = max(abs(probability(ratings[r['team_a_id']], ratings[r['team_b_id']]) - r['elo']) for r in sample)
        if error > 1e-12:
            raise ValueError('Ratings diverged from existing v2 probabilities')
        modes[mode] = dict(forecast(regions, ratings), ratings=ratings, history=history,
                           eligible_games={t: state.n[t] for t in ratings},
                           verification=dict(v2_games=len(sample), max_probability_difference=error))
    if validation.hashes() != before:
        raise ValueError('Preserved baseline changed')
    code = list((ROOT/'tournament').glob('*.py')) + [ROOT/'historical'/n for n in ('baseline.py', 'team_fallback.py', 'eligibility.py', 'cutoffs.json')]
    return dict(schema_version=1, season=2025, development_only=True,
        model='fixed_neutral_elo_timing_v2', engine_version=1,
        forecast_cutoff=contract['seasons']['2025']['forecast_cutoff'],
        availability_rule=contract['availability_rule'], regions=regions,
        teams={r['team_id']: dict(name=r['source_name'], regional_seed=r['regional_seed']) for r in selected},
        modes=modes, provenance=dict(baseline_sha256=before, timing_evidence=refs,
            selection=selected[0]['provenance'],
            code_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(code)}),
        limitations=['2025 historical development demonstration; not an untouched accuracy test.',
            'Cutoff reconstructed from dates, not certified publication times.',
            'Fixed neutral team Elo; pitcher availability, home advantage and richer profiles are unmodeled.',
            'Exact odds under independent games and fixed strength; no calibrated strength uncertainty.',
            'Fresh nationwide data ingestion is not certified.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'app/data/forecast.json')
    parser.add_argument('--standalone', type=Path, help='Also write a self-contained HTML app')
    args = parser.parse_args()
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    if args.standalone:
        template = (ROOT/'app/index.html').read_text()
        payload = json.dumps(result).replace('<', chr(92) + 'u003c')
        html = template.replace('<script id="embedded-forecast" type="application/json">null</script>',
            '<script id="embedded-forecast" type="application/json">' + payload + '</script>')
        args.standalone.parent.mkdir(parents=True, exist_ok=True)
        args.standalone.write_text(html)
    for mode, value in result['modes'].items():
        champion = value['picks']['champion']
        print(mode, result['teams'][champion]['name'], len(value['picks']['games']), 'picked games;', value['verification'])
    print('Wrote', args.output)


if __name__ == '__main__':
    main()
