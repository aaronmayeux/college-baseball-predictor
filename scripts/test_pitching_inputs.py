import copy
import datetime as dt
import unittest
from pitching_inputs import qualify_appearances, summarize, aggregate, structured_game


def pitcher(key='a', gs=1, pitches=20):
    return dict(match_key=key, name=key, game_started='1', pitch_count=pitches,
                counts=dict(outs=3, H=1, R=1, ER=1, SO=1, BB=1, BF=6,
                            AB=3, HBP=0, SF=0, SH=1, CI=1, GS=gs))


class PitchingTests(unittest.TestCase):
    def test_interference_in_bf(self):
        self.assertEqual(qualify_appearances([pitcher()], 6, 6)['BF'], 6)

    def test_components_fail_closed(self):
        p = pitcher(); p['counts']['CI'] = 0
        with self.assertRaises(ValueError): qualify_appearances([p], 6, 6)

    def test_opposing_and_team_checks(self):
        for pa, bf in [(5, 6), (6, 5)]:
            with self.assertRaises(ValueError): qualify_appearances([pitcher()], pa, bf)

    def test_explicit_start_not_lineup_or_order(self):
        apps = [pitcher('relief', 0), pitcher('starter', 1)]
        qualify_appearances(apps, 12, 12)
        result = {p['player_key']:p for p in summarize(apps)}
        self.assertEqual(result['relief']['observed_role'], 'relief_only')
        self.assertEqual(result['starter']['starts'], 1)

    def test_invalid_or_multiple_starts(self):
        for apps in [[pitcher(gs=0)], [pitcher(gs=2)], [pitcher('a'), pitcher('b')]]:
            with self.assertRaises(ValueError): qualify_appearances(apps, 6*len(apps), 6*len(apps))

    def test_missing_duplicate_and_bad_counts(self):
        for apps in [[], [pitcher(), pitcher()]]:
            with self.assertRaises(ValueError): qualify_appearances(apps, 0, 0)
        for value in [None, -1, True]:
            p = pitcher(); p['counts']['BF'] = value
            with self.assertRaises(ValueError): qualify_appearances([p], 6, 6)

    def test_mixed_role_and_missing_pitches(self):
        result = summarize([pitcher(), pitcher(gs=0, pitches=None)])[0]
        self.assertEqual((result['starts'], result['relief_appearances'], result['observed_role']), (1, 1, 'mixed'))
        self.assertIsNone(result['pitches'])
        self.assertEqual(result['known_pitches'], 20)
        self.assertEqual(result['rest_status'], 'unknown')

    def test_zero_out_appearance_retained(self):
        p = pitcher(); p['counts']['outs'] = 0
        qualify_appearances([p], 6, 6)
        self.assertIsNone(summarize([p])[0]['ERA'])
        self.assertEqual(summarize([p])[0]['appearances'], 1)

    def test_zero_bf_is_not_zero_quality(self):
        p = pitcher(); p['counts'] = dict.fromkeys(p['counts'], 0); p['counts']['GS'] = 1
        qualify_appearances([p], 0, 0)
        self.assertIsNone(summarize([p])[0]['strikeout_minus_walk_rate'])

    def test_structured_adapter_and_missing_interference(self):
        from unittest.mock import patch
        p = pitcher(); p['raw'] = {'catchersInterferenceAllowed': '1'}
        ours = dict(name='School', totals={'pitching': {'battersFaced': '6'}})
        other = dict(name='Opponent', totals={'hitting': dict(atBats='3', walks='1', hitByPitch='0',
            sacrificeFlies='0', sacrificeHits='1', reachedOnCatchersInteference='1')})
        data = {'boxscore': {'boxscore': {'one': {'homeTeam': ours, 'visitingTeam': other}}}}
        original = copy.deepcopy(p)
        with patch('pitching_inputs.payload', return_value=data):
            players, check = structured_game('', 'url', {'team_name': 'School'}, [p])
            self.assertEqual(check['opponent_PA'], 6)
            self.assertEqual(p, original)
            del other['totals']['hitting']['reachedOnCatchersInteference']
            with self.assertRaises(KeyError): structured_game('', 'url', {'team_name': 'School'}, [p])

    def test_rates_sum_counts_before_dividing(self):
        a = pitcher(); b = pitcher(gs=0)
        b['counts'].update(BF=12, SO=4, BB=0)
        result = summarize([a, b])[0]
        self.assertAlmostEqual(result['strikeout_minus_walk_rate'], 4/18)
        self.assertEqual(result['ERA'], 9)

    def test_cutoffs_missing_game_and_season_gate(self):
        def game(gid, date, phase):
            return dict(game_id=gid, game_date=date, stage=phase, reciprocal_check='pass',
                        team_a_id='wn:LSU', team_b_id='other')
        cutoff = dt.datetime.fromisoformat('2025-05-28T12:00:00+00:00')
        games = [game('r', '2025-05-24', 'regular'), game('c', '2025-05-24', 'conference_tournament'),
                 game('late', '2025-05-27', 'regular')]
        records = [dict(game_id=g['game_id'], issues=[], pitchers=[pitcher()]) for g in games]
        result = aggregate(records, games, 'wn:LSU', cutoff, ['regular'], True)
        self.assertEqual(result['eligible_game_ids'], ['r'])
        self.assertTrue(result['complete'])
        for rows, ok in [(records[1:], True), (records, False)]:
            self.assertIsNone(aggregate(rows, games, 'wn:LSU', cutoff, ['regular'], ok)['players'])
        bad = copy.deepcopy(records); bad[0]['issues'] = ['bad BF']
        self.assertFalse(aggregate(bad, games, 'wn:LSU', cutoff, ['regular'], True)['complete'])
        with self.assertRaises(ValueError): aggregate(records+records, games, 'wn:LSU', cutoff, ['regular'], True)


if __name__ == '__main__': unittest.main()
