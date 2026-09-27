# Offensive hit-by-pitch rate experiment

## Locked protocol — before scoring

Hypothesis: reaching base through hit-by-pitches contains predictive information beyond
Elo. Test the inventory's offensive HBP/PA feature alone, not a revised OBP model or
a retuned walk-rate model. The walk-rate candidate and closed candidates stay unchanged.
HBP is sparse and can reflect opponents or approach; no causal or stable-skill claim.

Feature: HBP/(AB+BB+HBP+SF+SH) from retained NCAA reports, labeled **recorded PA**
because catcher interference is unavailable. One feature, fixed ridge 0.01, no
interactions, weights search, automatic stacking with walks or extra candidate variants.

Reuse the existing component preparation's identity, dated-source, discrepancy and
sample-size rules. Dates: May 23, 2021; May 25, 2022; May 28, 2023; May 26, 2024.
Conference-inclusive, all-opponent NCAA counts alongside D1 Elo. Preserve source hashes,
small count differences, non-D1 warnings and omitted games. Either missing/invalid
team forces exact Elo for the entire matchup. Retain both original app modes.

Fit 2021–2022 NCAA matchups with training-only difference RMS scaling, fixed Elo
log-odds offset, no intercept. Select HBP rate only if both 2023 log loss and Brier
improve over Elo on identical games; otherwise close at selection without 2024 HBP
scoring. Refit a selected feature on 2021–2023 and persist its lock before 2024 scoring.
2024 is exposed retrospective evidence, 2025 development remains unscored for this
candidate, and 2026 is excluded. Repeated experiments on exposed seasons increase
selection optimism; any positive result needs later confirmation, not a holdout claim.

For a selected feature, retain all/covered/fallback game scores, calibration, secondary
accuracy, stage and regional-group results, plus the fixed seed comparator. Freeze
regional probabilities before reading champions; use the existing exact engine and
legal-path checks, including agreement with the super-regional field. Report champion
log loss, four-class summed Brier, pick accuracy, calibration and 5,000 paired-regional
bootstrap draws, seed 20240926 (exploratory, within-season only).

Fixed sensitivities with no reselection: flagged matchups fall back to Elo; fit the
same selected feature without 2021. Both 2024 game and advancement scores must improve
without material unexplained stage/sensitivity regression before a separate deployment
review. No automatic promotion or retuning after seeing metrics. If selection fails,
report its fit/coverage and stop; do not run meaningless Elo-versus-Elo advancement.

## Reproduction

Reuse baseline/v2 and the combined NCAA checkpoint from [DATA.md](DATA.md).

```sh
python3 historical/hit_by_pitch.py prepare --evidence-dir /absolute/path/to/ncaa
python3 historical/hit_by_pitch.py evaluate --evidence-dir /absolute/path/to/ncaa
python3 -m unittest discover -s historical -p 'test_hit_by_pitch.py'
```

Preparation reuses `team_components.prepare` for input qualification only, never for
closed-candidate fitting/scoring. Independent locks and outputs remain ignored under
`historical/hit_by_pitch_output/`. Source/code/protocol changes reject stale locks;
identical reruns must match bytes. No provider downloads or new coverage audits.

## Results — September 27, 2026

**Closed at 2023 selection; retain Elo.** This single-feature HBP-rate challenger
worsened both probability scores and selected fewer winners. No 2024 candidate
scoring, advancement scoring, refit through 2023, post-result sensitivity search,
or 2025/2026 evaluation was performed. The existing walk-rate model is unchanged.

| 2023 model, same 137 games | Log loss ↓ | Brier ↓ | Correct winners |
|---|---:|---:|---:|
| Conference-inclusive Elo | 0.628158 | 0.218569 | 91/137 |
| Elo + offensive HBP rate | 0.645132 | 0.226878 | 89/137 |
| Fixed regional-seed benchmark | 0.631385 | 0.219621 | 66.1%* |

*Seed accuracy gives half credit to exact 50/50 predictions, as in the baseline.
The challenger worsens log loss by 0.016974 and Brier by 0.008309. The negative
training coefficient (−0.2060876271; RMS 0.0102216537) was fitted on 266 covered
2021–2022 games, not forced. It does not imply getting hit causes worse performance;
it could reflect opponent differences, sampling variation or omitted factors.
Reversing its sign after seeing selection failure would be a new, exposed-data tune
and was not attempted.

Preparation preserves all 64 teams per year. Usable inputs are 60/64 in 2021,
63/64 in 2022 and 64/64 in 2023/2024. Training has 266/280 covered games; all 137
selection games are covered. The 14 uncovered training-season matchups retain exact
Elo and are excluded from coefficient/scaling fitting. Snapshot ages are 10, 7, 3
and 3 days. Per-team source hashes, raw counts, non-D1 flags, omitted game IDs and
small discrepancies remain in preparation; the [existing input-gap report](Team_Component_Experiment.md#usable-inputs-and-retained-gaps)
owns their details. No missing counts were replaced with zeros or repaired.

The report retains 2023 calibration and the seed comparison. For example, the
challenger's 40–50% bin averages 44.5% versus 31.6% observed over 38 games. No
calibration correction or alternative specification was fitted afterward. Selection
failure is enough to close this tested candidate without another data audit.

281 data-free tests pass (199 scripts, 82 historical), including eight new HBP
tests. These cover recorded-PA arithmetic, invalid counts, training-only scaling,
future/tied training rejection, pairwise fallback, symmetry, immutable locks and
stopping before validation/advancement after failed selection. Three HBP outputs
reproduce byte-for-byte. Source/protected-input fingerprints pass; walk-rate code
and all five outputs, app files and closed model code remain unchanged.
`git diff --check` passes. No provider collection, cost or new coverage audit.

Next: retain the promising walk-rate candidate for its already documented locked
2025 development confirmation. This result closes only standalone HBP rate under
this protocol; it does not establish that all hitting or pitching statistics fail.
Do not reopen HBP or force an untested combination into the app.
