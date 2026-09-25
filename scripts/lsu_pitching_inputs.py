"""LSU StatCrew pitching qualification from explicit lineup and count evidence."""
import datetime as dt
import json
import re
from collections import defaultdict
from audit_official_pitching import plain
from audit_official_player_sample import read
from audit_official_season_inventory import REPO
from audit_season_appearances import audit, key, count, rows, tables, season_totals
from hitting_inputs import play_counts
from pitching_inputs import aggregate


def starter(text, players):
    blocks = re.findall(r'LSU starters:(.*?)(?:</td>|</p>)', text, re.S | re.I)
    if len(blocks) != 1:
        raise ValueError('Missing/duplicate LSU starting lineup')
    entries = [re.fullmatch(r'\s*\d+/([^ ]+) (.+?)\s*', entry)
               for entry in plain(blocks[0]).split(';') if entry.strip()]
    if not entries or any(e is None for e in entries):
        raise ValueError('Invalid starting lineup entry')
    pitchers = [e[2] for e in entries if 'p' in e[1].split('/')]
    if len(pitchers) != 1:
        raise ValueError('Expected one explicit lineup pitcher')
    # Exact surname token suffix, unique within the school/game pitching list;
    # no fuzzy matching or first-row fallback. Retain the original label.
    label = pitchers[0].lower()
    matches = [p for p in players if p['match_key'] == label or p['match_key'].endswith(' ' + label)]
    if len(matches) != 1:
        raise ValueError('Ambiguous/unmatched starting pitcher label')
    return matches[0]['match_key'], pitchers[0]


def pitcher_extras(text, opponent, start, players):
    """Allocate sacrifice/interference events along explicit pitching changes."""
    labels = {p['match_key'].split()[-1]: p['match_key'] for p in players}
    if len(labels) != len(players):
        raise ValueError('Ambiguous pitcher surnames in play events')
    extra = {p['match_key']:dict(SF=0, SH=0, CI=0) for p in players}
    active = start
    parts = re.split(r'<a\s+name="GAME.PLY"\s*>', text, flags=re.I)
    if len(parts) != 2: raise ValueError('Missing play section')
    for table in tables(parts[1]):
        body = plain(table)
        match = re.match(re.escape(opponent) + r' \d+(?:st|nd|rd|th) - ', body)
        if not match: continue
        body = re.sub(r'\(\d+-\d+ [A-Z ]+\)', '', body[match.end():])
        body = re.sub(r'Previous play reviewed,[^.]*\.', '', body)
        body = re.sub(r'\b[A-Za-z][A-Za-z ]* challenged (?:the previous play|previous call),[^.]*\.', '', body)
        events = re.finditer(r"(?P<change>[A-Za-z]+) to p(?: for (?P<old>[A-Za-z]+))?\.|"
                             r"(?P<SF>\bSF\b)|(?P<SH>\bSAC\b)|"
                             r"(?P<CI>\breached on (?:catcher's )?interference\b)", body)
        changes = 0
        for event in events:
            if event['change']:
                changes += 1
                new = labels.get(event['change'].lower())
                old = labels.get(event['old'].lower()) if event['old'] else active
                # A pitcher may enter a different batting slot when the DH
                # is lost; require explicit removal of the active pitcher.
                removed = re.search(r'/ for ' + re.escape(active.split()[-1]) + r'\.', body, re.I)
                if new is None or (old != active and not (old is None and removed)):
                    raise ValueError('Unmatched pitching change or prior pitcher')
                active = new
            else:
                extra[active][event.lastgroup] += 1
        if changes != len(re.findall(r'\bto p(?: for |\.)', body)):
            raise ValueError('Unparsed pitching change')
    return extra


