"""Offline archive qualification; never treats cumulative totals as features.

Game inventory and additive cumulative sums are separate from unverified
per-player appearance histories. Does not collect or modify baseline files.
"""
import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin
from audit_official_player_sample import read
from audit_official_season_inventory import REPO, parse_index, reconcile, plain
from eligibility import reject
from statcrew_archives import cumulative, conference_index

RECAP = 'https://seminoles.com/news/2025/5/4/baseball-series-evened-as-no-5-fsu-edged-by-no-3-clemson-in-suspended-game'


def clemson_completion(inventory, games, evidence):
    """Resolve only the verified 6-3 result; preserve every strict source row."""
    original = [r for r in inventory['games'] if r['date'] == '2025-05-03' and r['teams'] == ['Clemson', 'Florida State'] and r['runs'] == [6, 3]]
    candidates = [g for g in games if g['game_date'] == '2025-05-04' and {g['team_a_id'], g['team_b_id']} == {'wn:Clemson', 'wn:Florida-State'} and {g['team_a_id']: g['runs_a'], g['team_b_id']: g['runs_b']} == {'wn:Clemson': 6, 'wn:Florida-State': 3}]
    if len(original) != 1 or len(candidates) != 1 or original[0]['issues'] != ['ambiguous_or_missing_baseline_match']:
        raise ValueError('Unexpected Clemson date exception')
    return dict(original_record=deepcopy(original[0]), game_id=candidates[0]['game_id'],
        start_date='2025-05-03', completion_date='2025-05-04', reason='independently_confirmed_overnight_suspension',
        actual_pitcher_work_dates=None, recent_workload='unknown', evidence=evidence)


def audit(raw):
    paths = [REPO/'historical/player_sources.json', REPO/'historical/2025/games.json', REPO/'historical/2025/teams.json', REPO/'historical/cutoffs.json']
    registry, games, teams, contract = [json.loads(p.read_text()) for p in paths]
    if any(x['season'] != 2025 for x in games+teams): raise ValueError('Wrong baseline season')
    configs = [c for c in registry['entries'] if c['adapter'] == 'statcrew_archive_v1']
    if {c['key'] for c in configs} != {'clemson_2025', 'little_rock_2025'}: raise ValueError('Unreviewed archive configuration')
    output = []
    for config in configs:
        year = config['season'];name = config['team_name'];team_id = config['team_id']
        if year != 2025: raise ValueError('Wrong configured season')
        index, im = read(raw, config['schedule_key']);cume, cm = read(raw, config['cumulative_key'])
        if im['url'] != config['schedule_url'] or cm['url'] != config['cumulative_url']: raise ValueError('Source URL mismatch')
        if config['schedule_format'] == 'statcrew_index':
            if '<title>2025 Clemson Baseball</title>' not in index: raise ValueError('Wrong historical index identity')
            links = [urljoin(im['url'], u) for u in re.findall(r'href=["\']([^"\']+)', index, re.I)]
            if cm['url'] not in links or '<title>Clemson - Season Statistics</title>' not in cume: raise ValueError('Unlinked or wrong cumulative identity')
            source_rows = parse_index(index, im['url'], year)
        else:
            source_rows = conference_index(index, im['url'], year, name)
        if len(source_rows) != config['expected_completed_games']: raise ValueError('Archive inventory count changed')
        identities = {t['name']: t['team_id'] for t in teams}
        # Upper-case labels are a presentation convention, not fuzzy matching.
        for n, ident in list(identities.items()):
            if n.upper() in identities and identities[n.upper()] != ident: raise ValueError('Ambiguous uppercase identity')
            identities[n.upper()] = ident
        for n, ident in config.get('team_aliases', {}).items():
            if ident not in identities.values() or n in identities and identities[n] != ident: raise ValueError('Invalid explicit alias')
            identities[n] = ident
        strict = reconcile(source_rows, games, identities, team_id)
        groups = cumulative(cume, cm['url'], year)
        annotations = []
        if config['key'] == 'clemson_2025':
            recap, rm = read(raw, 'fsu_clemson_recap.html')
            if rm['url'] != RECAP: raise ValueError('Unexpected independent recap')
            text = plain(recap)
            if not all(phrase in text for phrase in ['6-3', 'started on Saturday and was completed on Sunday', '16 hour, 46 minute delay']):
                raise ValueError('Suspension evidence changed')
            annotations = [clemson_completion(strict, games, rm)]
        # A separate view uses confirmed result completion; original rows are unchanged.
        accepted = {r['game_id'] for r in strict['games'] if not r['issues']}
        accepted.update(a['game_id'] for a in annotations)
        cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        modes = {}
        for mode, stages in contract['modes'].items():
            expected = {g['game_id'] for g in games if team_id in (g['team_a_id'], g['team_b_id']) and reject(g, cutoff, stages) is None}
            matched = accepted & expected
            modes[mode] = dict(expected_games=len(expected), verified_result_inventory=len(matched),
                inventory_complete=bool(expected) and matched == expected,
                player_histories_verified=False, recent_workload='unknown', needs_validated_fallback=True)
        output.append(dict(config=config, evidence=dict(index=im, cumulative=cm), strict_inventory=strict,
            completion_annotations=annotations, cumulative_groups=groups,
            appearance_histories_reconciled=False, feature_qualified=False, forecast_modes=modes))
    return dict(schema_version=1, development_only=True, season=2025,
        input_sha256={str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, archives=output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();result = audit(a.raw_dir)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    for row in result['archives']:
        print(row['config']['key'], row['strict_inventory']['matched_games'], 'strict matches;', len(row['completion_annotations']), 'completion annotations;', row['forecast_modes'])
