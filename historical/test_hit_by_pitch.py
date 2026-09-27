"""Data-free checks of hit-by-pitch counts, chronology, probability and lock safety."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io

import hit_by_pitch as w


class HitByPitch(unittest.TestCase):
    def rows(self):
        return [dict(season=2021+i%2, elo=.5, covered=True, flagged=False,
                     tie=False, differences={'hit_by_pitch': x*.01},
                     outcome=int(i%10 < (8 if x>0 else 2)))
                for x in (-2,-1,1,2) for i in range(20)]

    def test_recorded_pa_includes_sacrifices_and_hbp(self):
        bat=dict(AB=800,BB=100,HBP=20,SF=10,SH=20)
        values,reasons=w.row_features(bat)
        self.assertEqual(reasons,[])
        self.assertEqual(values,dict(hit_by_pitch=20/950))
        self.assertNotEqual(values['hit_by_pitch'],20/930)
        self.assertEqual(w.row_features(dict(bat,HBP=0))[0]['hit_by_pitch'],0)

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
        model=w.fit(rows,'hit_by_pitch')
        self.assertGreater(model['beta'][0],0)
        self.assertAlmostEqual(model['scale'][0],.00025**.5)
        self.assertEqual(model['training_seasons'],[2021,2022])
        self.assertEqual(rows,original)
        self.assertEqual(model,w.fit(rows,'hit_by_pitch'))
        self.assertLess(w.metric(w.scored(rows,model),'challenger')['log_loss'],
                        w.metric(rows,'elo')['log_loss'])
        row=dict(rows[0],elo=.7)
        reverse=dict(row,elo=.3,differences={'hit_by_pitch':-.01*-2})
        self.assertAlmostEqual(w.probability(row,model)+w.probability(reverse,model),1)

    def test_future_seasons_and_ties_cannot_train(self):
        for change in ({'season':2024},{'season':2025},{'season':2026},{'tie':True}):
            with self.assertRaises(ValueError):
                w.fit([dict(self.rows()[0],**change)],'hit_by_pitch')

    def test_uncovered_rows_excluded_from_fit(self):
        rows=self.rows()
        model=w.fit(rows,'hit_by_pitch')
        missing=dict(rows[0],covered=False,differences={},outcome=0)
        self.assertEqual(model,w.fit(rows+[missing],'hit_by_pitch'))
        with self.assertRaises(ValueError): w.fit([missing],'hit_by_pitch')
        with self.assertRaises(ValueError):
            w.fit([dict(rows[0],differences={'hit_by_pitch':0})],'hit_by_pitch')

    def test_entire_pair_falls_back_exactly(self):
        model=w.fit(self.rows(),'hit_by_pitch')
        field={'a':dict(values=dict(hit_by_pitch=.12),flags=[]),
               'b':dict(values=None,flags=['known_non_d1'])}
        row=w.build_row('a','b',.731,field)
        self.assertFalse(row['covered'])
        self.assertEqual(row['differences'],{})
        self.assertEqual(w.probability(row,model),.731)
        field['b']['values']=dict(hit_by_pitch=.08)
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
