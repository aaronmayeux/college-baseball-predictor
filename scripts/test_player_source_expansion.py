"""Synthetic tests for historical identity, roster participation and coverage gates."""
import copy
import json
import unittest
from unittest.mock import patch
from sidearm_structured import decode, payload, schedule, box, PITCH, BAT
from audit_player_source_expansion import compare
from player_coverage_ledger import coverage_ledger

CONFIG=dict(team_name='School',season=2024,schedule_url='https://school.test/sports/baseball/schedule/2024',expected_completed_games=1)


def fixture_game():
    return dict(id=10,date='2024-02-16T13:00:00',enddate=None,noplay_text='',type='R',
        opponent={'title':'#12 Other'},result=dict(status='W',team_score='1',opponent_score='0',boxscore={'url':'/sports/baseball/stats/2024/other/boxscore/10'}))


def fixture_box():
    hitting={v[0]:'0' for v in BAT.values()}
    pitching={v[0]:'0' for v in PITCH.values()};pitching.update(inningsPitched='1.0',gamesStarted='1',battersFaced='3',pitches='0')
    p=dict(name='Pitcher, One',gamePlayed='1',gameStarted='1',position='p',rosterPlayerId='p1',hitting=hitting,pitching=pitching)
    batter=dict(name='Batter, One',gamePlayed='1',gameStarted='1',position='cf',rosterPlayerId='b1',hitting=hitting,pitching=None)
    unused=dict(name='Unused, One',gamePlayed='0',gameStarted='0',position='',rosterPlayerId='u1',hitting=None,pitching=None)
    side=dict(name='School',scoringSummary={'runs':'0'},players=[p,batter,unused],totals=dict(pitching=copy.deepcopy(pitching),hitting=copy.deepcopy(hitting)))
    return dict(venue={'date':'2/16/2024'},homeTeam=side,visitingTeam=dict(name='Other',scoringSummary={'runs':'0'}),gameId='10')


class ExpansionTests(unittest.TestCase):
    def test_payload_reference_decoder(self):
        text='<script id="__NUXT_DATA__">'+json.dumps([{'path':1,'pinia':2},'/archive',{'season':3},2024])+'</script>'
        self.assertEqual(decode(text)['pinia']['season'],2024)
        self.assertEqual(payload(text,'https://school.test/archive'),{'season':2024})
        with self.assertRaises(ValueError):payload(text,'https://school.test/other')

    def test_decoder_rejects_cycles_and_executable_tags(self):
        for nodes in [[{'loop':0}],[['Function',1],'bad'],[{'bad':55}]]:
            with self.assertRaises(ValueError):decode('<script id="__NUXT_DATA__">'+json.dumps(nodes)+'</script>')

    def test_schedule_preserves_exhibition_and_cancellation(self):
        game=fixture_game();fall=copy.deepcopy(game);fall['date']='2023-09-01T00:00:00';fall['id']=11
        canceled=copy.deepcopy(game);canceled['result']=None;canceled['noplay_text']='Canceled'
        data={'schedule':{'schedules':{'schedules-baseball,2024':dict(season={'title':'2024'},sport={'shortname':'baseball'},games=[game,fall,canceled])}}}
        with patch('sidearm_structured.payload',return_value=data):rows,excluded=schedule('',CONFIG)
        self.assertEqual(rows[0]['teams'],['School','Other']);self.assertEqual(rows[0]['source_opponent'],'#12 Other')
        self.assertEqual([r['reason'] for r in excluded],['outside_calendar_season','no_completed_result'])

    def test_schedule_rejects_wrong_season_and_duplicate_games(self):
        data={'schedule':{'schedules':{'schedules-baseball,2024':dict(season={'title':'2026'},sport={'shortname':'baseball'},games=[])}}}
        with patch('sidearm_structured.payload',return_value=data):
            with self.assertRaises(ValueError):schedule('',CONFIG)
        data['schedule']['schedules']['schedules-baseball,2024'].update(season={'title':'2024'},games=[fixture_game(),fixture_game()])
        with patch('sidearm_structured.payload',return_value=data):
            with self.assertRaises(ValueError):schedule('',dict(CONFIG,expected_completed_games=2))

    def test_unused_roster_rows_are_not_appearances(self):
        data=fixture_box()
        with patch('sidearm_structured.payload',return_value={'boxscore':{'boxscore':{'x':data}}}):
            parsed,details=box('','',dict(date='2024-02-16',teams=['School','Other'],runs=[0,0]),CONFIG)
        self.assertEqual(len(parsed['pitching']),1);self.assertEqual(len(parsed['batting']),2)
        self.assertEqual(len(details['unused_roster_rows']),1);self.assertIsNone(parsed['pitching'][0]['pitch_count'])

    def test_unused_player_with_counts_blocks_box(self):
        data=fixture_box();data['homeTeam']['players'][-1]['hitting']={}
        with patch('sidearm_structured.payload',return_value={'boxscore':{'boxscore':{'x':data}}}):
            with self.assertRaises(ValueError):box('','',dict(date='2024-02-16',teams=['School','Other'],runs=[0,0]),CONFIG)

    def test_wrong_box_date_or_opponent_blocks(self):
        for date,other in [('2024-02-17','Other'),('2024-02-16','Wrong')]:
            with patch('sidearm_structured.payload',return_value={'boxscore':{'boxscore':{'x':fixture_box()}}}):
                with self.assertRaises(ValueError):box('','',dict(date=date,teams=['School',other],runs=[0,0]),CONFIG)

    def test_zero_out_pitcher_keeps_appearance(self):
        counts={k:0 for k in PITCH};target={'one pitcher':dict(counts=dict(counts,appearances=1),provider_player_id='1')}
        app=dict(match_key='one pitcher',counts=counts,name='Pitcher, One',provider_player_id='1',position='p',box_url='game')
        self.assertTrue(compare([app],target,'pitching')['totals_match'])
        self.assertFalse(compare([],target,'pitching')['totals_match'])

    def test_unknown_batting_substitute_is_not_discarded(self):
        app=dict(match_key='sub',counts={k:0 for k in BAT},name='Sub',provider_player_id=None,position='ph',box_url='game')
        self.assertFalse(compare([app],{},'batting')['totals_match'])
        app['position']='p';self.assertTrue(compare([app],{},'batting')['totals_match'])

    def test_every_requested_team_gets_coverage_row(self):
        rows=coverage_ledger(['one','two'],[],2025,'regular_only')
        self.assertEqual([r['team_id'] for r in rows],['one','two'])
        self.assertTrue(all(r['recent_workload']=='unknown' and r['needs_validated_fallback'] for r in rows))
        with self.assertRaises(ValueError):coverage_ledger(['one','one'],[],2025,'regular_only')

    def test_coverage_requires_matching_season_and_mode(self):
        audit=dict(config={'team_id':'one','season':2024},forecast_modes={'regular_only':{'complete':False},'conference_inclusive':{'complete':True}},comparisons={'batting':{'totals_match':True},'pitching':{'totals_match':True}})
        self.assertEqual(coverage_ledger(['one'],[audit],2025,'conference_inclusive')[0]['hitting_counts'],'unverified')
        self.assertEqual(coverage_ledger(['one'],[audit],2024,'regular_only')[0]['hitting_counts'],'unverified')
        row=coverage_ledger(['one'],[audit],2024,'conference_inclusive')[0]
        self.assertEqual(row['hitting_counts'],'reconciled_core_counts');self.assertEqual(row['recent_workload'],'unknown')


if __name__=='__main__':unittest.main()
