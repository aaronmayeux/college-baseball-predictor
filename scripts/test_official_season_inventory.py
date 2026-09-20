"""Synthetic coverage failure tests; no external data or network required."""
import copy
import unittest
from audit_official_season_inventory import parse_index, reconcile


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(date='2025-05-01', teams=['A', 'B'], runs=[3, 2], box_url='https://school/one')
        self.game = dict(game_id='g1', game_date='2025-05-01', team_a_id='a', team_b_id='b', runs_a=3, runs_b=2)

    def check_rows(self, rows, games=None):
        return reconcile(rows, games or [self.game], {'A': 'a', 'B': 'b'}, 'a')

    def test_reverse_order(self):
        row = dict(self.row, teams=['B', 'A'], runs=[2, 3])
        self.assertTrue(self.check_rows([row])['inventory_pass'])

    def test_equal_counts_do_not_prove_coverage(self):
        row = dict(self.row, date='2025-05-02')
        result = self.check_rows([row])
        self.assertFalse(result['inventory_pass'])
        self.assertEqual(result['missing_baseline_games'], ['g1'])

    def test_duplicate_link_and_reused_game(self):
        result = self.check_rows([self.row, self.row])
        self.assertFalse(result['inventory_pass'])
        self.assertIn('duplicate_box_url', result['games'][0]['issues'])
        self.assertIn('reused_baseline_game', result['games'][0]['issues'])

    def test_doubleheader_ambiguity(self):
        game = dict(self.game, game_id='g2')
        result = self.check_rows([self.row], [self.game, game])
        self.assertFalse(result['inventory_pass'])
        self.assertIsNone(result['games'][0]['game_id'])

    def test_unknown_team_and_score_conflict(self):
        for row in [dict(self.row, teams=['A', 'Unknown']), dict(self.row, runs=[4, 2])]:
            self.assertFalse(self.check_rows([row])['inventory_pass'])

    def test_distinct_doubleheader_scores(self):
        game = dict(self.game, game_id='g2', runs_a=5)
        row = dict(self.row, runs=[5, 2], box_url='https://school/two')
        self.assertTrue(self.check_rows([self.row, row], [self.game, game])['inventory_pass'])

    def test_inputs_unchanged(self):
        original = copy.deepcopy(self.row)
        self.check_rows([self.row])
        self.assertEqual(self.row, original)

    def test_parser_guards(self):
        row = '<tr><td>May 01, 2025</td><td>Park</td><td>A 3, B 2</td><td><a href="one">Box score</a></td></tr>'
        self.assertEqual(parse_index(row, 'https://school/index', 2025)[0]['runs'], [3, 2])
        for text, year in [(row, 2024), (row.replace('A 3, B 2', 'TBA'), 2025), ('', 2025)]:
            with self.assertRaises(ValueError):
                parse_index(text, 'https://school/index', year)


if __name__ == '__main__':
    unittest.main()
