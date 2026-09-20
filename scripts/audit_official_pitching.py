"""Bounded offline comparison of two disputed ESPN boxes with official schools.

No corrections are applied to inputs; this is not a full-season importer.
"""
import argparse
import html
import datetime as dt
import json
from pathlib import Path
import re
from audit_official_player_sample import read
from audit_player_coverage import outs, API, read_or_fetch

REPO = Path(__file__).resolve().parents[1]
SAMPLES = [
    dict(key='towson_ncstate_20240301.html', event='401632674', year=2024,
         date='3/1/2024', teams=['Towson', 'NC State'], scores=[5, 6],
         url='https://towsontigers.com/sports/baseball/stats/2024/nc-state/boxscore/28316'),
    dict(key='most_arkansas_20220503.html', event='401394978', year=2022,
         date='5/3/2022', teams=['Missouri State', 'Arkansas'], scores=[6, 4],
         url='https://missouristatebears.com/sports/baseball/stats/2022/arkansas/boxscore/5610'),
]
# Explicit single-game name crosswalk; never infer national player identities.
NAME_ALIASES = {'reece - p lang': 'reece lang', 'trey - p ziegenbein': 'trey ziegenbein'}
PITCH_HEADER = 'Player IP H R ER BB SO WP BK HBP IBB AB BF FO GO NP'.split()


def plain(s):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', s)).split())


def player_key(name):
    name = re.sub(r'\s*\([WLS],.*?\)\s*$', '', name).strip()
    if ',' in name:
        last, first = name.split(',', 1)
        name = first.strip() + ' ' + last.strip()
    name = ' '.join(name.lower().split())
    return NAME_ALIASES.get(name, name)


def table_cells(row):
    cells = []
    for attrs, content in re.findall(r'<t[dh]\b([^>]*)>(.*?)(?=<t[dh]\b|</t[dh]>)', row, re.S | re.I):
        span = re.search(r'colspan=["\']?(\d+)', attrs, re.I)
        cells.append(plain(content))
        cells.extend([''] * ((int(span[1]) if span else 1) - 1))
    return cells


def parse_pitching(text, expected_teams):
    result = {}
    for match in re.finditer(r'<table\b[^>]*>.*?</table>', text, re.S | re.I):
        table = match.group()
        rows = [table_cells(r) for r in re.findall(r'<tr\b[^>]*>(.*?)</tr>', table, re.S | re.I)]
        if not rows or rows[0] != PITCH_HEADER:
            continue
        caption = re.search(r'<caption[^>]*>(.*?)</caption>', table, re.S | re.I)
        if caption:
            team = plain(caption[1]).removesuffix(' - Pitching Stats')
        else:
            headings = re.findall(r'<h2\b[^>]*>(.*?)</h2>', text[:match.start()], re.S | re.I)
            team = plain(headings[-1]) if headings else None
        if team not in expected_teams or team in result:
            raise ValueError('Unknown or duplicate pitching team')
        players, totals = [], None
        for cells in rows[1:]:
            if len(cells) != len(PITCH_HEADER):
                raise ValueError('Pitching row width changed')
            values = dict(zip(PITCH_HEADER, cells))
            if values['Player'] == 'Totals':
                if totals is not None:
                    raise ValueError('Duplicate totals')
                totals = values
                continue
            stats = {}
            for field in PITCH_HEADER[1:]:
                value = values[field]
                if field == 'IP':
                    stats['outs'] = outs(value)
                elif re.fullmatch(r'\d+', value):
                    stats[field] = int(value)
                else:
                    raise ValueError('Missing or invalid pitching count')
            players.append(dict(name=values['Player'], match_key=player_key(values['Player']),
                                raw=values, counts=stats,
                                pitch_count=stats['NP'] if stats['NP'] > 0 else None))
        if not players or totals is None or len({p['match_key'] for p in players}) != len(players):
            raise ValueError('Missing rows/totals or ambiguous player name')
        sums = {k: sum(p['counts'][k] for p in players) for k in players[0]['counts']}
        checks = {}
        for field in PITCH_HEADER[2:]:
            if not re.fullmatch(r'\d+', totals[field]):
                raise ValueError('Invalid official total')
            checks[field] = sums[field] == int(totals[field])
        result[team] = dict(players=players, sums=sums, raw_totals=totals, totals_checks=checks,
                            positive_pitch_counts=sum(p['pitch_count'] is not None for p in players))
    if set(result) != set(expected_teams):
        raise ValueError('Expected two complete pitching tables')
    return result


