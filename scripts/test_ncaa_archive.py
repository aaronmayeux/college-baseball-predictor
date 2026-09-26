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


if __name__ == '__main__':
    unittest.main()
