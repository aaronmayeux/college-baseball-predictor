import unittest
from reconcile_ncaa_archive import totals, ncaa_totals, differences, field_mapping


class ReconciliationTests(unittest.TestCase):
    def test_ties_are_not_losses(self):
        self.assertEqual(totals([(5, 5), (6, 1), (0, 2)]),
                         dict(G=3, W=1, L=1, T=1, R=8))
        self.assertEqual(ncaa_totals({'G': 3, 'W-L': '1-1-1', 'R': 8}),
                         totals([(5, 5), (6, 1), (0, 2)]))

    def test_non_d1_addition_can_fix_record_without_fixing_runs(self):
        d1 = totals([(8, 3)])
        extra = totals([(10, 2)])
        expected = {k: d1[k] + extra[k] for k in d1}
        self.assertEqual(differences(dict(G=2, W=2, L=0, T=0, R=1), expected),
                         dict(G=0, W=0, L=0, T=0, R=-4))

    def field(self):
        return [dict(team_id=str(i), source_name=f'Team {i}') for i in range(64)]

    def test_typography_only_mapping_keeps_all_teams(self):
        field = self.field()
        field[0]['source_name'] = 'St. John’s (NY)'
        names = {r['source_name'].replace('’', "'") for r in field}
        self.assertEqual(field_mapping(field, names)[0]['report_name'], "St. John's (NY)")

    def test_missing_duplicate_and_fuzzy_names_rejected(self):
        field = self.field()
        names = {r['source_name'] for r in field}
        with self.assertRaises(ValueError):
            field_mapping(field[:-1], names)
        with self.assertRaises(ValueError):
            field_mapping(field[:-1]+[field[0]], names)
        with self.assertRaises(ValueError):
            field_mapping(field, (names-{'Team 0'}) | {'Team Zero'})
        field[0]['source_name'] = field[1]['source_name']
        with self.assertRaises(ValueError):
            field_mapping(field, names)
