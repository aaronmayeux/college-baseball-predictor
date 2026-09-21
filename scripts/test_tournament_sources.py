import unittest
from copy import deepcopy
from audit_tournament_sources import inspect_page, validate_field, historical_year
from audit_player_exceptions import annotate


class Sources(unittest.TestCase):
    def test_complete_field_and_omissions(self):
        rows=[dict(team_id=str(i),season=2025) for i in range(64)]
        validate_field(rows,{str(i) for i in range(64)})
        for bad in [rows[:-1],rows[:-1]+[rows[0]],rows[:-1]+[dict(team_id='other',season=2025)]]:
            with self.assertRaises(ValueError):validate_field(bad,{str(i) for i in range(64)})
    def test_mixed_season(self):
        rows=[dict(team_id=str(i),season=2025) for i in range(64)];rows[0]['season']=2026
        with self.assertRaises(ValueError):validate_field(rows,{str(i) for i in range(64)})
    def test_wrong_season_is_not_history(self):
        x=inspect_page('<title>Baseball 2025-26</title><a href="/sports/baseball/stats/2025/a/boxscore/1">Box</a>', 'https://example.test/schedule/2025','schedule')
        self.assertEqual(x['status'],'wrong_season_rejected');self.assertEqual(x['advertised_box_links'],0)
    def test_http_success_without_history_is_not_coverage(self):
        self.assertEqual(inspect_page('<title>Baseball</title>','https://example.test/2025','schedule')['status'],'unverified_payload')
    def test_links_are_unique_and_only_advertised(self):
        html='<title>2025 Baseball Schedule</title>'+2*'<a href="/sports/baseball/stats/2025/a/boxscore/1">Box</a>'
        x=inspect_page(html,'https://example.test','schedule')
        self.assertEqual(x['advertised_box_links'],1)
        self.assertEqual(x['status'],'historical_index_present')
    def test_explicit_year_formats_only(self):
        self.assertEqual(historical_year('5/25/25'),2025)
        self.assertEqual(historical_year('5/25/2025'),2025)
        for bad in ['5/25','2/30/2025','yesterday']:
            with self.assertRaises(ValueError):historical_year(bad)


class Exceptions(unittest.TestCase):
    def sample(self):
        return [dict(config=dict(key='davidson_2024'),comparisons=dict(batting=dict(totals_match=False,differences=[dict(player='jake dunagan',observed=dict(appearances=1))]))),
            dict(config=dict(key='missouri_state_2022'),records=[dict(date='2022-05-24',teams=['Missouri State','Illinois State'],runs=[9,4],issues=['ambiguous_or_missing_baseline_match'],parsed=True,game_id=None,box_url='box')],
            appearances=dict(pitching=[dict(box_url='box',game_id=None,actual_appearance_date=None,source_date='2022-05-24',pitch_count=None)]),
            forecast_modes=dict(conference_inclusive=dict(expected_games=57,verified_game_boxes=56,pitching_appearances=205,rest_status='unknown'),regular_only=dict(expected_games=51,verified_game_boxes=51))) ]
    def game(self):
        return dict(game_id='wn:2022:40418',game_date='2022-05-25',team_a_id='wn:Illinois-State',team_b_id='wn:Missouri-State',runs_a=4,runs_b=9)
    def test_annotations_preserve_original_and_unknown_workload(self):
        old=self.sample();before=deepcopy(old);g=self.game();gb=deepcopy(g)
        new=annotate(old,[g],dict(duke={},recap={}))['audits']
        self.assertEqual(old,before);self.assertEqual(g,gb)
        app=new[1]['appearances']['pitching'][0]
        self.assertIsNone(app['actual_appearance_date']);self.assertIsNone(app['pitch_count'])
        self.assertEqual(app['source_date'],'2022-05-24')
        self.assertEqual(new[1]['forecast_modes']['conference_inclusive']['rest_status'],'unknown')
        self.assertEqual(new[1]['forecast_modes']['regular_only'],old[1]['forecast_modes']['regular_only'])
        self.assertFalse(new[0]['comparisons']['batting']['totals_match'])
    def test_conflicting_score_rejected(self):
        g=self.game();g['runs_b']=8
        with self.assertRaises(ValueError):annotate(self.sample(),[g],dict(duke={},recap={}))
    def test_ambiguous_game_rejected(self):
        with self.assertRaises(ValueError):annotate(self.sample(),[self.game(),self.game()],dict(duke={},recap={}))
    def test_other_issue_not_cleared(self):
        x=self.sample();x[1]['records'][0]['issues'].append('missing_pitcher')
        with self.assertRaises(ValueError):annotate(x,[self.game()],dict(duke={},recap={}))


if __name__=='__main__':unittest.main()
