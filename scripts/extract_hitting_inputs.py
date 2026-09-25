"""Rebuild separate cutoff-specific hitting inputs from retained pilot evidence.

Never downloads, fits a model, or writes baseline/app data. Cumulative totals
are checks only. Outputs are retrospective reconstructions, not certified
point-in-time forecasts or nationally qualified model inputs.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from audit_official_player_sample import read
from audit_official_season_inventory import REPO
from audit_season_appearances import audit as season_audit
from audit_player_source_expansion import audit as expansion_audit
from audit_player_exceptions import run as exception_audit
from eligibility import reject
from hitting_inputs import FIELDS, rates, statcrew_team, cumulative_team


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate(records, games, team_id, cutoff, phases):
    """No partial-season rates: missing eligible games block the whole mode."""
    expected = {g['game_id'] for g in games
                if team_id in (g['team_a_id'], g['team_b_id']) and reject(g, cutoff, phases) is None}
    indexed = {}
    for row in records:
        if row['game_id'] is not None:
            if row['game_id'] in indexed:
                raise ValueError('Duplicate game ID')
            indexed[row['game_id']] = row
    missing = sorted(g for g in expected if g not in indexed or indexed[g]['issues'] or not indexed[g].get('counts'))
    result = dict(expected_games=len(expected), eligible_game_ids=sorted(expected),
                  blocked_game_ids=missing, complete=bool(expected) and not missing,
                  forecast_cutoff=cutoff.isoformat(), counts=None, rates=None)
    if not result['complete']:
        return result
    selected = [indexed[g]['counts'] for g in sorted(expected)]
    for c in selected:
        rates(c)
    counts = {f: sum(c[f] for c in selected) for f in FIELDS}
    for f in ('CI', 'PA'):
        counts[f] = sum(c[f] for c in selected) if all(c.get(f) is not None for c in selected) else None
    result.update(counts=counts, rates=rates(counts), PA_complete=counts['PA'] is not None)
    return result


def run(season_raw, expansion_raw, exception_raw):
    contract_path = REPO/'historical/cutoffs.json'
    inputs = [contract_path, REPO/'historical/player_sources.json'] + [
        REPO/f'historical/{year}/{kind}.json' for year in (2022, 2024, 2025) for kind in ('games', 'teams')]
    before = {str(p.relative_to(REPO)): fingerprint(p) for p in inputs}
    contract = json.loads(contract_path.read_text())
    lsu = next(a for a in season_audit(season_raw) if a['school'] == 'lsu')
    expanded = expansion_audit(expansion_raw)
    # Existing evidence-checked annotation resolves only the result join.
    with TemporaryDirectory() as directory:
        original = Path(directory)/'audit.json'; annotated = Path(directory)/'annotated.json'
        original.write_text(json.dumps(expanded, indent=2)+'\n')
        exception_audit(SimpleNamespace(original_audit=original, raw_dir=exception_raw, output=annotated))
        annotations = json.loads(annotated.read_text())
    most = next(a for a in annotations['audits'] if a['config']['key'] == 'missouri_state_2022')
    cache = {}
    for p in sorted(season_raw.glob('*.meta.json')):
        meta = json.loads(p.read_text())
        cache.setdefault(meta['url'], p.name.removesuffix('.meta.json'))
    lsu_rows = []
    for row in lsu['records']:
        record = dict(game_id=row['game_id'], box_url=row['box_url'], source_date=row['date'],
                      issues=list(row['issues']), counts=None, source=row.get('source'))
        try:
            text, meta = read(season_raw, cache[row['box_url']])
            if meta['url'] != row['box_url']:
                raise ValueError('Wrong source URL')
            record['source'] = meta
            record.update(statcrew_team(text, row))
        except (ValueError, KeyError) as error:
            record['issues'].append(str(error))
        lsu_rows.append(record)
    cume, cume_meta = read(season_raw, 'lsu_cume.html')
    target = cumulative_team(cume)
    observed = {f: sum(r['counts'][f] for r in lsu_rows if r['counts']) for f in FIELDS}
    full_match = lsu['season_counts_reconciled'] and all(r['counts'] is not None for r in lsu_rows) and observed == target
    # The known postseason date mismatch is retained; it does not prevent a
    # count-only season reconciliation or enter either pre-NCAA mode.
    lsu_check = dict(pass_counts=full_match, observed=observed, expected=target, source=cume_meta)
    most_rows = []
    for row in most['records']:
        apps = [p for p in most['appearances']['batting'] if p['box_url'] == row['box_url']]
        counts = {f: sum(p['counts'][f] for p in apps) for f in FIELDS} if apps else None
        if counts is not None:
            counts.update(PA=None, CI=None)  # not parsed/qualified in this adapter
            rates(counts)
        most_rows.append(dict(game_id=row['game_id'], box_url=row['box_url'], source_date=row['date'],
                              result_completion_date=row.get('result_completion_date'),
                              issues=list(row['issues']), counts=counts, source=row.get('source'),
                              timing_evidence=row.get('timing_evidence'),
                              original_game_id=row.get('original_game_id', row['game_id']),
                              original_issues=row.get('original_issues', row['issues'])))
    results = []
    for team_id, year, records, check in [('wn:LSU', 2025, lsu_rows, lsu_check),
            ('wn:Missouri-State', 2022, most_rows, dict(pass_counts=most['comparisons']['batting']['totals_match'],
                                                     sources=most['sources']))]:
        games = json.loads((REPO/f'historical/{year}/games.json').read_text())
        cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        modes = {mode: aggregate(records, games, team_id, cutoff, phases) for mode, phases in contract['modes'].items()}
        if not check['pass_counts']:
            for m in modes.values():
                m.update(complete=False, counts=None, rates=None, block_reason='full_season_count_reconciliation_failed')
        results.append(dict(team_id=team_id, season=year, full_season_check=check, forecast_modes=modes, records=records))
    if any(fingerprint(REPO/p) != sha for p, sha in before.items()):
        raise ValueError('Baseline/config changed during extraction')
    return dict(schema_version=1, dataset_version='hitting_inputs_pilot_v1', input_sha256=before,
                code_sha256={p.name: fingerprint(p) for p in (Path(__file__), Path(__file__).with_name('hitting_inputs.py'))},
                point_in_time_certified=False, model_adjustments_enabled=False,
                limitation='Two pilot teams only; no national coverage, fitting, opponent/park adjustment or rest inference.',
                teams=results)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--season-raw-dir', required=True, type=Path)
    p.add_argument('--expansion-raw-dir', required=True, type=Path)
    p.add_argument('--exception-raw-dir', required=True, type=Path)
    p.add_argument('--output', type=Path, default=REPO/'historical/model_inputs/hitting_inputs.json')
    args = p.parse_args()
    # Avoid accidental overwrites of source or model inputs, even via a CLI typo.
    output = args.output.resolve()
    allowed = (REPO/'historical/model_inputs').resolve()
    if not output.is_relative_to(allowed) or output.suffix != '.json':
        p.error('--output must be a JSON file under historical/model_inputs/')
    result = run(args.season_raw_dir, args.expansion_raw_dir, args.exception_raw_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    for team in result['teams']:
        print(team['team_id'], 'season counts:', team['full_season_check']['pass_counts'])
        for mode, summary in team['forecast_modes'].items():
            print(mode, summary['expected_games'], 'complete:', summary['complete'], summary['rates'])
