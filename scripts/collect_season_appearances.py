"""Bounded two-season pilot, not a national importer or bulk-access permission.

First extract the supplied discovery, player and official-pitching evidence ZIPs
into separate directories. Pass their raw directories in that order. Existing
successes/failures are cached; no automatic retries. Never requests 2026.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import sys
import time
from urllib.parse import urlparse
from audit_season_appearances import parse_index, towson_index, read, REPO
sys.path.insert(0,str(REPO/'historical/research'))
import fetch


def collect(root, sources):
    raw=root/'raw';raw.mkdir(parents=True,exist_ok=True)
    for source in sources:
        for mp in sorted(source.glob('*.meta.json')):
            key=mp.name.removesuffix('.meta.json')
            if not (key.startswith('lsu') or key=='towson_2024_schedule.html' or key=='towson_ncstate_20240301.html'):continue
            read(source,key)  # verify original bytes before reusing
            for path in [mp,mp.with_name(key)]:
                dest=raw/path.name
                if dest.exists() and dest.read_bytes()!=path.read_bytes():raise ValueError('Conflicting cache '+str(dest))
                if not dest.exists():shutil.copyfile(path,dest)
    fetch.ROOT=root
    for key,url in [('lsu_cume.html','https://static.lsusports.net/assets/docs/bb/25stats/teamcume.htm'),
                    ('towson_cume.html','https://towsontigers.com/sports/baseball/stats/2024')]:
        fetch.fetch(key,url)
    known={json.loads(p.read_text()).get('url') for p in raw.glob('*.meta.json')}
    def school_jobs(school):
        index,meta=read(raw,'lsu_index_2025.html' if school=='lsu' else 'towson_2024_schedule.html')
        inventory=parse_index(index,meta['url'],2025) if school=='lsu' else towson_index(index,meta['url'])
        if len(inventory)!=(68 if school=='lsu' else 54):raise ValueError('Pilot inventory changed; review before collection')
        for row in inventory:
            url=row['box_url'];parsed=urlparse(url)
            prefix='https://static.lsusports.net/assets/docs/bb/25stats/' if school=='lsu' else 'https://towsontigers.com/sports/baseball/stats/2024/'
            if not url.startswith(prefix):raise ValueError('Outside fixed pilot source')
            if url in known:continue
            key=school+'_'+parsed.path.rsplit('/',1)[-1]+'.html'
            _,meta=fetch.fetch(key,url)
            print(school,key,meta.get('http_status'),meta.get('error',''),flush=True)
            time.sleep(1)
    # At most one outstanding request per school host.
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(school_jobs,['lsu','towson']))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence-dir',type=Path,required=True)
    p.add_argument('--source-raw-dirs',type=Path,nargs='+',required=True);a=p.parse_args()
    collect(a.evidence_dir,a.source_raw_dirs)