def game(text, row, appearances):
    players = [dict(p, match_key=key(p['name'], 'lsu'), counts=dict(p['counts'])) for p in appearances]
    if not players or len({p['match_key'] for p in players}) != len(players):
        raise ValueError('Missing/duplicate pitchers')
    start, label = starter(text, players)
    plays = play_counts(text, row['teams'])
    opponent = next(t for t in row['teams'] if t != 'LSU')
    totals = {}; team = None; header = None
    for table in tables(text):
        for cells in rows(table):
            if not cells: continue
            m = re.fullmatch(r'(.+) (\d+) \([\d-]+[^)]*\)', cells[0])
            if m: team = m[1]
            if cells[0] == 'Player' and 'ab' in cells: header = [c.upper() for c in cells]
            if header and cells[0] == 'Totals' and len(cells) == len(header):
                if team in totals: raise ValueError('Duplicate batting totals')
                totals[team] = dict(zip(header, cells))
    c = {f:count(totals[opponent][f]) for f in ('AB', 'BB', 'H', 'SO', 'R')}
    c.update({f:plays[opponent][f] for f in ('HBP', 'SF', 'SH', 'CI')})
    if c['H'] != plays[opponent]['H'] or c['R'] != plays[opponent]['R']:
        raise ValueError('Opponent play totals differ from box')
    for f in ('AB', 'BB', 'H', 'SO', 'R', 'HBP'):
        if sum(p['counts'][f] for p in players) != c[f]:
            raise ValueError('Opponent totals disagree: ' + f)
    pa = sum(c[f] for f in ('AB', 'BB', 'HBP', 'SF', 'SH', 'CI'))
    if sum(p['counts']['BF'] for p in players) != pa:
        raise ValueError('LSU BF disagrees with opponent PA')
    extras = pitcher_extras(text, opponent, start, players)
    for f in ('SF', 'SH', 'CI'):
        if sum(v[f] for v in extras.values()) != c[f]:
            raise ValueError('Pitcher play extras disagree: ' + f)
    for p in players:
        v = p['counts']
        if v['BF'] < v['AB'] + v['BB'] + v['HBP']:
            raise ValueError('Pitcher BF below known components')
        v['GS'] = int(p['match_key'] == start)
        v.update(extras[p['match_key']])
        if v['BF'] != sum(v[f] for f in ('AB', 'BB', 'HBP', 'SF', 'SH', 'CI')):
            raise ValueError('Pitcher BF differs from complete components')
    return players, dict(BF=pa, opponent_PA=pa, opponent_counts=c,
                         starter_label=label, starter_key=start,
                         per_appearance_BF_components_complete=True)


def season_check(records, targets, core_ok):
    sums = defaultdict(lambda:dict(BF=0, GS=0, appearances=0, CI=0, SF=0, SH=0))
    complete = all(r['BF_check'] is not None for r in records)
    interference = sum(r['BF_check']['opponent_counts']['CI'] for r in records if r['BF_check'])
    for r in records:
        for p in r['pitchers'] or []:
            c = sums[p['match_key']]
            for f in ('CI', 'SF', 'SH'): c[f] += p['counts'][f]
            c['BF'] += p['counts']['BF']; c['GS'] += p['counts']['GS']; c['appearances'] += 1
    differences = []
    for name in sorted(set(sums) | set(targets)):
        raw = targets.get(name, {}).get('raw')
        if raw is None:
            differences.append(dict(player=name, reason='missing_cumulative_player')); continue
        app, gs = map(count, raw['APP-GS'].split('-'))
        # Cumulative CI is unavailable: add independently allocated play CI
        # to the cumulative denominator and reconcile sacrifices separately.
        ci = sums.get(name, {}).get('CI', 0)
        bf = sum(count(raw[f]) for f in ('AB', 'BB', 'HBP', 'SFA', 'SHA')) + ci
        expected = dict(BF=bf, GS=gs, appearances=app, CI=ci,
                        SF=count(raw['SFA']), SH=count(raw['SHA']))
        if sums.get(name) != expected:
            differences.append(dict(player=name, observed=sums.get(name), expected=expected))
    return dict(pass_counts=bool(core_ok and complete and not differences),
                core_counts_pass=core_ok, all_games_checked=complete,
                opponent_interference=interference, differences=differences,
                per_player_observed=dict(sorted(sums.items())))


def run(raw, contract):
    a = next(a for a in audit(raw) if a['school'] == 'lsu')
    cache = {}
    for p in sorted(raw.glob('*.meta.json')):
        meta = json.loads(p.read_text()); cache.setdefault(meta['url'], p.name.removesuffix('.meta.json'))
    records = []
    for row in a['records']:
        r = dict(row, issues=list(row['issues']), pitchers=None, BF_check=None)
        try:
            text, meta = read(raw, cache[row['box_url']])
            if meta['url'] != row['box_url']: raise ValueError('Wrong source URL')
            apps = [p for p in a['appearances']['pitching'] if p['box_url'] == row['box_url']]
            players, check = game(text, row, apps)
            r.update(pitchers=players, BF_check=check, source=meta)
        except (ValueError, KeyError, TypeError) as error:
            r['issues'].append('pitching: ' + str(error))
        records.append(r)
    text, cm = read(raw, 'lsu_cume.html')
    check = season_check(records, season_totals(text, 'lsu')['pitching'], a['comparisons']['pitching']['totals_match'])
    check['source'] = cm
    games = json.loads((REPO/'historical/2025/games.json').read_text())
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2025']['forecast_cutoff'])
    modes = {mode:aggregate(records, games, 'wn:LSU', cutoff, phases, check['pass_counts'])
             for mode, phases in contract['modes'].items()}
    return dict(team_id='wn:LSU', season=2025, sources=a['sources'], records=records,
                pitching_season_check=check, full_season_pass=check['pass_counts'], forecast_modes=modes,
                batting_check_pass=a['comparisons']['batting']['totals_match'])
