# Schedule-only correction — 2025 development

## Locked protocol

One candidate: conference-inclusive frozen Elo log odds plus a fitted difference in
mean opponent Elo. Use every eligible D1 result through the recorded pre-NCAA cutoff,
including conference tournaments; enforce the existing two-day availability delay.
Repeated opponents count per game. Opponent Elo is measured at that same cutoff,
with date-batched updates and the unchanged regressed previous pre-NCAA state.
The proxy includes each team's own games against its opponents; it is not an
independent or causal measure of schedule quality.

Fit once on 2021–2023 NCAA matchups: one coefficient, training-only RMS scale,
fixed ridge 0.01, no intercept, no parameter search. Do not fit on 2024 or 2025.
2024 eligible pre-NCAA results still update the Elo state carried into 2025.
This extends the earlier diagnostic to full cutoff schedules and all otherwise
qualified teams, removing NCAA component-coverage restrictions. It is a new locked
specification, not an exact reproduction of the older snapshot-date diagnostic.
2021 training participants come from retained NCAA result identities; 2025 entrants
and regional seeds come from the verified pre-cutoff selection announcement.

Require 20 eligible games and current-season ratings for every opponent. Otherwise
use exact Elo for that entire matchup; absent current-season team history blocks
forecasting rather than silently defaulting. Retain exclusions and input IDs.
Small documented gaps do not trigger further collection. Predeclare a diagnostic
that drops one latest eligible game from each team's opponent average (ratings and
fitted weights unchanged) to measure sensitivity to one missing schedule appearance.
It cannot be selected or promoted after scoring.

Persist prepared inputs, fitted model and all 2025 regional probability forecasts
before computing 2025 candidate metrics. Report log loss, Brier, calibration,
secondary winner accuracy, stages, regional groups, coverage/fallback, fixed seed
benchmark, and exact regional advancement scores. Use the existing 5,000-draw paired
regional bootstrap (seed 20240926), exploratory within-season only. Favorable game
and advancement probability scores with no material unexplained sensitivity are
required even to consider a later app review; no automatic promotion.

2024 was already exposed and motivated this test. 2025 is known development data;
neither is an untouched test. No 2026 use, component/net-run reopening, new sources,
cutoff changes, app changes, or regular-only model changes.

## Reproduction

Restore/rebuild baseline and timing/seed v2 as described in [DATA.md](DATA.md), then:

```sh
python3 historical/schedule_only.py prepare
python3 historical/schedule_only.py evaluate
```

Outputs stay in ignored `historical/schedule_only_output/`. Matching locks are reused;
changed code, data or protocol rejects silent overwrites. No NCAA component archive
or new evidence checkpoint is needed.

## Results — September 26, 2026

**Failed the locked probability-score screen; retain Elo and close this candidate
without promotion or retuning.** The correction picks one extra game and regional
champion but assigns worse probabilities overall. This does not establish that
schedule information can never help; it rejects this specific locked correction.

### Coverage and model

All 64 teams qualify in each included season, with no fallback matchups. Training
uses 417 NCAA games (139/141/137 in 2021/2022/2023); 2025 evaluates 136 games.
Eligible schedules span 39–61, 46–62, 46–62 and 46–60 games respectively.
Fitted coefficient: **0.49266278513324113**; training RMS opponent-Elo difference:
**55.635753171120804**. 2024 contributes only eligible Elo state carried into 2025.
There are no new NCAA component counts or related identity/count gaps in this test.
Retained Nolan/official corrections and date-availability assumptions still apply;
provider reconciliation is not independent national completeness certification.

### Game and advancement comparison

| 2025 model | Game log loss ↓ | Game Brier ↓ | Winners | Regional champion log loss ↓ | Regional Brier ↓ | Champions |
|---|---:|---:|---:|---:|---:|---:|
| Elo | 0.660978 | 0.233853 | 86/136 | 1.132374 | 0.633688 | 7/16 |
| Schedule correction | 0.675974 | 0.237253 | 87/136 | 1.240951 | 0.677750 | 8/16 |
| Fixed regional seed | 0.658747 | 0.228176 | 65.8%* | 1.131484 | 0.613595 | 9/16 |

*Seed accuracy gives half credit to exact 50/50 games. These are observed-matchup
scores and separate regional forecasts, not full-bracket pick accuracy.

Candidate-minus-Elo game differences: **+0.014996 log loss, +0.003400 Brier**.
Regional games regress +0.014503/+0.002166 (102 games); super regionals regress
+0.065558/+0.028562 (20). Omaha improves −0.040253/−0.016352 (12), and the final
improves −0.133977/−0.066776 (2). Later-round gains do not offset earlier regressions.

Regional advancement differences: **+0.108577 log loss, +0.044062 Brier**.
Exploratory paired-regional 95% intervals are [−0.180758, +0.474115] and
[−0.088322, +0.187339]. Ten regions improve log loss and nine improve Brier,
but aggregate performance worsens. These intervals include zero, use only sixteen
regional groups, and do not measure future-season uncertainty. Calibration bins,
stage and regional-group metrics are retained in the reproducible ignored report.

The fixed one-appearance deletion diagnostic also loses to Elo: game scores
0.675316/0.237069; advancement 1.236696/0.676150; 88/136 games and 8/16 champions.
No fallback is introduced. This limited missing-appearance check leaves the decision
unchanged; it does not model all possible source errors or recompute opponent Elo
with the deleted results. No new coverage audit or source collection occurred.

### Verification and next step

242 data-free tests pass (175 scripts, 67 historical). New tests cover training-year
rejection, cutoff/postseason outcome invariance, deterministic missing-game sensitivity,
exact fallback, probability symmetry and lock tampering. All five output files rerun
byte-identically. All 136 observed/hypothetical comparisons match; all 16 observed
regional paths qualify and champions match the super-regional field. Restored baseline
and v2 pipelines pass their existing gates; protected fingerprints remain unchanged.
App, regular-only forecasts, prior experiments, cutoffs and raw sources are unchanged.
No 2026 modeling occurred.

The current correction is closed. Next concrete product step: implement a bounded,
free, on-demand Nolan refresh into a separate dataset version, preserving the verified
Elo model, cutoff checks and existing offline demo. Do not reopen broad source audits
or reinterpret repeated development comparisons as an untouched test. Further model
candidates need a distinct hypothesis and a new predeclared chronological protocol.
