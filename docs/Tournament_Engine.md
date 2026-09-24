# Tournament engine and first app

## Contract

The 2025 development engine freezes the existing neutral Elo ratings separately for regular-only and conference-inclusive inputs. It checks the baseline coverage/correction gates, retained timing evidence, independent schedules and cutoff-eligible NCAA selections before building. Every team needs eligible current-season results. Missing inputs block the build; there are no default ratings or player-rest assumptions.

`python3 -m tournament.build` writes `app/data/forecast.json` (ignored by Git). This is an offline rebuild, not a fresh internet import. Restore the original baseline and timing/seed checkpoints using [DATA.md](DATA.md) first. Existing historical outputs are read, never rewritten.

## Rules and placement

Verified against the [2024–25 NCAA pre-championship manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2024-25D1MBA_PreChampsManual.pdf), printed pages 15–16 and Appendix A, and the [NCAA selection-day 2025 bracket retained by Tennessee](https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/utsports.com/documents/2025/5/26/2025_NCAA_Bracket.pdf). The bracket PDF was visually inspected; SHA-256 `ddc059aa2776eb4aa517d9a94ed2dc2e9dbdcc5af6c8633084d2622d6fad5ce7`. Its bytes and retrieval metadata are retained separately in `College_Baseball_Tournament_Format_Evidence.zip`. The cutoff-eligible field/seed article remains in the timing/seed checkpoint. No actual NCAA tournament winner or final record determines ratings or placement.

`tournament/field.py` owns the fixed host order. Read each side of the selection bracket top to bottom: consecutive regional pairs feed a super regional; four consecutive super winners feed one Omaha group. Omaha opening matchups are consecutive super winners within that group. No reseeding.

Four-team groups open 1–4 and 2–3 (regionals), then losers meet, winners meet, the surviving one-loss teams meet, and the undefeated team meets the survivor. A loss by the undefeated team forces a reset. Omaha uses the same elimination structure with the predetermined opening pairings. Group losses start over in Omaha. Supers and the national final stop when either team wins twice. Game numbers in the app are local to each group, not broadcast schedule numbers. The first model does not simulate dates, weather, home-team designations or workload.

## Probabilities and picks

Advancement probabilities are exact under the fixed-strength, independent-game assumption, not Monte Carlo estimates. Enumerate regional paths; combine regional-winner distributions into each best-of-three; integrate possible Omaha entrants and group paths; combine finalists into the championship series. All possible opponents contribute. Totals reconcile to 16 regional winners, eight Omaha entrants, two finalists and one champion. This does not establish predictive calibration or bracket accuracy.

The displayed bracket separately picks the favorite in every game, breaking exact ties by stable team ID. It is a consistent complete path, not the globally most likely path or a contest-scoring optimum. Consequently its champion can differ from the highest marginal championship probability. Shared tournament game records preserve winners, losers and conditional matchup probabilities. There are no rating updates from generated results.

The export records cutoff, modes, model/engine versions, source fingerprints and limitations. Forecast data and generated game-by-game exports remain outside Git.

## App and reproduction

```sh
python3 -m tournament.build
python3 -m http.server 8000 --bind 127.0.0.1 --directory app
```

Open `http://localhost:8000`. Serve only `app/`, not the repository's private evidence. The static app has no external dependencies or network analytics. It offers both forecast modes, every round, game details, championship odds, all-team advancement odds, neutral head-to-head/series comparisons and CSV exports. It intentionally has no unqualified radar statistics.

For an offline browser copy with embedded predictions:

```sh
python3 -m tournament.build --standalone /absolute/path/College_Baseball_Predictor.html
```

Open that file in a browser; no server is needed. Some mobile file-preview apps do not execute JavaScript, so a hosted URL is still the next usability step. Hosting has not been configured. Do not represent a local development server or an HTML attachment as a deployed site.

## Verification

Nine new data-free tests cover all double-elimination outcome paths, reset/no-reset behavior, best-of-three stopping, the 60% → 64.8% benchmark, fair 64-team probabilities, fixed routing, field validation and invalid ratings. The historical and scripts suites total 121 passing tests. The retained-data build checks all 64 teams in both modes and matches existing v2 probabilities across 136 observed matchups per mode within `1.12e-16`. Those observed results validate adapter equivalence only, not advancement accuracy. Original baseline and timing/seed checkpoint data remain byte-identical.

JavaScript syntax and standalone DOM checks pass for all stage/mode controls, the 64-team table, same-team guard and both CSV exports (using linkedom with its missing select-value setter supplied). Actual visual/browser testing is still outstanding: the workspace has no browser and Playwright’s browser download failed. Verify phone/desktop rendering, stage/mode controls and CSV downloads before calling the interface acceptance complete. The current limitations remain historical development inputs, unmodeled player availability/venue effects, no strength uncertainty and no qualified fresh nationwide ingestion.
