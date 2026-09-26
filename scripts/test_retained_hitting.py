"""Synthetic regressions: no retained data, network, or outcome metrics required."""
from copy import deepcopy
import unittest
from extract_retained_hitting import (FIELDS, MAPPING, OPPONENT, OVERALL,
    extract_logs, identity, qualify_modes)

CONFIG = dict(team_name='Test',team_id='test',url='https://example.test/sports/baseball/stats/2022',expected=2)


def fixture():
    c = dict(AB=10,H=4,BB=2,SO=3,**{'2B':1,'3B':0,'HR':1,'HBP':1,'SF':1,'SH':1})
    hitting = {MAPPING[f][0]:str(v) for f,v in c.items()}
    hitting.update(runsScored='3',reachedOnCatchersInteference='1')
    pitching = {key:str(c[f] if f!='CI' else 1) for f,key in OPPONENT.items()}
    pitching['battersFaced']='16'
    own = []; opp = []
    for i in range(2):
        row = dict(isAFooterStat=False,date=f'5/{i+1}/2022',opponent='Other',ourScore='3',opponentScore='2',
            boxscoreUrl=f'/sports/baseball/stats/2022/other/boxscore/{i}',hitting=deepcopy(hitting))
        own.append(row)
        opp.append(dict(row,opponent='Test',ourScore='2',opponentScore='3',pitching=deepcopy(pitching)))
    own.append(dict(isAFooterStat=True,hitting={k:str(int(v)*2) for k,v in hitting.items()}))
    opp.append(dict(isAFooterStat=True,pitching={k:str(int(v)*2) for k,v in pitching.items()}))
    data = dict(gameByGameStats=dict(ourGameByGameStats=own,opponentGameByGameStats=opp),
        overallTeamStats=dict(teamStats={key:str(c[f]*2) for f,key in OVERALL.items()}))
    players = {'one':dict(counts={f:v*2 for f,v in c.items()})}
    return data,players


def run(data, players):
    return extract_logs(data, CONFIG, players)


