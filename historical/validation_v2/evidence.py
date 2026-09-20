"""Versioned evidence overlay; never rewrite the preserved baseline inventory."""
import copy
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.parse_sidearm import clean

RAW = ROOT / 'research/raw'
OUT = ROOT / 'validation_v2/output'
SOURCES = {
    'kent_recap_20230426.html': 'https://kentstatesports.com/news/2023/4/26/baseball-fly-the-flag-flashes-double-up-buckeyes-10-5',
    'ohio_recap_20230426.html': 'https://ohiostatebuckeyes.com/news/2023/4/26/buckeyes-split-home-and-home-series-against-kent-state',
    'columbia_recap_20230422.html': 'https://gocolumbialions.com/news/2023/4/22/baseball-defeats-dartmouth-in-game-one-game-two-called-due-to-darkness',
    'columbia_recap_20230423.html': 'https://gocolumbialions.com/news/2023/4/23/baseball-sweeps-dartmouth-with-two-wins-on-senior-day',
    'ncaa_selections_2023.html': 'https://www.ncaa.com/news/baseball/article/2023-05-29/2023-ncaa-division-i-baseball-championship-bracket-announced',
    'ncaa_selections_2024.html': 'https://www.ncaa.com/news/baseball/article/2024-05-27/2024-ncaa-division-i-baseball-championship-bracket-announced',
}
SOURCES.update({f'ncaa_di_selections_{y}.html': f'https://www.ncaa.com/news/baseball/article/{d}/{y}-ncaa-di-baseball-championship-bracket-announced'
    for y, d in [(2022, '2022-05-30'), (2025, '2025-05-26')]})

SOURCES.update({
    'fordham_recap_20230422.html': 'https://fordhamsports.com/news/2023/4/22/baseball-game-suspended-in-9th-rams-lead-12-9.aspx',
    'fordham_recap_20230423.html': 'https://fordhamsports.com/news/2023/4/23/baseball-falls-in-finale-at-richmond.aspx',
})
SOURCES.update({
    'canisius_2022.html': 'https://gogriffs.com/sports/baseball/schedule/2022',
    'arizona_2022.html': 'https://arizonawildcats.com/sports/baseball/schedule/2022',
    'uncg_2022.html': 'https://uncgspartans.com/sports/baseball/schedule/2022',
    'latech_2024.html': 'https://latechsports.com/sports/baseball/schedule/2024',
    'latech_recap_20240601.html': 'https://latechsports.com/news/2024/6/1/baseball-diamond-dogs-season-ends-in-the-fayetteville-regional',
})

TIMING = {
    'wn:2023:28885': dict(start_date='2023-04-22', completion_date='2023-04-23',
        official_schedule_date='2023-04-22', teams={'wn:Fordham', 'wn:Richmond'}, scores={9, 12},
        sources=['fordham_recap_20230422.html', 'fordham_recap_20230423.html'],
        reason='Suspended April 22, completed 12–9 Sunday April 23; original provider completion date confirmed.'),
    'wn:2023:30070': dict(start_date='2023-04-26', completion_date='2023-04-26',
        official_schedule_date='2023-04-25', teams={'wn:Kent-State', 'wn:Ohio-State'}, scores={5, 10},
        sources=['kent_recap_20230426.html', 'ohio_recap_20230426.html'],
        reason='Both schools report the completed 10–5 game Wednesday April 26; Kent schedule date is stale.'),
    'wn:2023:28465': dict(start_date='2023-04-22', completion_date='2023-04-23',
        official_schedule_date='2023-04-22', teams={'wn:Columbia', 'wn:Dartmouth'}, scores={13, 14},
        sources=['columbia_recap_20230422.html', 'columbia_recap_20230423.html'],
        reason='Suspended tied 11–11 April 22; resumed and finished 14–13 April 23 in 12 innings.'),
}

def read_source(name):
    path = RAW / name
    meta = json.loads(path.with_name(path.name + '.meta.json').read_text())
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != meta['sha256'] or meta.get('http_status') != 200:
        raise ValueError('Invalid evidence bytes: ' + name)
    if name in SOURCES and meta['url'] != SOURCES[name]:
        raise ValueError('Unexpected source URL: ' + name)
    return data.decode('utf-8'), dict(source_url=meta['url'], retrieved_at=meta['retrieved_at'],
        raw_sha256=meta['sha256'], raw_path='research/raw/' + name)

def article_text(html):
    match = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if match:
        values = json.loads(match[1])
        bodies = [clean(v) for v in values if isinstance(v, str) and len(v) > 500
                  and ('<p' in v or '<br' in v)]
        if not bodies:
            raise ValueError('Missing official article body')
        return ' '.join(bodies)
    return clean(re.sub(r'<(script|style)\b.*?</\1>', '', html, flags=re.S))

def verify_timing():
    required = {
        'fordham_recap_20230422.html': ['12-9 win', 'resumed on Sunday morning', 'final three outs'],
        'fordham_recap_20230423.html': ["yesterday's suspended game with a win", 'April 23, 2023'],
        'kent_recap_20230426.html': ['10-5 victory on Wednesday', 'struck out the side in the ninth'],
        'ohio_recap_20230426.html': ['10-5', 'Wednesday', 'top of the ninth'],
        'columbia_recap_20230422.html': ['11-11', 'darkness', 'resume at 12:15 p.m. on Sunday'],
        'columbia_recap_20230423.html': ['14-13', '12 innings', "Saturday's suspended game", 'Sunday'],
    }
    refs = {}
    for name, phrases in required.items():
        html, refs[name] = read_source(name)
        body = article_text(html)
        if not all(p in body for p in phrases):
            raise ValueError('Timing evidence assertion failed: ' + name)
        # Article date is checked separately from the URL and current-site navigation.
        day = name[-13:-5]
        expected = f'{day[:4]}-{day[4:6]}-{day[6:]}'
        if expected not in html:
            raise ValueError('Missing article date: ' + name)
    return refs

def overlay(games, refs):
    result = copy.deepcopy(games)
    for game in result:
        correction = TIMING.get(game['game_id'])
        if correction is None:
            continue
        if ({game['team_a_id'], game['team_b_id']} != correction['teams'] or
                {game['runs_a'], game['runs_b']} != correction['scores'] or
                game['game_date'] != correction['completion_date'] or game['timing_review'] != (game['game_id'] != 'wn:2023:28885')):
            raise ValueError('Timing overlay does not match preserved input: ' + game['game_id'])
        game['original_timing_fields'] = {k: game[k] for k in ['game_date', 'timing_review']}
        game['start_date'] = correction['start_date']
        game['completion_date'] = correction['completion_date']
        game['timing_review'] = False
        game['timing_resolution'] = dict(reason=correction['reason'],
            evidence_refs=[refs[n] for n in correction['sources']], precision='calendar_date',
            exact_completion_time=None, point_in_time_certified=False)
    return result

if __name__ == '__main__':
    from research.fetch import fetch
    for name, url in SOURCES.items():
        _, meta = fetch(name, url)
        print(name, meta.get('http_status'), meta.get('error', ''))
