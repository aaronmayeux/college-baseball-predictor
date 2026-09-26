"""Offline schema/count preflight for the retained NCAA 2024 CSV sample.

Reads only a supplied evidence directory; never collects or publishes features.
"""
import argparse
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re

SPECS = {
    'obp': ('On Base Percentage', ['Rank', 'Name', 'G', 'W-L', 'AB', 'H', 'BB', 'HBP', 'SF', 'SH', 'PCT']),
    'era': ('Earned Run Average', ['Rank', 'Name', 'G', 'W-L', 'IP', 'R', 'ER', 'ERA']),
}


def parse_report(text, kind, season, through):
    title, fields = SPECS[kind]
    if 'NCAA Baseball' not in text or f'Division I{title}' not in text:
        raise ValueError('Wrong sport/division/statistic')
    dates = re.findall(r'Through Games (\d{2}/\d{2}/\d{4})', text)
    if len(dates) != 1 or datetime.strptime(dates[0], '%m/%d/%Y').date() != through or through.year != season:
        raise ValueError('Wrong or ambiguous season/through date')
    lines = text.splitlines()
    header = next((i for i, line in enumerate(lines) if line.startswith('"Rank","Name"')), None)
    if header is None or next(csv.reader([lines[header]])) != fields:
        raise ValueError('Unexpected CSV fields')
    rows, names, issues = [], set(), []
    reclassifying = False
    for line in lines[header + 1:]:
        line = line.strip()
        if not line:
            continue
        if line.startswith('<script'):
            break  # NCAA appends analytics HTML to its CSV response.
        if line == 'Reclassifying':
            reclassifying = True
            continue
        cells = next(csv.reader([line]))
        if len(cells) != len(fields):
            raise ValueError('Malformed CSV row')
        row = dict(zip(fields, cells))
        if not row['Name'] or row['Name'] in names:
            raise ValueError('Missing or duplicate team')
        names.add(row['Name'])
        row['reclassifying'] = reclassifying
        count_fields = ['G', 'AB', 'H', 'BB', 'HBP', 'SF', 'SH'] if kind == 'obp' else ['G', 'R', 'ER']
        for key in count_fields:
            if not row[key].isdigit():
                raise ValueError('Missing or invalid count')
            row[key] = int(row[key])
        record = row['W-L'].split('-')
        if len(record) not in (2, 3) or any(not v.isdigit() for v in record) or sum(map(int, record)) != row['G']:
            issues.append([row['Name'], 'record_game_count'])
        if kind == 'obp':
            if row['H'] > row['AB']:
                issues.append([row['Name'], 'hits_exceed_at_bats'])
            denominator = row['AB'] + row['BB'] + row['HBP'] + row['SF']
            numerator, metric, quantum = row['H'] + row['BB'] + row['HBP'], 'PCT', Decimal('.001')
        else:
            ip = re.fullmatch(r'(\d+)\.([012])', row['IP'])
            if not ip:
                raise ValueError('Invalid baseball innings')
            row['outs'] = int(ip[1]) * 3 + int(ip[2])
            denominator, numerator, metric, quantum = row['outs'], 27 * row['ER'], 'ERA', Decimal('.01')
            if row['ER'] > row['R']:
                issues.append([row['Name'], 'earned_runs_exceed_runs'])
        if denominator <= 0:
            issues.append([row['Name'], 'zero_denominator'])
        elif (Decimal(numerator) / Decimal(denominator)).quantize(quantum, rounding=ROUND_HALF_UP) != Decimal(row[metric]):
            issues.append([row['Name'], 'display_rate_mismatch'])
        rows.append(row)
    if not rows:
        raise ValueError('Empty report')
    return rows, issues


def audit(raw_dir):
    through = date(2024, 5, 26)
    cutoff_file = Path(__file__).resolve().parents[1] / 'historical/cutoffs.json'
    cutoff = datetime.fromisoformat(json.loads(cutoff_file.read_text())['seasons']['2024']['forecast_cutoff'])
    tables, checks = {}, {}
    for kind in SPECS:
        metadata = json.loads((raw_dir / f'2024_{kind}.json').read_text())
        payload = (raw_dir / f'2024_{kind}.response').read_bytes()
        if hashlib.sha256(payload).hexdigest() != metadata['sha256']:
            raise ValueError('Source hash mismatch')
        if metadata['status'] != 200 or metadata['requested_season'] != 2024 or metadata['requested_through_date'] != through.isoformat():
            raise ValueError('Unexpected request metadata')
        form = dict(metadata['form'])
        expected_stat = '589' if kind == 'obp' else '211'
        stats = [v for k, v in metadata['form'] if k == 'statSeq']
        if (metadata['url'] != 'https://web1.ncaa.org/stats/StatsSrv/rankings'
                or metadata['method'] != 'POST'
                or any(form.get(k) != v for k, v in {'sportCode': 'MBA', 'academicYear': '2024',
                       'div': '1', 'rptWeeks': '90', 'rptType': 'CSV', 'doWhat': 'showrankings'}.items())
                or stats != ['-1', '-1', expected_stat, '-1']):
            raise ValueError('Unexpected source/form provenance')
        rows, issues = parse_report(payload.decode(), kind, 2024, through)
        tables[kind] = {row['Name']: row for row in rows}
        checks[kind] = {'rows': len(rows), 'reclassifying_rows': sum(r['reclassifying'] for r in rows), 'issues': issues, 'source_sha256': metadata['sha256']}
    common = set(tables['obp']) & set(tables['era'])
    mismatches = sorted(n for n in common if any(tables['obp'][n][k] != tables['era'][n][k] for k in ('G', 'W-L')))
    return {'season': 2024, 'through': through.isoformat(), 'tables': checks,
            'common_source_team_names': len(common), 'batting_only': sorted(set(tables['obp']) - common),
            'pitching_only': sorted(set(tables['era']) - common), 'cross_table_record_mismatches': mismatches,
            'through_date_passes_assumed_lag': through + timedelta(days=2) <= cutoff.date(),
            'publication_time_certified': False, 'field_identity_and_game_coverage_qualified': False,
            'regular_only_qualified': False, 'conference_inclusive_qualified': False,
            'model_feature_output': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.raw_dir), indent=2, sort_keys=True))
