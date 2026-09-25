"""Synthetic regression checks: no retained data or network required."""
import datetime as dt
import unittest
from hitting_inputs import rates, statcrew_team, play_counts, event_summary, cumulative_team
from extract_hitting_inputs import aggregate
from test_season_appearances import tr


def fixture():
    bat = 'Player ab r h rbi bb so po a lob'.split()
    pitch = 'ip h r er bb so wp bk hbp ibb ab bf fo go np'.split()
    text = '<title>Other vs LSU (Feb 14, 2025)</title><table>'
    for team, vals in [('Other', [3,0,0,0,0,3,3,0,0]), ('LSU', [3,2,2,2,1,1,3,0,3])]:
        text += tr([team + (' 2 (1-0)' if team == 'LSU' else ' 0 (0-1)')])
        text += tr(bat) + tr(['Hitter cf']+vals) + tr(['Totals']+vals)
    text += '</table><table><tr><td>LOB - Other 0; LSU 3. 2B - Batter(10). HR - Batter(12). HBP - Batter. SF - Batter(3). SH - Batter(1). Reached on CI - Batter.</td></tr></table>'
    text += '<table>'+tr(['LSU']+pitch)+tr(['Pitcher','1.0',0,0,0,0,3,0,0,0,0,3,3,0,0,12])+'</table>'
    text += '<table>'+tr(['Other']+pitch)+tr(['Pitcher','1.0',2,2,2,1,1,0,0,1,0,3,8,0,0,30])+'</table>'
    text += '<a name="GAME.PLY"> </a>'
    text += '<table><tr><td>Other 1st - A struck out swinging. B struck out swinging. C struck out swinging. 0 runs, 0 hits, 0 errors, 0 LOB.</td></tr></table>'
    text += '<table><tr><td>LSU 1st - Batter doubled (0-2 SF). Batter homered. Batter walked. Batter hit by pitch. Previous play reviewed, call confirmed, batter hit by pitch. Other challenged previous call, call stands, batter hit by pitch. Batter flied out, SF. Batter grounded out, SAC. Batter reached on catcher\'s interference. Batter struck out looking. 2 runs, 2 hits, 0 errors, 3 LOB.</td></tr></table>'
    return text


EXPECTED = dict(date='2025-02-14', teams=['Other', 'LSU'], runs=[0,2])


def counts(**changes):
    return dict(dict(AB=10, H=4, BB=2, SO=3, **{'2B':1, '3B':0, 'HR':1}, HBP=1, SF=1, SH=1, CI=1, PA=16), **changes)


