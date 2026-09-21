import copy
import unittest
from statcrew_archives import cumulative, conference_index, verify_season
from audit_statcrew_archives import clemson_completion
from audit_source_access import inspect_robots

URL = 'https://school.test/stats/2025/team.htm'
MARKER = r'<!File source:C:\TASBS\2025\reports\TEAM.MLB>'


def table(header, records):
    return '<table>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in [header]+records)+'</table>'


def cume():
    bh = ['Player', 'gp-gs', 'ab', 'r', 'h', 'rbi', 'bb', 'so']
    ph = ['Player', 'app-gs', 'ip', 'h', 'r', 'er', 'bb', 'so', 'wp', 'bk', 'hbp', 'ab']
    bat = [['Batter', '1-1', '3', '1', '1', '1', '0', '1'], ['Totals', '1-1', '3', '1', '1', '1', '0', '1'], ['Opponents', '1-1', '3', '1', '1', '1', '0', '1']]
    pitch = [['Pitcher', '1-1', '0.1', '1', '1', '1', '0', '1', '0', '0', '0', '3'], ['Totals', '1-1', '0.1', '1', '1', '0', '0', '1', '0', '0', '0', '3'], ['Opponents', '1-1', '0.1', '1', '1', '0', '0', '1', '0', '0', '0', '3']]
    return MARKER+table(bh, bat)+table(ph, pitch)


def index():
    header = ['', 'Game date', '', 'Opposing team', '', 'Score', '', 'r-h-e', '/', 'r-h-e', 'Inns', 'Overall', 'OVC', 'Pitcher of record', 'Attend', 'Time']
    row = ['', 'Feb 14, 2025', 'at', '#2 OTHER-1', 'W', '<a href="game1.htm">5-4</a>', '', '5-7-0', '/', '4-6-0', '9', '1-0', '0-0', 'Pitcher', '100', '3:00']
    return '<title>2025 Conference Baseball - School</title>'+MARKER+table(header, [row])


class StatCrew(unittest.TestCase):
    def test_cumulative_additive_counts_and_team_er_separate(self):
        result = cumulative(cume(), URL, 2025)
        self.assertTrue(result['pitching']['additive_counts_match'])
        self.assertEqual(result['pitching']['player_sums']['outs'], 1)
        self.assertEqual(result['pitching']['individual_er_sum'], 1)
        self.assertEqual(result['pitching']['team_er'], 0)
        self.assertEqual(result['pitching']['player_appearance_sum'], 1)

    def test_missing_or_wrong_season_never_inferred_from_url(self):
        for text, url in [(cume().replace(MARKER, ''), URL), (cume().replace('2025', '2026'), URL), (cume(), URL.replace('2025', '2026')), (cume()+MARKER.replace('2025', '2024'), URL)]:
            with self.assertRaises(ValueError): cumulative(text, url, 2025)

    def test_missing_bad_or_duplicate_player_not_silently_skipped(self):
        for text in [cume().replace('<td>Batter</td>', '<td></td>'), cume().replace('<td>3</td>', '<td>?</td>', 1), cume().replace('<td>Batter</td>', '<td>Batter</td><td>extra</td>'), cume().replace('<td>Opponents</td>', '<td>Batter</td>', 1), cume().replace('<td>1-1</td>', '<td>1-2</td>', 1)]:
            with self.assertRaises(ValueError): cumulative(text, URL, 2025)

    def test_additive_disagreement_remains_visible(self):
        result = cumulative(cume().replace('<td>3</td>', '<td>4</td>', 1), URL, 2025)
        self.assertFalse(result['batting']['additive_counts_match'])
        self.assertEqual(result['batting']['additive_differences']['AB'], {'player_sum': 4, 'team_total': 3})

    def test_index_preserves_source_and_doubleheader_label(self):
        result = conference_index(index(), URL, 2025, 'School')
        self.assertEqual(result[0]['teams'], ['School', 'OTHER'])
        self.assertEqual(result[0]['source_opponent'], '#2 OTHER-1')
        self.assertEqual(result[0]['box_url'], 'https://school.test/stats/2025/game1.htm')

    def test_index_wrong_team_year_missing_box_rejected(self):
        for text in [index().replace(' - School', ' - Wrong'), index().replace('Feb 14, 2025', 'Feb 14, 2026'), index().replace('<a href="game1.htm">5-4</a>', '5-4'), index().replace('game1.htm', 'https://other.test/stats/2025/game1.htm')]:
            with self.assertRaises(ValueError):conference_index(text, URL, 2025, 'School')

    def test_known_visual_divider_allowed(self):
        result = cumulative(cume().replace('</table>', '<tr><td>----------</td></tr></table>', 1), URL, 2025)
        self.assertEqual(len(result['batting']['players']), 1)
        with self.assertRaises(ValueError):
            cumulative(cume().replace('TEAM.MLB', 'TEAM.MLC'), URL, 2025)


class Completion(unittest.TestCase):
    def fixture(self):
        return dict(games=[dict(date='2025-05-03', teams=['Clemson', 'Florida State'], runs=[6, 3], game_id=None, issues=['ambiguous_or_missing_baseline_match'])]), [dict(game_id='g1', game_date='2025-05-04', team_a_id='wn:Clemson', team_b_id='wn:Florida-State', runs_a=6, runs_b=3)]

    def test_annotation_preserves_strict_record_and_unknown_work_dates(self):
        inventory, games = self.fixture();before = copy.deepcopy(inventory)
        a = clemson_completion(inventory, games, {})
        self.assertEqual(inventory, before)
        self.assertIsNone(a['original_record']['game_id'])
        self.assertIsNone(a['actual_pitcher_work_dates'])
        self.assertEqual(a['completion_date'], '2025-05-04')
        self.assertEqual(a['recent_workload'], 'unknown')

    def test_wrong_score_ambiguous_match_or_other_issue_blocks_annotation(self):
        for case in ('score', 'ambiguous', 'other_issue'):
            inventory, games = self.fixture()
            if case == 'score':games[0]['runs_a'] = 7
            elif case == 'ambiguous':games.append(games[0])
            else:inventory['games'][0]['issues'].append('missing_pitcher')
            with self.assertRaises(ValueError):clemson_completion(inventory, games, {})


class Access(unittest.TestCase):
    def test_html_http_success_does_not_mean_robots_allow(self):
        for text in ['<html>Not found</html>', '<html>User-agent: *\nAllow: /</html>', '']:
            result = inspect_robots(text, 'https://school.test/robots.txt', [URL])
            self.assertIsNone(result['paths'][0]['robots_allowed'])
            self.assertFalse(result['collection_enabled'])

    def test_rules_and_delay_are_not_bulk_permission(self):
        result = inspect_robots('User-agent: *\nCrawl-delay: 5\nDisallow: /private\n', 'https://school.test/robots.txt', [URL, 'https://school.test/private/data'])
        self.assertEqual(result['crawl_delay_seconds'], 5)
        self.assertTrue(result['paths'][0]['robots_allowed'])
        self.assertFalse(result['paths'][1]['robots_allowed'])
        self.assertEqual(result['bulk_permission'], 'unverified')
        self.assertFalse(result['collection_enabled'])

    def test_cross_origin_targets_and_redirects_rejected(self):
        with self.assertRaises(ValueError):inspect_robots('User-agent: *\nAllow: /', 'https://other.test/robots.txt', [URL])
        result = inspect_robots('User-agent: *\nAllow: /', 'https://school.test/robots.txt', [URL], 'https://other.test/robots.txt')
        self.assertIsNone(result['paths'][0]['robots_allowed'])


if __name__ == '__main__':unittest.main()
