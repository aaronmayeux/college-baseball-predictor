"""Bounded D1 HAVOC captures and complete excluded-game reconstruction.

Offline by default. collect-boxes fetches only links present in saved schedules;
never requests D1Baseball, retries a saved failure, or changes baseline records.
"""
import argparse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from reconstruct_havoc_pilot import FIELDS, REPO, box_counts, count, subtract

SAMPLES = {
    2021: ('Arizona-State', 'Fairfield', 'Jacksonville', 'Old-Dominion',
           'South-Carolina', 'Southern', 'Texas', 'Virginia'),
    2022: ('Air-Force', 'Auburn', 'Dallas-Baptist', 'Florida-State',
           'Louisiana-Tech', 'Southeastern-Louisiana', 'Texas', 'UCLA'),
    2023: ('Auburn', 'LSU', 'Oregon-State', 'Penn', 'Sam-Houston-State',
           'Samford', 'Southern-Miss', 'Tulane'),
}
# Exact D1 directory link text and URL slugs, retained in capture evidence.
IDENTITIES = {
    'Arizona-State': ('Arizona State', 'arizonast'), 'Fairfield': ('Fairfield', 'fairfield'),
    'Jacksonville': ('Jacksonville', 'jacksonvil'), 'Old-Dominion': ('Old Dominion', 'olddom'),
    'South-Carolina': ('South Carolina', 'scarolina'), 'Southern': ('Southern', 'southernu'),
    'Texas': ('Texas', 'texas'), 'Virginia': ('Virginia', 'virginia'),
    'Air-Force': ('Air Force', 'airforce'), 'Auburn': ('Auburn', 'auburn'),
    'Dallas-Baptist': ('Dallas Baptist', 'dallasbapt'), 'Florida-State': ('Florida State', 'floridast'),
    'Louisiana-Tech': ('Louisiana Tech', 'latech'),
    'Southeastern-Louisiana': ('Southeastern Louisiana', 'sela'), 'UCLA': ('UCLA', 'ucla'),
    'LSU': ('LSU', 'lsu'), 'Oregon-State': ('Oregon State', 'oregonst'),
    'Penn': ('Pennsylvania', 'upenn'), 'Sam-Houston-State': ('Sam Houston', 'samhouston'),
    'Samford': ('Samford', 'samford'), 'Southern-Miss': ('Southern Miss', 'smiss'),
    'Tulane': ('Tulane', 'tulane'),
}
BOX_ALIASES = {
    'wn:Air-Force': ('Air Force', 'Air Force Academy'),
    'wn:Texas-AM': ('Texas A&M',),
    'wn:Dallas-Baptist': ('DBU', 'Dallas Baptist'),
    'wn:Southern': ('Southern', 'Southern U.', 'Southern University'),
    'wn:Southern-Miss': ('Southern Miss',),
    'wn:South-Carolina': ('South Carolina',),
    'wn:Southeastern-Louisiana': ('Southeastern', 'Southeastern Louisiana', 'Southeastern La.'),
    'wn:Sam-Houston-State': ('Sam Houston', 'Sam Houston State'),
    'wn:Penn': ('Penn', 'Pennsylvania'),
}


def read(p):
    return json.loads(p.read_text())


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def identity(url):
    u = urlparse(url)
    m = re.fullmatch(r'/team/([^/]+)/(202[123])/(stats|schedule)/', u.path)
    if u.scheme != 'https' or u.netloc != 'd1baseball.com' or not m:
        raise ValueError('Not a locked historical D1 URL')
    year = int(m[2])
    matches = [t for t in SAMPLES[year] if IDENTITIES[t][1] == m[1]]
    if len(matches) != 1:
        raise ValueError('Team outside locked sample')
    return year, matches[0], m[3]


