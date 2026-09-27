"""Data-free tests of refresh-to-Elo fallback and evidence verification."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ingestion import candidate as c
from ingestion import nolan_refresh as n


def game(gid='wn:2024:1'):
    return dict(game_id=gid,season=2024,game_date='2024-05-20',team_a_id='wn:A',team_b_id='wn:B',
        a='a',b='b',runs_a=3,runs_b=1,tie=False,stage='regular_season',timing_review=False,
        reciprocal_check='pass',observation_refs=[{'raw_sha256':'original'}])


def staged(rows):
    return dict(season=2024,version='fixture',teams=['A','B'],games=rows,failures=[],source_sha256={'raw':'hash'})


def fresh():
    return dict(game(),observation_refs=[{'raw_sha256':'fresh'}],modes={'regular_only':{'eligible':True}})


class CandidateRefresh(unittest.TestCase):
    def test_confirmed_preserves_original_and_adds_provenance(self):
        original={2024:[game()]};before=deepcopy(original)
        result,report=c.merge_verified(original,staged([fresh()]))
        self.assertEqual(original,before)
        for key,value in original[2024][0].items():self.assertEqual(result[2024][0][key],value)
        self.assertEqual(result[2024][0]['refresh_confirmation']['observation_refs'],[{'raw_sha256':'fresh'}])
        self.assertEqual(report['counts'],{'confirmed_unchanged':1})

    def test_changed_scores_dates_phase_identity_and_timing_keep_baseline(self):
        for key,value in [('runs_a',0),('game_date','2024-05-31'),('stage','regional'),
                          ('team_a_id','wn:C'),('timing_review',True)]:
            row=dict(fresh(),**{key:value})
            original={2024:[game()]}
            result,report=c.merge_verified(original,staged([row]))
            self.assertEqual(result,original)
            self.assertEqual(report['counts'],{'fallback_changed_requires_review':1})
            self.assertEqual(report['decisions'][0]['changed_fields'],[key])

    def test_new_missing_unpaired_and_failed_pages_do_not_delete_history(self):
        original={2024:[game(),game('wn:2024:2')],2025:[]}
        bundle=staged([dict(fresh(),reciprocal_check='review'),dict(fresh(),game_id='wn:2024:3')])
        bundle['failures']=[{'team':'B','reason':'offline'}]
        result,report=c.merge_verified(original,bundle)
        self.assertEqual(result,original)
        self.assertEqual(report['counts'],{'fallback_unpaired_or_conflicting':1,'fallback_new_unreviewed':1})
        self.assertEqual(report['missing_baseline_game_ids'],['wn:2024:2'])
        self.assertEqual(report['source_failures'],bundle['failures'])

    def test_official_correction_survives_stale_source(self):
        corrected=dict(game(),game_date='2024-05-21',timing_resolution={'evidence':'official'},
                       original_timing_fields={'game_date':'2024-05-20'})
        result,report=c.merge_verified({2024:[corrected]},staged([fresh()]))
        self.assertEqual(result[2024][0],corrected)
        self.assertEqual(report['counts']['fallback_changed_requires_review'],1)

    def test_duplicate_mixed_and_unknown_seasons_rejected(self):
        for bundle in [staged([fresh(),fresh()]),staged([dict(fresh(),season=2025)]),
                       dict(staged([fresh()]),season=2026)]:
            with self.assertRaises(ValueError):c.merge_verified({2024:[game()]},bundle)

    def fixture(self,root):
        # Small complete raw-backed staging fixture; no external datasets required.
        roster=[dict(slug='A',team_id='wn:A',name='A',season=2024,conference='X'),
                dict(slug='B',team_id='wn:B',name='B',season=2024,conference='X')]
        contract={'seasons':{'2024':{'forecast_cutoff':'2024-05-29T12:00:00+00:00','ncaa_opening_date':'2024-05-31'}},
                  'modes':{'regular_only':['regular_season'],'conference_inclusive':['regular_season','conference_tournament']}}
        paths={'historical/2024/teams.json':json.dumps(roster),'historical/cutoffs.json':json.dumps(contract),
               'ingestion/nolan_refresh.py':'fixture','ingestion/nolan_parser.py':'fixture','historical/eligibility.py':'fixture'}
        for key,value in paths.items():
            path=root/key;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value)
        folder=root/'saved';(folder/'raw').mkdir(parents=True)
        request=dict(schema=1,season=2024,teams=['A'],inputs={k:n.digest((root/k).read_bytes()) for k in paths})
        n.write_new(folder/'request.json',request)
        body=b'<h2>2024 A Tigers Schedule</h2><li class="team-schedule"><span class="game-date--day">20</span><span class="game-date--month">May</span><a class="opp-line-link" href="/baseball/2024/schedule/B">B</a><div id="1-schedule-toggle"></div><div class="team-schedule__result">W 3 - 1</div></li>'
        meta=dict(url=n.url_for(2024,'A'),http_status=200,raw_path='raw/A.html',sha256=n.digest(body),retrieved_at='fixture')
        (folder/'raw/A.html').write_bytes(body);n.write_new(folder/'raw/A.html.meta.json',meta)
        obs=c.parse(roster[0],body.decode(),meta,2024,'2024-05-31')
        games,excluded=n.stage(obs,roster,2024,contract)
        for name,value in [('observations',obs),('games',games),('exclusions',excluded)]:n.write_new(folder/(name+'.json'),value)
        return folder

    def test_reparse_detects_generated_eligibility_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=self.fixture(root)
            with patch.object(c,'ROOT',root):
                result=c.verified_refresh(folder)
                self.assertEqual(result['season'],2024)
                games=n.read(folder/'games.json');games[0]['modes']['regular_only']['eligible']=True
                (folder/'games.json').write_text(json.dumps(games))
                with self.assertRaisesRegex(ValueError,'do not reproduce'):c.verified_refresh(folder)

    def test_raw_and_code_hash_tampering_rejected(self):
        for target in ('saved/raw/A.html','ingestion/nolan_parser.py'):
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp);folder=self.fixture(root)
                (root/target).write_text('tampered')
                with patch.object(c,'ROOT',root):
                    with self.assertRaises(ValueError):c.verified_refresh(folder)

    def test_candidate_cli_cannot_overwrite_app(self):
        from tournament import build
        with patch.object(sys,'argv',['build','--refresh','saved']),patch.object(build,'build') as mocked:
            with self.assertRaises(SystemExit):build.main()
            mocked.assert_not_called()


if __name__=='__main__':unittest.main()
