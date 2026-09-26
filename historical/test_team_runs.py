"""Synthetic leakage, aggregation and fitting regressions; no external data."""
import copy
import datetime as dt
import math
import unittest

from team_runs import aggregate, fit, probability, scored, select, summarize

CUT = dt.datetime.fromisoformat('2023-05-31T12:00:00+00:00')


def game(id='g1', **changes):
    row = dict(game_id=id, a='a', b='b', runs_a=7, runs_b=3,
               game_date='2023-05-29', reciprocal_check='pass', stage='regular_season')
    return dict(row, **changes)


def row(x=1, y=1, elo=.5, season=2021):
    return dict(elo=elo, outcome=y, tie=False, season=season,
                differences=dict(offense=x, prevention=x, net=x))


class TeamRunsTests(unittest.TestCase):
    def test_sum_counts_before_rates(self):
        totals, _ = aggregate([game(), game('g2', runs_a=1, runs_b=5)], CUT, ['regular_season'])
        self.assertEqual(totals['a']['offense'], 4)
        self.assertEqual(totals['a']['prevention'], -4)
        self.assertEqual(totals['a']['net'], 0)
        self.assertEqual(totals['b']['runs_for'], totals['a']['runs_against'])

    def test_cutoff_phase_and_conflicts(self):
        games = [game(), game('late', game_date='2023-05-30'),
                 game('ncaa', stage='regional'), game('conf', stage='conference_tournament'),
                 game('unknown', timing_review=True), game('bad', reciprocal_check='fail')]
        regular, excluded = aggregate(games, CUT, ['regular_season'])
        inclusive, _ = aggregate(games, CUT, ['regular_season', 'conference_tournament'])
        self.assertEqual(regular['a']['game_ids'], ['g1'])
        self.assertEqual(inclusive['a']['game_ids'], ['conf', 'g1'])
        self.assertEqual(sum(r['reason'] is not None for r in excluded), 5)

    def test_future_scores_do_not_change_features(self):
        games = [game(), game('future', game_date='2023-06-05', stage='regional')]
        expected = aggregate(games, CUT, ['regular_season'])
        games[-1]['runs_a'] = 999
        self.assertEqual(expected, aggregate(games, CUT, ['regular_season']))

    def test_duplicate_invalid_score_and_self_game_fail(self):
        for games in ([game(), game()], [game(runs_a=-1)], [game(runs_a=1.5)], [game(b='a')]):
            with self.assertRaises(ValueError):
                aggregate(games, CUT, ['regular_season'])

    def test_aggregate_does_not_mutate(self):
        games = [game()]
        original = copy.deepcopy(games)
        aggregate(games, CUT, ['regular_season'])
        self.assertEqual(games, original)

    def test_fitted_gradient_and_train_only_scale(self):
        rows = [row(1,1), row(-2,0), row(3,1), row(-4,1)]
        model = fit(rows, 'offense')
        self.assertAlmostEqual(model['scale'], math.sqrt(7.5))
        gradient = sum((probability(r,model)-r['outcome'])*r['differences']['offense']/model['scale'] for r in rows)/len(rows) + .01*model['beta']
        self.assertAlmostEqual(gradient, 0, places=10)
        saved = copy.deepcopy(model)
        probability(row(1000,0,season=2024), model)
        self.assertEqual(saved, model)

    def test_team_reversal_complements_probability(self):
        model = fit([row(), row(-1,0)], 'net')
        self.assertAlmostEqual(probability(row(2,1,.7), model) + probability(row(-2,0,.3), model), 1)

    def test_selection_rejects_regression(self):
        models = {'offense': dict(candidate='offense', beta=1, scale=1)}
        winner, _ = select([row(1,0), row(-1,1)], models)
        self.assertEqual(winner, 'elo')
        winner, _ = select([row(1,1), row(-1,0)], models)
        self.assertEqual(winner, 'offense')

    def test_zero_signal_empty_and_tie_training_fail(self):
        for rows in ([], [row(0)], [dict(row(), tie=True)]):
            with self.assertRaises(ValueError):
                fit(rows, 'offense')

    def test_elo_fallback_and_common_seed_sample(self):
        rows = [dict(row(), seed=.6), dict(row(-1,0), seed=.4)]
        result = summarize(scored(rows, dict(candidate='elo')))
        self.assertEqual(result['paired_delta']['log_loss'], 0)
        self.assertEqual(result['paired_delta']['brier'], 0)
        self.assertEqual({m['n'] for m in result['metrics'].values()}, {2})
        self.assertEqual(sum(b['n'] for b in result['calibration']['elo']), 2)


if __name__ == '__main__':
    unittest.main()
