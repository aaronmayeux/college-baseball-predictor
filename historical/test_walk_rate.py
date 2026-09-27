"""Data-free checks of walk counts, chronology, probability and lock safety."""
import copy
from pathlib import Path
import tempfile
import unittest

import walk_rate as w


class WalkRate(unittest.TestCase):
    def rows(self):
        return [dict(season=2021+i%2, elo=.5, covered=True, flagged=False,
                     tie=False, differences={'walk_rate': x*.01},
                     outcome=int(i%10 < (8 if x>0 else 2)))
                for x in (-2,-1,1,2) for i in range(20)]

    def test_recorded_pa_includes_sacrifices_and_hbp(self):
        bat=dict(AB=800,BB=100,HBP=20,SF=10,SH=20)
        values,reasons=w.row_features(bat)
        self.assertEqual(reasons,[])
        self.assertEqual(values,dict(walk_rate=100/950))
        self.assertNotEqual(values['walk_rate'],100/930)
        self.assertEqual(w.row_features(dict(bat,BB=0))[0]['walk_rate'],0)

    def test_missing_or_invalid_counts_never_become_zeros(self):
        bat=dict(AB=800,BB=100,HBP=20,SF=10,SH=20)
        bad=[None,{k:0 for k in bat}]
        for key in bat:
            bad.append({k:v for k,v in bat.items() if k!=key})
            for value in (-1,None,1.5,True):
                bad.append(dict(bat,**{key:value}))
        for row in bad:
            with self.subTest(row=row):
                values,reasons=w.row_features(row)
                self.assertIsNone(values)
                self.assertTrue(reasons)

    def test_fit_training_scaling_and_reverse_matchup(self):
        rows=self.rows()
        original=copy.deepcopy(rows)
        model=w.fit(rows,'walk_rate')
        self.assertGreater(model['beta'][0],0)
        self.assertAlmostEqual(model['scale'][0],.00025**.5)
        self.assertEqual(model['training_seasons'],[2021,2022])
        self.assertEqual(rows,original)
        self.assertEqual(model,w.fit(rows,'walk_rate'))
        self.assertLess(w.metric(w.scored(rows,model),'challenger')['log_loss'],
                        w.metric(rows,'elo')['log_loss'])
        row=dict(rows[0],elo=.7)
        reverse=dict(row,elo=.3,differences={'walk_rate':-.01*-2})
        self.assertAlmostEqual(w.probability(row,model)+w.probability(reverse,model),1)

    def test_future_seasons_and_ties_cannot_train(self):
        for change in ({'season':2024},{'season':2025},{'season':2026},{'tie':True}):
            with self.assertRaises(ValueError):
                w.fit([dict(self.rows()[0],**change)],'walk_rate')

    def test_uncovered_rows_excluded_from_fit(self):
        rows=self.rows()
        model=w.fit(rows,'walk_rate')
        missing=dict(rows[0],covered=False,differences={},outcome=0)
        self.assertEqual(model,w.fit(rows+[missing],'walk_rate'))
        with self.assertRaises(ValueError): w.fit([missing],'walk_rate')
        with self.assertRaises(ValueError):
            w.fit([dict(rows[0],differences={'walk_rate':0})],'walk_rate')

    def test_entire_pair_falls_back_exactly(self):
        model=w.fit(self.rows(),'walk_rate')
        field={'a':dict(values=dict(walk_rate=.12),flags=[]),
               'b':dict(values=None,flags=['known_non_d1'])}
        row=w.build_row('a','b',.731,field)
        self.assertFalse(row['covered'])
        self.assertEqual(row['differences'],{})
        self.assertEqual(w.probability(row,model),.731)
        field['b']['values']=dict(walk_rate=.08)
        row=w.build_row('a','b',.731,field)
        self.assertTrue(row['covered'])
        self.assertEqual(w.probability(row,model,strict=True),.731)
        self.assertEqual(w.probability(row,dict(candidate='elo')),.731)

    def test_locks_reject_changes_and_preserve_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'lock.json'
            w.lock(path,{'protocol':w.PROTOCOL,'input_hash':'first'})
            before=path.read_bytes()
            w.lock(path,{'protocol':w.PROTOCOL,'input_hash':'first'})
            self.assertEqual(path.read_bytes(),before)
            with self.assertRaises(ValueError):
                w.lock(path,{'protocol':w.PROTOCOL,'input_hash':'changed'})
            self.assertEqual(path.read_bytes(),before)


if __name__=='__main__': unittest.main()
