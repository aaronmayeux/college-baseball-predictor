"""Data-free checks of Guillen counts, chronology, probability and lock safety."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io

import guillen as w


class Guillen(unittest.TestCase):
    def rows(self):
        return [dict(season=2021+i%2, elo=.5, covered=True, flagged=False,
                     tie=False, differences={'guillen': x*.01},
                     outcome=int(i%10 < (8 if x>0 else 2)))
                for x in (-2,-1,1,2) for i in range(20)]

    def source_rows(self):
        base=dict(G=50,**{'W-L':'30-20'},reclassifying=False)
        return dict(base,HR=60),dict(base,R=400),base

    def test_guillen_proxy_and_zero_homers(self):
        hr,runs,base=self.source_rows()
        self.assertEqual(w.row_features(hr,runs,base),({'guillen':.24},[]))
        self.assertEqual(w.row_features(dict(hr,HR=0),runs,base)[0],{'guillen':0})

    def test_invalid_counts_records_and_missing_rows_fall_back(self):
        hr,runs,base=self.source_rows()
        for h,r,b in [(None,runs,base),(hr,None,base),(hr,runs,None),
                      (dict(hr,HR=-1),runs,base),(dict(hr,HR=401),runs,base),
                      (dict(hr,HR=True),runs,base),(hr,dict(runs,R=0),base),
                      (dict(hr,G=49),runs,base),(dict(hr,reclassifying=True),runs,base)]:
            values,reasons=w.row_features(h,r,b)
            self.assertIsNone(values)
            self.assertTrue(reasons)

    def test_fixed_positive_multiplier_cancels_under_rms_scaling(self):
        rows=self.rows()
        scaled=[dict(r,differences={'guillen':1.6*r['differences']['guillen']}) for r in rows]
        a,b=w.fit(rows,'guillen'),w.fit(scaled,'guillen')
        for r,t in zip(rows,scaled):
            self.assertAlmostEqual(w.probability(r,a),w.probability(t,b),places=14)

    def test_fit_training_scaling_and_reverse_matchup(self):
        rows=self.rows()
        original=copy.deepcopy(rows)
        model=w.fit(rows,'guillen')
        self.assertGreater(model['beta'][0],0)
        self.assertAlmostEqual(model['scale'][0],.00025**.5)
        self.assertEqual(model['training_seasons'],[2021,2022])
        self.assertEqual(rows,original)
        self.assertEqual(model,w.fit(rows,'guillen'))
        self.assertLess(w.metric(w.scored(rows,model),'challenger')['log_loss'],
                        w.metric(rows,'elo')['log_loss'])
        row=dict(rows[0],elo=.7)
        reverse=dict(row,elo=.3,differences={'guillen':-.01*-2})
        self.assertAlmostEqual(w.probability(row,model)+w.probability(reverse,model),1)

    def test_future_seasons_and_ties_cannot_train(self):
        for change in ({'season':2024},{'season':2025},{'season':2026},{'tie':True}):
            with self.assertRaises(ValueError):
                w.fit([dict(self.rows()[0],**change)],'guillen')

    def test_uncovered_rows_excluded_from_fit(self):
        rows=self.rows()
        model=w.fit(rows,'guillen')
        missing=dict(rows[0],covered=False,differences={},outcome=0)
        self.assertEqual(model,w.fit(rows+[missing],'guillen'))
        with self.assertRaises(ValueError): w.fit([missing],'guillen')
        with self.assertRaises(ValueError):
            w.fit([dict(rows[0],differences={'guillen':0})],'guillen')

    def test_entire_pair_falls_back_exactly(self):
        model=w.fit(self.rows(),'guillen')
        field={'a':dict(values=dict(guillen=.12),flags=[]),
               'b':dict(values=None,flags=['known_non_d1'])}
        row=w.build_row('a','b',.731,field)
        self.assertFalse(row['covered'])
        self.assertEqual(row['differences'],{})
        self.assertEqual(w.probability(row,model),.731)
        field['b']['values']=dict(guillen=.08)
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

    def test_failed_selection_stops_before_validation_or_advancement(self):
        training=self.rows()
        selection=[dict(r,season=2023,outcome=1-r['outcome']) for r in training]
        # Deliberately incomplete later row must never reach prediction/scoring.
        future={'season':2024}
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            w.common.write(out/'prepared.json',dict(inputs={'source':'fixed'},
                protocol=w.PROTOCOL,samples=training+selection+[future],coverage=[]))
            with patch.object(w,'OUT',out), patch.object(w.common,'gates',return_value=[]), \
                 patch.object(w,'fingerprints',return_value={'source':'fixed'}), \
                 patch.object(w.seeds,'load',side_effect=AssertionError('Advanced after rejection')), \
                 redirect_stdout(io.StringIO()):
                w.evaluate(Path(tmp))
            report=w.common.read(out/'report.json')
            self.assertEqual(report['decision'],'closed_at_2023_selection')
            self.assertFalse(report['validation_scored'])
            self.assertEqual(report['selection']['winner'],'elo')
            self.assertTrue((out/'selection_lock.json').exists())
            self.assertFalse((out/'forecast_lock.json').exists())
            self.assertFalse((out/'predictions.json').exists())


if __name__=='__main__': unittest.main()
