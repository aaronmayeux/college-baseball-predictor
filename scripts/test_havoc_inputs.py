import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from havoc_inputs import (FIELDS, batting, dom_batting, havoc_values, identity,
                          inventory, schedule_rows, verified_box, box_path, write, digest)
from test_reconstruct_havoc_pilot import fixture


def snapshot():
    return dict(heading='Virginia', selects=['2021','overall'],record='Overall 36-27(18-18 ACC)',
                rows=[['PLAYER','Team','GP']+list(FIELDS),['Batter','Virginia','60']+['10']*len(FIELDS)])


class BoundedHavocInputsTests(unittest.TestCase):
    def test_locked_identity_and_season(self):
        self.assertEqual(identity('https://d1baseball.com/team/virginia/2021/stats/'),(2021,'Virginia','stats'))
        for url in ('https://d1baseball.com/team/virginia/2026/stats/',
                    'https://d1baseball.com/team/virginia/2023/stats/',
                    'https://example.com/team/virginia/2021/stats/'):
            with self.assertRaises(ValueError):identity(url)

    def test_player_sums_and_team_game_count(self):
        r=batting(snapshot(),'https://d1baseball.com/team/virginia/2021/stats/')
        self.assertEqual(r['final_games'],63)
        self.assertEqual(r['final_counts']['K'],10)
        for change in ('team','split','loading','duplicate','missing_k','negative'):
            s=snapshot()
            if change=='team':s['rows'][1][1]='Other'
            if change=='split':s['selects'][-1]='conference'
            if change=='loading':s['rows'][1]=['Loading...']
            if change=='duplicate':s['rows'].append(s['rows'][1])
            if change=='missing_k':s['rows'][0][-3]='Pitching K'
            if change=='negative':s['rows'][1][-3]='-1'
            with self.assertRaises(ValueError,msg=change):batting(s,'https://d1baseball.com/team/virginia/2021/stats/')

    def test_dom_empty_non_count_cell_preserves_column_alignment(self):
        headers=['Player','Class','GP']+list(FIELDS)
        h=''.join(f'          - \'columnheader "{x}: activate to sort column ascending"\'\n' for x in headers)
        cells=['Batter','','10']+['1']*len(FIELDS)
        body='        - row "Batter":\n'+''.join('          - gridcell'+(' "'+c+'"' if c else '')+'\n' for c in cells)
        dom='heading "Batting"\n'+h+h+body+'    - status: Showing 1 to 1 of 1 entries\nheading "Pitching"'
        self.assertEqual(dom_batting(dom),[headers,cells])
        with self.assertRaises(ValueError):dom_batting(dom.replace('of 1 entries','of 2 entries'))

    def test_formula_and_missing_counts(self):
        c=dict(SB=71,CS=16,BB=284,HBP=74,K=368)
        self.assertAlmostEqual(havoc_values(c)['havoc'],1.35869565217)
        self.assertAlmostEqual(havoc_values(c)['havoc_net_steals'],1.27173913043)
        for key in c:
            v=dict(c);del v[key]
            with self.assertRaises(ValueError):havoc_values(v)
        with self.assertRaises(ValueError):havoc_values(dict(c,K=0))

    def test_schedule_counts_and_result_orientation(self):
        row=dict(cells=[dict(text='date',links=[dict(url='https://d1baseball.com/scores/?date=20220603')]),dict(text='vs',links=[]),dict(text='UCLA',links=[dict(url='https://d1baseball.com/team/ucla/schedule/')]),dict(text='L\n9 - 2',links=[dict(url='https://school.test/box')]),dict(text='',links=[]),dict(text='',links=[])])
        r=schedule_rows(dict(rows=[row]))[0]
        self.assertEqual((r['runs_for'],r['runs_against']),(2,9))
        self.assertEqual(r['date'],'2022-06-03')

    def test_hash_and_both_sides_required(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d);url='https://school.test/box';stem=box_path(raw,url)
            stem.parent.mkdir(parents=True)
            body=fixture().replace('<h2>Test</h2>','<h2>Virginia</h2>')
            body+=fixture().replace('<h2>Test</h2>','<h2>Texas</h2>')
            stem.with_suffix('.html').write_text(body)
            write(stem.with_suffix('.json'),dict(url=url,status=200,sha256=digest(stem.with_suffix('.html')),retrieved_at_utc='2026-09-27T00:00:00+00:00'))
            game=dict(team_a_id='wn:Virginia',team_b_id='wn:Texas',runs_a=1,runs_b=1,game_date='2023-06-02')
            self.assertEqual(verified_box(raw,url,game,'wn:Virginia')['K'],1)
            with self.assertRaises(ValueError):verified_box(raw,url,dict(game,runs_b=2),'wn:Virginia')
            stem.with_suffix('.html').write_text(body+'tamper')
            with self.assertRaises(ValueError):verified_box(raw,url,game,'wn:Virginia')

    def test_non_d1_and_cutoff_inventory(self):
        contract=dict(seasons={'2021':dict(forecast_cutoff='2021-06-02T12:00:00+00:00')},modes={'conference_inclusive':['regular_season','conference_tournament']})
        games=[dict(game_id='a',team_a_id='wn:Virginia',team_b_id='wn:Texas',game_date='2021-05-31',stage='conference_tournament'),dict(game_id='b',team_a_id='wn:Virginia',team_b_id='wn:Texas',game_date='2021-06-01',stage='regular_season')]
        excluded=[dict(team_id='wn:Virginia',status='completed',non_d1_explicit=True,game_date='2021-05-10',runs_for=3)]
        with patch('havoc_inputs.read',side_effect=[contract,games,excluded]):
            _,inc,exc,non=inventory(2021,'wn:Virginia')
        self.assertEqual([x['game_id'] for x in inc],['a'])
        self.assertEqual([x['game_id'] for x in exc],['b'])
        self.assertEqual(len(non),1)
        excluded[0]['game_date']='2021-06-01'
        with patch('havoc_inputs.read',side_effect=[contract,games,excluded]),self.assertRaises(ValueError):inventory(2021,'wn:Virginia')

    def test_rendered_capture_requires_provenance_and_rejects_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d);url='https://school.test/box'
            stem=box_path(raw,url);rendered=raw/'rendered_boxes'/stem.name
            stem.parent.mkdir(parents=True);rendered.parent.mkdir()
            body=fixture().replace('<h2>Test</h2>','<h2>Virginia</h2>')
            body+=fixture().replace('<h2>Test</h2>','<h2>Texas</h2>')
            game=dict(team_a_id='wn:Virginia',team_b_id='wn:Texas',runs_a=1,runs_b=1,game_date='2023-06-02')
            def save(path,html,**metadata):
                path.with_suffix('.html').write_text(html)
                write(path.with_suffix('.json'),dict(url=url,sha256=digest(path.with_suffix('.html')),
                    retrieved_at_utc='2026-09-27T00:00:00+00:00',**metadata))
            save(stem,'unavailable',status=404)
            save(rendered,body,acquisition='browser_dom',rendered=False)
            with self.assertRaises(ValueError):verified_box(raw,url,game,'wn:Virginia')
            save(rendered,body,acquisition='browser_dom',rendered=True)
            self.assertEqual(verified_box(raw,url,game,'wn:Virginia')['K'],1)
            with self.assertRaises(ValueError):verified_box(raw,url,dict(game,game_date='2023-06-03'),'wn:Virginia')
            save(stem,body,status=200)
            self.assertEqual(verified_box(raw,url,game,'wn:Virginia')['K'],1)
            # Both player and total strikeouts agree within each capture, but
            # two individually valid captures disagree with each other.
            changed=body.replace('<td>0</td><td>1</td><td>1</td><td>1</td><td>0</td>',
                                 '<td>0</td><td>1</td><td>2</td><td>1</td><td>0</td>')
            save(rendered,changed,acquisition='browser_dom',rendered=True)
            with self.assertRaises(RuntimeError):verified_box(raw,url,game,'wn:Virginia')


if __name__=='__main__':unittest.main()
