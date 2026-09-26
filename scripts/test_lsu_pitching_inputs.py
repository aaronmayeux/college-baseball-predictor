"""Synthetic LSU role, event allocation and cumulative reconciliation checks."""
import copy
import unittest
from lsu_pitching_inputs import starter, pitcher_extras, season_check, game
from test_hitting_inputs import fixture, EXPECTED
from audit_season_appearances import lsu_box


def players():
    return [dict(match_key='alex relief'), dict(match_key='bob start')]


def play(body):
    return '<a name="GAME.PLY"><table><tr><td>Other 1st - '+body+'</td></tr></table>'


class LsuPitchingTests(unittest.TestCase):
    def test_starter_explicit_not_order_or_dh(self):
        text = '<td>LSU starters: 1/dh Relief; 2/p Start;</td>'
        self.assertEqual(starter(text, players()), ('bob start', 'Start'))

    def test_starter_fail_closed(self):
        for text in ['', '<td>LSU starters: 1/dh Start;</td>',
                     '<td>LSU starters: 1/p Start; 2/p Relief;</td>',
                     '<td>LSU starters: 1/p Unknown;</td>',
                     '<td>LSU starters: 1/p Start;</td>'*2]:
            with self.assertRaises(ValueError): starter(text, players())
        with self.assertRaises(ValueError):
            starter('<td>LSU starters: 1/p Start;</td>', players()+[dict(match_key='joe start')])

    def test_event_order_and_pitch_codes(self):
        body = "B flied out (0-2 SF). B reached on catcher's interference. Relief to p for Start. B flied out, SF. B grounded out, SAC."
        extra = pitcher_extras(play(body), 'Other', 'bob start', players())
        self.assertEqual(extra['bob start'], dict(SF=0, SH=0, CI=1))
        self.assertEqual(extra['alex relief'], dict(SF=1, SH=1, CI=0))

    def test_change_into_different_batting_slot(self):
        body = 'Relief to p for Hitter. / for Start. B flied out, SF.'
        self.assertEqual(pitcher_extras(play(body), 'Other', 'bob start', players())['alex relief']['SF'], 1)
        with self.assertRaises(ValueError):
            pitcher_extras(play(body.replace('/ for Start.', '')), 'Other', 'bob start', players())

    def test_bad_change_and_duplicate_surnames(self):
        for body in ['Unknown to p for Start.', 'Relief to p for Unknown.']:
            with self.assertRaises(ValueError): pitcher_extras(play(body), 'Other', 'bob start', players())
        with self.assertRaises(ValueError):
            pitcher_extras(play(''), 'Other', 'bob start', players()+[dict(match_key='joe start')])

    def test_game_adapter_and_mismatch(self):
        text = fixture().replace('<a name="GAME.PLY">', '<td>LSU starters: 1/p Pitcher;</td><a name="GAME.PLY">')
        apps = lsu_box(text, EXPECTED)['pitching']
        old = copy.deepcopy(apps)
        result, check = game(text, EXPECTED, apps)
        self.assertEqual(result[0]['counts']['GS'], 1)
        self.assertEqual(check['BF'], 3)
        self.assertEqual(apps, old)
        apps[0]['counts']['BF'] = 4
        with self.assertRaises(ValueError): game(text, EXPECTED, apps)

    def test_generic_team_preserves_counts_and_inputs(self):
        from audit_season_appearances import statcrew_box
        from hitting_inputs import statcrew_team
        text=fixture().replace('LSU','Arkansas').replace('<a name="GAME.PLY">',
            '<td>Arkansas starters: 1/p Pitcher;</td><a name="GAME.PLY">')
        expected=dict(EXPECTED,teams=['Arkansas' if t=='LSU' else t for t in EXPECTED['teams']])
        apps=statcrew_box(text,expected,'Arkansas')['pitching']
        before=copy.deepcopy(apps)
        pitchers,check=game(text,expected,apps,'Arkansas')
        self.assertEqual(apps,before)
        self.assertEqual(pitchers[0]['counts']['GS'],1)
        self.assertEqual(check['BF'],3)
        self.assertEqual(statcrew_team(text,expected,'Arkansas')['counts'],
                         statcrew_team(fixture(),EXPECTED)['counts'])
        with self.assertRaises(ValueError):game(text,expected,apps,'Unknown')

    def test_defensive_throw_is_not_a_pitching_change(self):
        body='B out at home c to p. Relief to p for Start. B flied out, SF.'
        extras=pitcher_extras(play(body),'Other','bob start',players())
        self.assertEqual(extras['alex relief']['SF'],1)
        self.assertEqual(extras['bob start']['SF'],0)

    def test_removed_review_and_multiple_spaces_before_change(self):
        body='B flied out. Previous play reviewed, call confirmed.   Relief to p for Start. B flied out, SF.'
        self.assertEqual(pitcher_extras(play(body),'Other','bob start',players())['alex relief']['SF'],1)

    def test_other_teams_lineup_is_not_a_substitute(self):
        text='<td>LSU starters: 1/p Start;</td>'
        with self.assertRaises(ValueError):starter(text,players(),'Arkansas')

    def test_season_interference_supplement_and_start_difference(self):
        targets = {'bob start':dict(raw={'APP-GS':'1-1', 'AB':'3', 'BB':'1', 'HBP':'0', 'SFA':'1', 'SHA':'0'})}
        records = [dict(BF_check={'opponent_counts':{'CI':1}}, pitchers=[
            dict(match_key='bob start', counts=dict(BF=6, GS=1, CI=1, SF=1, SH=0))])]
        self.assertTrue(season_check(records, targets, True)['pass_counts'])
        targets['bob start']['raw']['APP-GS'] = '1-0'
        self.assertFalse(season_check(records, targets, True)['pass_counts'])

    def test_missing_game_and_core_gate(self):
        self.assertFalse(season_check([dict(BF_check=None, pitchers=None)], {}, True)['pass_counts'])
        self.assertFalse(season_check([], {}, False)['pass_counts'])


if __name__ == '__main__': unittest.main()
