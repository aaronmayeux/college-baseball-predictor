"""Offline, fail-closed LSU 2025 / Towson 2024 appearance qualification.

Season totals are reconciliation targets ONLY, never forecast inputs.
Names identify players only within the sampled school-season.
"""
import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin
from audit_official_player_sample import read
from audit_official_pitching import table_cells, plain, player_key
from audit_official_season_inventory import parse_index, reconcile, ALIASES, REPO
from audit_player_coverage import outs
from eligibility import reject

PITCH_FIELDS = 'outs H R ER BB SO WP BK HBP AB'.split()
BAT_FIELDS = 'AB R H RBI BB SO'.split()
# Deliberate, reviewed source aliases, scoped to these school-seasons.
PLAYER_ALIASES = {'lsu': {}, 'towson': {}}
TEAM_ALIASES = dict(ALIASES, **{'NC State':'wn:North-Carolina-State',
    'Mount St. Mary\'s (Md.)':'wn:Mount-Saint-Marys', 'Charleston':'wn:Charleston',
    'Florida Atlantic':'wn:FAU', 'UNCW':'wn:UNCW'})


def rows(table):
    # StatCrew often omits closing TR tags; split on starts, not closing tags.
    return [table_cells(re.split(r'</tr>',r,maxsplit=1,flags=re.I)[0]) for r in re.split(r'<tr\b[^>]*>', table, flags=re.I)[1:]]


def tables(text):
    return re.findall(r'<table\b[^>]*>.*?</table>', text, re.S | re.I)


def key(name, school):
    name = re.sub(r'\s+(?:W|L|S),.*$', '', name)
    value = player_key(name)
    return PLAYER_ALIASES[school].get(value, value)


def count(value):
    if not re.fullmatch(r'\d+', value):
        raise ValueError('Invalid count: '+value)
    return int(value)


def season_totals(text, school):
    result = {}
    for table in tables(text):
        rr = rows(table)
        if not rr: continue
        header = [c.upper() for c in rr[0]]
        kind = 'pitching' if 'APP-GS' in header else 'batting' if 'GP-GS' in header else None
        if kind is None or kind in result: continue  # first = overall; later = conference
        entries = {}
        for r in rr[1:]:
            if len(r) != len(header): continue  # divider row
            raw = dict(zip(header,r)); name = raw['PLAYER']
            if school == 'towson':
                # Sidearm repeats the display name around the jersey number.
                number = raw.get('#')
                parts = name.split(' '+number+' ') if number else []
                if len(parts)==2 and parts[0]==parts[1]: name=parts[0]
            if name.lower() in ('totals','opponents','opponent'): continue
            if not name: continue
            k = key(name,school)
            if k in entries: raise ValueError('Duplicate cumulative player')
            fields = PITCH_FIELDS if kind=='pitching' else BAT_FIELDS
            values = {f: outs(raw['IP']) if f=='outs' else count(raw[f]) for f in fields}
            values['appearances'] = count(raw['APP-GS' if kind=='pitching' else 'GP-GS'].split('-')[0])
            entries[k] = dict(name=name, counts=values, raw=raw)
        if not entries: raise ValueError('Empty cumulative table')
        result[kind]=entries
    if set(result)!={'pitching','batting'}: raise ValueError('Missing cumulative tables')
    return result


