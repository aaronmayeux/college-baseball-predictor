# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed — practical OBP/ERA experiment

[Protocol/results](Team_Component_Experiment.md) owns the experiment; [DATA](DATA.md#practical-team-component-experiment)
owns restoration. Used retained NCAA conference-inclusive/all-opponent snapshots,
including small count gaps. Trained 2021–2022, selected 2023, refit through 2023,
evaluated previously exposed 2024. Five earlier identity gaps used Elo fallback;
2023/2024 each cover all 64 teams.

Combined OBP/ERA won selection but **failed 2024**: game log loss 0.620988 → 0.630395,
Brier 0.215786 → 0.221404; winners 89 → 88/133. Regional advancement worsened too;
champions 10 → 9/16. Flagged-pair Elo fallback and omitting 2021 from fitting did not
reverse the conclusion. **Close raw OBP/ERA without promotion; keep Elo.** Minor gaps
did not block the test and do not justify another cleanup round.

## Verification

230 tests pass; baseline/v2 rebuild succeeds; experiment reruns byte-identically.
270 observed/hypothetical pairing checks agree; all 32 regional paths qualify.
App, baseline, both modes and source evidence unchanged. Free retained inputs only;
no new evidence ZIP, paid service, 2025 candidate evaluation or 2026 modeling.

## Next concrete step

Lock one bounded **schedule-adjusted team-component** experiment using retained
opponent/Elo histories and NCAA snapshots. Define adjustment and chronology before
fitting; 2024 remains exposed development evidence, not an untouched test. Preserve
small-gap tolerance, leakage checks and Elo fallback. Do not retune raw OBP/ERA,
reopen net-run, resume broad coverage audits or individual pitchers/Stillwater.
D1 remains reference-only; UI/hosting work deferred.