class RetainedHittingTests(unittest.TestCase):
    def test_complete_counts_and_interference(self):
        records,check=run(*fixture())
        self.assertTrue(check['pass_counts']);self.assertTrue(check['PA_pass'])
        self.assertEqual(records[0]['counts']['PA'],16)
        self.assertEqual(records[0]['counts']['CI'],1)

    def test_missing_and_duplicate_games_fail(self):
        for mutation in ('missing','duplicate','opponent_duplicate','footer_duplicate'):
            d,p=fixture();g=d['gameByGameStats'];own=g['ourGameByGameStats']
            if mutation=='missing':own.pop(0)
            if mutation=='duplicate':own[1]=deepcopy(own[0])
            if mutation=='opponent_duplicate':g['opponentGameByGameStats'][1]=deepcopy(g['opponentGameByGameStats'][0])
            if mutation=='footer_duplicate':own.append(deepcopy(own[-1]))
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):run(d,p)

    def test_wrong_year_and_source_scope_fail(self):
        d,_=fixture();r=d['gameByGameStats']['ourGameByGameStats'][0]
        for changes in [dict(date='5/1/2026'),dict(boxscoreUrl='https://other.test/sports/baseball/stats/2022/a'),dict(boxscoreUrl='/sports/baseball/stats/2026/a')]:
            with self.assertRaises(ValueError):identity(dict(r,**changes),CONFIG)

    def test_bad_counts_and_score_fail_season(self):
        for field,value in [('atBats',None),('hits','20'),('doubles','-1'),('runsScored','99')]:
            d,p=fixture();d['gameByGameStats']['ourGameByGameStats'][0]['hitting'][field]=value
            rows,c=run(d,p)
            self.assertFalse(c['pass_counts']);self.assertTrue(rows[0]['issues'])

    def test_all_season_audit_targets_are_required(self):
        for target in ('footer','players','overall'):
            d,p=fixture()
            if target=='footer':d['gameByGameStats']['ourGameByGameStats'][-1]['hitting']['walks']='5'
            if target=='players':p['one']['counts']['BB']=5
            if target=='overall':d['overallTeamStats']['teamStats']['ourWalks']='5'
            self.assertFalse(run(d,p)[1]['pass_counts'])

    def test_bf_or_component_failure_preserves_power(self):
        for field in ('battersFaced','catchersInterferenceAllowed','hitsAllowed'):
            d,p=fixture();d['gameByGameStats']['opponentGameByGameStats'][0]['pitching'][field]='99'
            rows,c=run(d,p)
            self.assertTrue(c['pass_counts']);self.assertFalse(c['PA_pass'])
            self.assertIsNone(rows[0]['counts']['PA']);self.assertTrue(rows[0]['denominator_issues'])

    def test_missing_interference_is_unknown(self):
        d,p=fixture();del d['gameByGameStats']['ourGameByGameStats'][0]['hitting']['reachedOnCatchersInteference']
        rows,c=run(d,p)
        self.assertTrue(c['pass_counts']);self.assertFalse(c['PA_pass'])
        self.assertIsNone(rows[0]['counts']['CI'])

    def test_opponent_order_ignored_but_identity_required(self):
        d,p=fixture();d['gameByGameStats']['opponentGameByGameStats'].reverse()
        self.assertTrue(run(d,p)[1]['PA_pass'])
        d['gameByGameStats']['opponentGameByGameStats'][1]['opponent']='Unreviewed alias'
        self.assertFalse(run(d,p)[1]['PA_pass'])

    def test_only_explicit_self_alias_is_accepted(self):
        d,p=fixture();d['gameByGameStats']['opponentGameByGameStats'][0]['opponent']='Test St.'
        self.assertTrue(extract_logs(d,dict(CONFIG,self_aliases={'Test St.':'Test'}),p)[1]['PA_pass'])

    def test_season_bf_footer_must_reconcile(self):
        d,p=fixture();d['gameByGameStats']['opponentGameByGameStats'][-1]['pitching']['battersFaced']='31'
        rows,c=run(d,p)
        self.assertTrue(c['pass_counts']);self.assertFalse(c['PA_pass'])
        self.assertTrue(all(r['counts']['PA']==16 for r in rows))

    def test_modes_and_all_global_gates(self):
        rows,check=run(*fixture())
        for i,r in enumerate(rows):r.update(game_id=str(i),issues=[])
        games=[dict(game_id=str(i),game_date=r['date'],stage=('regular' if i==0 else 'conference_tournament'),
            reciprocal_check='pass',team_a_id='test',team_b_id='other') for i,r in enumerate(rows)]
        contract=dict(seasons={'2022':dict(forecast_cutoff='2022-06-01T12:00:00+00:00')},
            modes=dict(regular_only=['regular'],conference_inclusive=['regular','conference_tournament']))
        def modes(c=check,inventory=True,sample=True):return qualify_modes(rows,games,CONFIG,contract,c,inventory,sample)
        m=modes();self.assertEqual(m['regular_only']['counts']['AB'],10)
        self.assertEqual(m['conference_inclusive']['counts']['AB'],20)
        # Postseason and too-recent results never enter either frozen mode.
        for gid,date,stage in [('ncaa','2022-05-10','regional'),('late','2022-05-31','regular')]:
            games.append(dict(games[0],game_id=gid,game_date=date,stage=stage))
            extra=deepcopy(rows[0]);extra['game_id']=gid
            extra['counts']={f:(v*100 if v is not None else None) for f,v in extra['counts'].items()}
            rows.append(extra)
        self.assertEqual(modes(),m)
        for c,inv,sample in [(dict(check,pass_counts=False),True,True),(check,False,True),(check,True,False)]:
            self.assertTrue(all(x['rates'] is None and not x['complete'] for x in modes(c,inv,sample).values()))
        for x in modes(dict(check,PA_pass=False)).values():
            self.assertTrue(x['complete']);self.assertIsNotNone(x['rates']['ISO'])
            self.assertIsNone(x['rates']['strikeout_rate']);self.assertFalse(x['PA_complete'])

    def test_missing_eligible_count_blocks_mode(self):
        d,p=fixture();del d['gameByGameStats']['ourGameByGameStats'][0]['hitting']['atBats']
        rows,check=run(d,p)
        self.assertFalse(check['pass_counts']);self.assertIsNone(rows[0]['counts'])


if __name__=='__main__':unittest.main()
