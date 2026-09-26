import unittest
from datetime import date, datetime
from plan_ncaa_snapshots import snapshot_options, cover

CUTOFF = datetime.fromisoformat('2022-06-01T12:00:00+00:00')


def game(day, phase='regular_season', **kw):
    return dict(game_id=day+phase, game_date=day, stage=phase,
                reciprocal_check='pass', **kw)


def options(*days):
    return [(date.fromisoformat(d), str(i), False) for i,d in enumerate(days)]


class SnapshotTests(unittest.TestCase):
    def test_complete_preconference_window(self):
        gs = [game('2022-05-20'), game('2022-05-22', 'conference_tournament')]
        r = snapshot_options(gs, CUTOFF, ['regular_season'], options('2022-05-19','2022-05-20','2022-05-21','2022-05-22'))
        self.assertEqual([d['through'] for d in r['candidates']], ['2022-05-20','2022-05-21'])

    def test_late_regular_game_cannot_be_included_without_tournament(self):
        gs = [game('2022-05-20'), game('2022-05-22', 'conference_tournament'), game('2022-05-29')]
        r = snapshot_options(gs, CUTOFF, ['regular_season'], options('2022-05-20','2022-05-30'))
        self.assertEqual(r['candidates'], [])
        self.assertEqual(r['excluded_results_before_last_target'], ['2022-05-22conference_tournament'])

    def test_inclusive_scope_and_availability_lag(self):
        gs = [game('2022-05-20'), game('2022-05-29', 'conference_tournament')]
        r = snapshot_options(gs, CUTOFF, ['regular_season','conference_tournament'], options('2022-05-28','2022-05-29','2022-05-30','2022-05-31'))
        self.assertEqual([d['through'] for d in r['candidates']], ['2022-05-29','2022-05-30'])

    def test_same_date_mixed_phases_block_regular_only(self):
        gs = [game('2022-05-20'), game('2022-05-20','conference_tournament')]
        self.assertEqual(snapshot_options(gs,CUTOFF,['regular_season'],options('2022-05-20'))['candidates'], [])

    def test_timing_missing_dates_conflicts_and_final_reports_fail_closed(self):
        for extra in [game('2022-05-19',timing_review=True),
                      dict(game('2022-05-19'),game_date=None),
                      dict(game('2022-05-19'),reciprocal_check='fail')]:
            with self.subTest(extra=extra):
                r=snapshot_options([extra,game('2022-05-20')],CUTOFF,['regular_season'],options('2022-05-20'))
                self.assertEqual(r['candidates'],[])
        self.assertEqual(snapshot_options([game('2022-05-20')],CUTOFF,['regular_season'],[(date(2022,5,20),'1',True)])['candidates'],[])

    def test_empty_target_does_not_qualify(self):
        self.assertEqual(snapshot_options([],CUTOFF,['regular_season'],options('2022-05-20'))['candidates'],[])

    def test_minimum_cover_of_overlapping_date_intervals(self):
        rows=[dict(candidates=[dict(through=d) for d in values]) for values in [('a','b'),('b','c'),('c','d'),()]]
        self.assertEqual(cover(rows),['b','d'])
        self.assertEqual(cover([]),[])

    def test_noninterval_sets_rejected(self):
        with self.assertRaises(ValueError):
            cover([dict(candidates=[dict(through='a'),dict(through='c')]),dict(candidates=[dict(through='b')])])
