"""Data-free schedule chronology, fitting and fallback regression checks."""
from copy import deepcopy
from datetime import datetime
import unittest

import schedule_components as s


class ScheduleComponents(unittest.TestCase):
    def game(self,ident,day,a='a',b='b',ra=3,rb=1,stage='regular_season'):
        return dict(game_id=ident,game_date=day,a=a,b=b,runs_a=ra,runs_b=rb,tie=ra==rb,
                    stage=stage,reciprocal_check='pass',timing_review=False)

    def test_future_phase_and_lag_exclusion(self):
        initial=s.State()
        safe=self.game('safe','2023-05-20')
        games=[safe,self.game('after_snapshot','2023-05-21'),
               self.game('ncaa','2023-05-19',stage='regional'),
               dict(self.game('conflict','2023-05-18'),reciprocal_check='fail'),
               dict(self.game('unknown','2023-05-18'),game_date=None)]
        cutoff=datetime.fromisoformat('2023-05-25T12:00:00+00:00')
        state,eligible=s.update_through(initial,games,cutoff,['regular_season'],'2023-05-20')
        self.assertEqual([g['game_id'] for g in eligible],['safe'])
        self.assertEqual(state.n['a'],1)
        self.assertFalse(initial.n)
        early=datetime.fromisoformat('2023-05-21T12:00:00+00:00')
        _,eligible=s.update_through(initial,[safe],early,['regular_season'],'2023-05-20')
        self.assertEqual(eligible,[])

    def test_same_day_order_and_snapshot_separation(self):
        games=[self.game('one','2023-05-20'),self.game('two','2023-05-20',ra=1,rb=3),
               self.game('late','2023-05-22')]
        cutoff=datetime.fromisoformat('2023-05-25T12:00:00+00:00')
        initial=s.State()
        first,_=s.update_through(initial,games,cutoff,['regular_season'],'2023-05-20')
        second,_=s.update_through(initial,list(reversed(games)),cutoff,['regular_season'],'2023-05-20')
        self.assertEqual(dict(first.r),dict(second.r))
        full,_=s.update_through(initial,games,cutoff,['regular_season'],'2023-05-25')
        self.assertEqual(first.r['a'],1500)
        self.assertGreater(full.r['a'],first.r['a'])
        full.regress()
        self.assertGreater(full.r['a'],1500)  # Late eligible results survive into next year.
        self.assertEqual(first.r['a'],1500)  # Snapshot did not mutate.

    def test_repeated_opponents_are_game_weighted(self):
        state=s.State(); state.r.update(b=1600,c=1400);state.n.update(b=15,c=5)
        games=[self.game(str(i),'2023-05-20',b='b' if i<15 else 'c') for i in range(20)]
        feature=s.schedule_feature('a',games,state)
        self.assertEqual(feature['value'],1550)
        self.assertEqual(feature['unique_opponents'],2)
        self.assertEqual(feature['games'],20)
        self.assertIsNone(s.schedule_feature('a',games[:19],state)['value'])
        state.n['c']=0
        self.assertIsNone(s.schedule_feature('a',games,state)['value'])
        self.assertIn('missing_opponent_rating',s.schedule_feature('a',games,state)['reasons'])

    def rows(self):
        return [dict(season=2021+i%2,elo=.5,covered=True,flagged=False,tie=False,
                     differences=dict(obp=x*.01,era=x*.4,schedule=x*15+(i%3-1)*10),
                     outcome=int(i%10<(8 if x>0 else 2))) for x in (-2,-1,1,2) for i in range(20)]

    def test_fit_symmetry_and_training_scope(self):
        rows=self.rows(); original=deepcopy(rows)
        model=s.fit(rows)
        self.assertEqual(model['training_seasons'],[2021,2022])
        self.assertEqual(rows,original)
        self.assertLess(s.metric(s.components.scored(rows,model),'challenger')['log_loss'],s.metric(rows,'elo')['log_loss'])
        row=rows[0]
        reverse=dict(row,elo=1-row['elo'],differences={k:-v for k,v in row['differences'].items()})
        self.assertAlmostEqual(s.components.probability(row,model)+s.components.probability(reverse,model),1)
        for year in (2024,2025,2026):
            with self.assertRaises(ValueError): s.fit([dict(row,season=year)])
        with self.assertRaises(ValueError): s.fit([dict(row,tie=True)])

    def test_missing_inputs_use_exact_elo(self):
        features={'a':dict(values=dict(obp=.4,era=-3,schedule=1550),flags=[]),
                  'b':dict(values=None,flags=[])}
        row=s.pair('a','b',.712,features)
        self.assertFalse(row['covered'])
        self.assertEqual(s.components.probability(row,dict(candidate='new')),.712)
        model=s.fit(self.rows(),['schedule'],'schedule_only')
        flagged=dict(self.rows()[0],elo=.712,flagged=True)
        self.assertEqual(s.components.probability(flagged,model,strict=True),.712)

    def test_solver_agrees_with_legacy_two_feature_fit(self):
        rows=self.rows()
        actual=s.fit(rows,['obp','era'],'both')
        expected=s.components.fit(rows,'both')
        self.assertEqual(actual,expected)

    def test_selection_requires_both_scores(self):
        # Negative predictor is clearly worse; selection cannot rescue it by accuracy.
        rows=self.rows()
        good=s.fit(rows)
        selected,_=s.choose(rows,good)
        self.assertTrue(selected)
        bad=dict(good,beta=[-x for x in good['beta']])
        self.assertFalse(s.choose(rows,bad)[0])
        self.assertFalse(s.choose(rows,dict(candidate='elo'))[0])


if __name__=='__main__': unittest.main()
