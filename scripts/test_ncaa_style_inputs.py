"""Data-free checks of the count schemas used by the Guillen experiment."""
import unittest
from ncaa_style_inputs import parse


class StyleCounts(unittest.TestCase):
    def report(self):
        return '\n'.join(['NCAA Baseball','Division IHome Runs','Through Games 05/28/2023',
            '"Rank","Name","G","W-L","HR"','"1","Example","50","30-20","60"'])

    def test_valid_counts_and_reclassifying_flag(self):
        text=self.report()+'\nReclassifying\n"2","Other","50","25-25","40"'
        rows=parse(text,'hr',2023,'2023-05-28')
        self.assertEqual(rows['Example']['HR'],60)
        self.assertFalse(rows['Example']['reclassifying'])
        self.assertTrue(rows['Other']['reclassifying'])

    def test_wrong_scope_dates_and_duplicates_rejected(self):
        text=self.report()
        for changed in [text.replace('2023','2024'),text.replace('Division I','Division II'),
                        text.replace('Home Runs','Runs'),text+'\n'+text.splitlines()[-1],
                        text.replace('05/28/2023','05/29/2023')]:
            with self.assertRaises(ValueError): parse(changed,'hr',2023,'2023-05-28')

    def test_missing_negative_counts_and_bad_records_rejected(self):
        text=self.report()
        for changed in [text.replace('"60"','""'),text.replace('"60"','"-1"'),
                        text.replace('30-20','30-19'),text.replace('"HR"','"K"')]:
            with self.assertRaises(ValueError): parse(changed,'hr',2023,'2023-05-28')


if __name__=='__main__': unittest.main()
