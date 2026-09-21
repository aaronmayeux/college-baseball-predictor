"""Offline availability map for the complete 2025 development field.

Index/schema presence is not game/player reconciliation or bulk permission.
Consumes bounded discovery responses; does not download any sources.
"""
import argparse
from collections import Counter
import datetime as dt
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin
from audit_official_player_sample import read
from audit_official_season_inventory import REPO
from sidearm_structured import payload, only


def historical_year(value):
    # Accept explicit two/four-digit years, never an omitted or inferred year.
    if not re.fullmatch(r'\d{1,2}/\d{1,2}/(?:\d{2}|\d{4})', value):
        raise ValueError('Unrecognized historical date')
    return dt.datetime.strptime(value, '%m/%d/%Y' if len(value.rsplit('/', 1)[1]) == 4 else '%m/%d/%y').year


def inspect_page(text, url, kind):
    title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
    title = re.sub(r'\s+', ' ', unescape(title_match[1])).strip() if title_match else ''
    links = sorted(set(urljoin(url, unescape(u)) for u in re.findall(r'href=["\']([^"\']+)', text)))
    result = dict(title=title, status='unverified_payload', parser_family='unclassified',
        advertised_box_links=0, historical_stats_links=[], terms_links=[u for u in links if 'terms-of-service' in u or 'iubenda.com/terms' in u])
    if re.search(r'2025\s*[-–/]\s*(?:26|2026)', title) or ('2026' in title and '2025' not in title):
        result['status'] = 'wrong_season_rejected'
        return result
    title_ok = bool(re.search(r'2025|2024[-–/]25', title)) and 'baseball' in title.lower()
    result['parser_family'] = 'sidearm_embedded' if '__NUXT_DATA__' in text else ('sidearm_html' if 'sidearm' in text.lower() else 'other_html')
    if kind == 'cumulative' and '__NUXT_DATA__' in text:
        try:
            data = only(payload(text, url)['statsSeason']['cumulativeStats'].values())
            games = [g for g in data['gameByGameStats']['ourGameByGameStats'] if not g['isAFooterStat']]
            individual = data['overallIndividualStats']['individualStats']
            if not games or any(historical_year(g['date']) != 2025 for g in games):
                raise ValueError('Wrong/empty game season')
            if not individual['individualPitchingStats'] or not individual['individualHittingStats']:
                raise ValueError('Missing player groups')
            result.update(status='historical_player_groups_present', source_team_name=data['ourTeamName'])
        except (ValueError, KeyError, TypeError) as error:
            result['schema_issue'] = str(error)
    elif title_ok:
        if kind == 'schedule':
            result['status'] = 'historical_index_present'
        elif 'Cumulative Statistics' in title and re.search('Pitching', text, re.I) and re.search('Batting|Hitting', text, re.I):
            result['status'] = 'historical_player_groups_present'
    if result['status'] != 'unverified_payload':
        result['advertised_box_links'] = len([u for u in links if '/baseball/stats/2025/' in u and '/boxscore/' in u])
        result['historical_stats_links'] = [u for u in links if ('/stats/2025' in u or '/stats/season/2024-25' in u or '/25stats/' in u) and '/boxscore/' not in u and '/news/' not in u]
    return result


def validate_field(entries, expected):
    ids = [r['team_id'] for r in entries]
    if len(ids) != 64 or len(set(ids)) != 64 or set(ids) != set(expected):
        raise ValueError('Field must contain exactly the independently selected 64 teams')
    if any(r['season'] != 2025 for r in entries):
        raise ValueError('Mixed seasons')


def audit(raw, registry, lsu_audit):
    sys.path[:0] = [str(REPO/'historical/validation_v2'), str(REPO/'historical')]
    import seeds
    contract = json.loads((REPO/'historical/cutoffs.json').read_text())
    selected = [s for s in seeds.load(contract) if s['season'] == 2025]
    teams = json.loads((REPO/'historical/2025/teams.json').read_text())
    by_stable = {seeds.internal(t['slug']): t for t in teams}
    expected = {by_stable[s['team_id']]['team_id'] for s in selected}
    entries = json.loads(registry.read_text())['entries']
    validate_field(entries, expected)
    lsu = only(a for a in json.loads(lsu_audit.read_text()) if a['school'] == 'lsu' and a['season'] == 2025)
    output = []
    for entry in entries:
        row = dict(entry, probes=[], bulk_collection_enabled=False, recent_workload='unknown',
                   feature_qualified=False, fallback='team_level_model_requires_validation',
                   hitting_counts='unverified', pitching_counts='unverified')
        for probe in entry['probes']:
            meta = json.loads((raw/(probe['key']+'.meta.json')).read_text())
            if meta['url'] != probe['url']:
                raise ValueError('Source URL mismatch')
            item = dict(probe, evidence=meta)
            if meta.get('http_status') == 200:
                text, _ = read(raw, probe['key'])
                item.update(inspect_page(text, probe['url'], probe['kind']) if probe['kind'] != 'robots' else dict(status='robots_only_not_permission'))
            else:
                item['status'] = 'access_failed'
            row['probes'].append(item)
        row['schedule_status'] = 'historical_index_present' if any(p['kind']=='schedule' and p['status']=='historical_index_present' for p in row['probes']) else 'unverified_or_access_gap'
        row['cumulative_status'] = 'historical_player_groups_present' if any(p['kind']=='cumulative' and p['status']=='historical_player_groups_present' for p in row['probes']) else 'unverified_or_not_tested'
        row['terms_status'] = 'sidearm_personal_copying_terms_bulk_volume_unverified' if any(any('sidearmsports.com' in u for u in p.get('terms_links', [])) for p in row['probes']) else 'provider_terms_unverified'
        if entry['team_id'] == 'wn:LSU':
            for mode in ('regular_only', 'conference_inclusive'):
                if not lsu['forecast_modes'][mode]['inventory_and_boxes_complete']:
                    raise ValueError('LSU preserved coverage changed')
            if not lsu['season_counts_reconciled']:
                raise ValueError('LSU preserved count check failed')
            row.update(hitting_counts='reconciled_core_counts', pitching_counts='reconciled_core_counts',
                schedule_status='preserved_season_audit', cumulative_status='preserved_season_audit')
        output.append(row)
    return dict(schema_version=1, season=2025, development_only=True,
        input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [registry, lsu_audit, REPO/'historical/cutoffs.json']},
        selection_source=selected[0]['provenance'],
        summary={k:dict(Counter(r[k] for r in output)) for k in ['schedule_status','cumulative_status','hitting_counts','terms_status']},
        teams=output)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir', type=Path, required=True)
    p.add_argument('--registry', type=Path, default=REPO/'historical/tournament_sources_2025.json')
    p.add_argument('--lsu-audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args(); result=audit(a.raw_dir,a.registry,a.lsu_audit)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary'],indent=2))
