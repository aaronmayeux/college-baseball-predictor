"""Offline inventory for the proposed input expansion; no collection or fitting.

Restore baseline and timing/seed checkpoints per docs/DATA.md. JSON goes to
stdout; redirect only to an ignored analysis directory. Counts are result-game
inventories, not qualified boxes, permitted requests, or statistical power.
"""
import collections
import datetime as dt
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'historical/validation_v2'), str(ROOT / 'historical')]
import seeds
from baseline import load_games
from eligibility import NCAA, reject
from evidence import overlay, verify_timing
from reconcile import internal


def inventory(games, field, year, contract):
    result = {}
    cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
    for mode, stages in contract['modes'].items():
        eligible = [g for g in games if reject(g, cutoff, stages) is None
                    and (g['a'] in field or g['b'] in field)]
        counts = collections.Counter(t for g in eligible for t in (g['a'], g['b']) if t in field)
        result[mode] = dict(team_game_rows=sum(counts.values()),
                           unique_result_games=len(eligible),
                           games_by_team={t: counts[t] for t in sorted(field)})
    targets = [g for g in games if g['a'] in field and g['b'] in field
               and g['stage'] in NCAA and not g['tie']
               and g['reciprocal_check'] == 'pass' and not g.get('timing_review')
               and dt.datetime.fromisoformat(g['game_date'] + 'T00:00:00+00:00') > cutoff]
    return dict(team_count=len(field), modes=result, potential_ncaa_games=len(targets))


def run():
    contract = json.loads((ROOT / 'historical/cutoffs.json').read_text())
    selected = seeds.load(contract)  # Recheck selection bytes, dates and identities.
    refs = verify_timing()
    seasons = []
    roles = {2021: 'training_initialization_year', 2022: 'training',
             2023: 'selection', 2024: 'retrospective_validation'}
    for year, role in roles.items():
        games = overlay(load_games(year), refs)
        field = ({t for g in games if g['stage'] in NCAA for t in (g['a'], g['b'])}
                 if year == 2021 else {r['team_id'] for r in selected if r['season'] == year})
        if len(field) != 64:
            raise ValueError(f'Unexpected field inventory for {year}: {len(field)}')
        teams = json.loads((ROOT / f'historical/{year}/teams.json').read_text())
        by_id = {internal(t['slug']): t for t in teams}
        if not field <= by_id.keys():
            raise ValueError('Unmapped field team')
        seasons.append(dict(season=year, role=role,
            field_basis='result_participants_provisional' if year == 2021 else 'dated_selection_article',
            teams=[dict(team_id=t, name=by_id[t]['name'],
                        conference=by_id[t].get('conference')) for t in sorted(field)],
            **inventory(games, field, year, contract)))
    anchor = [r for r in selected if r['season'] == 2022 and r['team_id'] == internal('Missouri-State')]
    if len(anchor) != 1:
        raise ValueError('Missing unique retained-pilot regional')
    region = anchor[0]['regional']
    pilot = {r['team_id'] for r in selected if r['season'] == 2022 and r['regional'] == region}
    if len(pilot) != 4:
        raise ValueError('Pilot must contain the whole regional')
    paths = [ROOT / 'historical/cutoffs.json', pathlib.Path(__file__),
             ROOT / 'historical/baseline.py', ROOT / 'historical/eligibility.py',
             ROOT / 'historical/reconcile.py', ROOT / 'historical/validation_v2/seeds.py',
             ROOT / 'historical/validation_v2/evidence.py']
    paths += [ROOT / f'historical/{y}/{f}.json' for y in roles for f in ('games', 'teams')]
    return dict(schema_version=1, status='planning_only_no_qualified_feature_sample',
        collection_authorized=False, feature_metrics_computed=False,
        input_code_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in paths},
        selection_provenance={str(y): next(r['provenance'] for r in selected if r['season'] == y)
                              for y in (2022, 2023, 2024)}, timing_evidence=refs,
        seasons=seasons,
        preflight=dict(season=2022, regional=region, new_team_seasons=3,
            purpose='parser_access_feasibility_only_not_model_selection',
            **inventory(overlay(load_games(2022), refs), pilot, 2022, contract)))


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
