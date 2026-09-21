"""Shared StatCrew archive readers. Cumulative values are audit targets only."""
import datetime as dt
import re
from urllib.parse import urljoin, urlparse
from audit_season_appearances import tables, rows, count, PITCH_FIELDS, BAT_FIELDS
from audit_official_pitching import player_key
from audit_official_season_inventory import plain
from audit_player_coverage import outs


def verify_season(text, url, season):
    # Require both an explicit archive path and the report's own source marker.
    # A URL alone is not evidence of the returned season.
    if f'/{season}/' not in urlparse(url).path:
        raise ValueError('Missing historical archive path')
    markers = re.findall(r'<!File source:[^>]*[\\/](\d{4})(?:BASE)?[\\/]reports[\\/]', text, re.I)
    if not markers or set(markers) != {str(season)}:
        raise ValueError('Missing or conflicting StatCrew report season')


def cumulative(text, url, season):
    verify_season(text, url, season)
    section = re.search(r'<!File source:[^>]*[\\/]team\.mlb>(.*?)(?=<!File source:|\Z)', text, re.S | re.I)
    if not section: raise ValueError('Missing overall statistics section')
    result = {}
    for table in tables(section[1]):
        rr = rows(table)
        if not rr: continue
        header = [c.upper() for c in rr[0]]
        kind = 'pitching' if 'APP-GS' in header else 'batting' if 'GP-GS' in header else None
        if kind is None: continue
        if kind in result: raise ValueError('Duplicate overall statistics group')
        if len(set(header)) != len(header) or 'PLAYER' not in header:
            raise ValueError('Ambiguous cumulative header')
        fields = PITCH_FIELDS if kind == 'pitching' else BAT_FIELDS
        players = {}; totals = None; opponents = None
        for r in rr[1:]:
            if not r or not any(r): continue
            if len(r) == 1 and re.fullmatch(r'-+', r[0]): continue
            if len(r) != len(header):
                raise ValueError('Malformed cumulative row')
            raw = dict(zip(header, r)); name = raw['PLAYER']
            if not name: raise ValueError('Unnamed cumulative row')
            values = {f: outs(raw['IP']) if f == 'outs' else count(raw[f]) for f in fields}
            if name.lower() in ('totals', 'opponents', 'opponent'):
                if name.lower() == 'totals':
                    if totals is not None: raise ValueError('Duplicate total row')
                    totals = dict(counts=values, raw=raw)
                else:
                    if opponents is not None: raise ValueError('Duplicate opponents row')
                    opponents = dict(counts=values, raw=raw)
                continue
            key = player_key(name)
            if key in players: raise ValueError('Duplicate cumulative player')
            gp = raw['APP-GS' if kind == 'pitching' else 'GP-GS']
            if not re.fullmatch(r'\d+-\d+', gp): raise ValueError('Malformed appearances/starts')
            appearances, starts = map(int, gp.split('-'))
            if starts > appearances: raise ValueError('Starts exceed appearances')
            players[key] = dict(name=name, counts=values, appearances=appearances, starts=starts, raw=raw)
        if not players or totals is None or opponents is None: raise ValueError('Incomplete cumulative table')
        sums = {f: sum(p['counts'][f] for p in players.values()) for f in fields}
        # Individual ER can exceed team ER because of team-unearned scoring.
        differences = {f: dict(player_sum=sums[f], team_total=totals['counts'][f]) for f in fields if f != 'ER' and sums[f] != totals['counts'][f]}
        result[kind] = dict(players=players, team_total=totals, opponent_total=opponents,
            player_sums=sums, additive_differences=differences,
            additive_counts_match=not differences,
            player_appearance_sum=sum(p['appearances'] for p in players.values()),
            individual_er_sum=sums.get('ER'), team_er=totals['counts'].get('ER'))
    if set(result) != {'pitching', 'batting'}: raise ValueError('Missing cumulative player groups')
    return result


def conference_index(text, url, season, team_name):
    verify_season(text, url, season)
    title = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
    if not title or not plain(title[1]).endswith(' - '+team_name):
        raise ValueError('Wrong conference archive team')
    candidates = [t for t in tables(text) if rows(t) and 'Game date' in rows(t)[0] and 'Opposing team' in rows(t)[0]]
    if len(candidates) != 1: raise ValueError('Missing/ambiguous game table')
    result = []
    for raw in re.split(r'<tr\b[^>]*>', candidates[0], flags=re.I)[2:]:
        cells = rows('<table><tr>'+raw+'</table>')[0]
        if not any(cells): continue
        if len(cells) != 16: raise ValueError('Malformed conference game row')
        date = dt.datetime.strptime(cells[1], '%b %d, %Y').date()
        if date.year != season: raise ValueError('Wrong conference game year')
        score = re.fullmatch(r'(\d+)-(\d+)', cells[5])
        links = re.findall(r'href=["\']([^"\']+)["\']', raw, re.I)
        if not score or len(links) != 1: raise ValueError('Missing score or unique box link')
        box_url = urljoin(url, links[0])
        if urlparse(box_url).netloc != urlparse(url).netloc or f'/{season}/' not in urlparse(box_url).path:
            raise ValueError('Box outside historical archive')
        opponent = re.sub(r'^#\d+\s+', '', cells[3])
        # StatCrew appends a doubleheader number; retain the original label too.
        opponent = re.sub(r'-[12]$', '', opponent)
        result.append(dict(date=date.isoformat(), teams=[team_name, opponent],
            runs=[int(score[1]), int(score[2])], box_url=box_url,
            source_opponent=cells[3], source_row=cells))
    if not result: raise ValueError('Empty conference game table')
    if len({r['box_url'] for r in result}) != len(result): raise ValueError('Duplicate conference box URL')
    return result
