"""Offline pitching checks and descriptive workload; no quality thresholds."""
from collections import defaultdict
from audit_season_appearances import count
from sidearm_structured import only, payload
from eligibility import reject

COMPONENTS = ('AB', 'BB', 'HBP', 'SF', 'SH', 'CI')
FIELDS = ('outs', 'H', 'R', 'ER', 'SO', 'BB', 'BF')


def qualify_appearances(appearances, opponent_pa, team_bf):
    """Require explicit pitching GS and independently summed PA components."""
    if not appearances or len({p['match_key'] for p in appearances}) != len(appearances):
        raise ValueError('Missing/duplicate pitchers')
    for p in appearances:
        c = p['counts']
        for f in set(FIELDS + COMPONENTS + ('GS',)):
            if type(c.get(f)) is not int or c[f] < 0:
                raise ValueError('Missing/invalid pitching count: ' + f)
        if c['GS'] not in (0, 1):
            raise ValueError('Invalid pitching start flag')
        if c['BF'] != sum(c[f] for f in COMPONENTS):
            raise ValueError('Pitcher BF differs from components')
        if c['SO'] > c['BF'] or c['H'] > c['AB']:
            raise ValueError('Impossible pitching counts')
        np = p.get('pitch_count')
        if np is not None and (type(np) is not int or np <= 0):
            raise ValueError('Invalid pitch count')
    if sum(p['counts']['GS'] for p in appearances) != 1:
        raise ValueError('Expected one explicit pitching start')
    observed = sum(p['counts']['BF'] for p in appearances)
    if observed != opponent_pa or observed != team_bf:
        raise ValueError('BF disagrees with opponent PA or team total')
    return dict(BF=observed, opponent_PA=opponent_pa, team_BF=team_bf)


def structured_game(text, url, config, appearances):
    data = only(payload(text, url)['boxscore']['boxscore'].values())
    aliases = config.get('box_team_aliases', {})
    normalize = lambda n: aliases.get(n.strip(), n.strip()).casefold()
    sides = [data['homeTeam'], data['visitingTeam']]
    team = only(t for t in sides if normalize(t['name']) == normalize(config['team_name']))
    opponent = only(t for t in sides if t is not team)
    bat = opponent['totals']['hitting']
    pa = sum(count(bat[f]) for f in ('atBats', 'walks', 'hitByPitch', 'sacrificeFlies',
                                   'sacrificeHits', 'reachedOnCatchersInteference'))
    # Retain copies, never mutate original appearance audits.
    players = [dict(p, counts=dict(p['counts'], CI=count(p['raw']['catchersInterferenceAllowed'])))
               for p in appearances]
    check = qualify_appearances(players, pa, count(team['totals']['pitching']['battersFaced']))
    return players, check


def summarize(players):
    grouped = defaultdict(list)
    for p in players:
        grouped[p['match_key']].append(p)
    output = []
    for key, apps in sorted(grouped.items()):
        c = {f: sum(p['counts'][f] for p in apps) for f in FIELDS}
        starts = sum(p['counts']['GS'] for p in apps)
        relief = len(apps) - starts
        role = 'mixed' if starts and relief else 'starter_only' if starts else 'relief_only'
        pitches = [p['pitch_count'] for p in apps if p.get('pitch_count') is not None]
        output.append(dict(player_key=key, name=apps[0]['name'], appearances=len(apps),
            starts=starts, relief_appearances=relief, observed_role=role, counts=c,
            pitches=sum(pitches) if len(pitches) == len(apps) else None,
            known_pitches=sum(pitches), pitch_count_appearances=len(pitches),
            max_appearance_outs=max(p['counts']['outs'] for p in apps),
            strikeout_minus_walk_rate=(c['SO']-c['BB'])/c['BF'] if c['BF'] else None,
            ERA=27*c['ER']/c['outs'] if c['outs'] else None,
            RA9=27*c['R']/c['outs'] if c['outs'] else None,
            rest_status='unknown'))
    return output


def aggregate(records, games, team_id, cutoff, phases, season_ok):
    expected = {g['game_id'] for g in games if team_id in (g['team_a_id'], g['team_b_id'])
                and reject(g, cutoff, phases) is None}
    indexed = {}
    for r in records:
        if r['game_id'] is not None:
            if r['game_id'] in indexed:
                raise ValueError('Duplicate game ID')
            indexed[r['game_id']] = r
    blocked = sorted(g for g in expected if g not in indexed or indexed[g]['issues']
                     or not indexed[g].get('pitchers'))
    complete = bool(expected) and not blocked and season_ok
    players = summarize([p for g in sorted(expected) for p in indexed[g]['pitchers']]) if complete else None
    return dict(expected_games=len(expected), eligible_game_ids=sorted(expected), blocked_game_ids=blocked,
                complete=complete, season_reconciliation_pass=season_ok, forecast_cutoff=cutoff.isoformat(),
                players=players, rest_status='unknown')
