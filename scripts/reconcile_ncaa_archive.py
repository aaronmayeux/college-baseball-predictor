"""Offline 2024 NCAA field/record/phase reconciliation; no features or fitting."""
import argparse
from collections import Counter
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'historical'), str(ROOT / 'historical/validation_v2')]
from audit_ncaa_archive import audit, parse_report
from baseline import load_games
from eligibility import reject
from team_runs import gates
from validation_v2.evidence import overlay
from validation_v2.seeds import load as load_seeds


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def totals(results):
    return dict(G=len(results), W=sum(a > b for a, b in results),
                L=sum(a < b for a, b in results), T=sum(a == b for a, b in results),
                R=sum(b for a, b in results))


def ncaa_totals(row):
    record = list(map(int, row['W-L'].split('-')))
    return dict(G=row['G'], W=record[0], L=record[1],
                T=record[2] if len(record) == 3 else 0, R=row['R'])


def differences(observed, expected):
    return {key: observed[key] - expected[key] for key in expected}


def field_mapping(field, names):
    """Reuse verified selection identity aliases; only typography differs here."""
    if len(field) != 64 or len({r['team_id'] for r in field}) != 64:
        raise ValueError('Incomplete/duplicate tournament field')
    mapped = []
    for row in field:
        name = row['source_name'].replace('’', "'")
        if name not in names:
            raise ValueError('Unmapped NCAA report team: ' + name)
        mapped.append(dict(row, report_name=name))
    if len({r['report_name'] for r in mapped}) != 64:
        raise ValueError('NCAA report identity collision')
    return mapped


def reconcile(raw):
    schema = audit(raw)
    if (any(v['issues'] for v in schema['tables'].values()) or schema['batting_only']
            or schema['pitching_only'] or schema['cross_table_record_mismatches']):
        raise ValueError('NCAA schema/count gate failed')
    refs = gates()
    contract = json.loads((ROOT / 'historical/cutoffs.json').read_text())
    field = [r for r in load_seeds(contract) if r['season'] == 2024]
    through = date.fromisoformat(schema['through'])
    rows, _ = parse_report((raw / '2024_era.response').read_text(), 'era', 2024, through)
    table = {r['Name']: r for r in rows}
    field = field_mapping(field, table)
    games = overlay(load_games(2024), refs)
    crosswalk = {r['internal_team_id']: r for r in json.loads(
        (ROOT / 'historical/team_crosswalk.json').read_text()) if r['season'] == 2024}
    excluded_path = ROOT / 'historical/2024/excluded_observations.json'
    excluded = json.loads(excluded_path.read_text())
    cutoff = datetime.fromisoformat(contract['seasons']['2024']['forecast_cutoff'])
    output = []
    source_paths = set()
    for entry in field:
        team = entry['team_id']
        identity = crosswalk[team]
        source = table[entry['report_name']]
        if source['reclassifying']:
            raise ValueError('Tournament identity mapped to reclassifying row')
        modes = {}
        team_games = [g for g in games if team in (g['a'], g['b'])]
        for mode, stages in contract['modes'].items():
            eligible = [g for g in team_games if reject(g, cutoff, stages) is None]
            in_snapshot = [g for g in eligible if g['game_date'] <= through.isoformat()]
            values = [(g['runs_a'], g['runs_b']) if g['a'] == team
                      else (g['runs_b'], g['runs_a']) for g in in_snapshot]
            modes[mode] = dict(totals=totals(values), game_ids=[g['game_id'] for g in in_snapshot],
                               eligible_after_snapshot=[g['game_id'] for g in eligible if g not in in_snapshot],
                               phases=dict(Counter(g['stage'] for g in in_snapshot)))
        non_d1 = [r for r in excluded if r['team_id'] == identity['provider_id']
                  and r['non_d1_explicit'] and r['status'] == 'completed'
                  and r['game_date'] <= through.isoformat()]
        keys = [(r['source_url'], r['source_game_id'], r['game_date']) for r in non_d1]
        if len(set(keys)) != len(keys) or any(r['timing_review'] for r in non_d1):
            raise ValueError('Ambiguous non-D1 evidence')
        for r in non_d1:
            path = ROOT / 'historical/2024' / r['raw_path']
            if digest(path) != r['raw_sha256']:
                raise ValueError('Non-D1 source hash mismatch')
            source_paths.add(path)
        extra = totals([(r['runs_for'], r['runs_against']) for r in non_d1])
        d1 = modes['conference_inclusive']['totals']
        all_opponents = {k: d1[k] + extra[k] for k in d1}
        delta = differences(ncaa_totals(source), all_opponents)
        output.append(dict(team_id=team, provider_name=identity['provider_name'],
            ncaa_name=entry['report_name'], selection_source_name=entry['source_name'],
            identity_basis='verified_selection_mapping_with_apostrophe_normalization',
            ncaa=ncaa_totals(source), modes=modes, non_d1=non_d1,
            d1_plus_retained_non_d1=all_opponents, delta=delta,
            record_match=all(delta[k] == 0 for k in ('G', 'W', 'L', 'T')),
            runs_allowed_match=delta['R'] == 0))
    inputs = [ROOT / 'historical' / p for p in ('2024/games.json',
        '2024/excluded_observations.json', 'team_crosswalk.json', 'cutoffs.json',
        'validation_v2/output/seeds.json', 'validation_v2/seeds.py', 'validation_v2/evidence.py')]
    inputs += [Path(__file__), ROOT / 'scripts/audit_ncaa_archive.py']
    inputs += sorted(source_paths)
    summary = dict(field_teams=len(output), mapped_teams=len(output),
        record_matches=sum(r['record_match'] for r in output),
        runs_allowed_matches=sum(r['runs_allowed_match'] for r in output),
        full_matches=sum(r['record_match'] and r['runs_allowed_match'] for r in output),
        teams_with_non_d1=sum(bool(r['non_d1']) for r in output),
        retained_non_d1_games=sum(len(r['non_d1']) for r in output),
        teams_with_conference_tournament=sum(r['modes']['conference_inclusive']['phases'].get('conference_tournament', 0)>0 for r in output),
        teams_with_eligible_games_after_snapshot=sum(bool(r['modes']['conference_inclusive']['eligible_after_snapshot']) for r in output),
        unresolved=[dict(team=r['ncaa_name'], delta=r['delta']) for r in output
                    if not r['record_match'] or not r['runs_allowed_match']])
    return dict(schema=schema, summary=summary, teams=sorted(output, key=lambda r:r['ncaa_name']),
        inputs={str(p.relative_to(ROOT)):digest(p) for p in inputs},
        sample_source_hashes={p.name:digest(p) for p in sorted(raw.glob('2024_*'))},
        regular_only_qualified=False, conference_inclusive_qualified=False,
        feature_output=False, publication_time_certified=False,
        limits=['Record agreement does not prove individual component-game inclusion.',
                'NCAA all-opponent statistics and D1-only model scope differ.',
                'Conference tournaments cannot be removed from cumulative counts without additional evidence.',
                'No AB/H/BB/ER/outs game-level reconciliation or publication-time certification.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', required=True, type=Path)
    print(json.dumps(reconcile(parser.parse_args().raw_dir), indent=2, sort_keys=True))