def lsu_box(text, expected):
    title = re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
    date = re.search(r'\(([A-Z][a-z]+ +\d{1,2}, \d{4})\)',plain(title[1])) if title else None
    if not date or dt.datetime.strptime(date[1],'%b %d, %Y').date().isoformat()!=expected['date']: raise ValueError('Box date mismatch')
    result={'pitching':[], 'batting':[]}
    batting_team=None; header=None; pitching_team=None; ph=None; batting_totals={}
    for table in tables(text):
        for cells in rows(table):
            if not cells: continue
            if re.fullmatch(r'.+ \d+ \([\d-]+[^)]*\)',cells[0]):
                m=re.fullmatch(r'(.+) (\d+) \([\d-]+[^)]*\)',cells[0]); batting_team=m[1]
                if batting_team=='LSU' and int(m[2])!=expected['runs'][expected['teams'].index('LSU')]:
                    raise ValueError('LSU box score mismatch')
            if cells[0]=='Player' and 'ab' in cells: header=[v.upper() for v in cells];continue
            if header and cells[0]=='Totals' and len(cells)==len(header):batting_totals[batting_team]=dict(zip(header,cells))
            if len(cells)>1 and cells[1]=='ip':
                pitching_team=cells[0];ph=[v.upper() for v in cells]; continue
            if ph and len(cells)==len(ph) and pitching_team=='LSU' and re.fullmatch(r'\d+\.[012]',cells[1]):
                raw=dict(zip(ph[1:],cells[1:])); values={f:outs(raw['IP']) if f=='outs' else count(raw[f]) for f in PITCH_FIELDS}
                values['BF']=count(raw['BF']); np=None if raw['NP'] in ('','--','0') else count(raw['NP'])
                result['pitching'].append(dict(name=cells[0],counts=values,pitch_count=np or None,raw=raw))
            elif header and batting_team=='LSU' and len(cells)==len(header) and cells[0]!='Totals' and re.fullmatch(r'\d+',cells[1]):
                raw=dict(zip(header,cells)); name=re.sub(r'\s+(?:[123]b|ss|[lcr]f|[pc]|dh|ph|pr)(?:/(?:[123]b|ss|[lcr]f|[pc]|dh|ph|pr))*$', '', cells[0])
                values={f:count(raw[f]) for f in BAT_FIELDS}
                result['batting'].append(dict(name=name,counts=values,raw=raw))
    if not all(result.values()): raise ValueError('Missing LSU player tables')
    if set(batting_totals)!=set(expected['teams']):raise ValueError('Box opponents mismatch')
    for team,score in zip(expected['teams'],expected['runs']):
        if count(batting_totals[team]['R'])!=score:raise ValueError('Box score mismatch')
    for f in BAT_FIELDS:
        if sum(p['counts'][f] for p in result['batting'])!=count(batting_totals['LSU'][f]):raise ValueError('Batting sum mismatch')
    opponent=next(t for t in expected['teams'] if t!='LSU')
    for f in ['H','R','BB','SO']:
        if sum(p['counts'][f] for p in result['pitching'])!=count(batting_totals[opponent][f]):raise ValueError('Pitching versus opponent mismatch')
    if sum(p['counts']['outs'] for p in result['pitching'])!=count(batting_totals['LSU']['PO']):raise ValueError('Pitching outs versus putouts mismatch')
    return result


def towson_box(text, expected):
    title=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
    d=dt.date.fromisoformat(expected['date']); date=f'{d.month}/{d.day}/{d.year}'
    if not title or date not in plain(title[1]):raise ValueError('Box date mismatch')
    names=[plain(c).removesuffix(' - Pitching Stats').lower() for c in re.findall(r'<caption[^>]*>(.*?)</caption>',text,re.S|re.I) if plain(c).endswith(' - Pitching Stats')]
    expected_names=[n.lower().replace("mount st. mary's (md.)","mount st. mary's") for n in expected['teams']]
    if len(names)!=2 or set(names)!=set(expected_names):raise ValueError('Box opponents mismatch')
    pitching=[]; pitch_totals=None
    for table in tables(text):
        cap=re.search(r'<caption[^>]*>(.*?)</caption>',table,re.S|re.I)
        rr=rows(table)
        if not cap or plain(cap[1]).lower()!='towson - pitching stats':continue
        if not rr or rr[0] != 'Player IP H R ER BB SO WP BK HBP IBB AB BF FO GO NP'.split():
            raise ValueError('Pitching header changed')
        for cells in rr[1:]:
            if len(cells)!=len(rr[0]):raise ValueError('Pitching width changed')
            raw=dict(zip(rr[0],cells))
            if raw['Player']=='Totals':
                if pitch_totals is not None:raise ValueError('Duplicate pitching totals')
                pitch_totals=raw;continue
            values={f:outs(raw['IP']) if f=='outs' else count(raw[f]) for f in PITCH_FIELDS}
            values['BF']=count(raw['BF'])
            np=None if raw['NP'] in ('','--','0') else count(raw['NP'])
            pitching.append(dict(name=raw['Player'],counts=values,pitch_count=np,raw=raw))
    if not pitching or pitch_totals is None:raise ValueError('Missing Towson pitching')
    # Team ER can legitimately differ from summed individual ER (NCAA 10-22).
    for f in [v for v in PITCH_FIELDS[1:]+['BF'] if v!='ER']:
        if sum(p['counts'][f] for p in pitching)!=count(pitch_totals[f]):raise ValueError('Pitching total mismatch')
    if sum(p['counts']['R'] for p in pitching)!=expected['runs'][1]:raise ValueError('Opponent score mismatch')
    batting=[]; bat_totals=None
    for table in tables(text):
        cap=re.search(r'<caption[^>]*>(.*?)</caption>',table,re.S|re.I)
        rr=rows(table)
        if not cap or not re.fullmatch(r'towson \d+',plain(cap[1]).lower()) or not rr or rr[0][0]!='Position':continue
        header=rr[0]
        for cells in rr[1:]:
            if len(cells)!=len(header): raise ValueError('Batting width changed')
            raw=dict(zip(header,cells))
            if 'Totals' in raw['Player']:
                if bat_totals is not None:raise ValueError('Duplicate batting totals')
                bat_totals=raw;continue
            name=raw['Player']
            pos=raw['Position']
            if pos and name.startswith(pos+' '): name=name[len(pos)+1:]
            batting.append(dict(name=name,counts={f:count(raw[f]) for f in BAT_FIELDS},raw=raw))
    if not batting or bat_totals is None:raise ValueError('Missing Towson batting')
    for f in BAT_FIELDS:
        if sum(p['counts'][f] for p in batting)!=count(bat_totals[f]):raise ValueError('Batting total mismatch')
    if sum(p['counts']['R'] for p in batting)!=expected['runs'][0]:raise ValueError('Batting score mismatch')
    return {'pitching':pitching,'batting':batting}


