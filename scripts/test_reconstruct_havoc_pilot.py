import unittest
from reconstruct_havoc_pilot import FIELDS, box_counts, d1_counts, subtract


def fixture():
    header = ['Player', 'AB', 'R', 'H', 'HBP', 'BB', 'SO', 'SB', 'CS']
    values = ['Batter', '4', '1', '2', '0', '1', '1', '1', '0']
    def tr(row):
        return '<tr>' + ''.join('<td>'+v+'</td>' for v in row) + '</tr>'
    return ('<title>Baseball vs Test on 6/2/2023 - Box Score</title>'
            '<h2>Test</h2><table>' + tr(header) + tr(values) +
            tr(['Totals']+values[1:]) + '</table>')


class HavocReconstructionTests(unittest.TestCase):
    def test_legacy_composite_caption_identifies_team(self):
        html = fixture().replace('<h2>Test</h2><table>',
            '<h2>Visitors -vs- Hosts</h2><table><caption>Test 1'
            '<span> - Composite Stats</span></caption>')
        self.assertEqual(box_counts(html, 'Test', '2023-06-02')['K'], 1)
        with self.assertRaises(ValueError):
            box_counts(html, 'Hosts', '2023-06-02')
        with self.assertRaises(ValueError):
            box_counts(html.replace('<td>Totals</td><td>4</td>',
                                   '<td>Totals</td><td>5</td>'), 'Test', '2023-06-02')

    def test_batting_not_pitching(self):
        html = fixture() + '<h2>Test</h2><table><tr><th>IP</th><th>SO</th></tr></table>'
        self.assertEqual(box_counts(html, 'Test', '2023-06-02')['K'], 1)

    def test_wrong_date_team_and_future_year(self):
        for team, day in [('Other', '2023-06-02'), ('Test', '2023-06-03'), ('Test', '2026-06-02')]:
            with self.assertRaises(ValueError):
                box_counts(fixture(), team, day)

    def test_missing_negative_and_mismatched_counts(self):
        for bad in ['', '-1', '2']:
            html = fixture().replace('<td>Totals</td><td>4</td>', '<td>Totals</td><td>'+bad+'</td>')
            with self.assertRaises(ValueError):
                box_counts(html, 'Test', '2023-06-02')

    def test_ambiguous_tables(self):
        with self.assertRaises(ValueError):
            box_counts(fixture()*2, 'Test', '2023-06-02')

    def test_complete_exclusion_required(self):
        final = dict.fromkeys(FIELDS, 10)
        row = dict(game_id='g', counts=dict.fromkeys(FIELDS, 2))
        self.assertEqual(subtract(final, [row], ['g'])['K'], 8)
        for boxes, expected in [([], ['g']), ([row, row], ['g']), ([row], [])]:
            with self.assertRaises(ValueError):
                subtract(final, boxes, expected)

    def test_nonpositive_denominator_rejected(self):
        with self.assertRaises(ValueError):
            subtract(dict.fromkeys(FIELDS, 0), [], [])

    def test_d1_split_and_player_integrity(self):
        v = dict(season=2023, split='Overall', url='https://d1baseball.com/team/virginia/2023/stats/',
                 rows=[['PLAYER', 'Team']+list(FIELDS), ['Batter', 'Virginia']+['1']*len(FIELDS)],
                 browser_verified_totals=dict.fromkeys(FIELDS, 1))
        self.assertEqual(d1_counts(v)['K'], 1)
        v['split'] = 'Conference'
        with self.assertRaises(ValueError):
            d1_counts(v)
        v['split'] = 'Overall'
        v['rows'].append(v['rows'][1])
        with self.assertRaises(ValueError):
            d1_counts(v)


if __name__ == '__main__':
    unittest.main()
