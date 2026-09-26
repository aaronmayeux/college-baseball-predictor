"""Small, offline hitting-count adapters. No ratings, fitting or baseline writes."""
from collections import Counter
import re
from audit_official_pitching import plain
from audit_season_appearances import rows, tables, count, statcrew_box

FIELDS = ('AB', 'H', 'BB', 'SO', '2B', '3B', 'HR', 'HBP', 'SF', 'SH')
EXTRA = ('2B', '3B', 'HR', 'HBP', 'SF', 'SH', 'CI')
PATTERNS = {
    '1B': r'\bsingled\b', '2B': r'\bdoubled\b', '3B': r'\btripled\b',
    'HR': r'\bhomered\b', 'HBP': r'\bhit by pitch\b',
    'SF': r'\bSF\b', 'SH': r'\bSAC\b',
    'CI': r"\breached on (?:catcher's )?interference\b",
}


def rates(counts):
    """Only complete denominators yield rates; PA can explicitly be unknown."""
    for field in FIELDS:
        if type(counts.get(field)) is not int or counts[field] < 0:
            raise ValueError('Missing/invalid count: ' + field)
    if counts['2B'] + counts['3B'] + counts['HR'] > counts['H'] or counts['H'] > counts['AB']:
        raise ValueError('Impossible hit counts')
    if counts['SO'] > counts['AB']:
        raise ValueError('Strikeouts exceed at-bats')
    pa = counts.get('PA')
    if pa is not None:
        if type(pa) is not int or pa < 0 or type(counts.get('CI')) is not int or counts['CI'] < 0:
            raise ValueError('Invalid PA/interference count')
        if pa != sum(counts[f] for f in ('AB', 'BB', 'HBP', 'SF', 'SH', 'CI')):
            raise ValueError('PA components disagree')
    def divide(n, d):
        return n / d if d else None
    return dict(ISO=divide(counts['2B'] + 2*counts['3B'] + 3*counts['HR'], counts['AB']),
                OBP=divide(counts['H'] + counts['BB'] + counts['HBP'],
                           counts['AB'] + counts['BB'] + counts['HBP'] + counts['SF']),
                strikeout_rate=divide(counts['SO'], pa), HR_per_PA=divide(counts['HR'], pa))


def event_summary(text):
    """Game totals across both teams. Parenthesized numbers are season totals."""
    found = [plain(t) for t in tables(text) if re.search(r'\bLOB\s*-', plain(t))]
    if len(found) != 1:
        raise ValueError('Missing/duplicate game event summary')
    summary = found[0]
    labels = list(re.finditer(r'(?:^|\. )(?P<label>E|DP|LOB|2B|3B|HR|HBP|SH|SF|SB|CS|Reached on CI)\s*-\s*', summary))
    result = dict.fromkeys(EXTRA, 0)
    seen = set()
    for i, match in enumerate(labels):
        label = match['label']
        label = 'CI' if label == 'Reached on CI' else label
        if label not in result:
            continue
        if label in seen:
            raise ValueError('Duplicate summary label: ' + label)
        seen.add(label)
        value = summary[match.end():labels[i+1].start() if i+1 < len(labels) else len(summary)].rstrip('.')
        if not value:
            raise ValueError('Empty summary event')
        for item in value.split(';'):
            item = item.strip()
            # Names may contain periods and commas; never split on those.
            m = re.fullmatch(r'([^()]+?)(?:\((\d+)\))?', item)
            if not m:
                raise ValueError('Unrecognized event summary: ' + item)
            multiple = re.search(r' (\d+)$', m[1])
            n = int(multiple[1]) if multiple else 1
            if n < 1:
                raise ValueError('Invalid event multiplicity')
            result[label] += n
    return result


