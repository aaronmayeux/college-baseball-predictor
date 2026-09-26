"""External-data-free gates for historical advancement evaluation."""
import copy
import itertools
import math
import unittest

from tournament.engine import next_game
from regional_validation import champion, regions, score, summary


def games(bits):
    entrants=['a','b','c','d']; results=[]; rows=[]
    while (pair:=next_game(entrants,results)) is not None:
        a,b=pair
        win,lose=(a,b) if bits[len(results)] else (b,a)
        day=(1,1,2,2,3,3,4)[len(results)]
        rows.append(dict(game_id=str(len(results)),a=win,b=lose,runs_a=5,runs_b=2,
                         game_date=f'2024-06-0{day}',tie=False,reciprocal_check='pass',stage='regional'))
        results.append((win,lose))
    return rows,results[-1][0]


class RegionalTests(unittest.TestCase):
    def test_all_elimination_paths_and_row_order(self):
        for bits in itertools.product((0,1),repeat=7):
            rows,expected=games(bits)
            self.assertEqual(champion(['a','b','c','d'],rows)['winner'],expected)
            self.assertEqual(champion(['a','b','c','d'],list(reversed(rows)))['winner'],expected)

    def test_incomplete_duplicate_tie_crossgroup_and_bad_status(self):
        rows,_=games([1]*7)
        variants=[rows[:-1],rows+[rows[0]]]
        for changes in (dict(tie=True),dict(runs_a=2),dict(a='outside'),dict(reciprocal_check='fail'),dict(timing_review=True)):
            bad=copy.deepcopy(rows);bad[0].update(changes);variants.append(bad)
        for variant in variants:
            with self.assertRaises(ValueError):
                champion(['a','b','c','d'],variant)

    def test_dates_cannot_reverse_team_history(self):
        rows,_=games([1]*7)
        rows[-1]['game_date']='2024-05-01'
        with self.assertRaises(ValueError):
            champion(['a','b','c','d'],rows)

    def test_opening_broadcast_order_can_reverse(self):
        rows,expected=games([1]*7)
        rows[0]['game_date']='2024-06-02'
        self.assertEqual(champion(['a','b','c','d'],rows)['winner'],expected)

    def test_reset_topology_resolves_same_day_results(self):
        rows,expected=games([1,1,1,1,1,0,1])
        rows[-1]['game_date']=rows[-2]['game_date']
        self.assertEqual(champion(['a','b','c','d'],list(reversed(rows)))['winner'],expected)

    def test_fair_multiclass_scores(self):
        result=score(dict.fromkeys('abcd',.25),'a')
        self.assertAlmostEqual(result['log_loss'],math.log(4))
        self.assertEqual(result['brier'],.75)
        self.assertEqual(result['accuracy'],.25)
        with self.assertRaises(ValueError):
            score(dict.fromkeys('abcd',.3),'a')

    def test_seed_groups_and_duplicate_identity(self):
        rows=[dict(season=2024,regional=str(g),regional_seed=s,team_id=f'{g}-{s}') for g in range(16) for s in (1,2,3,4)]
        self.assertEqual(regions(rows,2024)[0]['teams'],['0-1','0-4','0-2','0-3'])
        rows[0]['team_id']=rows[1]['team_id']
        with self.assertRaises(ValueError):
            regions(rows,2024)

    def test_paired_cluster_bootstrap_identical_predictions(self):
        probs=dict.fromkeys('abcd',.25)
        row=dict(winner='a',probabilities={m:probs for m in ('elo','challenger','seed')},scores={m:score(probs,'a') for m in ('elo','challenger','seed')})
        result=summary([row]*16)
        self.assertEqual(result['paired_delta'],dict(log_loss=0,brier=0))
        self.assertEqual(result['exploratory_95pct_paired_regional_bootstrap'],dict(log_loss=[0,0],brier=[0,0]))
        self.assertEqual(result['calibration']['elo'][0]['teams'],64)


if __name__=='__main__':
    unittest.main()
