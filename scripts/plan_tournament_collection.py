"""Offline workload sizing, not permission or a downloader.

Counts known D1 games only. Non-D1 workload, unresolved inventories, retries,
PDFs and additional resources can increase the eventual request volume.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from audit_official_season_inventory import REPO
sys.path.insert(0, str(REPO/'historical'))
from eligibility import reject


def plan(field, games, contract):
    teams = field['teams']
    ids = [t['team_id'] for t in teams]
    if field['season'] != 2025 or len(ids) != 64 or len(set(ids)) != 64:
        raise ValueError('Expected complete 2025 development field')
    if any(t['season'] != 2025 for t in teams) or any(g['season'] != 2025 for g in games):
        raise ValueError('Mixed seasons')
    if len({g['game_id'] for g in games}) != len(games):
        raise ValueError('Duplicate baseline games')
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2025']['forecast_cutoff'])
    modes = {'full_season_audit': games}
    for mode in ('regular_only', 'conference_inclusive'):
        modes[mode] = [g for g in games if reject(g, cutoff, contract['modes'][mode]) is None]
    rows = []
    for team in teams:
        counts = {mode: sum(team['team_id'] in (g['team_a_id'], g['team_b_id']) for g in gs) for mode, gs in modes.items()}
        rows.append(dict(team_id=team['team_id'], name=team['name'], known_d1_games=counts,
            schedule_status=team['schedule_status'], cumulative_status=team['cumulative_status'],
            terms_status=team['terms_status'], collection_enabled=False,
            recent_workload='unknown', fallback='team_level_model_requires_validation'))
    summary = {}
    for mode, gs in modes.items():
        touched = [g for g in gs if set(ids).intersection((g['team_a_id'], g['team_b_id']))]
        summary[mode] = dict(team_game_sides=sum(r['known_d1_games'][mode] for r in rows),
            unique_games=len(touched), teams_with_no_known_games=[r['team_id'] for r in rows if not r['known_d1_games'][mode]])
    return dict(schema_version=1, season=2025, development_only=True, collection_enabled=False,
        request_count_certified=False, summary=summary, teams=rows,
        scope='Known D1 game counts, not an executable request budget. Shared boxes require both sides qualified; non-D1 physical workload and unresolved sources remain additional.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--field-audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    paths = [a.field_audit, REPO/'historical/2025/games.json', REPO/'historical/cutoffs.json']
    result = plan(*(json.loads(p.read_text()) for p in paths))
    result['input_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['summary'], indent=2))
