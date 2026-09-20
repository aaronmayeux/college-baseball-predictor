"""Broader school schedule checks, with explicit unknown phase and exclusions."""
import json
import re
from evidence import ROOT, TIMING, read_source
from official_checks import extract, opponent_key
from research.parse_sidearm import extract as legacy

SCHOOLS = {'oregon': 'Oregon-State', 'columbia': 'Columbia', 'ncstate': 'North-Carolina-State',
    'missouri': 'Missouri-State', 'ecu': 'East-Carolina', 'stjoseph': 'Saint-Josephs',
    'kent': 'Kent-State', 'evansville': 'Evansville', 'charlotte': 'Charlotte',
    'fordham': 'Fordham', 'ohio': 'Ohio-State', 'bgsu': 'Bowling-Green',
    'southernindiana': 'Southern-Indiana'}
# Only named postseason events certify phase. Absence of a label is not evidence.
PHASES = {'MAC Tournament': 'conference_tournament', 'Ivy League Tournament': 'conference_tournament',
    'Pac-12 Tournament': 'conference_tournament', 'ACC Championship': 'conference_tournament',
    'Conference USA Championship': 'conference_tournament', 'MVC Baseball Championship': 'conference_tournament',
    'American Conference Tournament': 'conference_tournament', 'NCAA Regionals': 'regional'}

# Explicit aliases reviewed against each source schedule and dated opponent records.
EXTRA_ALIASES = {'Southeast Missouri State': 'Southeast Missouri', 'Queens University': 'Queens', 'NC State': 'North Carolina State',
    'UMass Lowell': 'UMass-Lowell', 'UT Martin': 'Tennessee-Martin',
    'Lake Erie College': 'Lake Erie', 'Pitt': 'Pittsburgh', 'Tiffin University': 'Tiffin',
    'Miami University (OH)': 'Miami (OH)', 'SEMO': 'Southeast Missouri',
    'WKU': 'Western Kentucky', 'Florida Atlantic': 'FAU', 'Massachusetts': 'UMass',
    'UCONN': 'Connecticut', 'Cal': 'California', 'UNC Greensboro': 'UNCG',
    'Austin Peay State University': 'Austin Peay',
    'Southeast Missouri State University': 'Southeast Missouri',
    'University of Tennessee at Martin': 'Tennessee-Martin',
    'McKendree University': 'Mckendree University',
    'Southern Illinois University Edwardsville': 'SIUE',
    'University of Arkansas at Little Rock': 'Little Rock'}
for name in ['Western Illinois', 'Lipscomb', 'Bellarmine', 'Washington State', 'Oakland',
             'Saint Louis', 'Southern Illinois', 'Murray State', 'Belmont', 'Morehead State',
             'Ball State', 'Lindenwood', 'Oakland City', 'Eastern Illinois', 'Oral Roberts', 'Tennessee Tech']:
    EXTRA_ALIASES[name + ' University'] = name

def name_key(name, team_id):
    name = re.sub(r'^(?:(?:No\.\s*|#)\d+\s*|\(\d+\)\s*)+', '', name).strip()
    name = re.sub(r'\s*\((?:DH|Snowbird Classic|Frisco Classic)\)$', '', name).strip()
    if name == 'Miami' and team_id in {'wn:Ohio-State', 'wn:Bowling-Green'}:
        return 'Miami (OH)'
    return EXTRA_ALIASES.get(name, opponent_key(name))

def phase(label):
    if label in PHASES:
        return PHASES[label]
    if label and label.startswith('NCAA ') and 'Super Regional' in label:
        return 'super_regional'
    if label and label.startswith('NCAA ') and 'Regional' in label:
        return 'regional'
    return None

def compare(rows, observations, team_id):
    provider = [r for r in observations if r['team_id'] == team_id and r['status'] == 'completed']
    checks = []
    for row in rows:
        candidates = [r for r in provider if name_key(r['opponent_name'], team_id) == name_key(row['opponent'], team_id)
            and (r['runs_for'], r['runs_against']) == (row['team_score'], row['opponent_score'])]
        matches = [r for r in candidates if r['game_date'] == row['date']]
        resolution = None
        if not matches:
            for r in candidates:
                key = 'wn:2023:' + r['source_game_id']
                c = TIMING.get(key)
                if c and row['date'] == c['official_schedule_date'] and r['game_date'] == c['completion_date']:
                    matches.append(r)
                    resolution = key
        expected = phase(row['tournament'])
        checks.append(dict(official=row, matches=[r['source_game_id'] for r in matches],
            timing_resolution=resolution,
            independent_from_result_source=(not matches[0].get('provider', '').startswith('official_')) if len(matches) == 1 else False,
            non_d1=matches[0].get('non_d1_explicit', False) if len(matches) == 1 else None,
            date_score_status='pass' if len(matches) == 1 else 'review',
            official_phase=expected, provider_phase=matches[0]['stage'] if len(matches) == 1 else None,
            phase_status=('pass' if matches[0]['stage'] == expected else 'conflict')
                if expected and len(matches) == 1 else 'not_independently_verified'))
    used = [r['matches'][0] for r in checks if len(r['matches']) == 1]
    missing = sorted(set(r['source_game_id'] for r in provider) - set(used))
    return checks, missing, len(used) == len(set(used))

def run():
    output = []
    for year in range(2021, 2025):
        observations = json.loads((ROOT / str(year) / 'observations.json').read_text())
        for name, slug in SCHOOLS.items():
            if year != 2023 and name not in {'oregon', 'columbia'}:
                continue
            source = f'{name}_{year}.html'
            html, ref = read_source(source)
            try:
                rows = extract(ROOT / 'research/raw' / source)
            except ValueError:
                rows = legacy(html)
            item = dict(season=year, team=slug, provenance=ref)
            # The 2023 Missouri page includes one explicitly identified fall exhibition.
            if name == 'missouri' and year == 2023:
                excluded = [r for r in rows if r['date'] == '2022-10-01' and r['opponent'] == 'Drury']
                item['outside_season_rows'] = excluded
                rows = [r for r in rows if r not in excluded]
            if not rows or any(not r['date'].startswith(str(year) + '-') for r in rows):
                output.append(dict(item, status='unavailable_or_wrong_season', scored_rows=len(rows)))
                continue
            checks, missing, unique = compare(rows, observations, 'wn:' + slug)
            output.append(dict(item, status='pass' if unique and not missing and all(
                r['date_score_status'] == 'pass' and r['phase_status'] != 'conflict' for r in checks) else 'review',
                scored_rows=len(rows), unmatched_provider_ids=missing, unique_matches=unique, rows=checks))
    return output
