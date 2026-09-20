"""Synthetic official pitching parser checks; no downloads required."""
import unittest
from audit_official_pitching import PITCH_HEADER, parse_pitching, player_key, table_cells, compare


def box(name='A', innings='0.0', pitches='0', runs='0', total_runs=None):
    values = ['Pitcher, Pat', innings, '0', runs, runs, '1', '0', '0', '0', '0', '0', '0', '1', '0', '0', pitches]
    totals = ['Totals', ''] + values[2:]
    if total_runs is not None:
        totals[3] = total_runs
    def row(cells):
        return '<tr>' + ''.join('<td>'+c+'</td>' for c in cells) + '</tr>'
    return '<table><caption>'+name+' - Pitching Stats</caption>'+row(PITCH_HEADER)+row(values)+row(totals)+'</table>'


class OfficialPitchingTests(unittest.TestCase):
    def test_zero_out_appearance_and_unknown_pitches(self):
        parsed = parse_pitching(box(), ['A'])['A']
        self.assertEqual(len(parsed['players']), 1)
        self.assertEqual(parsed['sums']['outs'], 0)
        self.assertEqual(parsed['sums']['BF'], 1)
        self.assertIsNone(parsed['players'][0]['pitch_count'])
        self.assertEqual(parsed['players'][0]['raw']['NP'], '0')

    def test_baseball_outs_no_27_out_assumption(self):
        self.assertEqual(parse_pitching(box(innings='8.1'), ['A'])['A']['sums']['outs'], 25)
        with self.assertRaises(ValueError):
            parse_pitching(box(innings='8.3'), ['A'])

    def test_missing_count_rejected(self):
        with self.assertRaises(ValueError):
            parse_pitching(box(pitches='--'), ['A'])

    def test_totals_disagreement_retained(self):
        parsed = parse_pitching(box(runs='1', total_runs='2'), ['A'])['A']
        self.assertFalse(parsed['totals_checks']['R'])

    def test_unknown_duplicate_and_missing_team_rejected(self):
        for text, teams in [(box(), ['B']), (box()+box(), ['A']), (box(), ['A','B'])]:
            with self.assertRaises(ValueError):
                parse_pitching(text, teams)

    def test_duplicate_player_rejected(self):
        text = box()
        start = text.index('<tr><td>Pitcher')
        end = text.index('</tr>', start)+5
        text = text[:end]+text[start:end]+text[end:]
        with self.assertRaises(ValueError):
            parse_pitching(text, ['A'])

    def test_malformed_legacy_blank_cell(self):
        self.assertEqual(table_cells('<td>Totals</td><td><td>8</td></td>'), ['Totals','','8'])
        self.assertEqual(table_cells('<td colspan="2">Totals</td><td>8</td>'), ['Totals','','8'])

    def test_missing_appearance_is_reported(self):
        official = parse_pitching(box(), ['A'])['A']
        players = {'statistics': [{'type': 'pitching', 'labels': ['IP'], 'athletes': []}]}
        totals = {'statistics': [{'name': 'pitching', 'stats': []}]}
        result = compare(official, players, totals)
        self.assertEqual(result['missing_from_espn'], ['Pitcher, Pat'])
        self.assertIsNone(result['team_totals']['outs']['espn_team'])

    def test_team_total_disagreement_does_not_overwrite_rows(self):
        official = parse_pitching(box(innings='8.1'), ['A'])['A']
        players = {'statistics': [{'type': 'pitching', 'labels': ['IP','H','R','ER','BB','K'],
                    'athletes': [{'athlete': {'displayName': 'Pat Pitcher'},
                                  'stats': ['8.1','0','0','0','1','0']}]}]}
        totals = {'statistics': [{'name': 'pitching', 'stats': [
            {'name': 'thirdInnings', 'displayValue': '24'}]}]}
        result = compare(official, players, totals)
        self.assertEqual(result['common_row_differences'], [])
        self.assertEqual(result['team_totals']['outs'], {'official_rows': 25, 'espn_team': '24'})

    def test_name_crosswalk_is_conservative(self):
        self.assertEqual(player_key('Spencer, Bobby (L, 0-1)'), 'bobby spencer')
        self.assertEqual(player_key('Reece - P Lang'), 'reece lang')
        self.assertNotEqual(player_key('Pat Smith'), player_key('Patrick Smith'))


if __name__ == '__main__':
    unittest.main()
