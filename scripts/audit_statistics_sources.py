"""Read retained discovery probes; no network, feature fitting, or baseline writes."""
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED = {
    '401749148': (2025, '2025-05-16', [3, 5], 301),
    '401750347': (2025, '2025-03-04', [0, 0], 0),
    '401653540': (2024, '2024-05-16', [0, 0], 0),
    '401778093': (2025, '2025-06-15', [3, 4], 581),
}


def audit(root):
    for meta_path in sorted(root.glob('*.meta.json')):
        meta = json.loads(meta_path.read_text())
        if meta.get('http_status') == 200:
            data = (root / meta_path.name.removesuffix('.meta.json')).read_bytes()
            if hashlib.sha256(data).hexdigest() != meta['sha256']:
                raise ValueError(f'Changed source bytes: {meta_path.name}')
    results = []
    for event, (season, date, expected_counts, expected_plays) in EXPECTED.items():
        name = f'espn_{event}.json'
        meta = json.loads((root / (name + '.meta.json')).read_text())
        expected_url = ('https://site.api.espn.com/apis/site/v2/sports/'
                        f'baseball/college-baseball/summary?event={event}')
        if meta.get('http_status') != 200 or meta['url'] != expected_url:
            raise ValueError(f'Unexpected source: {event}')
        data = json.loads((root / name).read_text())
        header = data['header']
        if (str(header['id']) != event or header['season']['year'] != season
                or not header['competitions'][0]['date'].startswith(date)):
            raise ValueError(f'Wrong game or season: {event}')
        counts, teams = [], []
        for team in data['boxscore']['players']:
            group, = [g for g in team['statistics'] if g['type'] == 'pitching']
            counts.append(len(group['athletes']))
            outs, pitches = 0, []
            for athlete in group['athletes']:
                stats = dict(zip(group['labels'], athlete['stats']))
                innings, fraction = stats['IP'].split('.')
                if fraction not in {'0', '1', '2'}:
                    raise ValueError('Invalid baseball innings')
                outs += 3 * int(innings) + int(fraction)
                pc = int(stats['PC'])
                if pc <= 0 or pc != int(stats['PC-ST'].split('-')[0]):
                    raise ValueError('Missing or inconsistent pitch count')
                pitches.append(pc)
            if group['athletes'] and outs != 27:
                raise ValueError('Selected complete nine-inning game does not reconcile')
            teams.append(dict(team=team['team']['displayName'],
                              pitcher_rows=len(pitches), pitches=pitches,
                              outs=outs if pitches else None))
        if counts != expected_counts or len(data.get('plays', [])) != expected_plays:
            raise ValueError(f'Snapshot differs from documented probe: {event}')
        results.append(dict(event=event, season=season, date=date, teams=teams,
                            play_records=expected_plays))
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path(__file__).resolve().parents[1]
                        / 'historical/statistics_discovery/raw')
    args = parser.parse_args()
    print(json.dumps(audit(args.raw_dir), indent=2))
