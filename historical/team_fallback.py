"""Frozen neutral team-only fallback. No player availability is inferred.

This development adapter reuses fixed Elo and its existing cutoff contract.
It supplies matchup probabilities, not a tournament simulation or calibrated
uncertainty intervals. Teams without eligible current-season results remain
visible but blocked; State's default rating must not silently stand in for data.
"""
import datetime as dt
import itertools
import math

from baseline import State
from eligibility import reject

MODES = ('regular_only', 'conference_inclusive')


def reconstruct(games_by_year, contract, season, mode):
    if mode not in MODES or season != 2025:
        raise ValueError('Only the 2025 development field and frozen modes are supported')
    if set(games_by_year) != set(range(2021, season + 1)):
        raise ValueError('Require complete 2021–2025 initialization history')
    state = State()
    history = []
    for year in sorted(games_by_year):
        games = games_by_year[year]
        if any(g['season'] != year for g in games):
            raise ValueError('Mixed game seasons')
        if len({g['game_id'] for g in games}) != len(games):
            raise ValueError('Duplicate game IDs')
        if any(g['a'] == g['b'] for g in games):
            raise ValueError('Self matchup')
        if year > 2021:
            state.regress()
        cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        eligible = [g for g in games if reject(g, cutoff, contract['modes'][mode]) is None]
        for _, batch in itertools.groupby(sorted(eligible, key=lambda g: g['game_date']), lambda g: g['game_date']):
            state.update(list(batch))
        history.append(dict(season=year, eligible_games=len(eligible), forecast_cutoff=cutoff.isoformat()))
    return state, history


def snapshot(field, state, mode):
    if mode not in MODES or field['season'] != 2025:
        raise ValueError('Unsupported field or mode')
    teams = field['teams']
    for key in ('team_id', 'stable_team_id'):
        if len(teams) != 64 or len({t[key] for t in teams}) != 64 or any(not t[key] for t in teams):
            raise ValueError('Require 64 distinct team identities')
    if any(t['season'] != 2025 for t in teams):
        raise ValueError('Mixed field seasons')
    rows = []
    for team in teams:
        ident = team['stable_team_id']
        n = state.n.get(ident, 0)
        rating = state.r.get(ident)
        available = n > 0 and rating is not None and math.isfinite(rating)
        rows.append(dict(team_id=team['team_id'], stable_team_id=ident, name=team['name'],
            season=2025, mode=mode, eligible_current_season_games=n,
            elo_rating=rating if available else None,
            fallback_status='available_for_development_matchups' if available else 'blocked_missing_eligible_results',
            coverage={k: team.get(k, 'unverified') for k in ('schedule_status', 'cumulative_status', 'hitting_counts', 'pitching_counts')},
            recent_workload='unknown', available_pitchers=None,
            uncertainty=dict(player_availability='unmodeled_unknown', team_strength_interval=None,
                interval_status='not_calibrated', probability_basis='fixed_neutral_team_elo'),
            player_adjustments_applied=False, feature_qualified=False,
            production_fallback_validated=False, complete_bracket_ready=False))
    return rows


def matchup(a, b):
    if a['stable_team_id'] == b['stable_team_id']:
        raise ValueError('Self matchup')
    if a['season'] != b['season'] or a['mode'] != b['mode']:
        raise ValueError('Cannot mix seasons or forecast modes')
    if any(t['fallback_status'] != 'available_for_development_matchups' for t in (a, b)):
        return dict(status='blocked_missing_eligible_results', probability_a=None,
            recent_workload='unknown', player_adjustments_applied=False)
    p = 1 / (1 + 10 ** ((b['elo_rating'] - a['elo_rating']) / 400))
    return dict(status='development_team_only', probability_a=p,
        recent_workload='unknown', player_adjustments_applied=False)
