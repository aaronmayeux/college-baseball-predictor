"""Bounded 2021–2025 ESPN coverage pilot. Offline by default; never fits features."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

REPO = Path(__file__).resolve().parents[1]
API = 'https://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/'
MAJOR = {'SEC', 'ACC', 'Big 12', 'Big Ten', 'Pac-12'}
# Explicit provider-name equivalences; no fuzzy joins or current affiliations.
ALIASES = {'UConn': 'Connecticut', 'NC State': 'North Carolina State',
           'Ole Miss': 'Mississippi', 'Miami': 'Miami (FL)', 'Pitt': 'Pittsburgh',
           'UL Monroe': 'Louisiana-Monroe', 'UL Lafayette': 'Louisiana',
           'UT Martin': 'Tennessee-Martin', 'App State': 'Appalachian State',
           'Southern Miss': 'Southern Mississippi', 'Hawai\u0027i': 'Hawaii'}

def digest(b):
    return hashlib.sha256(b).hexdigest()


def read_or_fetch(root, key, url, collect=False):
    path = root / key
    mp = root / (key + '.meta.json')
    if mp.exists():
        meta = json.loads(mp.read_text())
        if meta['url'] != url:
            raise ValueError('Source URL changed: ' + key)
        if meta.get('sha256'):
            raw = path.read_bytes()
            if digest(raw) != meta['sha256']:
                raise ValueError('Source hash changed: ' + key)
        else:
            raw = b''
    elif not collect:
        raise FileNotFoundError(mp)
    else:
        root.mkdir(parents=True, exist_ok=True)
        meta = dict(url=url, retrieved_at=datetime.now(timezone.utc).isoformat())
        raw = b''
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CollegeBaseballCoverageAudit/0.1'})
            with urllib.request.urlopen(req, timeout=25) as response:
                raw = response.read()
                meta.update(http_status=response.status, final_url=response.url)
        except urllib.error.HTTPError as error:
            raw = error.read()
            meta.update(http_status=error.code, error=str(error))
        except (OSError, TimeoutError) as error:
            meta['error'] = str(error)
        if raw:
            path.write_bytes(raw)
            meta.update(sha256=digest(raw), bytes=len(raw))
        mp.write_text(json.dumps(meta, indent=2) + '\n')
    if meta.get('http_status') != 200:
        return None, meta
    try:
        return json.loads(raw), meta
    except ValueError:
        return None, dict(meta, parse_error='non-JSON response')


def verify_raw(root):
    """Validate all retained probes, including exploratory requests outside sampling."""
    count = 0
    for mp in sorted(root.glob('*.meta.json')):
        meta = json.loads(mp.read_text())
        if not meta.get('url') or not meta.get('retrieved_at'):
            raise ValueError('Missing provenance: ' + mp.name)
        if meta.get('sha256'):
            raw = (root/mp.name.removesuffix('.meta.json')).read_bytes()
            if digest(raw) != meta['sha256']:
                raise ValueError('Source hash changed: ' + mp.name)
        elif meta.get('http_status') == 200:
            raise ValueError('Successful response lacks source hash: ' + mp.name)
        count += 1
    return count


def sample_dates(year):
    # First Tuesday and Friday of March and May, fixed before inspecting boxes.
    for month in (3, 5):
        for weekday in (1, 4):
            start = date(year, month, 1)
            yield start + timedelta(days=(weekday - start.weekday()) % 7)


def outs(value):
    if not re.fullmatch(r'\d+(?:\.[012])?', str(value)):
        raise ValueError('Invalid baseball innings: ' + str(value))
    whole, _, part = str(value).partition('.')
    return 3 * int(whole) + int(part or 0)


def numeric(value):
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False


def inspect_summary(data, event, year):
    header = data.get('header', {})
    if str(header.get('id')) != event or header.get('season', {}).get('year') != year:
        return dict(status='identity_or_season_rejected')
    competition = header.get('competitions', [{}])[0]
    if not competition.get('date', '').startswith(str(year)):
        return dict(status='date_rejected')
    teams = []
    for team in data.get('boxscore', {}).get('players', []):
        item = dict(team_id=team['team']['id'], team=team['team'].get('location'), groups={})
        for group in team.get('statistics', []):
            kind = group.get('type')
            if kind not in {'batting', 'pitching'}:
                continue
            rows = group.get('athletes', [])
            labels = group.get('labels', [])
            values = [dict(zip(labels, r.get('stats', []))) for r in rows]
            complete = {k: sum(numeric(v.get(k)) for v in values) for k in labels}
            ids = [r.get('athlete', {}).get('id') for r in rows]
            g = dict(rows=len(rows), labels=labels, numeric_cells=complete,
                     ids_present=sum(bool(i) for i in ids), unique_ids=len(set(i for i in ids if i)),
                     starters=sum(r.get('starter') is True for r in rows),
                     row_width_errors=sum(len(r.get('stats', [])) != len(labels) for r in rows))
            if kind == 'pitching':
                try:
                    g['outs'] = sum(outs(v['IP']) for v in values) if rows else None
                except (ValueError, KeyError):
                    g['outs'] = None
                    g['invalid_innings'] = True
                g['positive_pitch_counts'] = sum(numeric(v.get('PC')) and float(v['PC']) > 0 for v in values)
            totals = next((t for t in data.get('boxscore', {}).get('teams', [])
                           if t['team']['id'] == team['team']['id']), {})
            totals_group = next((t for t in totals.get('statistics', []) if t.get('name') == kind), {})
            total_values = {t['name']: t.get('displayValue') for t in totals_group.get('stats', [])}
            mapping = {'AB': 'atBats', 'R': 'runs', 'H': 'hits', 'HR': 'homeRuns',
                       'BB': 'walks', 'K': 'strikeouts', 'ER': 'earnedRuns'}
            g['totals_checks'] = {}
            for label, name in mapping.items():
                if rows and complete.get(label) == len(rows) and numeric(total_values.get(name)):
                    g['totals_checks'][label] = sum(float(v[label]) for v in values) == float(total_values[name])
            if kind == 'pitching' and rows and g.get('outs') is not None and numeric(total_values.get('thirdInnings')):
                g['totals_checks']['outs'] = g['outs'] == float(total_values['thirdInnings'])
            item['groups'][kind] = g
        teams.append(item)
    team_stats = []
    for team in data.get('boxscore', {}).get('teams', []):
        groups = {g['name']: {s['name']: s.get('displayValue') for s in g.get('stats', [])}
                  for g in team.get('statistics', [])}
        team_stats.append(dict(team_id=team['team']['id'], groups=groups))
    return dict(status='ok', date=competition['date'], teams=teams, team_stats=team_stats,
                play_records=len(data.get('plays', [])),
                venue_present=bool(data.get('gameInfo', {}).get('venue')),
                completed=competition.get('status', {}).get('type', {}).get('completed'))


def run(root, collect=False):
    summaries, boards = [], []
    if collect:
        # Date requests are independent; cap concurrency, retain every failure.
        dates = [d for y in range(2021, 2026) for d in sample_dates(y)]
        def fetch_board(day):
            key = 'scoreboard_' + day.strftime('%Y%m%d') + '.json'
            url = API + 'scoreboard?dates=' + day.strftime('%Y%m%d') + '&limit=1000'
            return read_or_fetch(root, key, url, True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(fetch_board, dates))
    for year in range(2021, 2026):
        roster_path = REPO / f'historical/{year}/teams.json'
        games_path = REPO / f'historical/{year}/games.json'
        roster = json.loads(roster_path.read_text())
        lookup = {r['name']: r for r in roster}
        games = json.loads(games_path.read_text())
        for day in sample_dates(year):
            key = 'scoreboard_' + day.strftime('%Y%m%d') + '.json'
            url = API + 'scoreboard?dates=' + day.strftime('%Y%m%d') + '&limit=1000'
            data, meta = read_or_fetch(root, key, url, collect)
            candidates = {'major_involved': [], 'other_only': [], 'unmapped': []}
            events = data.get('events', []) if data else []
            rejected = 0
            for event in events:
                if event.get('season', {}).get('year') != year:
                    rejected += 1
                    continue
                competition = event.get('competitions', [{}])[0]
                if not competition.get('status', {}).get('type', {}).get('completed'):
                    continue
                competitors = competition.get('competitors', [])
                names = [c.get('team', {}).get('location', '') for c in competitors]
                mapped = [lookup.get(ALIASES.get(n, n)) for n in names]
                if len(mapped) != 2 or not all(mapped):
                    bucket = 'unmapped'
                else:
                    bucket = 'major_involved' if any(r['conference'] in MAJOR for r in mapped) else 'other_only'
                candidates[bucket].append((event, mapped))
            board = dict(season=year, requested_date=day.isoformat(), http_status=meta.get('http_status'),
                         baseline_games_on_date=sum(g['game_date'] == day.isoformat() for g in games),
                         returned_events=len(events), season_rejected=rejected,
                         candidates={k: len(v) for k, v in candidates.items()}, selected=[])
            # One event from each mapped stratum; never fill a missing stratum with a success.
            for bucket in ('major_involved', 'other_only'):
                if not candidates[bucket]:
                    continue
                event, mapped = min(candidates[bucket], key=lambda x: digest(x[0]['id'].encode()))
                event_id = event['id']
                payload, smeta = read_or_fetch(root, 'summary_' + event_id + '.json', API + 'summary?event=' + event_id, collect)
                result = inspect_summary(payload, event_id, year) if payload else dict(status='fetch_failed')
                if payload and result['status'] == 'ok':
                    actual = payload['header']['competitions'][0]
                    expected = event['competitions'][0]
                    def identity(c):
                        return sorted((str(t.get('id')), str(t.get('score'))) for t in c.get('competitors', []))
                    result['scoreboard_identity_score_match'] = identity(actual) == identity(expected)
                expected_competitors = event['competitions'][0]['competitors']
                expected_scores = {r['team_id']: int(c['score']) for r, c in zip(mapped, expected_competitors)}
                result['baseline_matches'] = [g['game_id'] for g in games
                    if g['game_date'] == day.isoformat()
                    and {g['team_a_id'], g['team_b_id']} == set(expected_scores)
                    and g['runs_a'] == expected_scores[g['team_a_id']]
                    and g['runs_b'] == expected_scores[g['team_b_id']]]
                result.update(event=event_id, season=year, requested_date=day.isoformat(), stratum=bucket,
                              teams_mapped=[dict(team_id=r['team_id'], conference=r['conference']) for r in mapped],
                              http_status=smeta.get('http_status'))
                summaries.append(result)
                board['selected'].append(event_id)
            boards.append(board)
            print(day, len(events), board['selected'], flush=True)
    return dict(retained_sources_verified=verify_raw(root), design='First Tue/Fri in March/May; lowest SHA256(event ID) per mapped conference stratum',
                baseline_input_hashes={str(p.relative_to(REPO)): digest(p.read_bytes())
                    for y in range(2021, 2026) for p in (REPO/f'historical/{y}/teams.json', REPO/f'historical/{y}/games.json')},
                scoreboards=boards, summaries=summaries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=REPO/'historical/player_coverage/raw')
    parser.add_argument('--output', type=Path, default=REPO/'historical/player_coverage/audit.json')
    parser.add_argument('--collect', action='store_true', help='Bounded pilot only; cache failures as well as successes')
    args = parser.parse_args()
    result = run(args.raw_dir, args.collect)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