def towson_index(text,url):
    result=[]
    for block in re.split(r'<li\b[^>]*class="sidearm-schedule-game\s',text)[1:]:
        outcome=re.search(r'<div class="sidearm-schedule-game-result[^>]*>(.*?)</div>',block,re.S)
        opponent=re.search(r'<div class="sidearm-schedule-game-opponent-name[^>]*>(.*?)</div>',block,re.S)
        date=re.search(r'on ([A-Z][a-z]+ \d{1,2}, 2024)',block)
        link=re.search(r'href="([^"]*/sports/baseball/stats/2024/[^\"]*/boxscore/\d+)"',block)
        if not outcome:continue
        score=re.search(r'\b([WLT]),?\s*(\d+)\s*-\s*(\d+)',plain(outcome[1]))
        if not score:continue
        if not all([opponent,date,link]):raise ValueError('Scored schedule row lacks identity/link')
        result.append(dict(date=dt.datetime.strptime(date[1],'%B %d, %Y').date().isoformat(),
            teams=['Towson',re.sub(r' \(DH\)$','',re.sub(r'^#\d+\s+','',plain(opponent[1])))],runs=[int(score[2]),int(score[3])],box_url=urljoin(url,link[1])))
    if not result:raise ValueError('No completed Towson games')
    return result


def compare_totals(appearances, totals, school, kind):
    sums=defaultdict(lambda:defaultdict(int));unknown=[]
    for app in appearances:
        k=key(app['name'],school)
        # StatCrew batting includes pitcher-only fielding lines absent from its batting leaderboard.
        if kind=='batting' and not any(app['counts'].values()) and ((school=='towson' and k not in totals and app.get('raw',{}).get('Position')=='p') or (school=='lsu' and app.get('raw',{}).get('PLAYER','').endswith(' p'))):
            unknown.append(dict(name=app['name'],reason='pitcher_only_zero_batting_line',game=app['box_url']));continue
        sums[k]['appearances']+=1
        for field in (PITCH_FIELDS if kind=='pitching' else BAT_FIELDS):sums[k][field]+=app['counts'][field]
    differences=[]
    for k in sorted(set(sums)|set(totals)):
        target=totals.get(k,{}).get('counts')
        if target is None:
            differences.append(dict(player=k,field='identity',observed=dict(sums[k]),expected=None));continue
        for field,expected in target.items():
            if sums[k][field]!=expected:differences.append(dict(player=k,field=field,observed=sums[k][field],expected=expected))
    return dict(player_count=len(totals),appearance_rows=len(appearances),differences=differences,
        ignored_zero_batting_lines=unknown,totals_match=not differences,
        per_player={k:dict(v) for k,v in sorted(sums.items())})


def coverage_status(expected, records):
    """A missing or invalid box cannot establish zero workload or rest."""
    by_url={r['box_url']:r for r in records}
    complete=(bool(expected) and len(set(expected))==len(expected) and len(by_url)==len(records)
              and set(by_url)==set(expected) and all(not by_url[u]['issues'] and by_url[u].get('parsed') for u in expected))
    return dict(complete_game_boxes=complete,rest_status='unknown',feature_qualified=False)


