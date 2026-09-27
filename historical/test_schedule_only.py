"""Data-free checks for the locked schedule-only development extension."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import tempfile
import unittest

import schedule_only as s


class ScheduleOnly(unittest.TestCase):
    def games(self):
        return [dict(game_id=str(i),game_date=f'2025-05-{1+i:02d}',a='a',b='b' if i<15 else 'c',
            runs_a=3,runs_b=1,tie=False,stage='regular_season',reciprocal_check='pass') for i in range(21)]

    def state(self):
        state=s.State();state.r.update(b=1600,c=1400);state.n.update(b=15,c=6)
        return state

    def test_drop_latest_is_deterministic_and_preserves_inputs(self):
        games=self.games(); original=deepcopy(games);state=self.state()
        actual=s.feature('a',games,state,True)
        self.assertEqual(actual,s.feature('a',list(reversed(games)),state,True))
        self.assertEqual(actual['games'],20)
        self.assertEqual(actual['value'],1550)
        self.assertEqual(games,original)
        self.assertEqual(state.r['c'],1400)
        self.assertNotIn('20',actual['game_ids'])

    def test_small_sample_and_missing_rating_fall_back_exactly(self):
        games=self.games(); state=self.state()
        features={'a':s.feature('a',games[:20],state,True),'b':dict(value=1600)}
        row=s.pair('a','b',.713,features)
        self.assertFalse(row['covered'])
        self.assertEqual(s.components.probability(row,dict(candidate='schedule_only')),.713)
        state.n['c']=0
        self.assertIsNone(s.feature('a',games,state)['value'])

    def test_2025_outcomes_and_late_results_cannot_change_inputs(self):
        games=self.games()
        cutoff=datetime.fromisoformat('2025-05-21T12:00:00+00:00')
        start=s.State()
        primary,eligible=s.schedule.update_through(start,games,cutoff,['regular_season'],'2025-05-21')
        changed=deepcopy(games)
        for g in changed:
            if g['game_date']>'2025-05-19':g['runs_a'],g['runs_b']=0,100
        changed.append(dict(games[0],game_id='ncaa',stage='regional',runs_a=0,runs_b=100))
        other,other_games=s.schedule.update_through(start,changed,cutoff,['regular_season'],'2025-05-21')
        self.assertEqual(dict(primary.r),dict(other.r))
        self.assertEqual(eligible,other_games)

    def test_fit_blocks_exposed_and_future_evaluation_years(self):
        rows=[dict(season=year,elo=.6,covered=True,tie=False,differences={'schedule':x},outcome=int(x>0))
              for year in (2021,2022,2023) for x in (-2,-1,1,2)]
        model=s.fit(rows)
        self.assertEqual(model['n'],12)
        self.assertEqual(model['training_seasons'],[2021,2022,2023])
        self.assertAlmostEqual(model['scale'][0],(2.5)**.5)
        for year in (2024,2025,2026):
            with self.assertRaises(ValueError):s.fit(rows+[dict(rows[0],season=year)])
        row=rows[0]
        reverse=dict(row,elo=1-row['elo'],differences={'schedule':-row['differences']['schedule']})
        self.assertAlmostEqual(s.components.probability(row,model)+s.components.probability(reverse,model),1)

    def test_lock_reuses_identical_and_refuses_changed_model(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'lock.json'
            s.components.lock(path,{'beta':.2})
            s.components.lock(path,{'beta':.2})
            with self.assertRaises(ValueError):s.components.lock(path,{'beta':.3})
            self.assertEqual(s.common.read(path),{'beta':.2})


if __name__=='__main__':unittest.main()
