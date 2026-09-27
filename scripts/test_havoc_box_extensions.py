import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from havoc_box_extensions import wmt_counts, subtraction_day, verified_wmt


def fixture():
    game=dict(game_id='wn:2022:1',season=2022,game_date='2022-06-20',
              team_a_id='wn:Auburn',team_b_id='wn:Stanford',runs_a=3,runs_b=2,stage='omaha')
    identity=dict(title='WMT Stats // Auburn - Stanford // 06/20/2022 // 3 - 2',
                  date='06/20/2022',heading='Auburn AT Stanford')
    box=dict(identity,tables=[]); comp=dict(identity,tables=[])
    for name,r,k,opp_r,opp_k in [('Auburn',3,4,2,7),('Stanford',2,7,3,4)]:
        box['tables'].append([['Pos','Player',name],['AB','R','H','RBI','BB','K','LOB'],
            ['DH','Batter','10',str(r),'4',str(r),'2',str(k),'1'],
            ['Total','10',str(r),'4',str(r),'2',str(k),'1']])
        comp['tables'].append([['',name],['Pos','Player','AB','R','H','BB','SB','CS','HBP','SO'],
            ['DH','Batter','10',str(r),'4','2','1','0','1','0'],
            ['Total','10',str(r),'4','2','1','0','1',str(opp_k)]])
        box['tables'].append([[name],['Player','IP','AB','R','H','BB','SO','HB'],
            ['Pitcher','9.0','10',str(opp_r),'4','2',str(opp_k),'1','1'],
            ['Total','9.0','10',str(opp_r),'4','2',str(opp_k),'1']])
    return dict(box=box,composite=comp),game


class BoxExtensionsTests(unittest.TestCase):
    def test_batting_k_not_composite_pitching_so(self):
        doc,g=fixture(); result=wmt_counts(doc,g,g['game_date'])
        self.assertEqual(result['wn:Auburn']['K'],4)
        self.assertEqual(result['wn:Stanford']['K'],7)
        self.assertEqual(result['wn:Auburn']['SB'],1)

    def test_identity_and_view_conflicts(self):
        doc,g=fixture()
        for field,value in [('title','wrong'),('date','06/21/2022'),('heading','Other')]:
            bad=copy.deepcopy(doc);bad['composite'][field]=value
            with self.assertRaises(ValueError):wmt_counts(bad,g,g['game_date'])
        with self.assertRaises(ValueError):wmt_counts(doc,dict(g,runs_a=4),g['game_date'])
        with self.assertRaises(ValueError):wmt_counts(doc,g,'2022-06-19')

    def test_incomplete_columns_players_and_pitching(self):
        doc,g=fixture()
        for change in ('missing','duplicate','player_conflict','sum','pitching','order'):
            bad=copy.deepcopy(doc)
            if change=='missing':bad['composite']['tables'][0][1][6]='OTHER'
            if change=='duplicate':bad['box']['tables'].append(bad['box']['tables'][0])
            if change=='player_conflict':bad['composite']['tables'][0][2][1]='Other Batter'
            if change=='sum':bad['box']['tables'][0][2][-2]='5'
            if change=='pitching':
                bad['box']['tables'][3][2][6]='5';bad['box']['tables'][3][3][6]='5'
            if change=='order':bad['box']['tables'][1][2][-1]='2'
            with self.assertRaises(ValueError,msg=change):wmt_counts(bad,g,g['game_date'])

    def test_date_review_bound_to_game_evidence_and_post_cutoff(self):
        _,g=fixture()
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d);p=raw/'recap.html';p.write_text('Official dated completion recap')
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            meta=dict(status=200,url='https://school.test/recap',sha256=sha,retrieved_at_utc='2026-09-27T00:00:00+00:00')
            p.with_suffix('.json').write_text(json.dumps(meta))
            row=dict(game_id=g['game_id'],box_urls=['https://school.test/box'],original=g,
                start_date='2022-06-19',completion_date=g['game_date'],review_reason='Reviewed suspended game',
                evidence=[dict(path='recap.html',sha256=sha,url=meta['url'])])
            (raw/'date_reviews.json').write_text(json.dumps([row]))
            self.assertEqual(subtraction_day(raw,'https://school.test/box',g),'2022-06-19')
            with self.assertRaises(ValueError):subtraction_day(raw,'https://school.test/box',dict(g,runs_a=8))
            row['start_date']='2022-05-31';(raw/'date_reviews.json').write_text(json.dumps([row]))
            with self.assertRaises(ValueError):subtraction_day(raw,'https://school.test/box',g)
            row['start_date']='2022-06-19';(raw/'date_reviews.json').write_text(json.dumps([row]))
            p.write_text('changed')
            with self.assertRaises(ValueError):subtraction_day(raw,'https://school.test/box',g)
            self.assertEqual(subtraction_day(raw,'https://unreviewed.test/box',g),g['game_date'])

    def test_capture_hash_and_official_parent_binding(self):
        doc,g=fixture()
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d);(raw/'wmt_boxes').mkdir();url='https://auburntigers.com/boxscore/1'
            embedded='https://wmt.games/auburn/stats/match/full/1'
            parent=raw/'parent.html';parent.write_text('<iframe src="'+embedded+'"></iframe>')
            stem=raw/'wmt_boxes'/hashlib.sha256(url.encode()).hexdigest();p=stem.with_suffix('.json')
            p.write_text(json.dumps(doc))
            meta=dict(url=url,embedded_url=embedded,acquisition='browser_dom',retrieved_at_utc='2026-09-27T00:00:00+00:00',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),parent_path='parent.html',parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest())
            stem.with_suffix('.meta.json').write_text(json.dumps(meta))
            self.assertEqual(verified_wmt(raw,url,g,g['game_date'])['wn:Auburn']['K'],4)
            parent.write_text('changed')
            with self.assertRaises(ValueError):verified_wmt(raw,url,g,g['game_date'])
