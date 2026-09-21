"""Access triage must not turn unknown rules into permission."""
import unittest
from audit_collection_scope import path_rules


class Scope(unittest.TestCase):
    def test_allow_with_delay_is_not_a_quota(self):
        row = path_rules('User-agent: *\nAllow: /\nCrawl-delay: 30',
            'https://a.test/robots.txt', 'https://a.test/sports/baseball')
        self.assertTrue(row['allowed'])
        self.assertEqual(row['delay_seconds'], 30)

    def test_denial_and_other_origin(self):
        self.assertFalse(path_rules('User-agent: *\nDisallow: /',
            'https://a.test/robots.txt', 'https://a.test/sports')['allowed'])
        with self.assertRaises(ValueError):
            path_rules('User-agent: *\nAllow: /', 'https://a.test/robots.txt', 'https://b.test/sports')

    def test_html_and_cross_origin_robots_are_unknown(self):
        for text, final in [('<html>app</html>', None), ('User-agent: *\nAllow: /', 'https://b.test/robots.txt')]:
            self.assertIsNone(path_rules(text, 'https://a.test/robots.txt', 'https://a.test/sports', final)['allowed'])

    def test_other_bot_deny_does_not_override_our_group(self):
        text = 'User-agent: OtherBot\nDisallow: /\n\nUser-agent: *\nDisallow: /*.js$\nAllow: /'
        self.assertTrue(path_rules(text, 'https://a.test/robots.txt', 'https://a.test/stats/2025')['allowed'])

    def test_relevant_wildcard_and_conflicting_prefix_are_unknown(self):
        for rules in ['Disallow: /*print=true*\nAllow: /', 'Disallow: /sports\nAllow: /sports/baseball']:
            row = path_rules('User-agent: *\n' + rules, 'https://a.test/robots.txt', 'https://a.test/sports/baseball?print=true')
            self.assertIsNone(row['allowed'])


if __name__ == '__main__': unittest.main()
