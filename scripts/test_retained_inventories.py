"""Reviewed school aliases must fail closed outside their evidence scope."""
import copy
import unittest
from unittest.mock import patch

from audit_retained_inventories import reviewed_aliases
from audit_official_season_inventory import reconcile


class ReviewedAliases(unittest.TestCase):
    def setUp(self):
        self.config = dict(season=2025, schedule_url='https://school.test/schedule/2025')
        self.review = dict(self.config, aliases={
            'Miami': dict(team_id='wn:Miami-FL', website='https://miami.test/', location='Coral Gables, FL'),
            '#4 Miami': dict(team_id='wn:Miami-FL', website='https://miami.test/', location='Coral Gables, FL')})
        self.identities = {'School': 'wn:School', 'Miami (FL)': 'wn:Miami-FL', 'Miami (OH)': 'wn:Miami-OH'}
        self.games = [dict(opponent=dict(title=n, website=r['website'], location=r['location']))
                      for n, r in self.review['aliases'].items()]

    def call(self):
        data = {'schedule': {'schedules': {'schedules-baseball,2025': {'games': self.games}}}}
        with patch('audit_retained_inventories.payload', return_value=data):
            return reviewed_aliases('', self.config, self.review, self.identities)

    def test_ranked_variants_map_without_modifying_source(self):
        original = copy.deepcopy(self.games)
        self.assertEqual(self.call(), {'Miami': 'wn:Miami-FL'})
        self.assertEqual(self.games, original)
        self.assertNotIn('Miami', self.identities)

    def test_wrong_season_or_source_cannot_reuse_review(self):
        for key, value in [('season', 2026), ('schedule_url', 'https://other.test/schedule/2025')]:
            with self.subTest(key=key):
                original = self.config[key]
                self.config[key] = value
                with self.assertRaises(ValueError): self.call()
                self.config[key] = original

    def test_each_occurrence_requires_both_metadata_fields(self):
        for key, value in [('website', 'https://oxford.test/'), ('location', 'Oxford, OH'), ('website', None)]:
            with self.subTest(key=key, value=value):
                changed = copy.deepcopy(self.games[0])
                changed['opponent'][key] = value
                self.games.append(changed)
                with self.assertRaises(ValueError): self.call()
                self.games.pop()

    def test_new_title_or_missing_reviewed_title_blocks(self):
        self.games[1]['opponent']['title'] = '#5 Miami'
        with self.assertRaises(ValueError): self.call()
        self.games.pop()
        with self.assertRaises(ValueError): self.call()

    def test_unknown_conflicting_or_overridden_identity_blocks(self):
        for target in ['wn:Unknown', 'wn:Miami-OH']:
            self.review['aliases']['#4 Miami']['team_id'] = target
            with self.assertRaises(ValueError): self.call()
        self.review['aliases']['#4 Miami']['team_id'] = 'wn:Miami-FL'
        self.identities['Miami'] = 'wn:Miami-OH'
        with self.assertRaises(ValueError): self.call()

    def test_alias_does_not_override_date_score_or_duplicate_gates(self):
        identities = dict(self.identities, **self.call())
        game = dict(game_id='g1', team_a_id='wn:School', team_b_id='wn:Miami-FL',
                    game_date='2025-03-01', runs_a=2, runs_b=1)
        row = dict(date='2025-03-01', teams=['School', 'Miami'], runs=[2, 1], box_url='box1')
        self.assertTrue(reconcile([row], [game], identities, 'wn:School')['inventory_pass'])
        for changed in [dict(row, date='2025-03-02'), dict(row, runs=[1, 2])]:
            self.assertFalse(reconcile([changed], [game], identities, 'wn:School')['inventory_pass'])
        self.assertFalse(reconcile([row, dict(row, box_url='box2')], [game], identities, 'wn:School')['inventory_pass'])


if __name__ == '__main__': unittest.main()
