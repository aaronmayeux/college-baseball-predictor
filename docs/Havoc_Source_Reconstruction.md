# HAVOC input route: D1Baseball minus excluded games

## Verified result

Aaron explicitly authorized public D1Baseball scraping on September 27, 2026,
superseding the earlier project-level restriction. **A complete Virginia 2023
source pilot now recovers the missing pre-NCAA batting strikeouts and every other
HAVOC count.** No model fitting, performance comparison or app change occurred.

The [D1 batting page](https://d1baseball.com/team/virginia/2023/stats/)
loads 17 player rows in the browser with all required columns. Direct HTTP and
web retrieval returned 403; ordinary browser navigation loaded the public table
without sign-in or a challenge. Season choices include 2021–2024; those other
seasons were not collected. Observed splits are Overall/Home/Away/Conference;
there is no date selector on this page. It shows final-season totals, not an
eligible historical snapshot.

The [2023 schedule](https://d1baseball.com/team/virginia/2023/schedule/)
links all eight NCAA games to official Army, East Carolina, Duke, Florida and TCU
box scores. All eight downloaded successfully. Their expanded batting tables
contain BB/HBP/SO/SB/CS, so neither play-by-play inference nor a full regular-season
box-score collection is needed for this pilot.

| Count | D1 full season | Eight NCAA games removed | Pre-NCAA reconstruction |
|---|---:|---:|---:|
| Games | 65 | 8 | 57 |
| Batting K | 418 | 50 | 368 |
| Walks | 319 | 35 | 284 |
| Hit by pitch | 82 | 8 | 74 |
| Stolen bases | 83 | 12 | 71 |
| Caught stealing | 20 | 4 | 16 |

Original HAVOC is **1.358696**; the fixed net-steals alternative is **1.271739**.
These are feature values, not claims of predictive improvement. Included games
end May 25, before the May 31 12:00 UTC cutoff and its two-day assumed availability
delay. Conference-tournament games remain included. AB/H/runs reconstruct to
2,029/678/519; final runs and each excluded matchup score match retained Nolan data.

## Reproducible checks and limits

`scripts/reconstruct_havoc_pilot.py` verifies the D1 season/team/split, full row
widths, distinct players and independently summed browser totals. For both teams
in every box it checks the exact sport/date, team heading, batting schema and
player sums against published totals. It verifies response hashes and compares
both scores to the retained game. The retained 65-game inventory determines the
57 eligible/eight excluded games; missing or duplicate excluded games and invalid
denominators fail. Seven synthetic tests pass; the real report repeats byte-for-byte.

This is a **one-team proof of the acquisition method**, not national coverage,
a replacement for the practical experiment contract or permission to use
unadjusted final totals. A later scoring correction can remain in reconstructed
earlier counts; historical publication time is not certified. D1 roster omissions,
inconsistent final/box scope, excluded games without full counts and non-D1 games
must be checked for each affected team. Never subtract an incomplete set and call
it pre-NCAA. Do not sum player GP as team games. No 2026 inputs were collected.

For extension, use one consistent numerator/denominator window. This pilot goes
through the final eligible pre-NCAA game, so it cannot silently mix with older
2021/2022 NCAA snapshots. Either remove every game after the chosen existing
snapshot or lock a new conference-inclusive source window before model scoring.
Keep the original two HAVOC formulas, training-only scaling and chronological
selection. Retain Elo for any unsupported matchup. No failed model is reopened.

## Next step

The [bounded chronological expansion](Havoc_Chronological_Experiment.md) now owns
continuation: a fixed 24-team-season sample, two additional complete 2022 reconstructions,
retained partial captures and a source-access blocker. Both formulas remain untested
because training/selection coverage is insufficient. Do not restart collection from
this one-team pilot or change the locked sample after scoring.

Restore the baseline and the separate HAVOC reconstruction evidence per
[DATA.md](DATA.md#havoc-d1baseball-reconstruction-pilot), then run:

```sh
python3 scripts/reconstruct_havoc_pilot.py --raw-dir /absolute/path/to/havoc/raw
python3 -m unittest discover -s scripts -p 'test_reconstruct_havoc_pilot.py'
```

Evidence preserves the rendered D1 table as cell strings (not original server
HTML), its independently summed DOM totals, eight raw official responses and
request metadata, the failed direct request and the derived reconstruction. Raw
data and outputs stay outside Git. Code and this source decision are authoritative
in the repository.
