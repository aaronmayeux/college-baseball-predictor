"""Read embedded SIDEARM/Nuxt historical data without executing page JavaScript."""
import json
import re
from urllib.parse import urljoin, urlparse
from audit_season_appearances import count


def decode(text):
    match=re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>',text,re.S)
    if not match:raise ValueError('No embedded historical payload')
    nodes=json.loads(match[1]);cache={};active=set()
    def resolve(index):
        if not isinstance(index,int) or isinstance(index,bool):raise ValueError('Invalid data reference')
        if index in (-1,-2):return None
        if index<0 or index>=len(nodes):raise ValueError('Unsupported data reference')
        if index in active:raise ValueError('Cyclic embedded data')
        if index in cache:return cache[index]
        active.add(index);value=nodes[index]
        if isinstance(value,dict):result={k:resolve(v) for k,v in value.items()}
        elif isinstance(value,list):
            if value and isinstance(value[0],str):
                tag=value[0]
                if tag in ('Reactive','ShallowReactive','Ref','ShallowRef') and len(value)==2:result=resolve(value[1])
                elif tag=='Set':result=[resolve(v) for v in value[1:]]
                else:raise ValueError('Unsupported payload tag: '+tag)
            else:result=[resolve(v) for v in value]
        else:result=value.replace('\\u002F','/') if isinstance(value,str) else value
        active.remove(index);cache[index]=result;return result
    result=resolve(0)
    if not isinstance(result,dict):raise ValueError('Invalid payload root')
    return result


def payload(text,url):
    data=decode(text)
    if data.get('path','').rstrip('/')!=urlparse(url).path.rstrip('/'):
        raise ValueError('Payload path differs from requested historical page')
    return data['pinia']


def schedule(text,config):
    year=config['season'];url=config['schedule_url']
    data=payload(text,url)['schedule']['schedules'][f'schedules-baseball,{year}']
    if data['season']['title']!=str(year) or data['sport']['shortname']!='baseball':raise ValueError('Wrong schedule season/sport')
    completed=[];excluded=[]
    for game in data['games']:
        result=game.get('result') or {};date=game['date'][:10]
        reason=None
        if int(date[:4])!=year:reason='outside_calendar_season'
        elif result.get('status') not in ('W','L','T'):reason='no_completed_result'
        elif game.get('noplay_text'):raise ValueError('Result conflicts with no-play label')
        if reason:
            excluded.append(dict(source_game=game,reason=reason));continue
        box=result.get('boxscore');box_url=urljoin(url,box['url']) if box else None
        if box_url and (urlparse(box_url).netloc!=urlparse(url).netloc or f'/stats/{year}/' not in box_url):raise ValueError('Box outside historical source scope')
        completed.append(dict(date=date,teams=[config['team_name'],re.sub(r'^(?:#\d+|\[\d+\])\s+','',game['opponent']['title'].strip())],
            runs=[count(result['team_score']),count(result['opponent_score'])],box_url=box_url,
            source_opponent=game['opponent']['title'],source_game_id=str(game['id']),source_start=game['date'],source_end=game.get('enddate'),
            source_type=game.get('type'),source_result=result['status']))
    if len(completed)!=config['expected_completed_games']:raise ValueError('Pilot game count changed; review inventory')
    urls=[r['box_url'] for r in completed if r['box_url']]
    if len(urls)!=len(set(urls)):raise ValueError('Duplicate box URL')
    return completed,excluded

# Canonical count fields mapped to the source's box and cumulative spellings.
PITCH = {'outs':('inningsPitched','inningsPitched'),'H':('hitsAllowed','hitsAllowed'),
    'R':('runsAllowed','runsAllowed'),'ER':('earnedRunsAllowed','earnedRunsAllowed'),
    'BB':('walksAllowed','walksAllowed'),'SO':('strikeouts','strikeouts'),
    'WP':('wildPitches','wildPitches'),'BK':('balks','balks'),'HBP':('hitBatters','hitBatters'),
    'AB':('opponentAtBats','opponentsAtBats'),'HR':('homerunsAllowed','homeRunsAllowed'),
    '2B':('doublesAllowed','doublesAllowed'),'3B':('triplesAllowed','triplesAllowed'),
    'SF':('sacrificeFliesAllowed','sacrificeFliesAllowed'),'SH':('sacrificeHitsAllowed','sacrificeHitsAllowed'),
    'GS':('gamesStarted','gamesStarted')}
BAT = {'AB':('atBats','atBats'),'R':('runsScored','runs'),'H':('hits','hits'),
    'RBI':('runsBattedIn','runsBattedIn'),'BB':('walks','walks'),'SO':('strikeouts','strikeouts'),
    'HR':('homeRuns','homeRuns'),'2B':('doubles','doubles'),'3B':('triples','triples'),
    'HBP':('hitByPitch','hitByPitch'),'SF':('sacrificeFlies','sacrificeFlies'),
    'SH':('sacrificeHits','sacrificeHits'),'SB':('stolenBases','stolenBases'),
    'CS':('caughtStealing','caughtStealing')}