class HittingTests(unittest.TestCase):
    def test_known_rates_and_interference(self):
        r = rates(counts())
        self.assertAlmostEqual(r['ISO'], .4)
        self.assertAlmostEqual(r['OBP'], .5)  # SH and CI do not enter OBP
        self.assertAlmostEqual(r['strikeout_rate'], 3/16)
        self.assertAlmostEqual(r['HR_per_PA'], 1/16)

    def test_missing_and_impossible_counts(self):
        for c in [counts(AB=None), counts(H=11), counts(SO=11), counts(BB=-1), counts(PA=15), counts(AB=True)]:
            with self.assertRaises(ValueError): rates(c)

    def test_zero_denominators_and_unknown_pa(self):
        self.assertTrue(all(v is None for v in rates({k:0 for k in counts()}).values()))
        r = rates(counts(PA=None, CI=None))
        self.assertEqual(r['ISO'], .4)
        self.assertIsNone(r['strikeout_rate'])
        self.assertIsNone(r['HR_per_PA'])

    def test_summary_game_multiplicity_not_cumulative_totals(self):
        text = '<table><tr><td>LOB - LSU 2. 2B - Name 2(21); Other, Jr.(9). HBP - Name 2; Other.</td></tr></table>'
        c = event_summary(text)
        self.assertEqual(c['2B'], 3)
        self.assertEqual(c['HBP'], 3)
        with self.assertRaises(ValueError): event_summary(text+text)

    def test_pitches_and_review_notes_are_not_extra_events(self):
        r = statcrew_team(fixture(), EXPECTED)
        self.assertEqual(r['counts']['SF'], 1)
        self.assertEqual(r['counts']['HBP'], 1)
        self.assertEqual(r['counts']['CI'], 1)
        self.assertEqual(r['counts']['PA'], 8)
        self.assertEqual(r['denominator_issues'], [])

    def test_bf_disagreement_blocks_contact_not_power(self):
        text = fixture().replace('<td>3</td><td>8</td>', '<td>3</td><td>7</td>')
        r = statcrew_team(text, EXPECTED)
        self.assertIsNone(r['counts']['PA'])
        self.assertTrue(r['denominator_issues'])
        self.assertIsNotNone(rates(r['counts'])['ISO'])
        self.assertIsNone(rates(r['counts'])['strikeout_rate'])

    def test_deleted_or_duplicated_scoring_event_fails(self):
        for replacement in ['', 'Batter doubled. Batter doubled.']:
            text = fixture().replace('Batter doubled (0-2 SF).', replacement)
            with self.assertRaises(ValueError): statcrew_team(text, EXPECTED)

    def test_missing_or_duplicate_inning_or_summary_fails(self):
        for text in [fixture().replace('Other 1st - ', 'Other 2nd - '),
                     fixture().replace('LSU 1st - ', 'Unknown 1st - '),
                     fixture()+fixture()[fixture().rindex('<table>'):],
                     fixture().replace('2B - Batter(10). ', '')]:
            with self.assertRaises(ValueError): statcrew_team(text, EXPECTED)

    def test_wrong_game_identity_fails(self):
        with self.assertRaises(ValueError): statcrew_team(fixture(),dict(EXPECTED, date='2025-02-15'))

    def test_cumulative_required_fields(self):
        fields = 'Player GP-GS AB H BB SO 2B 3B HR HBP SF SH'.split()
        values = ['Totals','10-10',10,4,2,3,1,0,1,1,1,1]
        text = '<table>'+tr(fields)+tr(values)+'</table>'
        self.assertEqual(cumulative_team(text)['HR'],1)
        with self.assertRaises((KeyError, ValueError)): cumulative_team(text.replace('<td>HR</td>','<td>OTHER</td>'))

    def test_cutoff_modes_and_postseason_exclusion(self):
        def game(gid, date, phase):
            return dict(game_id=gid, game_date=date, stage=phase, reciprocal_check='pass', team_a_id='lsu', team_b_id='other')
        games = [game('reg','2025-05-01','regular'), game('conf','2025-05-20','conference_tournament'),
                 game('ncaa','2025-05-23','regional'), game('late','2025-05-27','regular')]
        records = [dict(game_id=g['game_id'],issues=[],counts=counts()) for g in games]
        cutoff = dt.datetime(2025,5,28,12,tzinfo=dt.timezone.utc)
        reg = aggregate(records,games,'lsu',cutoff,['regular'])
        conf = aggregate(records,games,'lsu',cutoff,['regular','conference_tournament'])
        self.assertEqual(reg['eligible_game_ids'],['reg'])
        self.assertEqual(conf['eligible_game_ids'],['conf','reg'])
        self.assertEqual(conf['counts']['AB'],20)
        self.assertEqual(conf['rates'],reg['rates'])
        # Changing excluded postseason values cannot affect pre-cutoff rates.
        records[2]['counts'] = counts(AB=100,H=40,PA=106)
        self.assertEqual(aggregate(records,games,'lsu',cutoff,['regular']),reg)

    def test_missing_game_blocks_mode_and_duplicates_fail(self):
        game = dict(game_id='g',game_date='2025-05-01',stage='regular',reciprocal_check='pass',team_a_id='lsu',team_b_id='other')
        cutoff = dt.datetime(2025,5,28,12,tzinfo=dt.timezone.utc)
        row = dict(game_id='g',issues=['missing_field'],counts=None)
        for records in [[], [row]]:
            result = aggregate(records,[game],'lsu',cutoff,['regular'])
            self.assertFalse(result['complete']); self.assertIsNone(result['rates'])
        with self.assertRaises(ValueError): aggregate([row,row],[game],'lsu',cutoff,['regular'])

    def test_aggregate_rates_use_summed_denominators(self):
        games = [dict(game_id=str(i), game_date='2025-05-01',stage='regular',reciprocal_check='pass',team_a_id='lsu',team_b_id='other') for i in range(2)]
        records = [dict(game_id='0',issues=[],counts=counts()),dict(game_id='1',issues=[],counts=counts(AB=20,PA=26))]
        result = aggregate(records,games,'lsu',dt.datetime(2025,5,28,tzinfo=dt.timezone.utc),['regular'])
        self.assertAlmostEqual(result['rates']['ISO'],8/30)
        self.assertNotAlmostEqual(result['rates']['ISO'],(.4+.2)/2)


if __name__ == '__main__':
    unittest.main()
