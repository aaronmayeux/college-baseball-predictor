"""Data-free tournament rules, exact odds, routing and illegal-input tests."""
import itertools
import math
from pathlib import Path
import sys
import unittest
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tournament.engine import (forecast, group_probabilities, next_game, pick_bracket,
                               probability, series_probability, validate)
from tournament.field import HOST_ORDER, build_regions


def fixture():
    regions = [dict(id=f'r{i}', name=f'Regional {i}', teams=[f't{i*4+j:02}' for j in range(4)]) for i in range(16)]
    ratings = {t: 1500.0 for r in regions for t in r['teams']}
    return regions, ratings


class TournamentTests(unittest.TestCase):
    def test_series_benchmark_and_extremes(self):
        self.assertAlmostEqual(series_probability(.6), .648)
        for p in (0, .1, .5, .9, 1):
            self.assertAlmostEqual(series_probability(p) + series_probability(1-p), 1)
        for p in (-.1, 1.1, math.nan):
            with self.assertRaises(ValueError):
                series_probability(p)
        self.assertEqual(probability(-1000000, 1000000), 0)

    def test_fair_group(self):
        self.assertEqual(group_probabilities('abcd', lambda a,b: .5), dict.fromkeys('abcd', .25))

    def test_all_elimination_paths(self):
        lengths = set()
        for bits in itertools.product((0, 1), repeat=7):
            results, losses = [], Counter()
            while (pair := next_game('abcd', results)) is not None:
                a, b = pair
                self.assertLess(losses[a], 2)
                self.assertLess(losses[b], 2)
                if len(results) == 5:
                    self.assertEqual((losses[a], losses[b]), (0, 1))
                if len(results) == 6:
                    self.assertEqual((losses[a], losses[b]), (1, 1))
                winner, loser = (a,b) if bits[len(results)] == 0 else (b,a)
                losses[loser] += 1
                results.append((winner, loser))
            lengths.add(len(results))
            champion = results[-1][0]
            self.assertLess(losses[champion], 2)
            self.assertTrue(all(losses[t] == 2 for t in 'abcd' if t != champion))
        self.assertEqual(lengths, {6, 7})

    def test_exact_odds_against_full_path_enumeration(self):
        ratings = dict(zip('abcd', [1400, 1510, 1620, 1700]))
        p = lambda a,b: probability(ratings[a], ratings[b])
        expected = dict.fromkeys('abcd', 0.0)
        def enumerate_games(results, weight):
            pair = next_game('abcd', results)
            if pair is None:
                expected[results[-1][0]] += weight
                return
            a,b = pair
            enumerate_games(results+[(a,b)], weight*p(a,b))
            enumerate_games(results+[(b,a)], weight*(1-p(a,b)))
        enumerate_games([], 1)
        for t, value in group_probabilities('abcd', p).items():
            self.assertAlmostEqual(value, expected[t])

    def test_fair_complete_tournament(self):
        regions, ratings = fixture()
        result = forecast(regions, ratings)
        for odds in result['advancement'].values():
            for stage, expected in zip(('super_regional','omaha','final','champion'), (.25,.125,.03125,.015625)):
                self.assertAlmostEqual(odds[stage], expected)
        self.assertEqual(len(result['picks']['games']), 126)
        self.assertEqual(Counter(r['stage'] for r in result['picks']['rounds']),
                         dict(regional=16, super_regional=8, omaha=2, championship_series=1))

    def test_sweeps_and_deciding_games(self):
        regions, _ = fixture()
        # First entrant always wins => no reset, all series sweep.
        result = pick_bracket(regions, lambda a,b: .6, choose=lambda a,b,p: a)
        self.assertEqual(len(result['games']), 126)
        # Second entrant always wins => every double-elimination group resets.
        result = pick_bracket(regions, lambda a,b: .6, choose=lambda a,b,p: b)
        self.assertEqual(len(result['games']), 144)
        counts = Counter(g['group'] for g in result['games'])
        self.assertTrue(all(counts[r['id']] == 7 for r in regions))
        # Alternate winners only in repeated pairs: force split series.
        seen = Counter()
        def choose(a,b,p):
            seen[a,b] += 1
            return a if seen[a,b] % 2 else b
        result = pick_bracket(regions, lambda a,b: .6, choose=choose)
        for rnd in result['rounds']:
            rows = [g for g in result['games'] if g['group'] == rnd['id']]
            if rnd['stage'] in ('super_regional', 'championship_series'):
                self.assertEqual(len(rows), 3)
                self.assertEqual(Counter(g['winner'] for g in rows)[rnd['winner']], 2)

    def test_routing_without_reseeding(self):
        regions, _ = fixture()
        result = pick_bracket(regions, lambda a,b: 1, choose=lambda a,b,p: a)
        by_stage = {s: [r for r in result['rounds'] if r['stage']==s] for s in ('regional','super_regional','omaha','championship_series')}
        self.assertEqual(by_stage['super_regional'][0]['entrants'], ['t00','t04'])
        self.assertEqual(by_stage['omaha'][0]['entrants'], ['t00','t08','t16','t24'])
        self.assertEqual(by_stage['omaha'][1]['entrants'], ['t32','t40','t48','t56'])
        self.assertEqual(by_stage['championship_series'][0]['entrants'], ['t00','t32'])
        self.assertEqual(HOST_ORDER, ('Vanderbilt','Southern-Miss','Florida-State','Oregon-State','North-Carolina','Oregon','Coastal-Carolina','Auburn','Texas','UCLA','Ole-Miss','Georgia','LSU','Clemson','Tennessee','Arkansas'))

    def test_bad_fields_and_ratings(self):
        regions, ratings = fixture()
        for invalid in ({}, {**ratings, 'extra': 1500}, {**ratings, 't00': math.nan}):
            with self.assertRaises(ValueError):
                validate(regions, invalid)
        regions[1]['teams'][0] = regions[0]['teams'][0]
        with self.assertRaises(ValueError):
            validate(regions, ratings)
        with self.assertRaises(ValueError):
            group_probabilities('aabc', lambda a,b:.5)
        with self.assertRaises(ValueError):
            group_probabilities('abcd', lambda a,b:math.nan)

    def test_field_order_does_not_depend_on_article_order(self):
        rows = [dict(season=2025, regional=h, regional_seed=s,
                     team_id=h if s==1 else f'{h}-{s}') for h in HOST_ORDER for s in range(1,5)]
        regions = build_regions(list(reversed(rows)), lambda x:x)
        self.assertEqual([r['teams'][0] for r in regions], list(HOST_ORDER))
        rows[0]['season'] = 2026
        with self.assertRaises(ValueError):
            build_regions(rows, lambda x:x)


if __name__ == '__main__':
    unittest.main()
