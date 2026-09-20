"""Synthetic coverage guards; no external evidence or network required."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from audit_player_coverage import inspect_summary, outs, read_or_fetch, sample_dates


class CoverageTests(unittest.TestCase):
    def test_baseball_innings(self):
        self.assertEqual(outs('6.2'),20)
        self.assertEqual(outs('0.0'),0)
        for bad in ('6.3','6.20','-1','--'):
            with self.assertRaises(ValueError): outs(bad)

    def test_wrong_season_and_identity(self):
        data={'header':{'id':'1','season':{'year':2026}}}
        self.assertEqual(inspect_summary(data,'1',2025)['status'],'identity_or_season_rejected')
        self.assertEqual(inspect_summary(data,'2',2026)['status'],'identity_or_season_rejected')

    def test_empty_box_is_not_complete(self):
        data={'header':{'id':'1','season':{'year':2025},'competitions':[{'date':'2025-05-01'}]},'boxscore':{'players':[]}}
        result=inspect_summary(data,'1',2025)
        self.assertEqual(result['teams'],[])
        self.assertEqual(result['play_records'],0)

    def test_missing_fields_are_not_zero(self):
        data={'header':{'id':'1','season':{'year':2025},'competitions':[{'date':'2025-05-01'}]},
              'boxscore':{'players':[{'team':{'id':'t'},'statistics':[{'type':'pitching','labels':['IP','PC'],
                  'athletes':[{'athlete':{'id':'p'},'stats':['0.0','--']}]}]}]}}
        group=inspect_summary(data,'1',2025)['teams'][0]['groups']['pitching']
        self.assertEqual(group['outs'],0)
        self.assertEqual(group['positive_pitch_counts'],0)
        self.assertNotIn('BF',group['numeric_cells'])

    def test_hash_and_url_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'x.json';p.write_text('{}')
            (root/'x.json.meta.json').write_text(json.dumps({'url':'u','http_status':200,'sha256':hashlib.sha256(b'{}').hexdigest()}))
            self.assertEqual(read_or_fetch(root,'x.json','u')[0],{})
            with self.assertRaises(ValueError): read_or_fetch(root,'x.json','wrong')
            p.write_text('{"changed":true}')
            with self.assertRaises(ValueError): read_or_fetch(root,'x.json','u')

    def test_fixed_date_design(self):
        for year in range(2021,2026):
            dates=list(sample_dates(year))
            self.assertEqual(len(dates),4)
            self.assertTrue(all(d.day<=7 and d.weekday() in (1,4) for d in dates))


if __name__=='__main__': unittest.main()
