"""Offline LSU 2025 game-link reconciliation. Links are not player appearances."""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'historical'))
from eligibility import reject
from audit_official_player_sample import read

INDEX_URL = 'https://static.lsusports.net/assets/docs/bb/25stats/teamstat.htm'
# Explicit source spellings; verified against dated opponents and reciprocal scores.
ALIASES = {'Sam Houston': 'wn:Sam-Houston-State',
           'UL Lafayette': 'wn:Louisiana',
           'Southeastern La': 'wn:Southeastern-Louisiana'}


def plain(value):
    return ' '.join(html.unescape(re.sub('<[^>]*>', ' ', value)).split())


def parse_index(text, url, season):
    rows = []
    for raw in re.findall(r'<tr\b[^>]*>(.*?)</tr>', text, re.I | re.S):
        if not re.search(r'>\s*Box score\s*</a>', raw, re.I):
            continue
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', raw, re.I | re.S)
        links = re.findall(r'href=["\']([^"\']+)["\'][^>]*>\s*Box score\s*</a>', raw, re.I)
        if len(cells) != 4 or len(links) != 1:
            raise ValueError('Unrecognized box-link row')
        date = dt.datetime.strptime(plain(cells[0]), '%b %d, %Y').date()
        if date.year != season:
            raise ValueError('Wrong archive season')
        result = re.fullmatch(r'(.+?) (\d+), (.+?) (\d+)', plain(cells[2]))
        if not result:
            raise ValueError('Unrecognized score')
        a, ra, b, rb = result.groups()
        rows.append(dict(date=date.isoformat(), teams=[a, b], runs=[int(ra), int(rb)],
                         source_result=plain(cells[2]), box_url=urljoin(url, links[0])))
    if not rows:
        raise ValueError('No game rows')
    return rows


def reconcile(rows, games, identities, team_id):
    expected = [g for g in games if team_id in (g['team_a_id'], g['team_b_id'])]
    urls = Counter(r['box_url'] for r in rows)
    matched = Counter()
    output = []
    for row in rows:
        ids = [identities.get(name) for name in row['teams']]
        reasons = []
        if None in ids or len(set(ids)) != 2 or team_id not in ids:
            reasons.append('unmapped_or_invalid_teams')
            candidates = []
        else:
            scores = dict(zip(ids, row['runs']))
            candidates = [g for g in expected if g['game_date'] == row['date']
                          and {g['team_a_id'], g['team_b_id']} == set(ids)
                          and scores[g['team_a_id']] == g['runs_a']
                          and scores[g['team_b_id']] == g['runs_b']]
        if urls[row['box_url']] != 1:
            reasons.append('duplicate_box_url')
        if len(candidates) != 1:
            reasons.append('ambiguous_or_missing_baseline_match')
        game_id = candidates[0]['game_id'] if len(candidates) == 1 else None
        if game_id:
            matched[game_id] += 1
        output.append(dict(row, game_id=game_id, issues=reasons))
    for row in output:
        if row['game_id'] and matched[row['game_id']] > 1:
            row['issues'].append('reused_baseline_game')
    missing = sorted(g['game_id'] for g in expected if not matched[g['game_id']])
    return dict(index_rows=len(rows), baseline_games=len(expected),
                matched_games=len(matched), missing_baseline_games=missing,
                inventory_pass=bool(expected) and not missing and not any(r['issues'] for r in output),
                games=output)


def audit(root):
    text, meta = read(root, 'lsu_index_2025.html')
    if meta['url'] != INDEX_URL:
        raise ValueError('Unexpected index URL')
    paths = [REPO/'historical/2025/games.json', REPO/'historical/2025/teams.json',
             REPO/'historical/cutoffs.json']
    games, teams, contract = [json.loads(p.read_text()) for p in paths]
    identities = {t['name']: t['team_id'] for t in teams}
    if any(t['season'] != 2025 for t in teams + games):
        raise ValueError('Wrong baseline season')
    identities.update(ALIASES)
    result = reconcile(parse_index(text, meta['url'], 2025), games, identities, 'wn:LSU')
    cached = set()
    for path in sorted(root.glob('*.meta.json')):
        m = json.loads(path.read_text())
        if m.get('http_status') == 200 and m.get('url') in {r['box_url'] for r in result['games']}:
            read(root, path.name.removesuffix('.meta.json'))
            cached.add(m['url'])
    by_id = {g['game_id']: g for g in games}
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2025']['forecast_cutoff'])
    modes = {}
    for mode, stages in contract['modes'].items():
        eligible = [r for r in result['games'] if not r['issues']
                    and reject(by_id[r['game_id']], cutoff, stages) is None]
        expected_eligible = [g for g in games if 'wn:LSU' in (g['team_a_id'], g['team_b_id'])
                             and reject(g, cutoff, stages) is None]
        modes[mode] = dict(expected_eligible_games=len(expected_eligible),
                           eligible_inventory_games=len(eligible),
                           cached_box_responses=sum(r['box_url'] in cached for r in eligible))
    for row in result['games']:
        row['box_response_cached'] = row['box_url'] in cached
        row['appearances_verified'] = False
    result.update(season=2025, team_id='wn:LSU', source=meta,
                  baseline_sha256={str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  aliases=ALIASES, cached_box_responses=len(cached), forecast_modes=modes,
                  appearance_coverage_qualified=False, point_in_time_certified=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=REPO/'historical/statistics_discovery/raw')
    args = parser.parse_args()
    print(json.dumps(audit(args.raw_dir), indent=2))
