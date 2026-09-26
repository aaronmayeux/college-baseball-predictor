"""Offline national snapshot date/phase plan, not feature qualification or fitting."""
import argparse
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'historical'), str(ROOT / 'historical/validation_v2')]
from audit_ncaa_archive import menu_dates, selected_date, audit
from baseline import load_games
from eligibility import reject, NCAA
from team_runs import gates
from validation_v2.evidence import overlay
from validation_v2.seeds import load as load_seeds


def snapshot_options(games, cutoff, stages, options):
    """A date must include every eligible target and no excluded D1 result."""
    target = [g for g in games if reject(g, cutoff, stages) is None]
    unknown_date = any(not g.get('game_date') for g in games)
    candidates = []
    for day, report_id, final in options:
        if final or day + timedelta(days=2) > cutoff.date():
            continue
        included = [g for g in games if g.get('game_date') and g['game_date'] <= day.isoformat()]
        if (target and not unknown_date
                and {g['game_id'] for g in included} == {g['game_id'] for g in target}):
            candidates.append(dict(through=day.isoformat(), report_id=report_id))
    last_target = max((g['game_date'] for g in target), default=None)
    interleaved = [g['game_id'] for g in games if last_target and g.get('game_date')
                   and g['game_date'] <= last_target and reject(g, cutoff, stages) is not None]
    return dict(target_game_ids=sorted(g['game_id'] for g in target),
                excluded_results_before_last_target=sorted(interleaved),
                last_target_date=last_target,
                unknown_date=unknown_date, candidates=sorted(candidates, key=lambda r:r['through']))


def cover(rows):
    """Minimum date cover for contiguous date intervals; reject noninterval sets."""
    dates = sorted({d['through'] for row in rows for d in row['candidates']})
    sets = [set(d['through'] for d in row['candidates']) for row in rows if row['candidates']]
    for values in sets:
        if values != {d for d in dates if min(values) <= d <= max(values)}:
            raise ValueError('Candidate sets are not date intervals')
    chosen = []
    while sets:
        day = min(max(values) for values in sets)
        chosen.append(day)
        sets = [values for values in sets if day not in values]
    return chosen


