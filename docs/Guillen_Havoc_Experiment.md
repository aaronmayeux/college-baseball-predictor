# Guillen and HAVOC experiment

## Locked protocol — before scoring

Aaron authorized testing these workbook ideas on September 27, 2026. This supersedes
the inventory's earlier decision to skip their legacy formulas as model inputs:
they are now experimental benchmarks, never assumed quality scores. Preserve the
original workbooks and previous candidates. No automatic penalty for home-run power.

Three prespecified single-feature challengers, each added to unchanged Elo:

- Guillen proxy: `1.6 * HR / runs_scored`. This estimates HR dependence, not actual
  runs scored on HR plays. A fixed positive 1.6 factor cancels under training RMS
  scaling; it is not an empirically calibrated run value.
- Original HAVOC: `(2*SB + BB + HBP) / batting_K`.
- Caught-stealing alternative: `(2*(SB-CS) + BB + HBP) / batting_K`. This is a fixed
  net-steals alternative, not a claim that each caught stealing costs exactly two runs.

No combinations, threshold search, sign constraints or post-scoring replacements.
Do not use pitching strikeouts as batting strikeouts. Missing counts or nonpositive
denominators make the affected candidate unavailable; never manufacture zeros.

Acquire only free dated national NCAA reports needed for these counts at the existing
snapshots: May 23, 2021; May 25, 2022; May 28, 2023; May 26, 2024. Reuse retained
menus/OBP/ERA and their exact identity mappings. Existing availability lag, sample-size,
date/phase and practical discrepancy rules apply. Cross-report records must agree;
disclose all-opponent scope, source age, non-D1 and omitted-game flags. Compare source
run totals to eligible retained results; small differences remain warnings, not audits.
No school sweep, broad archive investigation, D1 requests or paid sources.

Fit 2021–2022, select on 2023, refit the selected specification on 2021–2023, then
evaluate exposed 2024. Require usable training and selection inputs for each candidate;
do not fit an unavailable candidate. Compare candidates and Elo on identical full-field
games with exact pairwise Elo fallback. Training-only RMS difference scaling, fixed
Elo log-odds offset, no intercept, ridge 0.01. Select only if both 2023 log loss and
Brier improve; order qualifying candidates by log loss, Brier, name. Lock selection
before 2024 scoring. If none qualifies, stop without 2024 candidate scoring.

For a selected candidate: report game log loss, Brier, calibration, secondary accuracy,
covered/fallback cases, stage and regional-group scores, and the fixed seed comparator.
Freeze exact-engine regional probabilities before champion scoring; retain legal-path
and super-field checks. Advancement scores: champion log loss, summed four-class Brier,
pick accuracy, calibration and 5,000 paired-regional bootstrap draws (seed 20240926).
Fixed sensitivities only: flagged pairs use Elo; fit the same candidate without 2021.
Both 2024 game and advancement probability scores must improve without unexplained
material stage/sensitivity regression before a separate deployment review.

No 2025/2026 candidate scoring, app promotion, prior-candidate reopening or retuning
after results. Exposed historical seasons and repeated experiments cannot constitute
an untouched holdout. A candidate blocked by unavailable counts stays explicitly
untested; complete any supported candidate without waiting on a coverage audit.

The subsequent [D1Baseball source pilot](Havoc_Source_Reconstruction.md) supersedes the acquisition restriction for new HAVOC work only. This original protocol and Guillen results remain unchanged.

## Results — September 27, 2026

Current status: the frozen candidate subsequently failed [2025 development
confirmation](Batting_Confirmation_2025.md); no promotion or retuning. Original
2024 results below remain historical evidence.

**Guillen passed this original 2024 comparison.** HAVOC was unavailable in this
NCAA-report experiment; its later [bounded D1 test](Havoc_Chronological_Experiment.md)
failed selection and is closed. The original
Guillen proxy passed 2023 selection and improved 2024 game and regional probability
scores. Both prespecified sensitivity checks retain those gains. Elo remains in the
app; neither this feature nor a combination with walks was deployed.

