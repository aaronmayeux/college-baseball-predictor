"""Offline full-field equivalence check for a saved refresh with historical fallback."""
import argparse
from itertools import permutations
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tournament.build import build
from tournament.engine import probability


def check(folder):
    baseline=build()
    candidate=build(folder)
    if candidate['teams']!=baseline['teams'] or len(candidate['teams'])!=64:
        raise ValueError('Incomplete or changed field')
    checks={}
    for mode in ('regular_only','conference_inclusive'):
        old=baseline['modes'][mode];new=candidate['modes'][mode]
        pairs=list(permutations(candidate['teams'],2))
        error=max(abs(probability(new['ratings'][a],new['ratings'][b])-
                      probability(old['ratings'][a],old['ratings'][b])) for a,b in pairs)
        if error!=0 or old!=new:
            raise ValueError('Fallback/corroboration changed forecast probabilities or bracket')
        checks[mode]=dict(teams=64,ordered_matchups=len(pairs),max_probability_difference=error,
                         complete_forecast_and_picks_equal=True)
    return dict(refresh=candidate['refresh']['refresh_version'],counts=candidate['refresh']['counts'],
                missing_baseline_games=candidate['refresh']['missing_baseline_games'],modes=checks,
                baseline_preserved=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('refresh',type=Path)
    args=parser.parse_args()
    print(json.dumps(check(args.refresh),indent=2))
