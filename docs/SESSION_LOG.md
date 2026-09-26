# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed

Followed the team-level-first plan with a concrete experiment, using retained Warren Nolan results plus official corrections and v2 timing. No new collection or individual pitcher work. The [experiment report](Team_Run_Experiment.md) owns source tradeoffs, locked settings, results and reproduction.

Added a repeatable offline batch importer and challenger evaluation: all 256 tournament team-seasons in 2021–2024, 550 NCAA matchups in each mode, no missing team features. Locked scoring, run-prevention and net-run candidates before fitting. Trained on 2021–2022, selected net runs/game on 2023, refit through 2023 and checked once on 2024. Both probability metrics improved slightly in primary 2024 scoring, but winner accuracy fell 93/133 → 90/133; group and conference-inclusive results were mixed. **Keep Elo in the app.** Run prevention includes defense; richer component stats remain unqualified.

## Verification

192 tests pass (152 scripts, 40 historical). Baseline/v2 cached rebuilds succeeded. Repeat preparation/evaluation is byte-identical; protected baseline/v2 inputs and app remain unchanged. No raw data committed or new evidence ZIP needed. Restore the baseline and v2 checkpoints via [DATA](DATA.md), then run `historical/team_runs.py prepare` and `evaluate`.

## Next

Evaluate the unchanged candidate's historical regional advancement after qualifying selection-day routing and locking scoring. No retuning on 2024; no app promotion from the small game-level gain. If advancement remains mixed, close this candidate. Any richer component-data acquisition needs a bounded sample/access decision, not renewed piecemeal probes.

Preserve both modes, common samples, Elo fallback and evaluation rules. 2025 remains development and unused for this candidate; 2026 excluded. Individual pitchers, Stillwater preflight, UI/hosting/spreadsheet work stay deferred.