### Source acquisition and HAVOC limitation

Ten free national reports were acquired: HR and runs for each of the four fixed dates,
plus 2023 stolen-base and batting-average schema samples. All were populated and retain
request forms, UTC retrieval times, hashes and response bytes. Existing menus supply
report IDs and team-stat selectors; no guessed statistic IDs, final totals, school
sweep or broad source audit. HR/run tables each contain 293/301/305/305 rows by year.

The 2023 stolen-base report provides `SB` and `CS`; the batting-average report provides
`AB`, `H`, `BA`. Neither supplies **offensive strikeouts**. The retained team menu's
strikeout rate and strikeout-to-walk categories are pitching statistics and cannot
supply the HAVOC denominator. Both HAVOC candidates were explicitly marked unavailable
before fitting. This is a limitation of the tested reports, not proof no free source
exists. We did not replace K with PA, invent zeros or reject HAVOC as ineffective.

All reports use the existing qualified snapshot dates, with ages 10/7/3/3 days and
all-opponent scope. Later retrieval does not certify historical publication time.
Usable teams are 60/64, 63/64, 64/64 and 64/64. Covered NCAA games are 127/139,
139/141, 137/137 and 133/133; missing pairs retain Elo. The existing five unresolved
identities and older-snapshot omissions remain; no coverage cleanup was needed.

New runs-scored comparisons were bounded feature checks, not collection audits.
NCAA-minus-retained differences among mapped teams are:

- 2021: UC Irvine +1, Fairfield −9, Maryland +4, UC Santa Barbara −1.
- 2022: Georgia Southern +2.
- 2023: Alabama −1, Santa Clara −9, Eastern Illinois +5, Ball State −2, Washington −5.
- 2024: Georgia Tech +1, Western Michigan −4, Evansville −3, Northern Kentucky +8,
  Southern Miss −1.

