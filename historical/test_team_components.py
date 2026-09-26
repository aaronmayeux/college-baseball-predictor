"""Data-free regression checks for leakage, fitting and exact Elo fallback."""
import copy
import unittest
import team_components as c


class Components(unittest.TestCase):
    def rows(self):
        return [dict(season=2021+i%2,elo=.5,covered=True,flagged=False,tie=False,
                     differences=dict(obp=x*.01,era=x*.5),outcome=int(i%10 < (8 if x>0 else 2)))
                for x in (-2,-1,1,2) for i in range(20)]

    def test_fit_and_symmetry(self):
        rows=self.rows()
        for candidate in c.CANDIDATES:
            model=c.fit(rows,candidate)
            self.assertLess(c.metric(c.scored(rows,model),'challenger')['log_loss'],c.metric(rows,'elo')['log_loss'])
            row=rows[0]
            reverse=dict(row,elo=1-row['elo'],differences={k:-v for k,v in row['differences'].items()})
            self.assertAlmostEqual(c.probability(row,model)+c.probability(reverse,model),1)
            self.assertEqual(model['training_seasons'],[2021,2022])

    def test_exact_fallback(self):
        model=c.fit(self.rows(),'both')
        row=dict(self.rows()[0],elo=.731,covered=False,differences={})
        self.assertEqual(c.probability(row,model),.731)
        row=dict(self.rows()[0],elo=.731,flagged=True)
        self.assertEqual(c.probability(row,model,strict=True),.731)
        self.assertEqual(c.probability(row,dict(candidate='elo')),.731)

    def test_future_and_tied_training_rejected(self):
        for changed in ({'season':2024},{'season':2025},{'season':2026},{'tie':True}):
            with self.assertRaises(ValueError): c.fit([dict(self.rows()[0],**changed)],'obp')

    def test_missing_training_not_zero_imputed(self):
        rows=self.rows()
        model=c.fit(rows,'both')
        other=c.fit(rows+[dict(rows[0],covered=False,differences={},outcome=0)],'both')
        self.assertEqual(model,other)
        with self.assertRaises(ValueError): c.fit([dict(rows[0],covered=False)],'obp')

    def test_training_only_scaling(self):
        rows=self.rows()
        saved=copy.deepcopy(rows)
        model=c.fit(rows,'obp')
        self.assertAlmostEqual(model['scale'][0],(.00025)**.5)
        self.assertEqual(rows,saved)
        self.assertEqual(model,c.fit(rows,'obp'))

    def test_invalid_denominators_and_records(self):
        bat=dict(G=30,AB=900,H=240,BB=100,HBP=10,SF=10,**{'W-L':'20-10'},reclassifying=False)
        pitch=dict(G=30,outs=750,ER=80,**{'W-L':'20-10'},reclassifying=False)
        values,reasons=c.row_features(bat,pitch,[])
        self.assertFalse(reasons)
        self.assertAlmostEqual(values['obp'],350/1020)
        self.assertAlmostEqual(values['era'],-27*80/750)
        for b,p in [(None,pitch),(bat,dict(pitch,outs=0)),(dict(bat,G=10),pitch),
                    (dict(bat,reclassifying=True),pitch), (dict(bat,AB=0,BB=0,HBP=0,SF=0),pitch)]:
            values,reasons=c.row_features(b,p,[])
            self.assertIsNone(values)
            self.assertTrue(reasons)
        self.assertIsNone(c.row_features(bat,pitch,['hits_exceed_at_bats'])[0])

    def test_matchup_fallback_not_partial_adjustment(self):
        features={'a':dict(values=dict(obp=.4,era=-3),flags=[]),'b':dict(values=None,flags=[])}
        row=c.build_row('a','b',.6,features)
        self.assertFalse(row['covered'])
        self.assertEqual(row['differences'],{})


if __name__=='__main__': unittest.main()
