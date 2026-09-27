# Offensive walk-rate experiment

## Locked protocol — before scoring

Hypothesis: offensive walks per recorded plate appearance add information beyond Elo
that combined OBP can hide. This is the inventory's BB/PA candidate, not another
OBP/ERA combination, adjusted scoring model or schedule-only correction. One feature,
one fixed ridge penalty, no interactions or coefficient/threshold search.

Use BB / (AB + BB + HBP + SF + SH) from the retained NCAA reports. Include sacrifice
bunts, unlike the OBP denominator; catcher interference is unavailable, so call this
**recorded PA**, not a certified complete PA count. BB includes any intentional walks
in the source and is not a pure plate-discipline measurement. Do not infer strikeouts,
power, pitching control or individual arms from these reports.

Conference-inclusive only. Reuse the original component preparation's exact identity,
dated-source, sample-size and discrepancy rules; do not rerun any closed candidate's
fitting/evaluation. That offline preparation verifies existing evidence, not new source
coverage. Source dates are May 23, 2021; May 25, 2022; May 28, 2023; May 26, 2024.
Retain all-opponent scope, snapshot age, small count differences, omitted games and
non-D1 warnings. Unknown/invalid counts or either missing team force exact Elo for
the whole matchup. Preserve both app modes, source bytes and old experiment code.

Fit on 2021–2022 NCAA games: training-only matchup-difference RMS scaling, fixed Elo
log-odds offset, no intercept, ridge 0.01. Select BB/recorded-PA only if both 2023
log loss and Brier improve over Elo on identical games. Otherwise select Elo and
close this candidate; report its 2023 comparison without searching alternatives.
Refit a selected feature on 2021–2023 and lock before any 2024 candidate scoring.
No candidate scoring on 2025/2026. 2024 is previously exposed retrospective evidence,
not an untouched holdout. The sign is fitted, not forced; no causal claim.

Report full/covered/fallback games, calibration, secondary winner accuracy, stages
and regional groups; compare Elo and the fixed seed benchmark on common samples.
Freeze regional probabilities before reading regional champions. Use the established
exact four-team engine and legal-result-path checks, including agreement with the
super-regional field. Report champion log loss, summed four-class Brier, pick accuracy,
calibration and 5,000 paired-regional bootstrap draws (seed 20240926; exploratory).

Fixed sensitivities, no reselection: flagged matchups revert to Elo; fit the same
selected specification without 2021. Promotion requires both 2024 game and regional
probability scores to improve without material unexplained stage/sensitivity regression,
then a separate deployment review. No automatic app changes, even on a positive result.
One exposed season cannot establish reliable future improvement.

## Reproduction

Restore/rebuild baseline and timing/seed v2 and extract the combined NCAA checkpoint
as described in [DATA.md](DATA.md). No new downloads from statistical providers.

```sh
python3 historical/walk_rate.py prepare --evidence-dir /absolute/path/to/ncaa
python3 historical/walk_rate.py evaluate --evidence-dir /absolute/path/to/ncaa
python3 -m unittest discover -s historical -p 'test_walk_rate.py'
```

Preparation reuses `team_components.prepare` solely for existing input qualification
and its unchanged prepared-input file, then builds independent walk-rate inputs.
New model/forecast locks and reports live in ignored `historical/walk_rate_output/`.
Changed inputs/code/protocol reject stale locks; identical reruns must match bytes.

## Results — September 27, 2026

**Promising; retain the locked candidate for confirmation, with Elo still in the app.**
Walk rate passed 2023 selection and improved both primary 2024 game and regional
probability scores. Both prespecified sensitivity checks retain those improvements.
This is a distinct successful retrospective comparison, not proof of future accuracy.
No closed candidate was refitted or rescored; no new source collection, coverage audit,
paid service, app change or 2025/2026 candidate evaluation occurred.

### Inputs and fitted model

| Season | Snapshot age | Usable teams | Covered / total NCAA games | Elo fallback games |
|---|---:|---:|---:|---:|
| 2021 | 10 days | 60/64 | 127/139 | 12 |
| 2022 | 7 days | 63/64 | 139/141 | 2 |
| 2023 | 3 days | 64/64 | 137/137 | 0 |
| 2024 | 3 days | 64/64 | 133/133 | 0 |

