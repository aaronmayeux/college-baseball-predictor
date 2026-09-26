import unittest
from datetime import date
from audit_ncaa_archive import parse_report

OBP = '''NCAA Baseball
Division IOn Base Percentage
Through Games 05/26/2024
"Rank","Name","G","W-L","AB","H","BB","HBP","SF","SH","PCT"
"1","Example","2","1-1","10","3","2","1","1","0","0.429"
'''
ERA = '''NCAA Baseball
Division IEarned Run Average
Through Games 05/26/2024
"Rank","Name","G","W-L","IP","R","ER","ERA"
"1","Example","2","1-1","8.2","5","3","3.12"
'''


class NCAAArchiveTests(unittest.TestCase):
    def parse(self, text=OBP, kind='obp'):
        return parse_report(text, kind, 2024, date(2024, 5, 26))

    def test_rates_use_counts_and_baseball_outs(self):
        self.assertEqual(self.parse()[1], [])
        rows, issues = self.parse(ERA, 'era')
        self.assertEqual((rows[0]['outs'], issues), (26, []))

    def test_wrong_year_date_division_or_statistic_rejected(self):
        for old, new in [('2024', '2025'), ('05/26', '06/26'), ('Division IOn', 'Division IIOn'), ('On Base Percentage', 'Other')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                self.parse(OBP.replace(old, new))

    def test_invalid_innings_and_missing_counts_rejected(self):
        with self.assertRaises(ValueError):
            self.parse(ERA.replace('8.2', '8.3'), 'era')
        with self.assertRaises(ValueError):
            self.parse(OBP.replace('"10"', '""'))

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            self.parse(OBP + OBP.splitlines()[-1] + '\n')

    def test_reclassification_retained_analytics_ignored(self):
        text = OBP + 'Reclassifying\n' + OBP.splitlines()[-1].replace('Example', 'New School').replace('"1",', '"NR",', 1) + '\n<script type="text/javascript">\nnot data\n'
        rows, issues = self.parse(text)
        self.assertEqual(len(rows), 2)
        self.assertFalse(rows[0]['reclassifying'])
        self.assertTrue(rows[1]['reclassifying'])
        self.assertEqual(issues, [])

    def test_inconsistent_record_or_rate_reported(self):
        self.assertIn(['Example', 'record_game_count'], self.parse(OBP.replace('1-1', '2-1'))[1])
        self.assertIn(['Example', 'display_rate_mismatch'], self.parse(OBP.replace('0.429', '0.430'))[1])

    def test_empty_or_malformed_report_rejected(self):
        with self.assertRaises(ValueError):
            self.parse('\n'.join(OBP.splitlines()[:-1]))
        with self.assertRaises(ValueError):
            self.parse(OBP + 'unexpected line\n')

class MenuTests(unittest.TestCase):
    def menu(self):
        return '''<input type="hidden" name="academicYear" value=2024>
var div1txt = new Array("Through Games 06/24/2024(Final)","Through Games 05/26/2024");
var div1val = new Array("108","90");'''

    def test_menu_ids_come_from_paired_labels(self):
        from audit_ncaa_archive import menu_dates
        self.assertEqual(menu_dates(self.menu(), 2024)[1], (date(2024, 5, 26), '90', False))

    def test_menu_mismatches_rejected(self):
        from audit_ncaa_archive import menu_dates
        for text in [self.menu().replace('value=2024', 'value=2023'),
                     self.menu().replace(',"90"', ''),
                     self.menu().replace('"90"', '"108"'),
                     self.menu().replace('05/26/2024', '05/26/2023')]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                menu_dates(text, 2024)

    def test_explicit_no_rankings_is_not_valid_empty_dataset(self):
        from audit_ncaa_archive import NoRankings
        text = '\n'.join(OBP.splitlines()[:-1]) + '\nNo rankings for this category\n'
        with self.assertRaises(NoRankings):
            parse_report(text, 'obp', 2024, date(2024, 5, 26))
        with self.assertRaises(ValueError):
            parse_report(OBP + 'No rankings for this category\n', 'obp', 2024, date(2024, 5, 26))

    def test_latest_eligible_selection_checks_provenance(self):
        import tempfile
        import json
        import hashlib
        from pathlib import Path
        from datetime import datetime
        from audit_ncaa_archive import selected_date
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp)
            (raw / '2024_menu.html').write_text(self.menu())
            meta = dict(url='https://web1.ncaa.org/stats/StatsSrv/rankings', method='POST',
                        form=dict(sportCode='MBA', academicYear='2024', doWhat='display'),
                        sha256=hashlib.sha256(self.menu().encode()).hexdigest())
            (raw / '2024_menu.json').write_text(json.dumps(meta))
            cutoff = datetime.fromisoformat('2024-05-29T12:00:00+00:00')
            self.assertEqual(selected_date(raw, 2024, cutoff), (date(2024, 5, 26), '90'))
            with self.assertRaises(ValueError):
                selected_date(raw, 2024, cutoff, date(2024, 6, 24))
            with self.assertRaises(ValueError):
                selected_date(raw, 2024, datetime.fromisoformat('2024-05-27T12:00:00+00:00'))
            (raw / '2024_menu.html').write_text(self.menu()+'changed')
            with self.assertRaises(ValueError):
                selected_date(raw, 2024, cutoff)


if __name__ == '__main__':
    unittest.main()
