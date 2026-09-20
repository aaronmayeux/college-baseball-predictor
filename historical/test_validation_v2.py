"""Offline regressions for timing, evidence integrity and seed leakage gates."""
import copy
import datetime as dt
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'validation_v2'))
import evidence
from evidence import TIMING, overlay
from independent import compare, phase, name_key
from seeds import parse, probability, eligible
from eligibility import available_at, reject

class ValidationTests(unittest.TestCase):
    def test_overlay_preserves_original_and_waits_for_completion(self):
        games = []
        for gid, c in TIMING.items():
            a, b = sorted(c['teams'])
            games.append(dict(game_id=gid, team_a_id=a, team_b_id=b,
                runs_a=min(c['scores']), runs_b=max(c['scores']), game_date=c['completion_date'],
                timing_review=gid != 'wn:2023:28885', stage='regular_season', reciprocal_check='pass'))
        old = copy.deepcopy(games)
        refs = {name: {} for c in TIMING.values() for name in c['sources']}
        corrected = overlay(games, refs)
        self.assertEqual(old, games)
        columbia = next(g for g in corrected if g['game_id'] == 'wn:2023:28465')
        self.assertEqual(columbia['start_date'], '2023-04-22')
        self.assertEqual(available_at(columbia).isoformat(), '2023-04-25T00:00:00+00:00')
        self.assertIsNotNone(reject(columbia, dt.datetime.fromisoformat('2023-04-24T12:00:00+00:00'), ['regular_season']))
        self.assertIsNone(reject(columbia, available_at(columbia), ['regular_season']))
        games[0]['runs_a'] = 999
        with self.assertRaises(ValueError):
            overlay(games, refs)

    def test_corrupted_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'example.html'
            p.write_text('changed')
            p.with_name(p.name + '.meta.json').write_text(json.dumps(dict(http_status=200,
                sha256=hashlib.sha256(b'original').hexdigest())))
            with patch.object(evidence, 'RAW', pathlib.Path(d)), self.assertRaises(ValueError):
                evidence.read_source('example.html')

    def test_seed_cutoff_includes_modification_time(self):
        cut = dt.datetime.fromisoformat('2024-05-29T12:00:00+00:00')
        record = dict(published_at=cut.isoformat(), modified_at=cut.isoformat())
        self.assertTrue(eligible(record, cut))
        for key in record:
            other = dict(record)
            other[key] = (cut + dt.timedelta(microseconds=1)).isoformat()
            self.assertFalse(eligible(other, cut))

    def test_seed_symmetry_ties_and_order(self):
        self.assertEqual(probability(2, 2), .5)
        for a in range(1, 5):
            for b in range(1, 5):
                self.assertAlmostEqual(probability(a, b) + probability(b, a), 1)
                self.assertEqual(probability(a, b) > .5, a < b)
        self.assertEqual(probability(1, 4), 8 / 9)

    def test_seed_parser_requires_complete_unique_identity(self):
        teams = [dict(name=f'Team {i}', slug=f'Team-{i}') for i in range(64)]
        text = '2024 NCAA Division I Baseball Championship Games '
        for group in range(16):
            text += f'City Regional hosted by Host{group} '
            text += ' '.join(f'#{seed} Team {4*group+seed-1} (1-0)' for seed in range(1, 5)) + ' '
        self.assertEqual(len(parse(text, 2024, teams)), 64)
        for changed in (text.replace('Team 63', 'Unknown'), text.replace('Team 63', 'Team 62'),
                        text.replace('#4 Team 63', '#3 Team 63')):
            with self.assertRaises(ValueError):
                parse(changed, 2024, teams)
        with self.assertRaises(ValueError):
            parse(text, 2025, teams)
        # Navigation cannot supply a missing seed record.
        with self.assertRaises(ValueError):
            parse(text.replace('#4 Team 63 (1-0)', '') + 'LATEST COLLEGE BASEBALL NEWS #4 Team 63 (1-0)', 2024, teams)

    def test_phase_checks_do_not_infer_regular_from_missing_label(self):
        self.assertIsNone(phase(None))
        self.assertIsNone(phase('College Baseball Classic'))
        self.assertEqual(phase('MAC Tournament'), 'conference_tournament')
        row = dict(date='2023-05-24', opponent='B', team_score=4, opponent_score=2, tournament='MAC Tournament')
        obs = dict(team_id='wn:A', opponent_name='B', status='completed', game_date=row['date'],
            runs_for=4, runs_against=2, source_game_id='1', stage='regular_season')
        checks, _, _ = compare([row], [obs], 'wn:A')
        self.assertEqual(checks[0]['phase_status'], 'conflict')
        obs['game_date'] = '2023-05-25'
        checks, _, _ = compare([row], [obs], 'wn:A')
        self.assertEqual(checks[0]['date_score_status'], 'review')

    def test_ambiguous_matches_and_miami_identity(self):
        row = dict(date='2023-04-01', opponent='B', team_score=4, opponent_score=2, tournament=None)
        obs = dict(team_id='wn:A', opponent_name='B', status='completed', game_date=row['date'],
            runs_for=4, runs_against=2, source_game_id='1', stage='regular_season')
        checks, _, _ = compare([row], [obs, dict(obs, source_game_id='2')], 'wn:A')
        self.assertEqual(checks[0]['date_score_status'], 'review')
        self.assertEqual(name_key('Miami', 'wn:Bowling-Green'), 'Miami (OH)')
        self.assertEqual(name_key('Miami', 'wn:Canisius'), 'Miami (FL)')

if __name__ == '__main__':
    unittest.main()
