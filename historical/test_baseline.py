"""Meaningful leakage/order regression tests; no network."""
import copy,datetime as dt,unittest
from baseline import State,daily,frozen
from eligibility import available_at,reject
from reconcile import internal

def game(day,score=(3,1),ident='x',a='a',b='b',stage='regular_season'):
 return {'season':2024,'game_date':day,'game_id':ident,'a':a,'b':b,'runs_a':score[0],'runs_b':score[1],'tie':score[0]==score[1],'stage':stage,'reciprocal_check':'pass','timing_review':False}
class LeakageTests(unittest.TestCase):
 def test_future_results_cannot_change_earlier_predictions(self):
  gs=[game('2024-04-01',ident='a'),game('2024-04-02',ident='b'),game('2024-04-04',ident='c')];other=copy.deepcopy(gs);other[-1]['runs_a']=0
  a=daily(gs,State());b=daily(other,State())
  self.assertEqual([r['elo'] for r in a],[r['elo'] for r in b])
  self.assertEqual(a[1]['elo'],.5) # prior day still unavailable
  self.assertGreater(a[2]['elo'],.5)
 def test_same_day_order_invariance(self):
  a=game('2024-04-01',ident='a');b=game('2024-04-01',(0,5),ident='b');c=game('2024-04-03',ident='c')
  x=daily([a,b,c],State());y=daily([b,a,c],State())
  self.assertEqual({r['game_id']:r['elo'] for r in x},{r['game_id']:r['elo'] for r in y})
 def test_frozen_excludes_conference_and_ncaa_results(self):
  gs=[game('2024-05-18'),game('2024-05-23',(10,0),'conf',stage='conference_tournament'),game('2024-05-31',(1,0),'reg',stage='regional'),game('2024-06-01',(1,0),'reg2',stage='regional')]
  cut=dt.datetime.fromisoformat('2024-05-29T12:00:00+00:00');x=frozen(gs,State(),'regular_only',cut,['regular_season'])
  gs[1]['runs_a']=0;gs[1]['runs_b']=10;gs[2]['runs_a']=0;gs[2]['runs_b']=1
  y=frozen(gs,State(),'regular_only',cut,['regular_season'])
  self.assertEqual([r['elo'] for r in x],[r['elo'] for r in y]);self.assertEqual(x[0]['elo'],x[1]['elo'])
 def test_cutoff_boundary_and_quarantine(self):
  g=game('2024-05-27');cut=dt.datetime.fromisoformat('2024-05-29T00:00:00+00:00')
  self.assertIsNone(reject(g,cut,['regular_season']));self.assertIsNotNone(reject(g,cut-dt.timedelta(microseconds=1),['regular_season']))
  g['timing_review']=True;self.assertIsNotNone(reject(g,cut,['regular_season']))
 def test_ties_and_zero_sum_updates(self):
  s=State();s.update([game('2024-04-01',(1,1))]);self.assertEqual(s.r['a'],1500);self.assertEqual(s.r['b'],1500)
  s.update([game('2024-04-02')]);self.assertAlmostEqual(s.r['a']+s.r['b'],3000)
 def test_identity_rename_and_distinct_schools(self):
  self.assertEqual(internal('Houston-Baptist'),internal('Houston-Christian'));self.assertEqual(internal('Dixie-State'),internal('Utah-Tech'));self.assertNotEqual(internal('Houston'),internal('Houston-Christian'))
if __name__=='__main__':unittest.main()
