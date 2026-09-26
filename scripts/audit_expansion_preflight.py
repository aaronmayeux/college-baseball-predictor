"""Offline three-school 2022 preflight and separate 2021 selection evidence.

No collection, feature fitting or season qualification. Restore the exact
preflight checkpoint plus baseline/timing evidence according to docs/DATA.md.
"""
import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'historical/validation_v2'), str(ROOT/'historical')]
from audit_official_player_sample import read
from audit_official_season_inventory import parse_index, reconcile
from audit_season_appearances import statcrew_box
from audit_source_access import inspect_robots
from audit_player_exceptions import checked
from evidence import overlay, verify_timing
from eligibility import reject
from hitting_inputs import statcrew_team
from lsu_pitching_inputs import game as statcrew_pitching_game
from pitching_inputs import structured_game
import selection_2021
import sidearm_structured as sidearm

SOURCES = {
    'arkansas': dict(team_name='Arkansas', team_id='wn:Arkansas', expected=67,
        url='https://arkansasrazorbacks.com/stats/baseball/2022/teamstat.htm',
        first='https://arkansasrazorbacks.com/stats/baseball/2022/ark01.htm',
        aliases={'UAPB':'wn:Arkansas-Pine-Bluff', 'Mizzou':'wn:Missouri',
                 'Grambling':'wn:Grambling-State', 'Southeastern':'wn:Southeastern-Louisiana'}),
    'okstate': dict(team_name='Oklahoma State', team_id='wn:Oklahoma-State', expected=64,
        url='https://okstate.com/sports/baseball/stats/2022/',
        first='https://okstate.com/sports/baseball/stats/2022/vanderbilt/boxscore/13622',
        aliases={'Sam Houston':'wn:Sam-Houston-State', 'SE Missouri State':'wn:Southeast-Missouri', 'DBU':'wn:Dallas-Baptist'}),
    'gcu': dict(team_name='Grand Canyon', team_id='wn:Grand-Canyon', expected=62,
        url='https://gculopes.com/sports/baseball/stats/2022',
        first='https://gculopes.com/sports/baseball/stats/2022/nevada/boxscore/18092',
        aliases={'Seattle U':'wn:Seattle-University'})}


def source(raw, key, url=None):
    text, meta = read(raw,key)
    if meta.get('http_status') != 200 or (url is not None and meta['url'] != url):
        raise ValueError('Unexpected preflight source: '+key)
    return text, meta


def annotate_arkansas(inventory, games, evidence):
    result=deepcopy(inventory)
    targets=[r for r in result['games'] if r['box_url']==SOURCES['arkansas']['url'].replace('teamstat.htm','ark50.htm')]
    matches=[g for g in games if g['game_id']=='wn:2022:36425']
    if len(targets)!=1 or len(matches)!=1:
        raise ValueError('Missing unique Arkansas timing target')
    row=targets[0];game=matches[0]
    score={game['team_a_id']:game['runs_a'],game['team_b_id']:game['runs_b']}
    if (row['date'],row['teams'],row['runs'],row['game_id'],row['issues']) != (
        '2022-05-14',['Arkansas','Vanderbilt'],[11,6],None,['ambiguous_or_missing_baseline_match']):
        raise ValueError('Original Arkansas timing exception changed')
    if game['game_date']!='2022-05-15' or score!={'wn:Arkansas':11,'wn:Vanderbilt':6}:
        raise ValueError('Arkansas completion identity changed')
    row.update(original_game_id=None,original_issues=list(row['issues']),
        game_id=game['game_id'],issues=[],result_completion_date=game['game_date'],
        actual_player_work_dates='unknown',timing_evidence=evidence)
    joined={r['game_id'] for r in result['games'] if not r['issues']}
    result['matched_games']=len(joined)
    result['missing_baseline_games']=[g for g in result['missing_baseline_games'] if g not in joined]
    result['inventory_pass']=not result['missing_baseline_games'] and not any(r['issues'] for r in result['games'])
    return result



def retained_coverage(raw, rows, config):
    """Cache inventory only. Links are leads, never proof of retained bytes."""
    successful={}
    for mp in sorted(raw.glob('*.meta.json')):
        m=json.loads(mp.read_text())
        if m.get('http_status')==200:
            path=raw/mp.name.removesuffix('.meta.json')
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=m.get('sha256'):
                raise ValueError('Retained response missing or corrupt: '+path.name)
            successful[m['url']]=m['sha256']
    boxes={r['box_url'] for r in rows}
    cached=sorted(boxes & successful.keys())
    report=dict(scope='supplied_preflight_raw_directory_only', expected_season_boxes=len(boxes),
        retained_box_urls=cached,missing_box_count=len(boxes)-len(cached),
        full_season_appearances_qualified=False)
    if config['team_name']=='Arkansas':
        text,_=source(raw,'arkansas_index.html',config['url'])
        required={label:urljoin(config['url'],filename) for label,filename in
                  [('season_counts','teamcume.htm'),('dated_team_counts','teamgbg.htm')]}
        links={urljoin(config['url'],href) for href in re.findall(r'href=["\']([^"\']+)["\']',text,re.I)}
        if not set(required.values())<=links:
            raise ValueError('Arkansas count-report links changed')
        report['linked_count_reports']={k:dict(url=u,retained=u in successful) for k,u in required.items()}
        report['season_hitting_qualified']=False
        report['block_reason']='Only sample counts checked; linked season reports and full histories require separate qualification.'
    return report


