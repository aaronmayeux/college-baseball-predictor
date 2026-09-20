"""Offline whole-season audit for explicit entries in player_sources.json."""
import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
from pathlib import Path
from audit_official_player_sample import read
from audit_official_season_inventory import REPO, reconcile, ALIASES
from sidearm_structured import schedule, cumulative, box, PITCH, BAT
from eligibility import reject

REGISTRY=REPO/'historical/player_sources.json'


def compare(apps,targets,kind):
    mapping=PITCH if kind=='pitching' else BAT;sums=defaultdict(lambda:defaultdict(int));excluded=[];ids=defaultdict(set)
    for app in apps:
        key=app['match_key']
        if kind=='batting' and key not in targets and app['position']=='p' and not any(app['counts'].values()):
            excluded.append(dict(name=app['name'],box_url=app['box_url'],reason='pitcher_only_zero_batting_line'));continue
        sums[key]['appearances']+=1
        for field in mapping:sums[key][field]+=app['counts'][field]
        if app['provider_player_id']:ids[key].add(app['provider_player_id'])
    differences=[];id_issues=[]
    for key in sorted(set(sums)|set(targets)):
        target=targets.get(key)
        if target is None:differences.append(dict(player=key,field='identity',observed=dict(sums[key]),expected=None));continue
        for field,expected in target['counts'].items():
            if sums[key][field]!=expected:differences.append(dict(player=key,field=field,observed=sums[key][field],expected=expected))
        target_id=target['provider_player_id']
        if target_id is None or ids[key]!={target_id}:id_issues.append(dict(player=key,cumulative_id=target_id,box_ids=sorted(ids[key])))
    return dict(player_count=len(targets),appearance_rows=len(apps),counted_appearances=sum(v['appearances'] for v in sums.values()),
        differences=differences,totals_match=not differences,player_id_issues=id_issues,
        excluded_pitcher_only_batting_rows=excluded,per_player={k:dict(v) for k,v in sorted(sums.items())})


def audit(root):
    configs=json.loads(REGISTRY.read_text())['entries'];contract_path=REPO/'historical/cutoffs.json';contract=json.loads(contract_path.read_text())
    cache={}
    for mp in sorted(root.glob('*.meta.json')):
        meta=json.loads(mp.read_text());cache.setdefault(meta['url'],mp.name.removesuffix('.meta.json'))
    def source(url):
        if url not in cache:raise ValueError('missing_source')
        text,meta=read(root,cache[url])
        if meta['url']!=url:raise ValueError('Source URL mismatch')
        return text,meta
    result=[]
    for config in configs:
        if config['adapter']!='sidearm_embedded_v1':continue
        year=config['season'];text,sm=source(config['schedule_url']);rows,excluded=schedule(text,config)
        text,cm=source(config['cumulative_url']);targets,cume_games=cumulative(text,config)
        cume_by_url={g['boxscoreUrl'].rstrip('/').rsplit('/',1)[-1]:g for g in cume_games}
        if len(cume_by_url)!=len(cume_games):raise ValueError('Duplicate cumulative game URL')
        games_path=REPO/f'historical/{year}/games.json';teams_path=REPO/f'historical/{year}/teams.json'
        games=json.loads(games_path.read_text());teams=json.loads(teams_path.read_text())
        if any(x['season']!=year for x in games+teams):raise ValueError('Baseline season mismatch')
        identities={t['name']:t['team_id'] for t in teams};identities.update(ALIASES);identities.update(config.get('team_aliases',{}))
        inventory=reconcile(rows,games,identities,config['team_id']);appearances={'pitching':[],'batting':[]};records=[]
        for row in inventory['games']:
            record=dict(row,issues=list(row['issues']),parsed=False)
            g=cume_by_url.get(row['source_game_id'])
            if g is None:record['issues'].append('absent_from_cumulative_games')
            elif (dt.datetime.strptime(g['date'],'%m/%d/%Y').date().isoformat()!=row['date']
                  or [int(g['ourScore']),int(g['opponentScore'])]!=row['runs']):record['issues'].append('cumulative_game_disagreement')
            try:
                text,meta=source(row['box_url']);parsed,details=box(text,row['box_url'],row,config)
                record.update(parsed=True,source=meta,details=details)
                for kind,players in parsed.items():
                    for p in players:appearances[kind].append(dict(p,source_date=row['date'],actual_appearance_date=None,
                        game_id=row['game_id'],box_url=row['box_url'],source_sha256=meta['sha256']))
            except (ValueError,KeyError,TypeError) as error:record['issues'].append('box: '+str(error))
            records.append(record)
        comparisons={k:compare(v,targets[k],k) for k,v in appearances.items()};cutoff=dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        modes={}
        for mode,phases in contract['modes'].items():
            expected={g['game_id'] for g in games if config['team_id'] in (g['team_a_id'],g['team_b_id']) and reject(g,cutoff,phases) is None}
            good=[r for r in records if r['game_id'] in expected and not r['issues']]
            modes[mode]=dict(expected_games=len(expected),verified_game_boxes=len(good),
                complete=bool(expected) and len(good)==len(expected),
                pitching_appearances=sum(p['game_id'] in expected for p in appearances['pitching']),rest_status='unknown')
        result.append(dict(config=config,sources=[sm,cm],inventory=inventory,excluded_schedule_rows=excluded,records=records,
            appearances=appearances,comparisons=comparisons,forecast_modes=modes,
            count_reconciliation_complete=all(r['parsed'] for r in records) and all(v['totals_match'] for v in comparisons.values()),
            actual_work_dates_qualified=False,point_in_time_certified=False,feature_qualified=False,
            baseline_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [games_path,teams_path,contract_path,REGISTRY]}))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    data=audit(a.raw_dir);a.output.write_text(json.dumps(data,indent=2)+'\n')
    for r in data:print(r['config']['key'],sum(x['parsed'] for x in r['records']),len(r['records']),{k:len(v['differences']) for k,v in r['comparisons'].items()})
