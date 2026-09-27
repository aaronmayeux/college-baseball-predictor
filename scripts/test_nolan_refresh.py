"""Data-free bounded import, source integrity, chronology and staging checks."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion import nolan_refresh as n
from ingestion.nolan_parser import parse

TEAM=dict(slug='Alpha',name='Alpha',season=2024,team_id='wn:Alpha',conference='Test')
META=dict(url=n.url_for(2024,'Alpha'),retrieved_at='2026-09-27T00:00:00+00:00',sha256='fixture',raw_path='raw/Alpha.html')
CONTRACT={'seasons':{'2024':{'forecast_cutoff':'2024-05-29T12:00:00+00:00'}},
          'modes':{'regular_only':['regular_season'],'conference_inclusive':['regular_season','conference_tournament']}}


def page(year=2024,name='Alpha',label='',day=20,result='W 3 - 1'):
    return f'''<h2>{year} {name} Tigers Schedule</h2>
<li class="team-schedule__special--start">{label}</li>
<li class="team-schedule"><span class="game-date--day">{day}</span><span class="game-date--month">May</span>
<a class="opp-line-link" href="/baseball/{year}/schedule/Beta">Beta</a>
<div id="123-schedule-toggle"></div><div class="team-schedule__result">{result}</div></li>'''


def observation(team='wn:Alpha',opponent='wn:Beta',runs=3,against=1,outcome='W',day='2024-05-20'):
    return dict(team_id=team,opponent_id=opponent,source_game_id='123',status='completed',
        non_d1_explicit=False,game_date=day,stage='regular_season',runs_for=runs,runs_against=against,
        outcome=outcome,timing_review=False,raw_path='raw/test.html',raw_sha256='fixture',
        source_url='fixture',retrieved_at='fixture')


class NolanRefresh(unittest.TestCase):
    def pair(self):
        return [observation(),observation('wn:Beta','wn:Alpha',1,3,'L')]

    def stage(self,rows):
        return n.stage(rows,[{'team_id':'wn:Alpha'},{'team_id':'wn:Beta'}],2024,CONTRACT)

    def test_wrong_year_team_and_empty_pages_rejected(self):
        for content in [page(2026),page(name='Other'),'<h2>2024 Alpha Tigers Schedule</h2>']:
            with self.assertRaises(ValueError):parse(TEAM,content,META,2024,'2024-05-31')
        self.assertEqual(parse(TEAM,page(),META,2024,'2024-05-31')[0]['runs_for'],3)

    def test_phases_and_ties_preserved(self):
        for label,stage in [('SEC Tournament','conference_tournament'),('NCAA Regional','regional'),
                            ('NCAA Super Regional','super_regional'),('College World Series','omaha'),
                            ('CWS Championship','championship_series')]:
            row=parse(TEAM,page(label=label,result='T 2 - 2'),META,2024,'2024-05-31')[0]
            self.assertEqual(row['stage'],stage)
            self.assertEqual(row['outcome'],'T')
        self.assertEqual(parse(TEAM,page(day=31),META,2024,'2024-05-31')[0]['stage'],'late_season_unclassified')

    def test_duplicate_game_id_rejected(self):
        with self.assertRaises(ValueError):parse(TEAM,page()+page(),META,2024,'2024-05-31')

    def test_reciprocal_conflicts_and_missing_pages_block(self):
        good=self.pair()
        self.assertTrue(self.stage(good)[0][0]['modes']['regular_only']['eligible'])
        cases=[good[:1],good+good[:1], [good[0],dict(good[1],runs_for=4)],
               [good[0],dict(good[1],game_date='2024-05-21')],
               [good[0],dict(good[1],stage='conference_tournament')],
               [dict(good[0],outcome='L'),good[1]]]
        for rows in cases:
            self.assertFalse(self.stage(rows)[0][0]['modes']['conference_inclusive']['eligible'])

    def test_cutoff_two_day_lag_and_modes(self):
        rows=self.pair()
        for row in rows:row.update(stage='conference_tournament',game_date='2024-05-27')
        game=self.stage(rows)[0][0]
        self.assertTrue(game['modes']['conference_inclusive']['eligible'])
        self.assertFalse(game['modes']['regular_only']['eligible'])
        for row in rows:row['game_date']='2024-05-28'
        self.assertEqual(self.stage(rows)[0][0]['modes']['conference_inclusive']['exclusion_reason'],'after_cutoff_with_two_day_lag')
        for row in rows:row.update(game_date='2024-05-20',stage='regional')
        self.assertFalse(self.stage(rows)[0][0]['modes']['conference_inclusive']['eligible'])

    def test_unknown_opponent_unscored_and_non_d1_retained(self):
        rows=[dict(observation(),opponent_id='wn:Unknown'),dict(observation(),non_d1_explicit=True),
              dict(observation(),status='not_scored')]
        games,excluded=self.stage(rows)
        self.assertEqual(games,[])
        self.assertEqual([r['reason'] for r in excluded],['unknown_opponent','non_d1','unscored'])

    def test_source_integrity_cache_and_immutable_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);old=root/'old';raw=root/'raw';old.mkdir();raw.mkdir()
            body=page().encode();path=old/'Alpha.html';path.write_bytes(body)
            meta=dict(META,sha256=n.digest(body),http_status=200)
            path.with_name(path.name+'.meta.json').write_text(json.dumps(meta))
            original=n.source(raw,2024,'Alpha',old)
            with patch.object(n,'build_opener',side_effect=AssertionError('No repeat network call')):
                self.assertEqual(n.source(raw,2024,'Alpha'),original)
            (raw/'Alpha.html').write_bytes(b'tampered')
            with self.assertRaises(ValueError):n.source(raw,2024,'Alpha')
            lock=root/'request.json';n.write_new(lock,{'season':2024})
            with self.assertRaises(ValueError):n.write_new(lock,{'season':2025})

    def test_failed_requests_cached_without_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            raw=Path(temp)
            with patch.object(n,'build_opener',side_effect=OSError('offline')) as mocked:
                body,meta=n.source(raw,2024,'Alpha')
                self.assertIsNone(body)
                self.assertIn('offline',meta['error'])
                self.assertEqual(n.source(raw,2024,'Alpha'),(body,meta))
                self.assertEqual(mocked.call_count,1)

    def test_unknown_season_unsafe_name_and_budget_fail_before_io(self):
        for season,teams,version in [(2026,['LSU'],'test'),(2024,['LSU'],'../escape'),
                                      (2024,['LSU']*9,'test'),(2024,['LSU','LSU'],'test')]:
            with patch.object(n,'read',return_value=CONTRACT):
                with self.assertRaises(ValueError):n.run(season,teams,version)
        with self.assertRaises(ValueError):n.url_for(2024,'../../escape')

    def test_redirects_not_followed(self):
        self.assertIsNone(n.NoRedirect().redirect_request(None,None,302,'',{},'https://elsewhere'))


if __name__=='__main__':unittest.main()