def counts(raw,mapping,column):
    from audit_player_coverage import outs
    result={}
    for key,source in mapping.items():
        value=raw.get(source[column])
        if not isinstance(value,str):raise ValueError('Missing source field '+source[column])
        result[key]=outs(value) if key=='outs' else count(value)
    return result


def only(values):
    items=list(values)
    if len(items)!=1:raise ValueError('Expected one historical data object')
    return items[0]


def cumulative(text,config):
    import datetime as dt
    from audit_official_pitching import player_key
    data=only(payload(text,config['cumulative_url'])['statsSeason']['cumulativeStats'].values())
    if data['ourTeamName']!=config['team_name'] or f'/baseball/{config["season"]}/' not in data['pdfDoc']:
        raise ValueError('Wrong cumulative team/season')
    game_rows=[g for g in data['gameByGameStats']['ourGameByGameStats'] if not g['isAFooterStat']]
    for g in game_rows:
        if dt.datetime.strptime(g['date'],'%m/%d/%Y').year!=config['season']:raise ValueError('Wrong cumulative game year')
    if len(game_rows)!=config['expected_completed_games']:raise ValueError('Cumulative game count differs')
    result={}
    individual=data['overallIndividualStats']['individualStats']
    for kind,source,mapping in [('pitching','individualPitchingStats',PITCH),('batting','individualHittingStats',BAT)]:
        players={}
        for p in individual[source]:
            if p['isAFooterStat']:continue
            key=player_key(p['playerName'])
            if key in players:raise ValueError('Ambiguous cumulative player')
            values=counts(p,mapping,1);values['appearances']=count(p['appearances'] if kind=='pitching' else p['gamesPlayed'])
            players[key]=dict(name=p['playerName'],provider_player_id=p['playerRosterBioId'] or None,counts=values,raw=p)
        if not players:raise ValueError('Empty cumulative players')
        result[kind]=players
    return result,game_rows


def box(text,url,expected,config):
    import datetime as dt
    from audit_official_pitching import player_key
    data=only(payload(text,url)['boxscore']['boxscore'].values());venue=data['venue']
    date=dt.datetime.strptime(venue['date'],'%m/%d/%Y').date().isoformat()
    if date!=expected['date']:raise ValueError('Box date mismatch')
    # Compare explicit source aliases only; do not fuzzy-match schools.
    aliases=config.get('box_team_aliases',{})
    team_key=lambda name:aliases.get(name.strip(),name.strip()).casefold()
    sides=[data['homeTeam'],data['visitingTeam']]
    actual={team_key(t['name']):count(t['scoringSummary']['runs']) for t in sides}
    wanted={team_key(n):r for n,r in zip(expected['teams'],expected['runs'])}
    if len(actual)!=2 or actual!=wanted:raise ValueError('Box teams/scores mismatch')
    team=only(t for t in sides if team_key(t['name'])==team_key(config['team_name']))
    result={'pitching':[],'batting':[]};unused=[]
    for p in team['players']:
        if p['gamePlayed'] not in ('0','1'):raise ValueError('Unknown player participation')
        if p['gamePlayed']=='0':
            if p.get('pitching') is not None or p.get('hitting') is not None:raise ValueError('Unused player has statistics')
            unused.append(dict(name=p['name'],provider_player_id=p.get('rosterPlayerId')));continue
        for kind,mapping,field in [('pitching',PITCH,'pitching'),('batting',BAT,'hitting')]:
            raw=p.get(field)
            if raw is None:continue
            values=counts(raw,mapping,0)
            row=dict(name=p['name'],match_key=player_key(p['name']),counts=values,
                provider_player_id=p.get('rosterPlayerId') or None,position=p['position'],
                game_started=p['gameStarted'],raw=raw)
            if kind=='pitching':
                row['counts']['BF']=count(raw['battersFaced'])
                row['pitch_count']=None if raw.get('pitches') in (None,'','0','--') else count(raw['pitches'])
            result[kind].append(row)
    for kind in result:
        if not result[kind] or len({p['match_key'] for p in result[kind]})!=len(result[kind]):raise ValueError('Empty/duplicate player appearances')
    # Individual ER can differ from team ER. Never force them to match.
    for kind,mapping,field in [('pitching',PITCH,'pitching'),('batting',BAT,'hitting')]:
        total=team['totals'][field]
        for k,(source,_) in mapping.items():
            if k in ('ER','GS'):continue
            value=counts({source:total[source]},{k:(source,source)},0)[k]
            if sum(p['counts'][k] for p in result[kind])!=value:raise ValueError(kind+' total mismatch: '+k)
    if sum(p['counts']['GS'] for p in result['pitching'])!=1:raise ValueError('Expected one starting pitcher')
    return result,dict(venue=venue,unused_roster_rows=unused,provider_game_id=data['gameId'])
