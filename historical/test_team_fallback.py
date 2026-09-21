"""Fallback failures and leakage guards; no external evidence required."""
import copy
import unittest

from baseline import State
from team_fallback import reconstruct, snapshot, matchup


def fixture():
    field = dict(season=2025, teams=[dict(team_id=f'wn:{i}', stable_team_id=f'cb:{i}',
        name=str(i), season=2025) for i in range(64)])
    state = State()
    for t in field['teams']:
        state.r[t['stable_team_id']] = 1500
        state.n[t['stable_team_id']] = 1
    return field, state


def history_fixture():
    contract = dict(modes=dict(regular_only=['regular'], conference_inclusive=['regular', 'conference_tournament']),
        seasons={str(y): dict(forecast_cutoff=f'{y}-05-28T12:00:00+00:00') for y in range(2021, 2026)})
    def game(year, suffix, date, stage='regular', **kwargs):
        return dict(season=year, game_id=f'{year}:{suffix}', a='a', b='b',
            game_date=f'{year}-{date}', stage=stage, reciprocal_check='pass',
            tie=False, runs_a=4, runs_b=1, **kwargs)
    games = {y: [game(y, '1', '03-01')] for y in range(2021, 2026)}
    return games, contract, game


class Fallback(unittest.TestCase):
    def test_missing_player_data_keeps_all_teams_and_probabilities(self):
        field, state = fixture()
        rows = snapshot(field, state, 'regular_only')
        self.assertEqual(len(rows), 64)
        self.assertTrue(all(r['coverage']['pitching_counts'] == 'unverified' for r in rows))
        self.assertEqual(matchup(*rows[:2])['probability_a'], .5)

    def test_untrusted_coverage_never_implies_rested_or_feature_qualified(self):
        field, state = fixture()
        field['teams'][0].update(recent_workload='rested', available_pitchers=25,
            feature_qualified=True, pitching_counts='reconciled_core_counts', elo_rating=9999)
        row = snapshot(field, state, 'regular_only')[0]
        self.assertEqual(row['recent_workload'], 'unknown')
        self.assertIsNone(row['available_pitchers'])
        self.assertFalse(row['feature_qualified'])
        self.assertFalse(row['player_adjustments_applied'])
        self.assertIsNone(row['uncertainty']['team_strength_interval'])
        self.assertEqual(row['elo_rating'], 1500)

    def test_missing_results_remain_visible_and_do_not_use_default_rating(self):
        field, state = fixture()
        del state.n['cb:0']
        del state.r['cb:1']
        state.r['cb:2'] = float('nan')
        rows = snapshot(field, state, 'regular_only')
        self.assertEqual(len(rows), 64)
        for row in rows[:3]:
            self.assertIsNone(row['elo_rating'])
            self.assertIsNone(matchup(row, rows[3])['probability_a'])
        self.assertNotIn('cb:1', state.r)

    def test_field_identity_and_season_guards(self):
        for mutation in ('missing', 'duplicate_provider', 'duplicate_stable', 'season'):
            field, state = fixture()
            if mutation == 'missing': field['teams'].pop()
            elif mutation == 'season': field['teams'][0]['season'] = 2026
            else:
                key = 'team_id' if mutation == 'duplicate_provider' else 'stable_team_id'
                field['teams'][0][key] = field['teams'][1][key]
            with self.assertRaises(ValueError): snapshot(field, state, 'regular_only')

    def test_matchup_modes_self_and_complements(self):
        field, state = fixture()
        state.r['cb:0'] = 1700
        rows = snapshot(field, state, 'regular_only')
        self.assertAlmostEqual(matchup(*rows[:2])['probability_a'] + matchup(*rows[:2][::-1])['probability_a'], 1)
        with self.assertRaises(ValueError): matchup(rows[0], rows[0])
        other = snapshot(field, state, 'conference_inclusive')
        with self.assertRaises(ValueError): matchup(rows[0], other[1])
        with self.assertRaises(ValueError): snapshot(field, state, 'daily_updated')

    def test_cutoff_phase_and_conflict_changes_cannot_leak(self):
        games, contract, game = history_fixture()
        base, _ = reconstruct(games, contract, 2025, 'regular_only')
        games[2025] += [game(2025, 'late', '05-27'), game(2025, 'post', '06-01', 'regional'),
            game(2025, 'conf', '05-20', 'conference_tournament'),
            game(2025, 'timing', '03-02', timing_review=True)]
        changed, _ = reconstruct(games, contract, 2025, 'regular_only')
        self.assertEqual(dict(base.r), dict(changed.r))
        self.assertEqual(dict(base.n), dict(changed.n))
        conference, _ = reconstruct(games, contract, 2025, 'conference_inclusive')
        self.assertEqual(conference.n['a'], base.n['a'] + 1)
        self.assertNotEqual(conference.r['a'], base.r['a'])

    def test_same_day_batch_and_cutoff_boundary(self):
        games, contract, game = history_fixture()
        games[2025] += [game(2025, '2', '05-26'), game(2025, '3', '05-26')]
        games[2025][-1].update(runs_a=0, runs_b=8)
        first, _ = reconstruct(games, contract, 2025, 'regular_only')
        reverse = copy.deepcopy(games)
        reverse[2025].reverse()
        second, _ = reconstruct(reverse, contract, 2025, 'regular_only')
        self.assertEqual(dict(first.r), dict(second.r))
        self.assertEqual(first.n['a'], 3)

    def test_history_guards(self):
        for kind in ('missing_year', 'mixed_season', 'duplicate', 'future', 'mode'):
            games, contract, _ = history_fixture()
            if kind == 'missing_year': del games[2021]
            if kind == 'mixed_season': games[2025][0]['season'] = 2026
            if kind == 'duplicate': games[2025] += games[2025]
            with self.assertRaises(ValueError):
                reconstruct(games, contract, 2026 if kind == 'future' else 2025,
                    'daily_updated' if kind == 'mode' else 'regular_only')


if __name__ == '__main__':
    unittest.main()
