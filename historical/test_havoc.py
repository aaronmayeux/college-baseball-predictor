import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import havoc


def row(y=2021,d=.2,p=.6,outcome=1,covered=True):
    return dict(season=y,tie=False,covered=covered,elo=p,outcome=outcome,
                differences=dict(havoc=d,havoc_net_steals=d/2))


class HavocExperimentTests(unittest.TestCase):
    def test_coverage_requires_both_training_years_and_selection(self):
        rows=[row() for _ in range(16)]+[row(2023) for _ in range(8)]
        self.assertFalse(havoc.coverage_gate(rows)['pass_gate'])
        rows=[row() for _ in range(8)]+[row(2022) for _ in range(8)]+[row(2023) for _ in range(8)]
        self.assertTrue(havoc.coverage_gate(rows)['pass_gate'])
        rows[-1]['covered']=False
        self.assertFalse(havoc.coverage_gate(rows)['pass_gate'])

    def test_training_only_and_symmetry(self):
        rows=[row(d=.2),row(2022,d=-.3,outcome=0)]
        model=havoc.fit(rows,'havoc')
        self.assertAlmostEqual(model['scale'],math.sqrt((.04+.09)/2))
        a=havoc.probability(row(),model)
        b=havoc.probability(row(d=-.2,p=.4,outcome=0),model)
        self.assertAlmostEqual(a+b,1.)
        for y in (2023,2024,2025,2026):
            with self.assertRaises(ValueError):havoc.fit(rows+[row(y)],'havoc')

    def test_fallback_is_exact_and_needs_both_teams(self):
        p=dict(row(),team_a_id='a',team_b_id='b')
        built=havoc.sample_row(p,{'a':dict(values=dict(havoc=1,havoc_net_steals=.9))})
        self.assertFalse(built['covered'])
        self.assertEqual(havoc.probability(built,dict(candidate='havoc',beta=99,scale=.1)),p['elo'])

    def test_lock_immutable_and_repeatable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'lock.json';havoc.lock(p,dict(a=1));first=p.read_bytes()
            havoc.lock(p,dict(a=1));self.assertEqual(first,p.read_bytes())
            with self.assertRaises(ValueError):havoc.lock(p,dict(a=2))

    def test_insufficient_data_stops_before_any_fit(self):
        data=dict(protocol=havoc.PROTOCOL,inputs={'hash':'x'},samples=[row()],coverage=[])
        with tempfile.TemporaryDirectory() as d,patch.object(havoc,'OUT',Path(d)),patch.object(havoc.common,'gates'),patch.object(havoc,'fingerprints',return_value=data['inputs']),patch.object(havoc,'fit') as fit:
            havoc.common.write(Path(d)/'prepared.json',data)
            havoc.evaluate(Path(d))
            report=havoc.common.read(Path(d)/'report.json')
            fit.assert_not_called()
            self.assertFalse(report['scored'])
            self.assertFalse((Path(d)/'selection_lock.json').exists())

    def test_two_candidates_score_only_selection_and_never_promote(self):
        rows=[row(y,d=.2 if i%2 else -.2,outcome=i%2) for y in (2021,2022,2023) for i in range(8)]
        rows.append(row(2023,covered=False))
        data=dict(protocol=havoc.PROTOCOL,inputs={'hash':'x'},samples=rows,coverage=[])
        with tempfile.TemporaryDirectory() as d,patch.object(havoc,'OUT',Path(d)),patch.object(havoc.common,'gates'),patch.object(havoc,'fingerprints',return_value=data['inputs']):
            havoc.common.write(Path(d)/'prepared.json',data)
            havoc.evaluate(Path(d))
            report=havoc.common.read(Path(d)/'report.json')
            self.assertEqual(set(report['models']),set(havoc.CANDIDATES))
            self.assertFalse(report['promoted'])
            for key in havoc.CANDIDATES:
                self.assertEqual(report['models'][key]['training_seasons'],[2021,2022])
                self.assertEqual(report['results'][key]['all']['metrics']['elo']['n'],9)
                self.assertEqual(report['results'][key]['covered']['metrics']['elo']['n'],8)

    def test_fixed_flagged_sensitivity_is_exact_elo(self):
        r=dict(row(),flagged=True)
        model=dict(candidate='havoc',scale=.3,beta=1)
        self.assertEqual(havoc.probability(r,model,strict=True),r['elo'])
        self.assertNotEqual(havoc.probability(r,model),r['elo'])


if __name__=='__main__':unittest.main()
