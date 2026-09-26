"""Synthetic regression checks; no retained evidence or network required."""
import datetime as dt
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'historical/validation_v2'),str(ROOT/'historical')]
from selection_2021 import parse_bracket,article_dates,latest_utc
from audit_season_appearances import statcrew_box


def bracket():
    teams=[];lines=[]
    for side,x in enumerate((90,620)):
        for i in range(32):
            n=side*32+i;name=f'Team {n}'
            teams.append(dict(name=name,slug=f'Team-{n}'))
            seed=(1,4,3,2)[i%4]
            # One regional has the host at seed 2, not seed 1.
            host=(i%4==3 if side==1 and i<4 else i%4==0)
            text=f'#{seed} {"*" if host else ""}{name} (30 - 10)'
            lines.append(f'<line xMin="{x}" yMin="{100+i*10}"><word>{text}</word></line>')
    xml='<html xmlns="http://www.w3.org/1999/xhtml"><page width="792">'+''.join(lines)+'</page></html>'
    return xml,teams


def article(published='2021-05-31T13:42:00',modified='2021-05-31T13:50:31'):
    r={'@type':'NewsArticle','headline':'JAGS TO COMPETE AT NCAA GAINESVILLE REGIONAL AS NO. 3 SEED',
       'datePublished':published,'dateModified':modified}
    return '<script type="application/ld+json">'+json.dumps(r)+'</script>'


class SelectionTests(unittest.TestCase):
    def test_complete_field_and_non_top_seed_host(self):
        xml,teams=bracket();rows=parse_bracket(xml,teams)
        self.assertEqual(len(rows),64)
        self.assertEqual({r['regional_seed'] for r in rows if r['host_marker']},{1,2})

    def test_missing_duplicate_and_unmapped_teams_rejected(self):
        xml,teams=bracket()
        for bad in [xml.replace('#4 Team 1 (30 - 10)','#4 Unknown (30 - 10)'),
                    xml.replace('#4 Team 1 (30 - 10)','#4 Team 0 (30 - 10)'),
                    xml.replace('#4 Team 1 (30 - 10)','Team 1')]:
            with self.assertRaises(ValueError):parse_bracket(bad,teams)

    def test_wrong_seed_or_host_rejected(self):
        xml,teams=bracket()
        for bad in [xml.replace('#4 Team 1','#3 Team 1'),xml.replace('#4 Team 1','#4 *Team 1')]:
            with self.assertRaises(ValueError):parse_bracket(bad,teams)

    def test_naive_timestamp_conservative_bound(self):
        cutoff=dt.datetime.fromisoformat('2021-06-02T12:00:00+00:00')
        self.assertEqual(article_dates(article(),cutoff)['modification_latest_utc'],'2021-06-01T01:50:31+00:00')
        self.assertEqual(latest_utc('2021-05-31T13:42:00-04:00').hour,17)

    def test_late_modified_article_rejected(self):
        with self.assertRaises(ValueError):
            article_dates(article(modified='2021-06-03T00:00:00'),dt.datetime.fromisoformat('2021-06-02T12:00:00+00:00'))

    def test_missing_date_or_wrong_article_rejected(self):
        cutoff=dt.datetime.fromisoformat('2021-06-02T12:00:00+00:00')
        with self.assertRaises(ValueError):article_dates(article().replace('JAGS TO','OTHER TO'),cutoff)
        with self.assertRaises(ValueError):article_dates(article()+article(),cutoff)

    def test_generic_statcrew_preserves_counts_and_unknown_pitches(self):
        from test_season_appearances import fixture
        from audit_season_appearances import lsu_box
        original=lsu_box(fixture(),dict(date='2025-02-14',teams=['LSU','Other'],runs=[1,0]))
        generic=statcrew_box(fixture().replace('LSU','Arkansas'),
            dict(date='2025-02-14',teams=['Arkansas','Other'],runs=[1,0]),'Arkansas')
        self.assertEqual(original,generic)
        self.assertEqual(generic['pitching'][0]['counts']['outs'],0)
        self.assertIsNone(generic['pitching'][0]['pitch_count'])

    def test_completion_annotation_preserves_original(self):
        from copy import deepcopy
        from audit_expansion_preflight import annotate_arkansas, SOURCES
        row=dict(box_url=SOURCES['arkansas']['url'].replace('teamstat.htm','ark50.htm'),
            date='2022-05-14',teams=['Arkansas','Vanderbilt'],runs=[11,6],
            game_id=None,issues=['ambiguous_or_missing_baseline_match'])
        original=dict(games=[row],matched_games=0,missing_baseline_games=['wn:2022:36425'],inventory_pass=False)
        before=deepcopy(original)
        game=dict(game_id='wn:2022:36425',game_date='2022-05-15',team_a_id='wn:Arkansas',
                  team_b_id='wn:Vanderbilt',runs_a=11,runs_b=6)
        result=annotate_arkansas(original,[game],[])
        self.assertEqual(original,before)
        self.assertTrue(result['inventory_pass'])
        self.assertEqual(result['games'][0]['actual_player_work_dates'],'unknown')
        with self.assertRaises(ValueError):annotate_arkansas(original,[dict(game,runs_a=12)],[])

    def test_statcrew_does_not_substitute_other_team(self):
        with self.assertRaises(ValueError):
            statcrew_box('<title>A vs B (Feb 18, 2022)</title>',
                dict(date='2022-02-18',teams=['A','B'],runs=[1,0]),'C')


if __name__=='__main__':unittest.main()
