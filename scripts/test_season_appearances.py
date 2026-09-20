"""Synthetic qualification failures; no external data or network required."""
import unittest
from audit_season_appearances import (rows, coverage_status, compare_totals,
    lsu_box, towson_box, PITCH_FIELDS, BAT_FIELDS)


def tr(cells,close=True):
    return '<tr>'+''.join('<td>'+str(x)+'</td>' for x in cells)+('</tr>' if close else '')


def fixture():
    bat='Player ab r h rbi bb so po a lob'.split()
    pitch='ip h r er bb so wp bk hbp ibb ab bf fo go np'.split()
    text='<title>Other vs LSU (Feb 14, 2025)</title><table>'
    for team,player,vals in [('Other','Opponent cf',[1,0,0,0,0,1,0,0,0]),('LSU','Hitter cf',[1,1,1,1,0,0,3,0,0])]:
        text+=tr([team+(' 0 (0-1)' if team=='Other' else ' 1 (1-0,0-0 SEC)')])+tr(bat)+tr([player]+vals)+tr(['Totals']+vals)
    text+='</table><table>'+tr(['LSU']+pitch)
    # Retain both a zero-out appearance and missing positive pitch count.
    text+=tr(['Pitcher One','0.0',0,0,0,0,0,0,0,0,0,0,0,0,0,0],False)
    text+=tr(['Pitcher Two W,1-0','1.0',0,0,0,0,1,0,0,0,0,1,1,0,0,5],False)
    return text+'</table>'


class SeasonTests(unittest.TestCase):
    def test_unclosed_rows_and_orphan_cells(self):
        self.assertEqual(rows('<table>'+tr(['a','1'],False)+tr(['b','2'])+'<td>orphan</td></table>'),[['a','1'],['b','2']])

    def test_lsu_zero_out_and_unknown_pitches(self):
        p=lsu_box(fixture(),{'date':'2025-02-14','teams':['LSU','Other'],'runs':[1,0]})
        self.assertEqual(len(p['pitching']),2)
        self.assertEqual(p['pitching'][0]['counts']['outs'],0)
        self.assertIsNone(p['pitching'][0]['pitch_count'])
        self.assertEqual(len(p['batting']),1)

    def test_lsu_wrong_opponent_score_date(self):
        for row in [{'date':'2025-02-14','teams':['LSU','Wrong'],'runs':[1,0]},
                    {'date':'2025-02-14','teams':['LSU','Other'],'runs':[2,0]},
                    {'date':'2025-02-15','teams':['LSU','Other'],'runs':[1,0]}]:
            with self.assertRaises(ValueError):lsu_box(fixture(),row)

    def test_lsu_missing_pitcher_blocks_sum_check(self):
        text=fixture().replace('Pitcher Two W,1-0','Totals')
        # A malformed count cannot silently become zero.
        text=text.replace('<td>1.0</td>','<td>--</td>')
        with self.assertRaises(ValueError):lsu_box(text,{'date':'2025-02-14','teams':['LSU','Other'],'runs':[1,0]})

    def test_missing_box_is_unknown_rest(self):
        r=coverage_status(['one','two'],[dict(box_url='one',parsed=True,issues=[])])
        self.assertFalse(r['complete_game_boxes']);self.assertEqual(r['rest_status'],'unknown')

    def test_duplicate_and_unparsed_boxes_fail(self):
        row=dict(box_url='one',parsed=True,issues=[])
        self.assertFalse(coverage_status(['one'],[row,row])['complete_game_boxes'])
        self.assertFalse(coverage_status(['one','one'],[row])['complete_game_boxes'])
        self.assertFalse(coverage_status(['one'],[dict(row,parsed=False)])['complete_game_boxes'])
        self.assertFalse(coverage_status([],[])['complete_game_boxes'])

    def test_complete_boxes_do_not_certify_rest_or_features(self):
        r=coverage_status(['one'],[dict(box_url='one',parsed=True,issues=[])])
        self.assertTrue(r['complete_game_boxes']);self.assertEqual(r['rest_status'],'unknown');self.assertFalse(r['feature_qualified'])

    def test_missing_player_and_zero_out_appearance(self):
        counts={f:0 for f in PITCH_FIELDS}
        totals={'pitcher':dict(counts=dict(counts,appearances=1))}
        p=dict(name='Pitcher',counts=counts,box_url='game')
        self.assertTrue(compare_totals([p],totals,'lsu','pitching')['totals_match'])
        r=compare_totals([],totals,'lsu','pitching')
        self.assertEqual(r['differences'],[dict(player='pitcher',field='appearances',observed=0,expected=1)])

    def test_unknown_identity_not_merged(self):
        p=dict(name='P. One',counts={f:0 for f in PITCH_FIELDS},box_url='game')
        self.assertFalse(compare_totals([p],{},'lsu','pitching')['totals_match'])

    def test_towson_missing_np_and_team_earned_runs(self):
        h='Player IP H R ER BB SO WP BK HBP IBB AB BF FO GO NP'.split()
        text='<title>Baseball 3/1/2024</title><table><caption>Towson - Pitching Stats</caption>'+tr(h)
        text+=tr(['Pitcher','1.0',1,1,1,0,0,0,0,0,0,3,3,0,3,'--'])
        text+=tr(['Totals','',1,1,0,0,0,0,0,0,0,3,3,0,3,''])+'</table>'
        text+='<table><caption>Other - Pitching Stats</caption></table>'
        text+='<table><caption>Towson 0</caption>'+tr('Position Player AB R H RBI BB SO LOB'.split())
        text+=tr(['cf','cf Batter',1,0,0,0,0,0,0])+tr(['','Totals',1,0,0,0,0,0,0])+'</table>'
        expected={'date':'2024-03-01','teams':['Towson','Other'],'runs':[0,1]}
        result=towson_box(text,expected)
        self.assertIsNone(result['pitching'][0]['pitch_count'])
        self.assertEqual(result['pitching'][0]['counts']['ER'],1)
        with self.assertRaises(ValueError):towson_box(text,dict(expected,teams=['Towson','Wrong']))

    def test_source_specific_two_way_player_conventions(self):
        counts={f:0 for f in BAT_FIELDS}
        totals={'two way':dict(counts=dict(counts,appearances=1))}
        p=dict(name='Two Way',counts=counts,box_url='game',raw={'Position':'p'})
        self.assertTrue(compare_totals([p],totals,'towson','batting')['totals_match'])
        p['raw']={'PLAYER':'Two Way p'}
        self.assertFalse(compare_totals([p],totals,'lsu','batting')['totals_match'])

    def test_zero_batting_exclusion_is_recorded(self):
        p=dict(name='Pitcher Only',counts={f:0 for f in BAT_FIELDS},box_url='game',raw={'PLAYER':'Pitcher Only p'})
        r=compare_totals([p],{},'lsu','batting')
        self.assertEqual(len(r['ignored_zero_batting_lines']),1)
        fielder=dict(p,raw={'PLAYER':'Unknown cf'})
        self.assertFalse(compare_totals([fielder],{},'lsu','batting')['totals_match'])
        p['counts']['AB']=1
        self.assertFalse(compare_totals([p],{},'lsu','batting')['totals_match'])


if __name__=='__main__':unittest.main()