Input gaps and count differences match the [original qualified-input report](Team_Component_Experiment.md#usable-inputs-and-retained-gaps).
No identities/counts were repaired. Sources cover all opponents; 2021/2022 omit up to
six eligible late games per team. Five unresolved identities use fallback. Four 2024
teams have known non-D1 input and five have small count discrepancies. Strict fallback
affects 16/137 matchups in 2023 and 21/133 in 2024. Generated preparation preserves
per-team raw counts, source hashes, dates, discrepancies and omitted game IDs.

Initial fit: 266 covered 2021–2022 games, RMS 0.0226535135, coefficient 0.1223174363.
Refit: 403 covered 2021–2023 games, RMS 0.0220777611, coefficient 0.1677624119.
The locked adjustment is `0.1677624119 × (walk_rate_A − walk_rate_B) / 0.0220777611`
added to Elo log odds. Coefficients and preprocessing use training games only.
Higher walk rate gets a positive adjustment; no opponent/park or intentional-walk
adjustment is claimed. Complete precision remains reproducible in the model lock.

### Common game comparisons

Lower log loss and Brier are better. Accuracy is secondary.

| Season/model | Games | Log loss | Brier | Correct winners |
|---|---:|---:|---:|---:|
| 2023 selection: Elo | 137 | 0.628158 | 0.218569 | 91 |
| 2023 selection: Elo + walks | 137 | 0.622519 | 0.215967 | 90 |
| 2024 retrospective: Elo | 133 | 0.620988 | 0.215786 | 89 |
| 2024 retrospective: Elo + walks | 133 | 0.616370 | 0.213651 | 90 |
| 2024 fixed seed benchmark | 133 | 0.660503 | 0.229979 | 65.4%* |

*Seed accuracy gives half credit to exact 50/50 predictions, matching the baseline.
The selected model improves 2024 log loss by 0.004618 and Brier by 0.002135.
Its one additional correct pick is in Omaha; this is matchup accuracy, not a filled
bracket score. All 2023/2024 games have source-qualified walk inputs.

| 2024 stage | Games | Walk-minus-Elo log loss | Walk-minus-Elo Brier |
|---|---:|---:|---:|
| Regionals | 100 | −0.007090 | −0.003493 |
| Super regionals | 18 | +0.004923 | +0.003087 |
| Omaha groups | 12 | −0.003102 | −0.000957 |
| Championship series | 3 | +0.014490 | +0.007072 |

Later-round regression is real and unexplained; small samples do not erase it.
Consequently this result is a confirmation candidate, not a completed promotion gate.
Calibration bins are retained for each model, stage and sensitivity. For example,
the candidate's 2024 50–60% bin averages 55.0% versus 68.8% observed (32 games),
while its 60–70% bin averages 64.3% versus 57.1% observed (14 games). The small overall
score gain is not a claim that probabilities are well calibrated in every range.

### Regional advancement and fixed sensitivities

| 2024 regional model | Champion log loss | Four-class Brier | Champions picked |
|---|---:|---:|---:|
| Elo | 1.157268 | 0.636643 | 10/16 |
| Elo + walks | 1.117877 | 0.613727 | 10/16 |
| Seed benchmark | 1.429963 | 0.637239 | 10/16 |

Twelve of 16 regional groups improve champion log loss; eleven improve Brier.
Candidate-minus-Elo exploratory 95% intervals are [−0.107114, +0.033747] for log loss
and [−0.063814, +0.019879] for Brier. Both include zero. They account for regional
clustering within 2024, not future-season variation or repeated historical experiments.
2023 selection-exposed advancement is mixed: log loss 1.065144 → 1.063961, Brier
0.598209 → 0.605028, and picks 9/16 → 8/16. It was not used to retune the model.

| 2024 fixed variant | Game loss delta | Game Brier delta | Advancement loss delta | Advancement Brier delta |
|---|---:|---:|---:|---:|
| Primary | −0.004618 | −0.002135 | −0.039391 | −0.022916 |
| Flagged pairs use Elo | −0.006705 | −0.002959 | −0.037068 | −0.023590 |
| Same feature fitted without 2021 | −0.004778 | −0.002168 | −0.047479 | −0.026474 |

Negative is better. Removing 2021 retains the older 2022 snapshot, so it is not a
complete age control. These diagnostics support keeping the hypothesis for confirmation;
they do not justify switching to whichever diagnostic scores best.

### Verification and next step

273 data-free tests pass (199 scripts, 74 historical), including seven new walk-rate
tests covering count validity, sacrifice-bunt denominator, training-only scaling,
future-season/tie rejection, pairwise exact fallback, symmetry and immutable locks.
Baseline/v2 rebuilds succeed. All five generated walk-rate outputs reproduce byte-for-byte;
270 observed/hypothetical matchup probabilities agree. All 32 regional paths qualify
and their champions agree with the super-regional fields. Protected-input hashes,
app files and closed-candidate code remain unchanged. `git diff --check` passes.

Next: lock this exact model and a 2025 development confirmation protocol before any
new scoring. It needs dated pre-NCAA 2025 walk counts; the current national checkpoint
contains only 2021–2024, and final workbook totals are ineligible. If those counts are
not already retained, use a bounded free NCAA report acquisition in a separately scoped
session, not a broad source/coverage audit or school sweep. No 2024 retuning; 2026 remains
excluded. Review later-round behavior and full-bracket implications before deployment.