def audit(raw):
    games = overlay(json.loads((ROOT/'historical/2022/games.json').read_text()), verify_timing())
    teams = json.loads((ROOT/'historical/2022/teams.json').read_text())
    identities = {t['name']:t['team_id'] for t in teams}
    contract = json.loads((ROOT/'historical/cutoffs.json').read_text())
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2022']['forecast_cutoff'])
    output = []
    for key, config in SOURCES.items():
        raw_key = key + ('_index.html' if key=='arkansas' else '_cumulative.html')
        text, meta = source(raw,raw_key,config['url'])
        counts = None
        if key=='arkansas':
            rows = parse_index(text,config['url'],2022)
        else:
            cfg=dict(config,season=2022,cumulative_url=config['url'],expected_completed_games=config['expected'])
            cumulative, entries = sidearm.cumulative(text,cfg)
            counts = {kind:len(players) for kind,players in cumulative.items()}
            rows=[dict(date=dt.datetime.strptime(g['date'],'%m/%d/%Y').date().isoformat(),
                teams=[config['team_name'],g['opponent']],runs=[int(g['ourScore']),int(g['opponentScore'])],
                box_url=urljoin(config['url'],g['boxscoreUrl'])) for g in entries]
        if len(rows)!=config['expected']:
            raise ValueError('Unexpected season inventory')
        inv=reconcile(rows,games,dict(identities,**config['aliases']),config['team_id'])
        first=min(rows,key=lambda r:(r['date'],r['box_url']))
        if first['box_url']!=config['first']:
            raise ValueError('Sample is not the first listed game')
        box, box_meta=source(raw,key+'_first_box.html',config['first'])
        sample=[]
        for name in first['teams']:
            hitting=None
            if key=='arkansas':
                parsed=statcrew_box(box,first,name)
                hitting=statcrew_team(box,first,name)
                _,bf=statcrew_pitching_game(box,first,parsed['pitching'],name)
            else:
                cfg=dict(config,team_name=name)
                parsed,_=sidearm.box(box,config['first'],first,cfg)
                _,bf=structured_game(box,config['first'],cfg,parsed['pitching'])
            sample.append(dict(team=name, batting_rows=len(parsed['batting']),
                pitching_rows=len(parsed['pitching']),core_counts_pass=True,BF_check=bf,statcrew_hitting_check=hitting,
                BF_roles_qualified_for_sample=bf is not None))
        rb,rb_meta=source(raw,key+'_robots.txt')
        access=inspect_robots(rb,rb_meta['url'],[config['url'],config['first']],rb_meta['final_url'])
        annotated = None
        if key=='arkansas':
            evidence=[checked(raw,'arkansas_suspension.html',
                'https://arkansasrazorbacks.com/game-two-between-arkansas-vanderbilt-suspended-in-sixth-inning/',
                ['May 14, 2022','Sunday, May 15','8-6']),
                checked(raw,'vanderbilt_completion.html',
                'https://vucommodores.com/arkansas-holds-on-to-even-series/',
                ['May 15, 2022','11-6','Sunday morning','suspended on Saturday'])]
            annotated=annotate_arkansas(inv,games,evidence)
        mode_counts={}
        joined={r['game_id'] for r in (annotated or inv)['games'] if not r['issues']}
        for mode,stages in contract['modes'].items():
            ids={g['game_id'] for g in games if config['team_id'] in (g['team_a_id'],g['team_b_id']) and reject(g,cutoff,stages) is None}
            mode_counts[mode]=dict(expected=len(ids),matched=len(ids & joined),complete_inventory=bool(ids) and ids<=joined)
        retained_scope=retained_coverage(raw,rows,config)
        output.append(dict(retained_scope=retained_scope,key=key,team=config['team_name'],season=2022,source=meta,
            explicit_aliases=config['aliases'],inventory=inv,completion_annotated_inventory=annotated,modes=mode_counts,
            cumulative_player_rows=counts,first_box=box_meta,sample_sides=sample,
            robots=access,robots_evidence=rb_meta,full_season_features_qualified=False,
            full_season_collection_enabled=False,bulk_permission='unverified'))
    evidence={}
    for mp in sorted(raw.glob('*.meta.json')):
        m=json.loads(mp.read_text());p=raw/mp.name.removesuffix('.meta.json')
        if 'sha256' in m and (not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=m['sha256']):
            raise ValueError('Evidence hash mismatch: '+p.name)
        evidence[mp.name]=dict(metadata_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),source=m)
    paths=[ROOT/'historical/2022/games.json',ROOT/'historical/2022/teams.json',ROOT/'historical/cutoffs.json',
           ROOT/'historical/2021/games.json',ROOT/'historical/2021/teams.json']
    paths+=sorted((ROOT/'scripts').glob('*.py'))
    paths+=sorted((ROOT/'historical/validation_v2').glob('*.py'))
    return dict(schema_version=2,requests_performed=0,schools=output,
        selection_2021=selection_2021.audit(raw,ROOT),evidence=evidence,
        input_code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        collection_scope='retained_single_game_probes_only_no_season_sweep',
        metrics_computed=False,bulk_collection_enabled=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(audit(args.raw_dir),indent=2,sort_keys=True))
