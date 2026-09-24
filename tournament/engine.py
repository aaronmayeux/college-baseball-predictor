"""Exact advancement odds and a coherent game-by-game favorites bracket.

Ratings stay frozen. Games are conditionally independent given those ratings.
No home advantage, reseeding, pitcher availability or strength uncertainty.
"""
from collections import defaultdict
from itertools import product
import math


def probability(rating_a, rating_b):
    if not all(math.isfinite(x) for x in (rating_a, rating_b)):
        raise ValueError('Ratings must be finite')
    # Stable logistic, including synthetic extreme ratings.
    x = (rating_b - rating_a) * math.log(10) / 400
    return math.exp(-x) / (1 + math.exp(-x)) if x >= 0 else 1 / (1 + math.exp(x))


def series_probability(p):
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError('Invalid game probability')
    return p * p * (3 - 2 * p)


def next_game(entrants, results):
    """Entrants are in opening-game order: A/B, C/D. Results are (winner, loser)."""
    n = len(results)
    if n < 2:
        return entrants[n * 2:n * 2 + 2]
    if n == 2:
        return results[0][1], results[1][1]
    if n == 3:
        return results[0][0], results[1][0]
    if n == 4:
        return results[2][0], results[3][1]
    if n == 5:
        return results[3][0], results[4][0]
    if n == 6 and results[5][0] != results[3][0]:
        return results[3][0], results[4][0]
    return None


def group_probabilities(entrants, p):
    """Enumerate first five results, then integrate the final and possible reset."""
    if len(entrants) != 4 or len(set(entrants)) != 4:
        raise ValueError('A group requires four unique entrants')
    odds = dict.fromkeys(entrants, 0.0)

    def visit(results, weight):
        a, b = next_game(entrants, results)
        chance = p(a, b)
        if not math.isfinite(chance) or not 0 <= chance <= 1:
            raise ValueError('Invalid game probability')
        if len(results) == 5:
            # a is undefeated; b needs consecutive wins, a needs either win.
            odds[a] += weight * (chance + (1 - chance) * chance)
            odds[b] += weight * (1 - chance) ** 2
            return
        if chance:
            visit(results + [(a, b)], weight * chance)
        if chance < 1:
            visit(results + [(b, a)], weight * (1 - chance))

    visit([], 1.0)
    return odds


def series_mixture(left, right, p):
    odds = defaultdict(float)
    for a, wa in left.items():
        for b, wb in right.items():
            q = series_probability(p(a, b))
            odds[a] += wa * wb * q
            odds[b] += wa * wb * (1 - q)
    return dict(odds)


def group_mixture(slots, p):
    odds = defaultdict(float)
    for entries in product(*(list(slot.items()) for slot in slots)):
        weight = math.prod(w for _, w in entries)
        if not weight:
            continue
        for team, chance in group_probabilities([t for t, _ in entries], p).items():
            odds[team] += weight * chance
    return dict(odds)


def validate(regions, ratings):
    if len(regions) != 16 or len({r['id'] for r in regions}) != 16:
        raise ValueError('Require 16 unique regionals in bracket order')
    teams = [t for r in regions for t in r['teams']]
    if any(len(r['teams']) != 4 for r in regions) or len(set(teams)) != 64:
        raise ValueError('Require 64 unique teams, four per regional')
    if set(teams) != set(ratings) or not all(math.isfinite(r) for r in ratings.values()):
        raise ValueError('Require exactly one finite rating for every field team')


def forecast(regions, ratings):
    """Regions: left side top-to-bottom, then right; teams in 1,2,3,4 seed order."""
    validate(regions, ratings)
    pairs = {(a, b): probability(ra, rb) for a, ra in ratings.items()
             for b, rb in ratings.items() if a != b}
    p = lambda a, b: pairs[a, b]
    regional = [group_probabilities([r['teams'][i] for i in (0, 3, 1, 2)], p) for r in regions]
    supers = [series_mixture(regional[i], regional[i + 1], p) for i in range(0, 16, 2)]
    omaha = [group_mixture(supers[i:i + 4], p) for i in (0, 4)]
    champion = series_mixture(*omaha, p)
    advancements = {t: dict(super_regional=0.0, omaha=0.0, final=0.0, champion=champion.get(t, 0.0)) for t in ratings}
    for stage, groups in [('super_regional', regional), ('omaha', supers), ('final', omaha)]:
        for group in groups:
            if not math.isclose(sum(group.values()), 1, abs_tol=1e-10):
                raise ValueError('Probability mass failed')
            for t, chance in group.items():
                advancements[t][stage] = chance
    if not math.isclose(sum(champion.values()), 1, abs_tol=1e-10):
        raise ValueError('Championship mass failed')
    for row in advancements.values():
        values = [1.0, *row.values(), 0.0]
        if any(a + 1e-10 < b for a, b in zip(values, values[1:])):
            raise ValueError('Non-monotone advancement probability')
    return dict(advancement=advancements, picks=pick_bracket(regions, p),
                method='exact_enumeration_fixed_independent_game_probabilities')


def pick_bracket(regions, p, choose=None):
    """One legal path; per-game favorite, lexical ID tie-break. Not contest optimization.

    choose is an optional winner callback used for alternate paths and rule tests.
    Group losses reset at the next stage; all games share this tournament record.
    """
    games, rounds = [], []

    def game(a, b, stage, group, number):
        chance = p(a, b)
        winner = choose(a, b, chance) if choose else (a if chance > .5 else b if chance < .5 else min(a, b))
        if winner not in (a, b) or a == b:
            raise ValueError('Invalid game winner or matchup')
        loser = b if winner == a else a
        games.append(dict(id=f'{group}-g{number}', stage=stage, group=group,
                          number=number, a=a, b=b, probability_a=chance,
                          winner=winner, loser=loser))
        return winner, loser

    def group(entrants, stage, ident, label):
        results = []
        while (pair := next_game(entrants, results)) is not None:
            results.append(game(*pair, stage, ident, len(results) + 1))
        winner = results[-1][0]
        rounds.append(dict(id=ident, stage=stage, label=label, entrants=list(entrants), winner=winner))
        return winner

    def series(a, b, stage, ident, label):
        wins = {a: 0, b: 0}
        n = 0
        while max(wins.values()) < 2:
            n += 1
            winner, _ = game(a, b, stage, ident, n)
            wins[winner] += 1
        rounds.append(dict(id=ident, stage=stage, label=label, entrants=[a, b], winner=winner))
        return winner

    regional = [group([r['teams'][i] for i in (0, 3, 1, 2)], 'regional', r['id'], r['name']) for r in regions]
    supers = [series(regional[i], regional[i + 1], 'super_regional', f'super-{i//2+1}',
                     f'Super regional {i//2+1}') for i in range(0, 16, 2)]
    finalists = [group(supers[i:i + 4], 'omaha', f'omaha-{i//4+1}',
                       f'Omaha group {i//4+1}') for i in (0, 4)]
    champion = series(*finalists, 'championship_series', 'final', 'Championship series')
    return dict(champion=champion, rounds=rounds, games=games,
                policy='Per-game favorite; stable ID breaks exact ties. Not a most-likely complete path or optimized contest entry.')