def play_counts(text, teams):
    """Read inning blocks once, and require their hits/runs to reconcile later."""
    parts = re.split(r'<a\s+name="GAME.PLY"\s*>', text, flags=re.I)
    if len(parts) != 2:
        raise ValueError('Missing/duplicate play-by-play section')
    counts = {team: Counter() for team in teams}
    seen = set()
    for table in tables(parts[1]):
        body = plain(table)
        match = re.match(r'(.+?) (\d+)(?:st|nd|rd|th) - ', body)
        if not match:
            continue
        team, inning = match[1], int(match[2])
        if team not in counts or (team, inning) in seen:
            raise ValueError('Unknown team or duplicate inning')
        seen.add((team, inning))
        end = re.search(r'(\d+) runs?, (\d+) hits?, \d+ errors?, \d+ LOB\.$', body)
        if not end:
            raise ValueError('Missing inning summary')
        events = body[match.end():end.start()]
        # Pitch codes such as (0-2 SF) are not sacrifice flies. Review
        # commentary repeats the already corrected scoring event.
        events = re.sub(r'\(\d+-\d+ [A-Z ]+\)', '', events)
        events = re.sub(r'Previous play reviewed,[^.]*\.', '', events)
        events = re.sub(r'\b[A-Za-z][A-Za-z ]* challenged (?:the previous play|previous call),[^.]*\.', '', events)
        values = {f: len(re.findall(pattern, events)) for f, pattern in PATTERNS.items()}
        if sum(values[f] for f in ('1B', '2B', '3B', 'HR')) != int(end[2]):
            raise ValueError('Play hits differ from inning summary')
        counts[team].update(values)
        counts[team].update(R=int(end[1]), H=int(end[2]))
    for team in teams:
        innings = sorted(i for t, i in seen if t == team)
        if not innings or innings != list(range(1, max(innings)+1)):
            raise ValueError('Missing inning blocks')
    summary = event_summary(parts[0])
    for field in EXTRA:
        if sum(c[field] for c in counts.values()) != summary[field]:
            raise ValueError('Play/box summary mismatch: ' + field)
    return counts


def statcrew_team(text, expected, team_name="LSU"):
    """Check one named team; the default preserves the LSU pilot contract."""
    core = statcrew_box(text, expected, team_name)
    plays = play_counts(text, expected['teams'])
    batting = {}; pitching = {}; batting_team = None; header = None; pitch_team = None; ph = None
    for table in tables(text):
        for cells in rows(table):
            if not cells:
                continue
            m = re.fullmatch(r'(.+) (\d+) \([\d-]+[^)]*\)', cells[0])
            if m:
                batting_team = m[1]
            if cells[0] == 'Player' and 'ab' in cells:
                header = [s.upper() for s in cells]
            if header and cells[0] == 'Totals' and len(cells) == len(header):
                if batting_team in batting:
                    raise ValueError('Duplicate batting total')
                batting[batting_team] = dict(zip(header, cells))
            if len(cells) > 1 and cells[1] == 'ip':
                pitch_team = cells[0]; ph = [s.upper() for s in cells]
            elif ph and len(cells) == len(ph) and re.fullmatch(r'\d+\.[012]', cells[1]):
                pitching.setdefault(pitch_team, []).append(dict(zip(ph[1:], cells[1:])))
    if set(batting) != set(expected['teams']) or set(pitching) != set(expected['teams']):
        raise ValueError('Missing team tables')
    output = {}
    for team, score in zip(expected['teams'], expected['runs']):
        if plays[team]['H'] != count(batting[team]['H']) or plays[team]['R'] != score:
            raise ValueError('Play totals differ from box')
        c = {f: count(batting[team][f]) for f in ('AB', 'H', 'BB', 'SO')}
        c.update({f: plays[team][f] for f in EXTRA})
        opponent = next(t for t in expected['teams'] if t != team)
        for field in ('AB', 'H', 'BB', 'SO', 'HBP'):
            if sum(count(p[field]) for p in pitching[opponent]) != c[field]:
                raise ValueError('Opponent pitching disagreement: ' + field)
        c['PA'] = sum(c[f] for f in ('AB', 'BB', 'HBP', 'SF', 'SH', 'CI'))
        bf = sum(count(p['BF']) for p in pitching[opponent])
        issues = []
        if c['PA'] != bf:
            issues.append('PA_components_vs_opponent_BF:' + str(c['PA']) + ':' + str(bf))
            c['PA'] = None
        rates(c)
        output[team] = dict(counts=c, opponent_BF=bf, denominator_issues=issues)
    if any(sum(p['counts'][f] for p in core['batting']) != output[team_name]['counts'][f] for f in ('AB', 'H', 'BB', 'SO')):
        raise ValueError('Existing batting parser disagrees')
    return output[team_name]


def cumulative_team(text):
    for table in tables(text):
        rr = rows(table)
        if not rr or 'GP-GS' not in [c.upper() for c in rr[0]]:
            continue
        header = [c.upper() for c in rr[0]]
        totals = [dict(zip(header, r)) for r in rr[1:] if len(r) == len(header) and r[0].lower() == 'totals']
        if len(totals) != 1:
            raise ValueError('Missing/duplicate cumulative team total')
        return {f: count(totals[0][f]) for f in FIELDS}
    raise ValueError('Missing cumulative batting table')