def run(evidence):
    refs = gates()
    contract = json.loads((ROOT / 'historical/cutoffs.json').read_text())
    seeds = load_seeds(contract)
    crosswalk = json.loads((ROOT / 'historical/team_crosswalk.json').read_text())
    seasons = []
    inputs = [ROOT / 'historical' / p for p in ('cutoffs.json', 'team_crosswalk.json',
              'baseline.py', 'eligibility.py', 'validation_v2/seeds.py', 'validation_v2/evidence.py')]
    inputs += [Path(__file__), ROOT / 'scripts/audit_ncaa_archive.py']
    evidence_inputs = {}
    retained = {}
    for folder in ('raw', 'previous', 'weekly'):
        raw = evidence / folder
        for meta in sorted(raw.glob('*_obp.json')):
            metadata = json.loads(meta.read_text())
            y = metadata['requested_season']
            through = date.fromisoformat(metadata['requested_through_date'])
            check = audit(raw, y, through)
            retained[y, through.isoformat()] = dict(populated=check['national_tables_populated'],
                source_rows=check['common_source_team_names'],
                arithmetic_pass=not any(t['issues'] for t in check['tables'].values()),
                records_match=not check['cross_table_record_mismatches'], folder=folder)
        for path in sorted(raw.iterdir()):
            if path.is_file():
                evidence_inputs[str(path.relative_to(evidence))] = hashlib.sha256(path.read_bytes()).hexdigest()
    for year in range(2021, 2025):
        cutoff = datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        selected_date(evidence / 'raw', year, cutoff)  # Verify menu hash/provenance.
        options = menu_dates((evidence / 'raw' / f'{year}_menu.html').read_text(), year)
        games = overlay(load_games(year), refs)
        field = ({t for g in games if g['stage'] in NCAA for t in (g['a'], g['b'])}
                 if year == 2021 else {r['team_id'] for r in seeds if r['season'] == year})
        if len(field) != 64:
            raise ValueError('Incomplete field inventory')
        identity = {r['internal_team_id']:r for r in crosswalk if r['season'] == year}
        if not field <= identity.keys():
            raise ValueError('Unmapped field identity')
        excluded_path = ROOT / f'historical/{year}/excluded_observations.json'
        excluded = json.loads(excluded_path.read_text())
        inputs += [excluded_path, ROOT / f'historical/{year}/games.json']
        modes = {}
        for mode, stages in contract['modes'].items():
            teams = []
            for team in sorted(field):
                team_games = [g for g in games if team in (g['a'], g['b'])]
                row = snapshot_options(team_games, cutoff, stages, options)
                for candidate in row['candidates']:
                    candidate['retained_report'] = retained.get((year,candidate['through']))
                non_d1 = [r for r in excluded if r['team_id'] == identity[team]['provider_id']
                          and r['non_d1_explicit'] and r['status'] == 'completed'
                          and (not r['game_date'] or (row['last_target_date'] and r['game_date'] <= row['last_target_date']))]
                for observation in non_d1:
                    source = ROOT / f'historical/{year}' / observation['raw_path']
                    if hashlib.sha256(source.read_bytes()).hexdigest() != observation['raw_sha256']:
                        raise ValueError('Non-D1 evidence hash mismatch')
                teams.append(dict(team_id=team, name=identity[team]['provider_name'],
                    conference=identity[team]['source_conference'], non_d1_before_target=non_d1,
                    **row))
            # An explicit empty pair is not a usable candidate. Untested dates stay unqualified.
            usable = [dict(r, candidates=[d for d in r['candidates']
                       if d['retained_report'] is None or d['retained_report']['populated']]) for r in teams]
            chosen = cover(usable)
            date_plan = []
            for day in chosen:
                matches = [r for r in usable if any(d['through'] == day for d in r['candidates'])]
                report_ids = {d['report_id'] for r in matches for d in r['candidates'] if d['through'] == day}
                if len(report_ids) != 1:
                    raise ValueError('Ambiguous report ID')
                date_plan.append(dict(through=day, report_id=next(iter(report_ids)),
                    compatible_teams=[r['name'] for r in matches], retained_report=retained.get((year,day))))
            modes[mode] = dict(teams=teams, date_plan=date_plan,
                summary=dict(field_teams=64, menu_date_feasible=sum(bool(r['candidates']) for r in teams),
                    feasible_excluding_known_empty=sum(bool(r['candidates']) for r in usable),
                    compatible_retained_populated=sum(any(d['retained_report'] and d['retained_report']['populated'] for d in r['candidates']) for r in teams),
                    teams_with_retained_non_d1=sum(bool(r['non_d1_before_target']) for r in teams),
                    minimum_report_dates=len(chosen),
                    date_blocked_teams=[r['name'] for r in usable if not r['candidates']],
                    phase_interleaving_teams=[r['name'] for r in teams if r['excluded_results_before_last_target']] ))
        seasons.append(dict(season=year, field_basis='result_participants_provisional' if year==2021 else 'dated_selection_article', modes=modes))
    return dict(schema_version=1, status='date_and_phase_feasibility_only', seasons=seasons,
        inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        evidence_sha256=evidence_inputs, selection_provenance={str(y):next(r['provenance'] for r in seeds if r['season']==y) for y in (2022,2023,2024)},
        timing_evidence=refs, model_features_qualified=False, collection_performed=False,
        limits=['Menu options may be empty or stale; report-date compatibility is not team component coverage.',
                'NCAA non-D1 components remain unknown; score totals cannot remove them.',
                '2021 field uses retained tournament participants for planning, not dated seed qualification.',
                'No field team may be silently dropped and no partial snapshot substituted.',
                'No fitting, retuning, candidate metrics or changes to Elo/cutoffs.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    print(json.dumps(run(parser.parse_args().evidence_dir), indent=2, sort_keys=True))
