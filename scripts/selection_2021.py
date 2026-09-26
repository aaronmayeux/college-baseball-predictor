"""Offline 2021 selection-bracket qualification, separate from frozen v2 metrics."""
import datetime as dt
import html
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from audit_official_player_sample import read
from reconcile import internal
from seeds import ALIASES

PDF = 'selection_2021_school_copy.pdf'
ARTICLE = 'usa_2021_selection_article.html'
ALIASES_2021 = dict(ALIASES, **{'Southern U.': 'Southern', 'South Fla.': 'South-Florida',
    'Presbyterian': 'Presbyterian-College', 'McNeese': 'McNeese', 'Norfolk St.': 'Norfolk-State'})


def latest_utc(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    # Unknown publisher timezone: conservative latest instant in UTC-12..UTC+14.
    return (parsed.replace(tzinfo=dt.timezone.utc) + dt.timedelta(hours=12)
            if parsed.tzinfo is None else parsed.astimezone(dt.timezone.utc))


def article_dates(text, cutoff):
    records = [json.loads(b) for b in re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.S)]
    records = [r for r in records if isinstance(r, dict) and r.get('@type') == 'NewsArticle'
               and r.get('headline') == 'JAGS TO COMPETE AT NCAA GAINESVILLE REGIONAL AS NO. 3 SEED']
    if len(records) != 1:
        raise ValueError('Missing unique dated selection article')
    r = records[0]
    for key in ('datePublished', 'dateModified'):
        if not r[key].startswith('2021-05-31T') or latest_utc(r[key]) > cutoff:
            raise ValueError('Selection article timing is not cutoff eligible')
    return dict(published_at_source=r['datePublished'], modified_at_source=r['dateModified'],
        publication_latest_utc=latest_utc(r['datePublished']).isoformat(),
        modification_latest_utc=latest_utc(r['dateModified']).isoformat(),
        timezone_basis='source_offset_missing_use_latest_UTC_minus_12_bound')


def parse_bracket(xml, teams):
    ns = {'h': 'http://www.w3.org/1999/xhtml'}
    root = ET.fromstring(xml)
    pages = root.findall('.//h:page', ns)
    if len(pages) != 1:
        raise ValueError('Expected one selection bracket page')
    columns = {'left': [], 'right': []}
    by_name = {t['name']: t['slug'] for t in teams}
    slugs = {t['slug'] for t in teams}
    for line in root.findall('.//h:line', ns):
        text = ' '.join(w.text or '' for w in line.findall('h:word', ns))
        if not text.startswith('#'):
            continue
        m = re.fullmatch(r'#([1-4]) (\*?)(.+?) \(\d+ - \d+(?: - \d+)?\)', text)
        if not m:
            raise ValueError('Unrecognized seeded team line')
        x = float(line.attrib['xMin']); width = float(pages[0].attrib['width'])
        side = 'left' if x < width*.3 else 'right' if x > width*.7 else None
        if side is None:
            raise ValueError('Seeded team outside bracket columns')
        slug = ALIASES_2021.get(m[3], by_name.get(m[3]))
        if slug not in slugs:
            raise ValueError('Unmapped 2021 selection name: ' + m[3])
        columns[side].append(dict(team_id=internal(slug), source_name=m[3],
            regional_seed=int(m[1]), host_marker=bool(m[2]), source_line=text,
            source_y=float(line.attrib['yMin'])))
    result = []
    for side, rows in columns.items():
        rows.sort(key=lambda r: r['source_y'])
        if len(rows) != 32:
            raise ValueError('Expected 32 teams per bracket half')
        for offset in range(0, 32, 4):
            group = rows[offset:offset+4]
            if [r['regional_seed'] for r in group] != [1, 4, 3, 2] or sum(r['host_marker'] for r in group) != 1:
                raise ValueError('Invalid regional seeds or host markers')
            result.extend(dict(r, season=2021, regional=f'2021-{side}-{offset//4+1}') for r in group)
    if len({r['team_id'] for r in result}) != 64:
        raise ValueError('Duplicate field team')
    return result


def audit(raw, root):
    pdf_meta = json.loads((raw/(PDF+".meta.json")).read_text())
    if pdf_meta.get("http_status") != 200 or hashlib.sha256((raw/PDF).read_bytes()).hexdigest() != pdf_meta["sha256"]:
        raise ValueError("Selection PDF source hash/status mismatch")
    text, article_meta = read(raw, ARTICLE)
    if article_meta['url'] != 'https://usajaguars.com/news/2021/5/31/baseball-jags-to-compete-at-ncaa-gainesville-regional-as-no-3-seed.aspx':
        raise ValueError('Unexpected selection article URL')
    contract = json.loads((root/'historical/cutoffs.json').read_text())
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2021']['forecast_cutoff'])
    dates = article_dates(text, cutoff)
    filename = '2021_NCAA_Division_I_Baseball_Championship_Bracket_64_team.pdf'
    links = [html.unescape(u) for u in re.findall(r'href=["\']([^"\']+)', text)]
    links = [u for u in links if urlparse(u).path.endswith('/'+filename)
             and '/documents/2021/5/31/' in urlparse(u).path]
    if len(links) != 1 or not pdf_meta['url'].endswith('/'+filename) or '/usajaguars.com/documents/2021/5/31/' not in pdf_meta['url']:
        raise ValueError('Missing school article-to-document identity')
    info = subprocess.check_output(['pdfinfo', str(raw/PDF)], text=True)
    # These are document-edit timestamps, not an observed historical publication.
    if not all(re.search(k+r':\s+Mon May 31 08:48:20 2021 -04', info) for k in ('CreationDate', 'ModDate')):
        raise ValueError('Unexpected selection PDF edit metadata')
    xml = subprocess.check_output(['pdftotext', '-bbox-layout', str(raw/PDF), '-'])
    if b'2021' not in xml or b'Championship' not in xml:
        raise ValueError('Missing bracket title')
    teams = json.loads((root/'historical/2021/teams.json').read_text())
    rows = parse_bracket(xml, teams)
    games = json.loads((root/'historical/2021/games.json').read_text())
    opening = []
    for region in sorted({r['regional'] for r in rows}):
        by_seed = {r['regional_seed']: r['team_id'] for r in rows if r['regional'] == region}
        for a,b in ((1,4),(2,3)):
            matches = [g for g in games if g['stage']=='regional' and g['game_date']=='2021-06-04'
                and {internal(g['team_a_id'].removeprefix('wn:')),internal(g['team_b_id'].removeprefix('wn:'))}=={by_seed[a],by_seed[b]}
                and g['reciprocal_check']=='pass' and not g.get('timing_review')]
            if len(matches)!=1:
                raise ValueError('Unresolved 2021 opening matchup')
            opening.append(matches[0]['game_id'])
    return dict(status='retrospective_selection_qualified', point_in_time_certified=False,
        forecast_cutoff=cutoff.isoformat(), **dates, article=article_meta, document=pdf_meta,
        article_document_link=links[0], document_identity_basis='dated_school_link_and_matching_school_hosted_filename_not_observed_redirect_chain',
        pdf_creation_and_modification='2021-05-31T08:48:20-04:00',
        seeds=rows, opening_game_ids=opening, metrics_computed=False,
        routing_qualified=False, national_seed_inputs_used=False)
