# Schedule-adjusted team-component experiment

## Locked protocol — before fitting or scoring

One new candidate: unchanged conference-inclusive Elo log odds plus training-scaled
OBP difference, negative ERA difference, and mean-opponent-Elo difference. The third
term learns a schedule correction jointly with the batting/pitching terms; it is not
a causal estimate or separately opponent-adjusted offensive/defensive rating.
Use game-weighted opponent Elo as of the same through-date as each retained NCAA
snapshot. Repeated opponents count once per played game. Only eligible D1 games through
that date enter either the opponent list or the current-year rating updates. Start
each season from the preserved conference-inclusive Elo's regressed prior-season
pre-NCAA state; do not carry omitted late games forward as if they never occurred.
No current-year post-snapshot or NCAA outcomes enter this schedule feature. This
within-snapshot rating includes the team's own games against its opponents; it is a
practical schedule-strength proxy, not an independent measure of opponent quality.

Reuse the exact qualified source values, identity gaps, all-opponent scope, discrepancies,
old snapshots and Elo-fallback rules from [raw OBP/ERA](Team_Component_Experiment.md).
Require at least 20 eligible D1 games for a schedule mean and a current-year rating for
every opponent. Missing components or schedule use exact Elo for the entire matchup.
D1 schedule versus all-opponent NCAA rates remains an explicit scope mismatch. No new
source collection, identities, cutoff changes, net-run work or individual pitchers.

Train on 2021–2022; select this single candidate only if both 2023 log loss and Brier
beat Elo on identical games. Fit coefficient/scaling on training rows only; fixed
ridge 0.01, RMS scaling, no intercept, no hyperparameter search. Refit through 2023
if selected; lock all models before 2024 scoring. If selection fails, record the
failure and retain Elo; any predeclared 2024 candidate diagnostics cannot override it.
Both 2023 and 2024 are exposed development/retrospective seasons. No 2025 candidate
or 2026 use, no untouched-test claim, and no retuning after reading these results.

Predeclared diagnostics, ineligible for selection/promotion: the previously locked raw
OBP/ERA model; a schedule-only addition fitted on the same covered training games;
strict Elo fallback for any flagged pair; and the same three-term candidate fitted
without 2021. The schedule-only diagnostic distinguishes schedule information from
incremental batting/pitching value; do not select it after seeing its 2024 result.

Report same-game log loss, Brier, secondary accuracy, calibration, feature coverage,
fallback counts, stages and regional-group differences. Reuse exact regional enumeration
and complete observed-path checks for 2023/2024. Freeze forecasts before scoring;
report multiclass champion loss/Brier, top-pick accuracy, calibration and 5,000 paired
regional bootstrap draws (seed 20240926), exploratory within-season only. Potential
promotion requires favorable 2024 game and advancement probability scores without
material unexplained sensitivity/stage regressions, followed by separate review.
No automatic deployment: repeated development comparisons cannot certify future gains.

## Reproduction

Restore the original baseline, v2 and combined NCAA checkpoint per [DATA](DATA.md).
Reproduce the unchanged raw-component experiment first, then:

```sh
python3 historical/schedule_components.py prepare --evidence-dir /absolute/path/to/ncaa
python3 historical/schedule_components.py evaluate --evidence-dir /absolute/path/to/ncaa
```

Only ignored `historical/schedule_component_output/` is written. The prepared input,
selection and advancement locks reject silent changes. The prior experiment and its
fingerprints remain intact; reports are reproducible without a new evidence archive.

## Results — September 26, 2026

**Game probabilities improved; regional advancement did not establish a promotion.**
Keep Elo in the app. The single schedule-aware OBP/ERA candidate passed the predeclared
2023 probability-score screen, then improved both 2024 game scores. Its primary regional
champion scores remained slightly worse than Elo, with fewer champions picked. No weights,
source rules or models were changed after scoring. The raw OBP/ERA and net-run candidates
remain closed. Schedule strength is a useful research lead; incremental value from OBP/ERA
has not been demonstrated consistently.

### Coverage and fitting

The schedule check introduced **no additional fallback teams**: 60/64, 63/64, 64/64,
64/64 usable team-seasons in 2021–2024, covering 127/139, 139/141, 137/137 and 133/133
games. The five earlier exact-identity gaps retain Elo fallback. Small source discrepancies,
non-D1 scope and omitted late games remain as recorded in the raw-component report.
Usable schedule inventories contain 36–56, 45–58, 46–62 and 47–62 D1 games respectively.
All 64 teams remain represented in every season, including fallback cases.

The initial fit used 266 covered games; the refit used 403. Refit coefficients for
OBP, negative ERA and opponent Elo were **0.1011086848, 0.2778072541, 0.4922585092**;
training RMS scales were **0.0263141771, 1.1568685177, 54.8728016921**. These are joint
log-odds contributions above unchanged Elo, not separately calibrated stat ratings.

