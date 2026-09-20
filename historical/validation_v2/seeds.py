"""Pregame selection seeds only; fixed ordinal comparator, no outcome fitting."""
import datetime as dt
import json
import re
from evidence import ROOT, article_text, read_source
from reconcile import internal

SEASONS = (2022, 2023, 2024, 2025)
ALIASES = {'Alabama St': 'Alabama-State', 'Central Mich.': 'Central-Michigan', 'Coppin St.': 'Coppin-State', 'Ga. Southern': 'Georgia-Southern', 'Kennesaw St.': 'Kennesaw-State', 'Missouri St.': 'Missouri-State', 'New Mexico St.': 'New-Mexico-State', 'Southeastern La.': 'Southeastern-Louisiana', 'Texas St.': 'Texas-State', 'UNC Greensboro': 'UNCG', 'Wright St.': 'Wright-State', 'Grambling': 'Grambling-State', 'Arizona St.': 'Arizona-State', 'ETSU': 'East-Tennessee-State', 'Murray St.': 'Murray-State', 'North Dakota St.': 'North-Dakota-State', 'Saint Mary’s (CA)': 'Saint-Marys-College', 'Southern California': 'USC', 'USC Upstate': 'South-Carolina-Upstate', 'Western Ky.': 'Western-Kentucky', 'Sam Houston': 'Sam-Houston-State', 'NC State': 'North-Carolina-State', 'UConn': 'Connecticut', 'UNCW': 'UNCW',
    'DBU': 'Dallas-Baptist', 'Miami (FL)': 'Miami-FL', 'Oregon St.': 'Oregon-State',
    'Southern Miss.': 'Southern-Miss', 'Central Conn. St.': 'Central-Connecticut',
    'Ball St.': 'Ball-State', 'Eastern Ill.': 'Eastern-Illinois', 'San Jose St.': 'San-Jose-State',
    'Cal St. Fullerton': 'Cal-State-Fullerton', 'Oklahoma St.': 'Oklahoma-State',
    'Indiana St.': 'Indiana-State', 'Army West Point': 'Army', 'St. John’s (NY)': 'Saint-Johns',
    'Mississippi St.': 'Mississippi-State', 'Southeast Mo. St.': 'Southeast-Missouri',
    'Kansas St.': 'Kansas-State', 'Northern Ky.': 'Northern-Kentucky',
    'Western Mich.': 'Western-Michigan', 'Florida St.': 'Florida-State',
    'Fresno St.': 'Fresno-State', 'LIU': 'Long-Island'}

def parse(html, year, teams):
    text = article_text(html)
    # Never parse related links, current navigation, later results or final rankings.
    marker = f'{year} NCAA Division I Baseball Championship Games'
    if marker not in text:
        raise ValueError('Missing dated selection schedule')
    section = text.split(marker, 1)[1].split('LATEST COLLEGE BASEBALL NEWS', 1)[0]
    by_name = {t['name']: t['slug'] for t in teams}
    slugs = {t['slug'] for t in teams}
    rows = []
    groups = re.split(r'([A-Za-z -]+ Regional hosted by [^#]+)(?=#)', section)[1:]
    if len(groups) != 32:
        raise ValueError(f'Expected 16 regional groups; got {len(groups) // 2}')
    for label, group in zip(groups[::2], groups[1::2]):
        entries = re.findall(r'#([1-4])\s+(.+?)\s+\(\d+-\d+(?:-\d+)?\)', group)
        if sorted(int(s) for s, _ in entries) != [1, 2, 3, 4]:
            raise ValueError('Invalid regional seed set: ' + label)
        for seed, name in entries:
            slug = ALIASES.get(name, by_name.get(name))
            if slug not in slugs:
                raise ValueError('Unmapped NCAA team: ' + name + ' -> ' + str(slug))
            rows.append(dict(season=year, team_id=internal(slug), source_name=name,
                regional_seed=int(seed), regional=re.sub(r'^(?:(?:ESPN[U2+]*|ACCN|SECN|LHN)\s+)+', '', label.strip())))
    if len(rows) != 64 or len({r['team_id'] for r in rows}) != 64 or len({r['regional'] for r in rows}) != 16:
        raise ValueError('Duplicate/missing NCAA team identity')
    return rows

def probability(a, b):
    # Each better regional seed doubles odds; equal seeds are 50/50.
    # Fixed heuristic, deliberately not a claim of calibrated seed probabilities.
    return 1 / (1 + 2 ** (a - b))

def eligible(record, cutoff):
    return (dt.datetime.fromisoformat(record['published_at']) <= cutoff and
            dt.datetime.fromisoformat(record['modified_at']) <= cutoff)

def load(contract):
    output = []
    for year in SEASONS:
        html, ref = read_source(f'ncaa_{"di_" if year in (2022, 2025) else ""}selections_{year}.html')
        metadata = [json.loads(block) for block in re.findall(
            r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)]
        articles = [obj for obj in metadata if isinstance(obj, dict) and
                    obj.get('@type') == 'NewsArticle' and obj.get('url') == ref['source_url']]
        if len(articles) != 1:
            raise ValueError('Missing unique selection article metadata')
        article = articles[0]
        info = dict(published_at=article['datePublished'], modified_at=article['dateModified'], provenance=ref,
            availability_basis='publisher_dated_selection_article_retrieved_retrospectively',
            point_in_time_certified=False)
        cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        if not info['published_at'].startswith(str(year)) or not eligible(info, cutoff):
            raise ValueError('Selection article is not cutoff eligible')
        teams = json.loads((ROOT / str(year) / 'teams.json').read_text())
        output.extend(dict(row, **info) for row in parse(html, year, teams))
    return output
