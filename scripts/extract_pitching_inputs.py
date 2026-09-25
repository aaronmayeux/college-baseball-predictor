"""Verify cached structured pitcher BF/roles and summarize cutoff-safe workload."""
import argparse
import datetime as dt
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from audit_official_season_inventory import REPO
from audit_official_player_sample import read
from audit_player_source_expansion import audit
from audit_player_exceptions import run as exceptions
from extract_hitting_inputs import fingerprint
from pitching_inputs import structured_game, aggregate


def run(raw, exception_raw, season_raw=None):
    paths = [REPO/'historical/cutoffs.json', REPO/'historical/player_sources.json'] + [
        REPO/f'historical/{year}/{kind}.json' for year in ((2022, 2024, 2025) if season_raw else (2022, 2024)) for kind in ('games', 'teams')]
    before = {str(p.relative_to(REPO)): fingerprint(p) for p in paths}
    contract = json.loads(paths[0].read_text())
    original = audit(raw)
    with TemporaryDirectory() as directory:
        src = Path(directory)/'original.json'; dst = Path(directory)/'annotations.json'
        src.write_text(json.dumps(original))
        exceptions(SimpleNamespace(original_audit=src, raw_dir=exception_raw, output=dst))
        audits = json.loads(dst.read_text())['audits']
    cache = {}
    for p in sorted(raw.glob('*.meta.json')):
        m = json.loads(p.read_text()); cache.setdefault(m['url'], p.name.removesuffix('.meta.json'))
    teams = []
    for a in audits:
        config = a['config']; records = []
        for row in a['records']:
            r = dict(row, issues=list(row['issues']), pitchers=None, BF_check=None)
            try:
                text, meta = read(raw, cache[row['box_url']])
                if meta['url'] != row['box_url']:
                    raise ValueError('Wrong source URL')
                apps = [p for p in a['appearances']['pitching'] if p['box_url'] == row['box_url']]
                players, check = structured_game(text, row['box_url'], config, apps)
                r.update(pitchers=players, BF_check=check, source=meta)
            except (ValueError, KeyError, TypeError) as error:
                r['issues'].append('pitching: ' + str(error))
            records.append(r)
        # All mapped pitching counts, appearances and per-player GS already
        # reconcile against cumulative targets. Batting audit failures stay
        # visible but do not invalidate independently checked pitching.
        season_ok = a['comparisons']['pitching']['totals_match'] and all(r['BF_check'] for r in records)
        year = config['season']; games = json.loads((REPO/f'historical/{year}/games.json').read_text())
        cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        modes = {mode: aggregate(records, games, config['team_id'], cutoff, phases, bool(season_ok))
                 for mode, phases in contract['modes'].items()}
        teams.append(dict(team_id=config['team_id'], season=year, sources=a['sources'], records=records,
            pitching_season_check=a['comparisons']['pitching'], full_season_pass=bool(season_ok),
            forecast_modes=modes, batting_check_pass=a['comparisons']['batting']['totals_match']))
    if season_raw is not None:
        from lsu_pitching_inputs import run as lsu_run
        teams.append(lsu_run(season_raw, contract))
    if any(fingerprint(REPO/p) != sha for p, sha in before.items()):
        raise ValueError('Baseline/config changed during extraction')
    return dict(schema_version=1, dataset_version='pitching_inputs_pilot_v2', input_sha256=before,
        code_sha256={p.name:fingerprint(p) for p in sorted((REPO/'scripts').glob('*.py'))},
        point_in_time_certified=False, model_adjustments_enabled=False,
        limitation='Selected cached pilots; observed roles only, no ace/depth thresholds or rest inference.', teams=teams)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--season-raw-dir', type=Path, help='Include LSU from the season-appearance checkpoint')
    p.add_argument('--expansion-raw-dir', type=Path, required=True)
    p.add_argument('--exception-raw-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, default=REPO/'historical/model_inputs/pitching_inputs.json')
    args = p.parse_args(); output = args.output.resolve()
    if not output.is_relative_to((REPO/'historical/model_inputs').resolve()) or output.suffix != '.json':
        p.error('--output must be a JSON file under historical/model_inputs/')
    result = run(args.expansion_raw_dir, args.exception_raw_dir, args.season_raw_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    for t in result['teams']:
        print(t['team_id'], 'full season:', t['full_season_pass'])
        for mode, summary in t['forecast_modes'].items():
            print(mode, summary['expected_games'], 'complete:', summary['complete'])