def audit(root):
    cached={}
    for p in sorted(root.glob('*.meta.json')):
        m=json.loads(p.read_text()); k=p.name.removesuffix('.meta.json')
        if m.get('http_status')==200:cached.setdefault(m['url'],k)
    result=[]
    contract=json.loads((REPO/'historical/cutoffs.json').read_text())
    for school,year,team,index_key,cume_key in [('lsu',2025,'LSU','lsu_index_2025.html','lsu_cume.html'),('towson',2024,'Towson','towson_2024_schedule.html','towson_cume.html')]:
        index,im=read(root,index_key);cume,cm=read(root,cume_key)
        expected_url='https://static.lsusports.net/assets/docs/bb/25stats/teamcume.htm' if school=='lsu' else 'https://towsontigers.com/sports/baseball/stats/2024'
        if cm['url']!=expected_url:raise ValueError('Unexpected cumulative URL')
        if school=='towson' and '2024 Baseball' not in plain(cume):raise ValueError('Wrong cumulative year')
        index_url='https://static.lsusports.net/assets/docs/bb/25stats/teamstat.htm' if school=='lsu' else 'https://towsontigers.com/sports/baseball/schedule/2024'
        if im['url'].rstrip('/')!=index_url:raise ValueError('Unexpected index URL')
        official=parse_index(index,im['url'],year) if school=='lsu' else towson_index(index,im['url'])
        paths=[REPO/f'historical/{year}/{x}.json' for x in ['games','teams']]+[REPO/'historical/cutoffs.json']
        games,teams=[json.loads(p.read_text()) for p in paths[:2]]
        if any(g['season']!=year for g in games+teams):raise ValueError('Wrong baseline season')
        identities={t['name']:t['team_id'] for t in teams};identities.update(TEAM_ALIASES)
        inventory=reconcile(official,games,identities,'wn:'+team)
        totals=season_totals(cume,school); appearances={'pitching':[],'batting':[]};records=[]
        for row in inventory['games']:
            record=dict(row,issues=list(row['issues']),parsed=False)
            url=row['box_url']
            if url not in cached:record['issues'].append('missing_box')
            else:
                try:
                    text,meta=read(root,cached[url]);parsed=lsu_box(text,row) if school=='lsu' else towson_box(text,row)
                    for kind,players in parsed.items():
                        keys=[key(p['name'],school) for p in players]
                        if len(set(keys))!=len(keys):raise ValueError('Duplicate player appearance')
                    record.update(parsed=True,source=meta,
                        timing_warning=bool(re.search(r'\bsuspend(?:ed|ing|sion)?\b|\bresum(?:e|ed|ing)\b',plain(text),re.I)))
                    for kind,players in parsed.items():
                        for p in players:
                            # Date is the source box label, not certified actual appearance/completion time.
                            appearances[kind].append(dict(p,box_url=url,source_date=row['date'],game_id=row['game_id'],
                                actual_appearance_date=None,source_sha256=meta['sha256']))
                except (ValueError,KeyError) as e:record['issues'].append('parse: '+str(e))
            records.append(record)
        comparisons={k:compare_totals(v,totals[k],school,k) for k,v in appearances.items()}
        by_id={g['game_id']:g for g in games};cutoff=dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        modes={}
        for mode,stages in contract['modes'].items():
            eligible=[g for g in games if 'wn:'+team in (g['team_a_id'],g['team_b_id']) and reject(g,cutoff,stages) is None]
            ids={g['game_id'] for g in eligible};good=[r for r in records if r['game_id'] in ids and not r['issues']]
            modes[mode]=dict(expected_games=len(ids),verified_game_boxes=len(good),
                pitching_appearance_rows=sum(a['game_id'] in ids for a in appearances['pitching']),
                inventory_and_boxes_complete=len(good)==len(ids) and bool(ids),rest_status='unknown')
        result.append(dict(school=school,season=year,inventory=inventory,records=records,
            sources=[im,cm],baseline_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            comparisons=comparisons,appearances=appearances,forecast_modes=modes,
            status=coverage_status([r['box_url'] for r in official],records),
            season_counts_reconciled=all(r['parsed'] for r in records) and all(v['totals_match'] for v in comparisons.values()),
            actual_appearance_dates_qualified=False,stable_player_ids_qualified=False,
            point_in_time_certified=False))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();data=audit(args.raw_dir);args.output.write_text(json.dumps(data,indent=2)+'\n')
    for r in data:
        print(r['school'],r['inventory']['index_rows'],'games',sum(x['parsed'] for x in r['records']),'parsed',
              {k:len(v['differences']) for k,v in r['comparisons'].items()},r['forecast_modes'])
