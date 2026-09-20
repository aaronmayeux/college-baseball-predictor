"""Bounded historical collection for reviewed embedded-SIDEARM registry entries.

One request per school host; cache successes and failures without automatic
retries. Not a national importer or a source-permission grant.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlparse
from audit_official_season_inventory import REPO
from audit_official_player_sample import read
from sidearm_structured import schedule
sys.path.insert(0,str(REPO/'historical/research'))
import fetch


def collect(root):
    root.mkdir(parents=True,exist_ok=True);raw=root/'raw';raw.mkdir(exist_ok=True);fetch.ROOT=root
    configs=[c for c in json.loads((REPO/'historical/player_sources.json').read_text())['entries'] if c['adapter']=='sidearm_embedded_v1']
    if len(configs)>2 or any(c['season'] not in (2022,2024) for c in configs):raise ValueError('Outside reviewed two-season pilot')
    if len({urlparse(c['schedule_url']).netloc for c in configs})!=len(configs):raise ValueError('Duplicate host worker')
    cache={json.loads(p.read_text())['url']:p.name.removesuffix('.meta.json') for p in raw.glob('*.meta.json')}
    def run(config):
        def get(url,key):
            existing=cache.get(url)
            if existing:return read(raw,existing)
            if (raw/(key+'.meta.json')).exists():raise ValueError('Unresolved cached source; review before retry')
            fetch.fetch(key,url);time.sleep(1);return read(raw,key)
        text,_=get(config['schedule_url'],config['key']+'_schedule.html');inventory,_=schedule(text,config)
        get(config['cumulative_url'],config['key']+'_cumulative.html')
        for row in inventory:
            if row['box_url'] is None:continue
            get(row['box_url'],config['key']+'_box_'+row['source_game_id']+'.html')
        print(config['key'],'collection complete',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,configs))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence-dir',type=Path,required=True);a=p.parse_args();collect(a.evidence_dir)
