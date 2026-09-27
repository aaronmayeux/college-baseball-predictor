"""Offline Virginia 2023 source proof: final batting minus every excluded game.

Consumes a retained D1Baseball rendered table and linked official box-score HTML.
No network, fitting, app writes, or claim of nationwide input qualification.
"""
import argparse
from datetime import date, datetime, timedelta
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]
FIELDS = ('AB', 'R', 'H', 'HBP', 'BB', 'K', 'SB', 'CS')


def count(value):
    if not isinstance(value, str) or not value.isdigit():
        raise ValueError('Missing, negative, or invalid count')
    return int(value)


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = None
        self.cell = False
        self.in_heading = False
        self.heading = ''
        self.current_heading = ''
        self.in_title = False
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        if tag == 'h2':
            self.in_heading, self.heading = True, ''
        if tag == 'table':
            if self.table is not None:
                raise ValueError('Nested table unsupported')
            self.table = []
            self.tables.append((self.current_heading, self.table))
        if tag == 'tr' and self.table is not None:
            self.table.append([])
        if tag in ('td', 'th') and self.table:
            self.table[-1].append('')
            self.cell = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h2':
            self.in_heading = False
            self.current_heading = ' '.join(self.heading.split())
        if tag == 'table':
            self.table = None
        if tag in ('td', 'th'):
            self.cell = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_heading:
            self.heading += data
        if self.cell and self.table and self.table[-1]:
            self.table[-1][-1] += data


def box_counts(html, team, day):
    parser = Tables()
    parser.feed(html)
    m = re.search(r'Baseball .* on (\d{1,2})/(\d{1,2})/(\d{4}) - Box Score', parser.title)
    if not m or date(int(m[3]), int(m[1]), int(m[2])).isoformat() != day:
        raise ValueError('Wrong box-score date/sport')
    candidates = []
    for heading, rows in parser.tables:
        rows = [[c.strip() for c in row] for row in rows]
        if heading != team or not rows or not {'AB', 'CS', 'HBP', 'SO'} <= set(rows[0]):
            continue
        header = rows[0]
        if len(header) != len(set(header)):
            raise ValueError('Duplicate columns')
        totals = [r for r in rows[1:] if 'Totals' in r]
        players = [r for r in rows[1:] if 'Totals' not in r]
        if len(totals) != 1 or not players or any(len(r) != len(header) for r in rows):
            raise ValueError('Incomplete batting table')
        result = {}
        for key in FIELDS:
            idx = header.index('SO' if key == 'K' else key)
            result[key] = count(totals[0][idx])
            if sum(count(r[idx]) for r in players) != result[key]:
                raise ValueError('Player sums differ from batting totals')
        candidates.append(result)
    if len(candidates) != 1:
        raise ValueError('Missing or ambiguous team batting table')
    return candidates[0]


def d1_counts(snapshot):
    if (snapshot['season'] != 2023 or snapshot['split'] != 'Overall' or
            snapshot['url'] != 'https://d1baseball.com/team/virginia/2023/stats/'):
        raise ValueError('Wrong D1 season/team/split')
    header, *rows = snapshot['rows']
    if not rows or len(header) != len(set(header)) or any(len(r) != len(header) for r in rows):
        raise ValueError('Invalid D1 table')
    if len({r[header.index('PLAYER')] for r in rows}) != len(rows):
        raise ValueError('Duplicate player')
    if any(r[header.index('Team')] != 'Virginia' for r in rows):
        raise ValueError('Wrong player team')
    result = {k: sum(count(r[header.index(k)]) for r in rows) for k in FIELDS}
    if result != snapshot['browser_verified_totals']:
        raise ValueError('Capture differs from independently summed DOM observation')
    return result