def compare(official, espn_team, espn_totals):
    group, = [g for g in espn_team['statistics'] if g['type'] == 'pitching']
    rows = {}
    for athlete in group['athletes']:
        key = player_key(athlete['athlete']['displayName'])
        if key in rows or len(athlete['stats']) != len(group['labels']):
            raise ValueError('Ambiguous ESPN rows')
        rows[key] = dict(zip(group['labels'], athlete['stats']))
    matched, missing, differences = [], [], []
    for player in official['players']:
        key = player['match_key']
        if key not in rows:
            missing.append(player['name'])
            continue
        matched.append(key)
        for field, espn_field in [('outs','IP'), ('H','H'), ('R','R'), ('ER','ER'), ('BB','BB'), ('SO','K')]:
            raw = rows[key][espn_field]
            value = outs(raw) if field == 'outs' else int(raw)
            if value != player['counts'][field]:
                differences.append(dict(player=player['name'], field=field,
                                        official=player['counts'][field], espn=value))
    totals_group, = [g for g in espn_totals['statistics'] if g['name'] == 'pitching']
    totals = {s['name']: s.get('displayValue') for s in totals_group['stats']}
    total_comparison = {}
    for official_field, espn_field in [('outs','thirdInnings'),('H','hits'),('R','runs'),
                                      ('ER','earnedRuns'),('BB','walks'),('SO','strikeouts')]:
        total_comparison[official_field] = dict(official_rows=official['sums'][official_field],
                                               espn_team=totals.get(espn_field))
    return dict(official_pitchers=len(official['players']), espn_pitchers=len(rows),
                missing_from_espn=missing, unmatched_espn=sorted(set(rows)-set(matched)),
                common_row_differences=differences, team_totals=total_comparison,
                official=official)


def audit(official_root, espn_root):
    output = []
    for sample in SAMPLES:
        text, meta = read(official_root, sample['key'])
        title = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
        if meta['url'] != sample['url'] or not title or sample['date'] not in plain(title[1]):
            raise ValueError('Wrong official game/date')
        parsed = parse_pitching(text, sample['teams'])
        data, emeta = read_or_fetch(espn_root, 'summary_'+sample['event']+'.json',
                                   API+'summary?event='+sample['event'])
        if str(data['header']['id']) != sample['event'] or data['header']['season']['year'] != sample['year']:
            raise ValueError('Wrong ESPN game/season')
        competition, = data['header']['competitions']
        date_iso = dt.datetime.strptime(sample['date'], '%m/%d/%Y').date().isoformat()
        if not competition['date'].startswith(date_iso):
            raise ValueError('Wrong ESPN date')
        scores = {c['team']['location']: int(c['score']) for c in competition['competitors']}
        if scores != dict(zip(sample['teams'], sample['scores'])):
            raise ValueError('Wrong ESPN teams/scores')
        teams = {}
        for index, team in enumerate(sample['teams']):
            if parsed[team]['sums']['R'] != sample['scores'][1-index]:
                raise ValueError('Official pitching runs do not match opponent score')
            if not all(parsed[team]['totals_checks'].values()):
                raise ValueError('Official pitcher totals inconsistent')
            players, = [t for t in data['boxscore']['players'] if t['team']['location'] == team]
            totals, = [t for t in data['boxscore']['teams'] if t['team']['location'] == team]
            teams[team] = compare(parsed[team], players, totals)
        output.append(dict(event=sample['event'], season=sample['year'], teams=teams,
                           official_source=meta, espn_source=emeta,
                           feature_qualified=False, stable_player_ids_qualified=False))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--official-raw-dir', type=Path, default=REPO/'historical/research/raw')
    parser.add_argument('--espn-raw-dir', type=Path, default=REPO/'historical/player_coverage/raw')
    args = parser.parse_args()
    print(json.dumps(audit(args.official_raw_dir, args.espn_raw_dir), indent=2))
