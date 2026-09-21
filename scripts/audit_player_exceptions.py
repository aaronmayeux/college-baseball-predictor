"""Separate, evidence-checked annotations for the two source-expansion exceptions.

Never alters the baseline or the original audit. Completion dates qualify
result joins only, not pitcher work dates or rested status.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from html import unescape
from audit_official_player_sample import read
from audit_official_season_inventory import REPO

DUKE = 'https://goduke.com/sports/baseball/stats/2024/davidson/boxscore/21664'
RECAP = 'https://goredbirds.com/news/2022/5/25/baseball-illinois-state-out-of-mvc-tournament-after-loss-delays-postponement.aspx'


def checked(root, key, url, phrases):
    html, meta = read(root, key)
    if meta['url'] != url:
        raise ValueError('Wrong evidence URL')
    text = re.sub(r'\s+', ' ', unescape(re.sub('<[^>]+>', ' ', html))).lower()
    if any(p.lower() not in text for p in phrases):
        raise ValueError('Expected independent evidence missing')
    return meta


def annotate(original, games, evidence):
    result = deepcopy(original)
    by_key = {a['config']['key']: a for a in result}
    davidson = by_key['davidson_2024']
    differences = davidson['comparisons']['batting']['differences']
    if len(differences) != 1 or differences[0]['player'] != 'jake dunagan' or differences[0]['observed']['appearances'] != 1:
        raise ValueError('Davidson exception changed')
    davidson['exception_resolution'] = dict(status='appearance_independently_confirmed_cumulative_omission_unresolved',
        evidence=evidence['duke'], cumulative_repaired=False)
    most = by_key['missouri_state_2022']
    matches = [g for g in games if g['game_id'] == 'wn:2022:40418']
    if len(matches) != 1:
        raise ValueError('Missing unique baseline game')
    game = matches[0]
    if game['game_date'] != '2022-05-25' or {game['team_a_id'], game['team_b_id']} != {'wn:Missouri-State', 'wn:Illinois-State'}:
        raise ValueError('Baseline identity/date changed')
    score = {game['team_a_id']: game['runs_a'], game['team_b_id']: game['runs_b']}
    if score != {'wn:Missouri-State': 9, 'wn:Illinois-State': 4}:
        raise ValueError('Baseline score changed')
    rows = [r for r in most['records'] if r['date'] == '2022-05-24' and r['teams'] == ['Missouri State', 'Illinois State'] and r['runs'] == [9, 4]]
    if len(rows) != 1 or rows[0]['issues'] != ['ambiguous_or_missing_baseline_match'] or not rows[0]['parsed']:
        raise ValueError('Original exception changed')
    row = rows[0]
    row.update(original_game_id=row['game_id'], original_issues=list(row['issues']),
        game_id=game['game_id'], issues=[], result_completion_date='2022-05-25',
        source_start_date='2022-05-24', actual_player_work_dates='unknown', timing_evidence=evidence['recap'])
    added = 0
    for kind, apps in most['appearances'].items():
        for app in apps:
            if app['box_url'] == row['box_url']:
                if app['game_id'] is not None or app['actual_appearance_date'] is not None:
                    raise ValueError('Unexpected existing appearance mapping')
                app.update(original_game_id=None, game_id=game['game_id'], result_completion_date='2022-05-25')
                added += kind == 'pitching'
    mode = most['forecast_modes']['conference_inclusive']
    if (mode['expected_games'], mode['verified_game_boxes']) != (57, 56):
        raise ValueError('Mode denominator changed')
    mode.update(verified_game_boxes=57, complete=True, pitching_appearances=mode['pitching_appearances'] + added)
    most['exception_resolution'] = dict(status='start_completion_distinction_verified', evidence=evidence['recap'], baseline_date_changed=False)
    return dict(schema_version=1, dataset_version='player_exception_annotations_v1', audits=result,
                limitation='Game-result joins only; original inventory remains preserved; no rest/feature qualification')


def run(a):
    evidence = dict(duke=checked(a.raw_dir, 'duke_box.html', DUKE,
        ['DUNAGAN, J pinch ran for FRIEND, J.', 'DUNAGAN, J to cf.', 'WOODALL, JD pinch hit for DUNAGAN, J.']),
        recap=checked(a.raw_dir, 'illinois_recap.html', RECAP,
        ['9-4 loss to Missouri State', '20 hours and 50 minutes', 'postponement to Wednesday', '5/25/2022']))
    # His pitching/fielding entries establish identity, not batting GP equivalence.
    from sidearm_structured import payload, only
    url = 'https://davidsonwildcats.com/sports/baseball/stats/2024'
    html, meta = read(a.raw_dir, 'davidson_cumulative.html')
    if meta['url'] != url:
        raise ValueError('Wrong Davidson cumulative source')
    cume = only(payload(html, url)['statsSeason']['cumulativeStats'].values())
    individual = cume['overallIndividualStats']['individualStats']
    fielding = only(p for p in individual['individualFieldingStats'] if p['playerName'] == 'Dunagan, Jake')
    pitching = only(p for p in individual['individualPitchingStats'] if p['playerName'] == 'Dunagan, Jake')
    if any(p['playerName'] == 'Dunagan, Jake' for p in individual['individualHittingStats']):
        raise ValueError('Batting omission changed; review new snapshot')
    if fielding['playerRosterBioId'] != '9947' or pitching['playerRosterBioId'] != '9947':
        raise ValueError('Player identity changed')
    evidence['davidson'] = dict(source=meta, roster_id='9947',
        fielding_gp=fielding['gamesPlayed'], pitching_appearances=pitching['appearances'],
        batting_entry_present=False, provider_batting_inclusion_rule='unverified')
    games_path = REPO / 'historical/2022/games.json'
    result = annotate(json.loads(a.original_audit.read_text()), json.loads(games_path.read_text()), evidence)
    result['davidson_identity_evidence'] = evidence['davidson']
    result['input_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.original_audit, games_path]}
    a.output.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original-audit', type=Path, required=True)
    p.add_argument('--raw-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    run(p.parse_args())
