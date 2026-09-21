"""Safety checks for linked archives and offline collection sizing."""
import copy
import json
import unittest
from unittest.mock import patch
from sidearm_structured import decode
from audit_tournament_sources import inspect_page
from plan_tournament_collection import plan


def encoded(nodes):
    return '<script id="__NUXT_DATA__">'+json.dumps(nodes)+'</script>'


class Archives(unittest.TestCase):
    def test_empty_refs_preserve_falsy_types(self):
        for tag in ('EmptyRef', 'EmptyShallowRef'):
            for raw, expected in [('_', None), ('null', None), ('false', False), ('0', 0), ('0n', 0), ('""', '')]:
                result = decode(encoded([{'value': 1}, [tag, 2], raw]))['value']
                self.assertEqual(result, expected)
                self.assertIs(type(result), type(expected))

    def test_empty_refs_reject_unknown_values_cycles_and_shapes(self):
        for nodes in [[{'v': 1}, ['EmptyRef', 2], 'not empty'], [{'v': 1}, ['EmptyRef', 2], {}], [{'v': 1}, ['EmptyRef', 1]], [{'v': 1}, ['EmptyRef', 2, 2], '0']]:
            with self.assertRaises(ValueError):
                decode(encoded(nodes))

    def fixture(self):
        return dict(path='/sports/baseball/stats/season/2025', data={'sport-baseball-roster-season-2025': dict(season={'name': '2025', 'slug': '2025'}, sport={'slug': 'baseball'}, wmt_stats2_team_id=123, wmt_stats2_iframe_url='https://wmt.games/school/stats/season/123')})

    def inspect(self, data, final='https://school.test/sports/baseball/stats/season/2025'):
        with patch('audit_tournament_sources.decode', return_value=data):
            return inspect_page('<title>2025 Baseball</title>__NUXT_DATA__', 'https://school.test/sports/baseball/stats/2025', 'cumulative', final)

    def test_link_is_not_player_coverage(self):
        result = self.inspect(self.fixture())
        self.assertEqual(result['status'], 'historical_external_stats_link_only')
        self.assertEqual(result['historical_stats_links'], ['https://wmt.games/school/stats/season/123'])

    def test_redirect_requires_matching_host_year_and_payload(self):
        for final in [None, 'https://other.test/sports/baseball/stats/season/2025', 'https://school.test/sports/baseball/stats/season/2026']:
            self.assertEqual(self.inspect(self.fixture(), final)['status'], 'unverified_payload')
        data = self.fixture();data['path'] = '/current'
        self.assertEqual(self.inspect(data)['status'], 'unverified_payload')

    def test_link_identity_and_season_are_checked(self):
        for key, value in [('season', {'name': '2026', 'slug': '2026'}), ('sport', {'slug': 'softball'}), ('wmt_stats2_team_id', 999), ('wmt_stats2_iframe_url', 'https://other.test/school/stats/season/123')]:
            data = self.fixture();data['data']['sport-baseball-roster-season-2025'][key] = value
            self.assertEqual(self.inspect(data)['status'], 'unverified_payload')

    def test_schedule_heading_and_wrong_season_guard(self):
        self.assertEqual(inspect_page('<title>Schedule</title><h1><span>2024-25</span>Baseball Schedule</h1>', 'https://school.test', 'schedule')['status'], 'historical_index_present')
        self.assertEqual(inspect_page('<title>2025-26 Baseball</title><h1>2025 Baseball Schedule</h1>', 'https://school.test', 'schedule')['status'], 'wrong_season_rejected')
        self.assertEqual(inspect_page('<title>Schedule</title><select>2025 Baseball Schedule</select>', 'https://school.test', 'schedule')['status'], 'unverified_payload')


class Planning(unittest.TestCase):
    def fixture(self):
        field = dict(season=2025, teams=[dict(team_id=str(i), name=str(i), season=2025, schedule_status='gap', cumulative_status='gap', terms_status='unverified') for i in range(64)])
        games = [dict(game_id='g1', season=2025, game_date='2025-05-01', team_a_id='0', team_b_id='1', stage='regular_season', reciprocal_check='pass'), dict(game_id='g2', season=2025, game_date='2025-05-24', team_a_id='0', team_b_id='other', stage='conference_tournament', reciprocal_check='pass')]
        contract = dict(seasons={'2025': {'forecast_cutoff': '2025-05-28T12:00:00+00:00'}}, modes=dict(regular_only=['regular_season'], conference_inclusive=['regular_season', 'conference_tournament']))
        return field, games, contract

    def test_all_teams_retained_shared_games_deduplicated_modes_separate(self):
        args = self.fixture();before = copy.deepcopy(args);result = plan(*args)
        self.assertEqual(args, before)
        self.assertEqual(len(result['teams']), 64)
        self.assertEqual(result['summary']['regular_only']['team_game_sides'], 2)
        self.assertEqual(result['summary']['regular_only']['unique_games'], 1)
        self.assertEqual(result['summary']['conference_inclusive']['unique_games'], 2)
        self.assertFalse(result['collection_enabled'])
        self.assertTrue(all(t['recent_workload'] == 'unknown' and not t['collection_enabled'] for t in result['teams']))
        self.assertIn('63', result['summary']['regular_only']['teams_with_no_known_games'])

    def test_ineligible_games_do_not_enter_cutoff_volume(self):
        for edit in [dict(game_date='2025-05-28'), dict(stage='regional'), dict(timing_review=True), dict(reciprocal_check='fail')]:
            field, games, contract = self.fixture();games[0].update(edit)
            self.assertEqual(plan(field, games, contract)['summary']['regular_only']['unique_games'], 0)

    def test_bad_inventory_rejected(self):
        for case in ('missing_team', 'duplicate_team', 'duplicate_game', 'mixed_season'):
            field, games, contract = self.fixture()
            if case == 'missing_team':field['teams'].pop()
            elif case == 'duplicate_team':field['teams'][-1] = field['teams'][0]
            elif case == 'duplicate_game':games.append(games[0])
            else:games[0]['season'] = 2026
            with self.assertRaises(ValueError):plan(field, games, contract)


if __name__ == '__main__':
    unittest.main()