All fit the prespecified ten-run tolerance, remain uncorrected and flag strict fallback.
Other count/non-D1/omission flags remain from the [existing input-gap report](Team_Component_Experiment.md#usable-inputs-and-retained-gaps).
Strict fallback affects 22/137 selection games and 28/133 evaluation games.

### Fitting and game comparisons

Training uses 266 covered 2021–2022 games, RMS 0.1039224634 and coefficient 0.2688340464.
The selected model refits on 403 covered 2021–2023 games: RMS 0.1003294718,
coefficient **+0.2532239136**. Thus the fitted adjustment favors higher HR/run ratios,
not an assumed home-run-dependence penalty. It does not establish a causal effect or
separate power from parks/opponents. The fixed 1.6 factor cancels under RMS scaling.

| Common game comparison | Log loss ↓ | Brier ↓ | Correct winners |
|---|---:|---:|---:|
| 2023 selection Elo | 0.628158 | 0.218569 | 91/137 |
| 2023 selection Elo + Guillen | 0.622378 | 0.215938 | 90/137 |
| 2024 retrospective Elo | 0.620988 | 0.215786 | 89/133 |
| 2024 retrospective Elo + Guillen | 0.593697 | 0.203279 | 92/133 |
| 2024 fixed seed benchmark | 0.660503 | 0.229979 | 65.4%* |

*Seed accuracy gives half credit to 50/50 predictions. These are matchup picks,
not filled-bracket accuracy. The three extra correct 2024 picks comprise one regional
game and two Omaha-group games.

| 2024 stage | Games | Guillen-minus-Elo log loss | Guillen-minus-Elo Brier |
|---|---:|---:|---:|
| Regionals | 100 | −0.030151 | −0.013625 |
| Super regionals | 18 | +0.002417 | +0.000997 |
| Omaha groups | 12 | −0.053763 | −0.026055 |
| Championship series | 3 | −0.004340 | −0.002072 |

Supers regress slightly; their unchanged picks do not erase that score regression.
Calibration bins, regional-group game results and seed comparisons are reproduced.
For example, the 2024 candidate 60–70% bin averages 63.2% against 80.8% observed in
26 games. Overall score improvement does not certify calibration in every range.

### Advancement and fixed sensitivities

| 2024 regional model | Champion log loss ↓ | Four-class Brier ↓ | Champions picked |
|---|---:|---:|---:|
| Elo | 1.157268 | 0.636643 | 10/16 |
| Elo + Guillen | 1.031633 | 0.574031 | 10/16 |
| Seed benchmark | 1.429963 | 0.637239 | 10/16 |

Thirteen of sixteen groups improve log loss; eleven improve Brier. Exploratory paired
regional 95% intervals for candidate-minus-Elo are [−0.215764, −0.034748] in log loss
and [−0.113597, −0.012143] in Brier. These exclude zero within this season but do not
account for future-season variation or repeated historical feature selection. 2024
was already exposed, so this is not an untouched validation result.

2023 selection-exposed advancement also improves: loss 1.065144 → 1.004462,
Brier 0.598209 → 0.562642, with both picking 9/16 champions.

| 2024 fixed variant | Game loss delta | Game Brier delta | Advancement loss delta | Advancement Brier delta |
|---|---:|---:|---:|---:|
| Primary | −0.027291 | −0.012507 | −0.125635 | −0.062611 |
| Flagged pairs use Elo | −0.023069 | −0.010760 | −0.112664 | −0.053808 |
| Same feature fitted without 2021 | −0.026810 | −0.012295 | −0.123453 | −0.061580 |

Negative is better. Strict fallback picks 91 games; omitting 2021 picks 92. Each
still picks 10/16 regional champions. Removing 2021 does not remove older 2022
snapshot limitations. No diagnostic replaced the primary model after scoring.

### Verification and next step

293 data-free tests pass (202 scripts, 91 historical), including twelve new tests.
They cover source schema/date/division/duplicate checks, invalid counts, Guillen
arithmetic, fixed-factor scaling equivalence, training chronology, missing-pair Elo
fallback, symmetry, immutable locks and early stopping. Five generated outputs repeat
byte-for-byte, 270 observed/hypothetical probabilities agree, and 32 legal regional
paths match the super-regional fields. Protected-input hashes, previous model code/
outputs and app remain unchanged. `git diff --check` passes.

Guillen and walk rate subsequently failed [2025 confirmation](Batting_Confirmation_2025.md).
HAVOC obtained its missing batting K, completed the [bounded test](Havoc_Chronological_Experiment.md)
and failed selection. All remain undeployed; no post-result sample expansion or retuning.

## Reproduction and evidence

Restore baseline/v2 and the combined NCAA evidence per [DATA.md](DATA.md). Extract the
separate style-count checkpoint into a fresh directory. Using current repository code:

```sh
python3 historical/guillen.py prepare --evidence-dir /absolute/path/to/ncaa --style-dir /absolute/path/to/style
python3 historical/guillen.py evaluate --evidence-dir /absolute/path/to/ncaa --style-dir /absolute/path/to/style
python3 -m unittest discover -s historical -p 'test_guillen.py'
python3 -m unittest discover -s scripts -p 'test_ncaa_style_inputs.py'
```

Five locks/reports stay ignored in `historical/guillen_output/`. Source fingerprints
are portable; changed source/code/protocol reject stale locks. Preparation reuses only
existing input qualification, never the fitting/scoring of closed candidates.
`scripts/ncaa_style_inputs.py --evidence-dir <ncaa> --raw-dir <fresh>/raw` is an explicit,
bounded acquisition command, not required for offline reproduction. It requests only
eight HR/run reports and the two 2023 schema samples and refuses cached failures or
changed requests rather than overwriting/retrying them.