def dom_batting(text):
    if 'heading "Batting"' not in text or 'heading "Pitching"' not in text:
        raise ValueError('Missing batting section')
    part = text.split('heading "Batting"', 1)[1].split('heading "Pitching"', 1)[0]
    headers = re.findall(r'columnheader "([^":]+): activate', part)
    # DataTables repeats its header for horizontal scrolling.
    if len(headers) % 2 or headers[:len(headers)//2] != headers[len(headers)//2:]:
        raise ValueError('Unexpected repeated batting headers')
    header = headers[:len(headers)//2]
    rows = []
    for block in re.split(r'(?m)^        - row ', part)[1:]:
        cells = re.findall(r'(?m)^          - gridcell(?: ("(?:[^"\\]|\\.)*"))?[:\s]*$', block)
        if cells:
            rows.append([json.loads(c) if c else '' for c in cells])
    info = re.findall(r'Showing 1 to (\d+) of (\d+) entries', part)
    if len(info) != 1 or tuple(map(int, info[0])) != (len(rows), len(rows)):
        raise ValueError('Incomplete or paginated batting capture')
    return [header] + rows


def batting(snapshot, url, dom=False):
    year, team, kind = identity(url)
    name = IDENTITIES[team][0]
    if kind != 'stats':
        raise ValueError('Not a batting URL')
    if dom:
        if (f'heading "{name}" [level=1]' not in snapshot or
                f'option "{year}" [selected]' not in snapshot or
                'option "Overall" [selected]' not in snapshot):
            raise ValueError('Wrong identity, season or split')
        rows = dom_batting(snapshot)
        records = re.findall(r'heading "Overall (\d+)-(\d+)(?:-(\d+))?\(', snapshot)
        if len(records) != 1:
            raise ValueError('Missing team record')
        games = sum(int(v or 0) for v in records[0])
    else:
        if (snapshot['heading'] != name or str(year) not in snapshot['selects'] or
                snapshot['selects'][-1] != 'overall'):
            raise ValueError('Wrong identity, season or split')
        rows = snapshot['rows']
        m = re.match(r'Overall (\d+)-(\d+)(?:-(\d+))?\(', snapshot['record'])
        if not m:
            raise ValueError('Missing team record')
        games = sum(int(v or 0) for v in m.groups())
    header, *players = rows
    header = [h.upper() for h in header]
    if (not players or len(header) != len(set(header)) or
            not {'PLAYER', 'GP', *FIELDS} <= set(header) or
            any(len(r) != len(header) for r in players)):
        raise ValueError('Incomplete batting table')
    if len({r[header.index('PLAYER')] for r in players}) != len(players):
        raise ValueError('Duplicate player')
    if 'TEAM' in header and any(r[header.index('TEAM')] != name for r in players):
        raise ValueError('Wrong player team')
    totals = {k: sum(count(r[header.index(k)]) for r in players) for k in FIELDS}
    if totals['K'] <= 0 or any(count(r[header.index('GP')]) > games for r in players):
        raise ValueError('Invalid denominator or player GP')
    return dict(season=year, team_id='wn:'+team, final_games=games, final_counts=totals,
                players=len(players), url=url)


def schedule_rows(snapshot, dom=False):
    """Return explicit date/opponent/result links; ignore unscored rows."""
    rows = []
    if dom:
        for block in re.split(r'(?m)^        - row ', snapshot)[1:]:
            dates = re.findall(r'/scores/\?date=(\d{8})', block)
            opponents = re.findall(r'/url: https://d1baseball.com/team/([^/]+)/schedule/', block)
            scores = re.findall(r'- gridcell "([WLT]) (\d+) - (\d+)"', block)
            links = re.findall(r'- link "[WLT] \d+ - \d+":\n\s+- /url: (\S+)', block)
            if not scores:
                continue
            if len(dates) != 1 or len(opponents) != 1 or len(scores) != 1:
                raise ValueError('Ambiguous schedule row')
            rows.append((dates[0], opponents[0], scores[0], links))
    else:
        for row in snapshot['rows']:
            c = row['cells']
            if len(c) != 6:
                raise ValueError('Unexpected schedule schema')
            score = re.fullmatch(r'([WLT])\s+(\d+)\s*-\s*(\d+)', c[3]['text'].strip())
            if not score:
                continue
            dates = re.findall(r'date=(\d{8})', c[0]['links'][0]['url'])
            opp = re.fullmatch(r'https://d1baseball.com/team/([^/]+)/schedule/', c[2]['links'][0]['url'])
            if len(dates) != 1 or not opp:
                raise ValueError('Missing schedule date/opponent')
            rows.append((dates[0], opp[1], score.groups(), [x['url'] for x in c[3]['links']]))
    result = []
    for day, opp, (wl, high, low), links in rows:
        high, low = int(high), int(low)
        own, other = (low, high) if wl == 'L' else (high, low)
        result.append(dict(date=date.fromisoformat(day).isoformat(), opponent_slug=opp,
                           runs_for=own, runs_against=other, links=links))
    return result


def load_captures(raw):
    stats, schedules, issues = {}, defaultdict(list), []
    for path in sorted((raw/'captures').glob('*.json')):
        doc = read(path)
        # A retained browser-memory checkpoint contains named capture objects.
        docs = list(doc.values()) if path.name == 'havoc-memory-checkpoint.json' else [doc]
        for obj in docs:
            if not isinstance(obj, dict):
                continue
            parts = []
            if 'statsUrl' in obj:
                parts.append((obj['statsUrl'], obj['stats'], True))
                parts.append((obj['scheduleUrl'], obj['schedule'], True))
            elif 'url' in obj and ('rows' in obj or 'schedule' in obj):
                parts.append((obj['url'], obj.get('schedule', obj), 'schedule' in obj))
            for url, payload, dom in parts:
                try:
                    year, team, kind = identity(url)
                    datetime.fromisoformat(obj['retrieved_at_utc'].replace('Z', '+00:00'))
                    key = (year, 'wn:'+team)
                    if kind == 'stats':
                        row = batting(payload, url, dom)
                        if key in stats and stats[key] != row:
                            raise ValueError('Conflicting complete batting captures')
                        stats[key] = row
                    else:
                        if dom and (f'heading "{IDENTITIES[team][0]}" [level=1]' not in payload or
                                    f'option "{year}" [selected]' not in payload):
                            raise ValueError('Wrong schedule identity/year')
                        if not dom and payload['heading'] != IDENTITIES[team][0]:
                            raise ValueError('Wrong schedule identity')
                        rows = schedule_rows(payload, dom)
                        if not rows:
                            raise ValueError('Empty schedule capture')
                        for row in rows:
                            if row not in schedules[key]:
                                schedules[key].append(row)
                except (ValueError, KeyError, IndexError) as exc:
                    issues.append(dict(capture=path.name, url=url, reason=str(exc)))
    if any(x['reason'] == 'Conflicting complete batting captures' for x in issues):
        raise ValueError('Conflicting complete batting captures')
    return stats, schedules, issues


def inventory(year, team):
    contract = read(REPO/'historical/cutoffs.json')
    cutoff = datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff']).date()
    games = [g for g in read(REPO/f'historical/{year}/games.json')
             if team in (g['team_a_id'], g['team_b_id'])]
    if any(not g.get('game_date') or g.get('timing_review') for g in games):
        raise ValueError('Unresolved game timing')
    eligible = [g for g in games if g['stage'] in contract['modes']['conference_inclusive']
                and date.fromisoformat(g['game_date']) + timedelta(days=2) <= cutoff]
    excluded = [g for g in games if g not in eligible]
    # All-opponent scope can include explicit, dated pre-cutoff non-D1 games.
    non_d1 = [r for r in read(REPO/f'historical/{year}/excluded_observations.json')
              if r['team_id'] == team and
              r['status'] == 'completed' and r.get('non_d1_explicit')]
    if any(not r.get('game_date') or date.fromisoformat(r['game_date']) + timedelta(days=2) > cutoff for r in non_d1):
        raise ValueError('Unresolved excluded non-D1 scope')
    return games, eligible, excluded, non_d1


def own_scores(game, team):
    return ((game['runs_a'], game['runs_b']) if game['team_a_id'] == team
            else (game['runs_b'], game['runs_a']))


def linked_boxes(raw):
    stats, schedules, _ = load_captures(raw)
    links = defaultdict(set)
    for (year, team), rows in schedules.items():
        try:
            _, _, excluded, _ = inventory(year, team)
        except ValueError:
            continue  # Reconstruction records this team's explicit fallback reason.
        for g in excluded:
            own, other = own_scores(g, team)
            opponent = g['team_b_id'] if g['team_a_id'] == team else g['team_a_id']
            slug = IDENTITIES.get(opponent.removeprefix('wn:'), (None, None))[1]
            matches = [r for r in rows if r['date'] == g['game_date'] and
                       (r['runs_for'], r['runs_against']) == (own, other) and
                       (slug is None or r['opponent_slug'] == slug)]
            if len(matches) != 1:
                continue
            for url in matches[0]['links']:
                u = urlparse(url)
                if u.scheme in ('http', 'https') and u.hostname and u.hostname != 'd1baseball.com':
                    links[g['game_id']].add(url.replace('http://', 'https://', 1))
    # Only request games needed by a captured batting input.
    needed = set()
    for y, t in stats:
        try:
            needed.update(g['game_id'] for g in inventory(y,t)[2])
        except ValueError:
            continue
    # Replacement official links may be discovered on school schedules or via
    # search. Keep that discovery evidence; never replace a failed cached URL.
    supplemental = raw/'official_links.json'
    if supplemental.exists():
        for row in read(supplemental):
            u = urlparse(row['url'])
            if (row['game_id'] not in needed or u.scheme != 'https' or not u.hostname
                    or u.hostname == 'd1baseball.com'
                    or not row.get('discovery') or not row.get('retrieved_at_utc')):
                raise ValueError('Invalid bounded supplemental box link')
            datetime.fromisoformat(row['retrieved_at_utc'].replace('Z', '+00:00'))
            links[row['game_id']].add(row['url'])
    reverse = defaultdict(set)
    for game_id, urls in links.items():
        for url in urls:
            reverse[url].add(game_id)
    return {k: sorted(u for u in v if len(reverse[u]) == 1)
            for k,v in sorted(links.items()) if k in needed}


def box_path(raw, url):
    return raw/'boxes'/hashlib.sha256(url.encode()).hexdigest()


def collect_boxes(raw):
    urls = sorted({u for v in linked_boxes(raw).values() for u in v})
    collect_urls(raw, urls)


def collect_urls(raw, urls):
    supplemental = raw/'official_links.json'
    discovery = {r['url']: r['discovery'] for r in read(supplemental)} if supplemental.exists() else {}
    for url in urls:
        stem = box_path(raw, url)
        meta_path, body_path = stem.with_suffix('.json'), stem.with_suffix('.html')
        if meta_path.exists():
            meta = read(meta_path)
            if meta['url'] != url or digest(body_path) != meta['sha256']:
                raise ValueError('Changed cache: '+url)
            continue
        if body_path.exists():
            raise ValueError('Unpaired cache file')
        meta = dict(url=url, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                    discovery=discovery.get(url, 'retained D1 schedule; HTTP upgraded to HTTPS'))
        try:
            with urlopen(Request(url, headers={'User-Agent':'CollegeBaseballResearch/1.0'}), timeout=25) as res:
                body = res.read()
                meta.update(status=res.status, final_url=res.url)
        except HTTPError as exc:
            body = exc.read()
            meta.update(status=exc.code, final_url=exc.url)
        except (URLError, TimeoutError) as exc:
            body = b''
            meta.update(status=0, error=str(exc))
        stem.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(body)
        meta['sha256'] = hashlib.sha256(body).hexdigest()
        write(meta_path, meta)
        print(meta['status'], url, flush=True)


def verified_box(raw, url, game, team):
    results = []
    for directory in ('boxes', 'rendered_boxes'):
        stem = raw/directory/hashlib.sha256(url.encode()).hexdigest()
        try:
            results.append(verified_box_capture(stem, url, game, team))
        except (ValueError, FileNotFoundError):
            continue
    if not results:
        raise ValueError('No verified downloaded or rendered box')
    if any(r != results[0] for r in results):
        raise RuntimeError('Conflicting downloaded/rendered boxes')
    return results[0]


def verified_box_capture(stem, url, game, team):
    meta_path, body_path = stem.with_suffix('.json'), stem.with_suffix('.html')
    meta = read(meta_path)
    available = (meta.get('status') == 200 or
                 (meta.get('acquisition') == 'browser_dom' and meta.get('rendered') is True))
    if meta['url'] != url or not available or digest(body_path) != meta['sha256']:
        raise ValueError('Unavailable or changed box')
    datetime.fromisoformat(meta['retrieved_at_utc'])
    text = body_path.read_text(errors='replace')
    result = {}
    for t in (game['team_a_id'], game['team_b_id']):
        names = BOX_ALIASES.get(t, (t.removeprefix('wn:').replace('-', ' '),))
        found = []
        for name in names:
            try:
                found.append(box_counts(text, name, game['game_date']))
            except ValueError:
                pass
        if len(found) != 1 or found[0]['R'] != own_scores(game, t)[0]:
            raise ValueError('Box identity/date/player sums/scores unverified')
        result[t] = found[0]
    return result[team]


def reconstruct(raw):
    stats, schedules, capture_issues = load_captures(raw)
    links = linked_boxes(raw)
    features = []
    for year, teams in SAMPLES.items():
        for slug in teams:
            team = 'wn:'+slug
            row = dict(season=year, team_id=team, counts=None, values=None, reasons=[], flags=[], boxes=[])
            source = stats.get((year, team))
            if source is None:
                row['reasons'].append('missing_complete_batting_capture')
            else:
                row.update(source)
                try:
                    games, eligible, excluded, non_d1 = inventory(year, team)
                except ValueError as exc:
                    row['reasons'].append('unresolved_inventory:'+str(exc))
                    features.append(row)
                    continue
                expected_runs = sum(own_scores(g,team)[0] for g in games) + sum(r['runs_for'] for r in non_d1)
                row.update(final_games_expected=len(games)+len(non_d1),
                           included_games=len(eligible)+len(non_d1),
                           excluded_game_ids=[g['game_id'] for g in excluded],
                           non_d1_games=len(non_d1),
                           runs_delta=source['final_counts']['R']-expected_runs)
                if source['final_games'] != row['final_games_expected']:
                    row['reasons'].append('final_game_scope_mismatch')
                # Full final run agreement is a cheap scope check, not a coverage audit.
                if abs(row['runs_delta']) > 10:
                    row['reasons'].append('final_run_scope_mismatch')
                elif row['runs_delta']:
                    row['flags'].append('small_final_run_discrepancy')
                for g in excluded:
                    found = []
                    for url in links.get(g['game_id'], []):
                        try:
                            counts = verified_box(raw, url, g, team)
                            found.append(dict(game_id=g['game_id'], url=url, counts=counts))
                        except (ValueError, FileNotFoundError):
                            pass
                    if not found:
                        row['reasons'].append('missing_verified_box:'+g['game_id'])
                    elif any(x['counts'] != found[0]['counts'] for x in found):
                        row['reasons'].append('conflicting_boxes:'+g['game_id'])
                    else:
                        row['boxes'].append(found[0])
                if not row['reasons']:
                    counts = subtract(source['final_counts'], row['boxes'], row['excluded_game_ids'])
                    row['counts'] = counts
                    row['values'] = havoc_values(counts)
                    row['latest_included_game'] = max([g['game_date'] for g in eligible] + [r['game_date'] for r in non_d1])
            features.append(row)
    return dict(mode='conference_inclusive', features=features, capture_issues=capture_issues,
                raw_sha256={str(p.relative_to(raw)):digest(p) for p in sorted(raw.rglob('*')) if p.is_file()},
                limitations=['Retrospective reconstruction, not publication-time certification',
                             'Small fixed convenience sample; later scoring corrections may remain'])


def havoc_values(c):
    if any(type(c.get(k)) is not int or c[k] < 0 for k in ('SB','CS','BB','HBP','K')) or c['K'] <= 0:
        raise ValueError('Missing or invalid HAVOC count')
    return dict(havoc=(2*c['SB']+c['BB']+c['HBP'])/c['K'],
                havoc_net_steals=(2*(c['SB']-c['CS'])+c['BB']+c['HBP'])/c['K'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['inspect','collect-boxes','reconstruct'])
    ap.add_argument('--raw-dir', type=Path, required=True)
    args = ap.parse_args()
    if args.command == 'collect-boxes':
        collect_boxes(args.raw_dir)
    elif args.command == 'inspect':
        stats, schedules, issues = load_captures(args.raw_dir)
        print(json.dumps(dict(batting=list(stats.values()), schedules=[dict(season=k[0],team_id=k[1],rows=len(v)) for k,v in schedules.items()],issues=issues,boxes=linked_boxes(args.raw_dir)),indent=2))
    else:
        print(json.dumps(reconstruct(args.raw_dir),indent=2,sort_keys=True))
