"""Data-free guard checks for frozen confirmation."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import batting_confirmation as b


class ConfirmationTests(unittest.TestCase):
    def test_frozen_models_and_seasons(self):
        self.assertEqual(b.MODELS['guillen']['beta'],[0.25322391361463914])
        self.assertEqual(b.MODELS['walk_rate']['scale'],[0.022077761145654972])
        for m in b.MODELS.values():
            self.assertEqual(m['training_seasons'],[2021,2022,2023])
            self.assertEqual(m['n'],403)
        self.assertEqual(b.PROTOCOL['season'],2025)
        self.assertFalse(b.PROTOCOL['promoted'])

    def test_pair_symmetry_missing_and_flagged_fallback(self):
        ratings={'a':1600,'b':1500}
        for key in b.MODELS:
            fs={'a':dict(values={key:.25},flags=[]),'b':dict(values={key:.1},flags=[])}
            p=b.pair('a','b',ratings,fs,key)
            self.assertAlmostEqual(p+b.pair('b','a',ratings,fs,key),1)
            elo=b.pair('a','b',ratings,fs,key,'elo')
            self.assertGreater(p,elo)
            fs['a']['flags']=['count_discrepancy']
            self.assertEqual(b.pair('a','b',ratings,fs,key,'strict'),elo)
            fs['b']['values']=None
            self.assertEqual(b.pair('a','b',ratings,fs,key),elo)

    def test_stale_lock_rejected_before_scoring(self):
        with patch.object(b.common,'gates',return_value=[]), patch.object(b,'fingerprints',return_value={'new':'hash'}), patch.object(b.common,'read',return_value={'inputs':{'old':'hash'},'protocol':b.PROTOCOL}):
            with self.assertRaisesRegex(ValueError,'Stale forecast'):
                b.evaluate(Path('/unused'))

    def test_source_hash_and_scope_rejected(self):
        from datetime import date,datetime,timezone
        with tempfile.TemporaryDirectory() as tmp:
            raw=Path(tmp)
            (raw/'2025_obp.response').write_text('wrong bytes')
            b.common.write(raw/'2025_obp.json',{'status':200,'url':b.URL,'method':'POST',
                'form':[['statSeq','589']],'requested_season':2025,
                'requested_through_date':'2025-05-25','statistic':'obp','sha256':'wrong'})
            with patch.object(b,'scope',return_value=({},datetime(2025,5,28,tzinfo=timezone.utc),date(2025,5,25),{'obp':[('statSeq','589')]})):
                with self.assertRaisesRegex(ValueError,'provenance'): b.tables(raw)

    def test_stale_and_future_snapshot_rejected(self):
        from datetime import date,datetime,timezone
        for day in (date(2025,5,1),date(2025,5,27),date(2025,6,1)):
            with patch.object(b,'scope',return_value=({},datetime(2025,5,28,tzinfo=timezone.utc),day,{})):
                with self.assertRaisesRegex(ValueError,'Snapshot age'): b.tables(Path('/unused'))

    def test_unknown_features_do_not_become_zero(self):
        self.assertIsNone(b.walk_rate.row_features(None)[0])
        self.assertIsNone(b.guillen.row_features(None,None,None)[0])
        self.assertIsNone(b.walk_rate.row_features(dict(AB=0,BB=0,HBP=0,SF=0,SH=0))[0])


if __name__=='__main__': unittest.main()
