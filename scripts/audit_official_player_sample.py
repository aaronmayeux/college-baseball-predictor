"""Offline LSU archive inventory and earliest-game schema pilot; not national coverage."""
import argparse
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urljoin
from audit_player_coverage import REPO


def read(root, key):
    raw = (root/key).read_bytes()
    meta = json.loads((root/(key+'.meta.json')).read_text())
    if meta.get('http_status') != 200 or hashlib.sha256(raw).hexdigest() != meta['sha256']:
        raise ValueError('Invalid evidence: '+key)
    return (gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw).decode('utf-8'), meta


def audit(root):
    result = []
    for year in range(2021,2026):
        text, meta = read(root, f'lsu_{year}_index.html')
        if f'{year} LSU' not in text:
            raise ValueError('Wrong archive season')
        links = re.findall(r'href="([^"]+)"[^>]*>Box score',text,re.I)
        games = json.loads((REPO/f'historical/{year}/games.json').read_text())
        baseline_count = sum('wn:LSU' in (g['team_a_id'],g['team_b_id']) for g in games)
        box, bm = read(root, f'lsu_{year}_first_box.html')
        if bm['url'] != urljoin(meta['url'],links[-1]):
            raise ValueError('Wrong selected box URL')
        plain = re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]*>', ' ', box)))
        result.append(dict(season=year,index_url=meta['url'],box_links=len(links),
                           unique_links=len(set(links)), baseline_games=baseline_count,
                           sample_url=bm['url'], sample_rule='last box link in reverse-chronological index',
                           box_has_year=str(year) in plain,
                           pitching_header_has_bf=bool(re.search(r'\bip\s+h\s+r\s+er\b.{0,150}\bbf\b',plain,re.I)),
                           has_pitch_strike_notation='Pitches/strikes' in plain,
                           has_hbp_notation='HBP' in plain,
                           has_play_by_play='Play-by-Play' in plain))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir',type=Path,default=REPO/'historical/player_coverage/raw')
    a=p.parse_args()
    print(json.dumps(audit(a.raw_dir),indent=2))