### Game comparison

| Season / model | Log loss ↓ | Brier ↓ | Correct winners |
|---|---:|---:|---:|
| 2023 Elo | 0.628158 | 0.218569 | 91/137 |
| 2023 schedule-aware OBP/ERA | 0.625451 | 0.217955 | 90/137 |
| 2024 Elo | 0.620988 | 0.215786 | 89/133 |
| 2024 schedule-aware OBP/ERA | 0.592047 | 0.204155 | 89/133 |
| 2024 previously locked raw OBP/ERA | 0.630395 | 0.221404 | 88/133 |
| 2024 fixed seed benchmark | 0.660503 | 0.229979 | 65.4%* |

*The unchanged seed benchmark gives half credit to exact 50/50 predictions.
The new candidate improves 2024 log loss by **0.028940** and Brier by **0.011631**,
with unchanged winner accuracy. Gains occur in regional games (−0.026086/−0.009324,
100 games), supers (−0.030160/−0.016081, 18), and Omaha (−0.060322/−0.028157, 12).
The three championship games regress +0.008777/+0.004263. These are correlated
retrospective matchup scores, not complete-bracket accuracy or independent validation.

### Regional advancement

| Season / model | Champion log loss ↓ | Multiclass Brier ↓ | Champions picked |
|---|---:|---:|---:|
| 2023 Elo | 1.065144 | 0.598209 | 9/16 |
| 2023 schedule-aware OBP/ERA | 0.987093 | 0.574904 | 8/16 |
| 2024 Elo | 1.157268 | 0.636643 | 10/16 |
| 2024 schedule-aware OBP/ERA | 1.185875 | 0.637936 | 9/16 |

2024 primary differences are **+0.028607** log loss and **+0.001294** Brier, both
worse. Exploratory paired-regional 95% intervals are [−0.198770, +0.306576] and
[−0.112049, +0.123005]. They include zero and do not estimate future-season uncertainty.
Nine of sixteen regions improve log loss; eight improve Brier. The aggregate game gain
does not establish a better bracket forecast. Calibration bins, stage/group results,
source-covered/actually-adjusted/fallback subsets and full regional scores are reproducible.

### Predeclared diagnostics

Candidate-minus-Elo differences in 2024; negative means better:

| Diagnostic | Game log loss | Game Brier | Advancement log loss | Advancement Brier |
|---|---:|---:|---:|---:|
| Primary schedule-aware OBP/ERA | −0.028940 | −0.011631 | +0.028607 | +0.001294 |
| Flagged matchups use Elo | −0.040385 | −0.015863 | −0.044197 | −0.023815 |
| Same candidate fitted without 2021 | −0.026130 | −0.009396 | +0.053424 | −0.003117 |
| Schedule-only addition | −0.043548 | −0.018772 | −0.130498 | −0.062231 |

Strict fallback routes 21/133 observed 2024 games and 16/137 in 2023 to Elo. It applies
at prediction time, not by deleting flagged training data. Its better 2024 advancement
result shows the bracket conclusion is sensitive to the flagged inputs; it does not
establish that the source rows are wrong. Keep those rows and their uncertainties,
without a new coverage audit. Neither strict fallback nor schedule-only is eligible
for post-hoc selection under this experiment's lock.

The schedule-only diagnostic picks **91/133 games and 10/16 regional champions** in
2024, with game log loss/Brier 0.577440/0.197015 and advancement scores
1.026770/0.574412. However, it loses to Elo in 2023 on both game probability scores
(0.641179/0.223337) and advancement scores (1.076245/0.625614), picking 7/16 champions.
Choosing it because of 2024 would reuse that season for model selection. Likewise,
OBP/ERA helps the schedule-only model in 2023 but hurts it in 2024: the added component
value is unstable across these two exposed seasons.

### Verification and next action

**237 data-free tests pass** (175 scripts, 62 historical, including seven new checks).
The new checks cover future/snapshot/phase/availability exclusions, date batching,
prior-season carry, repeated opponents, missing ratings, exact fallback, training-year
restrictions, selection and numerical agreement with the legacy solver. All five output
files reproduce byte-identically. All 270 observed/hypothetical game comparisons match;
all 32 regional paths qualify and winners match the super-regional fields. The earlier
raw-component experiment remains byte-identical. Baseline/v2 preservation gates pass;
no app, cutoff, prior experiment, source evidence, 2025 candidate or 2026 changes occurred.

**Follow-up completed:** the separately locked [2025 schedule-only development
experiment](Schedule_Only_Development.md) failed game and regional probability-score
comparisons. It is closed without promotion; Elo remains. The earlier diagnostic
above and its original outputs are unchanged.
