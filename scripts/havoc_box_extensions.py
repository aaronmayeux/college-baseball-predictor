"""Strict adapters for reviewed suspended dates and WMT's two batting views.

WMT composite SO is pitching SO in the observed historical pages. Never use
that field as batting K: join the explicit hitting K by player, checking the
opposing pitching totals. Original captures remain unchanged.
"""
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
from reconstruct_havoc_pilot import FIELDS, count


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def subtraction_day(raw, url, game):
    path = raw/'date_reviews.json'
    if not path.exists():
        return game['game_date']
    rows = [r for r in read(path) if r['game_id'] == game.get('game_id') and url in r['box_urls']]
    if not rows:
        return game['game_date']
    if len(rows) != 1:
        raise ValueError('Ambiguous date review')
    r = rows[0]
    binding = {k:game[k] for k in ('game_id','season','game_date','team_a_id','team_b_id','runs_a','runs_b','stage')}
    if r['original'] != binding or r['completion_date'] != game['game_date']:
        raise ValueError('Date review does not match original game')
    start, end = date.fromisoformat(r['start_date']), date.fromisoformat(r['completion_date'])
    contract = read(Path(__file__).resolve().parents[1]/'historical/cutoffs.json')
    cutoff = datetime.fromisoformat(contract['seasons'][str(game['season'])]['forecast_cutoff']).date()
    if not (cutoff < start < end and (end-start).days == 1 and start.year == game['season']
            and game['stage'] in ('regional','super_regional','omaha','championship_series')):
        raise ValueError('Date review must be wholly post-cutoff NCAA subtraction')
    if not r['evidence'] or not r.get('review_reason'):
        raise ValueError('Missing date evidence')
    for e in r['evidence']:
        p = (raw/e['path']).resolve()
        if not p.is_relative_to(raw.resolve()) or digest(p) != e['sha256']:
            raise ValueError('Changed date evidence')
        meta = read(p.with_suffix('.json'))
        if meta['status'] != 200 or meta['url'] != e['url'] or meta['sha256'] != e['sha256']:
            raise ValueError('Unverified date evidence provenance')
        datetime.fromisoformat(meta['retrieved_at_utc'])
    return r['start_date']


def _one(tables, first):
    matches = [t for t in tables if t and t[0] == first]
    if len(matches) != 1:
        raise ValueError('Missing or duplicate WMT table')
    return matches[0]


def _rows(table, header, fields, player_index):
    if len(header) != len(set(header)) or not set(fields) <= set(header):
        raise ValueError('Incomplete WMT schema')
    players, totals = {}, []
    for ordinal, row in enumerate(table, 1):
        # WMT DOM includes an unheaded trailing pitcher display-order cell.
        if player_index == 0 and row[0] != "Total" and len(row) == len(header)+1 and row[-1] == str(ordinal):
            row = row[:-1]
        # Total spans the two descriptive columns in batting tables.
        if row[0] == 'Total' and player_index == 1:
            row = [row[0], ''] + row[1:]
        if len(row) != len(header):
            raise ValueError('Truncated WMT row')
        values = {k:count(row[header.index(k)]) for k in fields}
        if row[0] == 'Total':
            totals.append(values)
        else:
            name = row[player_index]
            if not name or name in players:
                raise ValueError('Missing/duplicate WMT player')
            players[name] = values
    if not players or len(totals) != 1 or any(sum(p[k] for p in players.values()) != totals[0][k] for k in fields):
        raise ValueError('WMT player sums differ')
    return players, totals[0]


def wmt_counts(doc, game, day):
    box, comp = doc['box'], doc['composite']
    names = [game[k].removeprefix('wn:').replace('-', ' ') for k in ('team_a_id','team_b_id')]
    scores = dict(zip(names, (game['runs_a'],game['runs_b'])))
    expected_day = datetime.strptime(day, '%Y-%m-%d').strftime('%m/%d/%Y')
    if box['title'] != comp['title'] or box['heading'] != comp['heading']:
        raise ValueError('WMT view identity differs')
    m = re.fullmatch(r'WMT Stats // (.+) - (.+) // (\d{2}/\d{2}/\d{4}) // (\d+) - (\d+)', box['title'])
    if (not m or {m[1],m[2]} != set(names) or m[3] != expected_day
            or (int(m[4]),int(m[5])) != (scores[m[1]],scores[m[2]])
            or box['date'] != expected_day or comp['date'] != expected_day):
        raise ValueError('Wrong WMT identity/date/score')
    result, pitching = {}, {}
    for name in names:
        c = _one(comp['tables'], ['',name])
        cp, ct = _rows(c[2:],c[1], ('AB','R','H','BB','SB','CS','HBP'),1)
        b = _one(box['tables'], ['Pos','Player',name])
        bp, bt = _rows(b[2:],['Pos','Player']+b[1], ('AB','R','H','BB','K'),1)
        if cp.keys() != bp.keys() or any(cp[p][k] != bp[p][k] for p in cp for k in ('AB','R','H','BB')):
            raise ValueError('WMT views disagree on player batting counts')
        if ct['R'] != scores[name]:
            raise ValueError('Wrong WMT batting score')
        p = _one(box['tables'], [name])
        _, pitching[name] = _rows(p[2:],p[1],('AB','R','H','BB','SO','HB'),0)
        result[name] = dict(ct,K=bt['K'])
    for name,opp in (names,names[::-1]):
        for own,other in (('AB','AB'),('R','R'),('H','H'),('BB','BB'),('K','SO'),('HBP','HB')):
            if result[name][own] != pitching[opp][other]:
                raise ValueError('Batting/opposing pitching mismatch')
    return {game[k]:result[name] for k,name in zip(('team_a_id','team_b_id'),names)}


def verified_wmt(raw, url, game, day):
    stem = raw/'wmt_boxes'/hashlib.sha256(url.encode()).hexdigest()
    meta, path = read(stem.with_suffix('.meta.json')), stem.with_suffix('.json')
    if meta['url'] != url or meta['acquisition'] != 'browser_dom' or digest(path) != meta['sha256']:
        raise ValueError('Changed WMT capture')
    datetime.fromisoformat(meta['retrieved_at_utc'])
    if not re.fullmatch(r'https://wmt.games/auburn/stats/match/full/\d+', meta['embedded_url']):
        raise ValueError('Unexpected embedded provider')
    # Retained official DOM or HTTP page must explicitly link this exact iframe.
    parent = (raw/meta['parent_path']).resolve()
    if not parent.is_relative_to(raw.resolve()) or digest(parent) != meta['parent_sha256'] or meta['embedded_url'] not in parent.read_text():
        raise ValueError('Unverified official embedding')
    return wmt_counts(read(path),game,day)