def subtract(final, boxes, expected_ids):
    ids = [b['game_id'] for b in boxes]
    if len(set(ids)) != len(ids) or set(ids) != set(expected_ids):
        raise ValueError('Missing, extra, or duplicate excluded game')
    result = {k: final[k] - sum(b['counts'][k] for b in boxes) for k in FIELDS}
    if any(v < 0 for v in result.values()) or result['K'] <= 0:
        raise ValueError('Invalid reconstructed counts')
    return result


def run(raw):
    games_path = REPO/'historical/2023/games.json'
    cutoff_path = REPO/'historical/cutoffs.json'
    contract = json.loads(cutoff_path.read_text())
    cutoff = datetime.fromisoformat(contract['seasons']['2023']['forecast_cutoff']).date()
    games = [g for g in json.loads(games_path.read_text())
             if 'wn:Virginia' in (g['team_a_id'], g['team_b_id'])]
    phases = contract['modes']['conference_inclusive']
    eligible = [g for g in games if g['stage'] in phases and
                date.fromisoformat(g['game_date']) + timedelta(days=2) <= cutoff]
    excluded = [g for g in games if g not in eligible]
    if len(games) != 65 or len(eligible) != 57 or len(excluded) != 8:
        raise ValueError('Pilot schedule scope changed')
    paths = [games_path, cutoff_path, raw/'d1_virginia_2023.json']
    final = d1_counts(json.loads(paths[-1].read_text()))
    if sum(g['runs_a'] if g['team_a_id'] == 'wn:Virginia' else g['runs_b'] for g in games) != final['R']:
        raise ValueError('D1 full-season runs do not match results inventory')
    boxes = []
    for game in excluded:
        stem = game['game_date'].replace('-', '')
        html_path, meta_path = raw/(stem+'.html'), raw/(stem+'.json')
        paths += [html_path, meta_path]
        payload = html_path.read_bytes()
        meta = json.loads(meta_path.read_text())
        if (meta['status'] != 200 or meta['season'] != 2023 or meta['game_date'] != stem
                or hashlib.sha256(payload).hexdigest() != meta['sha256']):
            raise ValueError('Invalid box provenance')
        counts = box_counts(payload.decode(), 'Virginia', game['game_date'])
        own_runs = game['runs_a'] if game['team_a_id'] == 'wn:Virginia' else game['runs_b']
        if counts['R'] != own_runs:
            raise ValueError('Box score differs from retained result')
        opponent_id = game['team_b_id'] if game['team_a_id'] == 'wn:Virginia' else game['team_a_id']
        opponent = {'wn:Army': 'Army', 'wn:East-Carolina': 'East Carolina',
                    'wn:Duke': 'Duke', 'wn:Florida': 'Florida', 'wn:TCU': 'TCU'}[opponent_id]
        other = box_counts(payload.decode(), opponent, game['game_date'])
        other_runs = game['runs_b'] if game['team_a_id'] == 'wn:Virginia' else game['runs_a']
        if other['R'] != other_runs:
            raise ValueError('Opponent box differs from retained result')
        boxes.append(dict(game_id=game['game_id'], date=game['game_date'],
                          counts=counts, url=meta['url']))
    pre = subtract(final, boxes, [g['game_id'] for g in excluded])
    return dict(team='wn:Virginia', season=2023, mode='conference_inclusive',
        forecast_cutoff=contract['seasons']['2023']['forecast_cutoff'],
        latest_included_game=max(g['game_date'] for g in eligible),
        final_games=len(games), included_games=len(eligible), excluded_games=len(boxes),
        final_counts=final, removed_counts={k: final[k]-pre[k] for k in FIELDS},
        reconstructed_counts=pre,
        original_havoc=(2*pre['SB']+pre['BB']+pre['HBP'])/pre['K'],
        net_steals_havoc=(2*(pre['SB']-pre['CS'])+pre['BB']+pre['HBP'])/pre['K'],
        boxes=boxes, source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        limitation='Single-team source proof, not model evaluation or point-in-time certification; later scoring corrections may remain.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.raw_dir), indent=2, sort_keys=True))
