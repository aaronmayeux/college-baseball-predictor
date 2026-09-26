# Team-level source decision and locked run experiment

## Source decision

**Go: reuse the retained Warren Nolan D1 result inventory, with the existing official corrections and v2 timing overlay, for team scoring and run prevention in 2021–2024.** No new source requests, licensing claims or school-by-school collection are needed. The original source bytes, retrieval times and hashes remain in the baseline/v2 checkpoints; normalized game IDs link features back to that evidence. This decision covers cached research, not permission or a guarantee for future bulk downloads.

**No-go for immediate nationwide component-stat collection.** The [triage](Statistics_Discovery_and_Triage.md) and [qualification](Model_Input_Qualification.md) retain the tested access limits. Dated SIDEARM team logs work for two 2022 teams but are not a ready four-season field dataset. NCAA access, ESPN historical completeness and bulk school access remain unresolved. D1Baseball remains prohibited. FanGraphs' [launch announcement](https://blogs.fangraphs.com/weve-got-college-data/) confirms college data back to 2021, but does not qualify historical forecast-date snapshots or our automation rights. [Highlightly documentation](https://highlightly.net/mlb-api/documentation/) advertises NCAA data; no authenticated 2021–2024 sample or cutoff-safe field coverage is verified. Those are candidates for a bounded provider-sample decision, not reasons to buy or start another unbounded audit. Neither provider was contacted.

This is a deliberately simpler first test: scoring includes hitting and baserunning; run prevention includes pitching **and defense**. It does not qualify ISO, OBP, strikeout rates, HR dependence, HAVOC, ERA, quality arms or individual workload. Scores lack innings/exposure and park adjustment; schedule strength is only controlled through the existing Elo offset. Retaining Elo costs no new acquisition effort; paid data would only be worthwhile after a dated, complete multi-season sample and suitable terms are verified. No paid price or coverage promise is accepted here.

## Protocol locked before candidate metrics

- Batch scope: all retained D1 games in 2021–2024; aggregate only eligible pre-cutoff games under each unchanged mode. No 2025 candidate analysis or 2026 ingestion. NCAA matchup coverage must include all 64 participating teams each year. Reject duplicate IDs, invalid scores, missing team features or incomplete v2 integrity gates. Preserve reasons for every excluded input and the exact common NCAA game IDs before fitting.
- Three fixed single-input challengers: A minus B runs scored/game (`offense`); B minus A runs allowed/game (`prevention`); A minus B net runs/game (`net`). Sum counts before division. No threshold grid, clipping, pseudo-games, opponent/park correction or extra combination search.
- Probability: logistic(logit(unchanged v2 Elo) + beta * feature_difference / training_RMS). No intercept, Elo reweighting or mean centering; reversing teams complements the probability. Fit one coefficient using mean binary log loss plus 0.01 * beta² / 2. Fit RMS on training NCAA matchup differences only; this is a scaling choice, not a quality label.
- Train on 2021–2022 regular-only NCAA matchups. 2021 remains initialization for the preserved baseline; its frozen predictions are used as challenger training observations only. Select on 2023 regular-only: a candidate must strictly improve both log loss and Brier over unchanged Elo. Choose the lowest log loss, then Brier, then fixed candidate name. If none passes, select Elo. No numerical settings may change after viewing results.
- After selection, refit that candidate/RMS on 2021–2023 regular-only and evaluate once on 2024 retrospective validation. Apply the same coefficients/scales to conference-inclusive sensitivity rows; do not tune or double the sample using the second mode. Preserve training fits and the selection decision before opening 2024 candidate metrics.
- Compare Elo, selected challenger and available unchanged seed probabilities on identical games. 2021 has no v2 seed comparator; report it missing rather than fabricate it. Report season/stage metrics, fixed probability-bin calibration, paired mean loss differences, and regional-tournament grouped differences. Later-round stages are separate groups, not independent replicates. One validation season cannot support credible season-cluster confidence intervals; no independent-game significance claim.
- No feature promotion unless probability-quality evidence is favorable without unexplained material regression, followed by separate historical advancement validation. A failed 2024 comparison means retain Elo, with no retuning on 2024. The 2025 app, baseline files, timing rules, raw evidence and individual-pitcher deferral remain intact.

## Reproduce

Restore/rebuild baseline and v2 as described in [DATA](DATA.md), then:

```sh
python3 historical/team_runs.py prepare
python3 historical/team_runs.py evaluate
python3 -m unittest discover -s historical -p 'test_*.py'
```

`prepare` writes ignored features, eligibility, source/config hashes and common samples without fitting. `evaluate` requires matching preparation fingerprints, writes a selection lock before validation, and produces deterministic ignored reports in `historical/team_run_output/`. Source/contract changes require a new explicit prepare; existing evaluation locks must match rather than silently change. No new evidence archive is necessary: both original checkpoints plus Git reproduce the work.

## Results

The importer processed **32,197 retained D1 games** in 2021–2024. Both modes cover all **256 tournament team-seasons** and the same **550 NCAA matchups** (139/141/137/133 by year); no matchup lacks a team feature. Eligible regular-only games per team range from 34–57, 43–56, 43–56 and 42–56 by year. Conference-inclusive ranges are 39–61, 46–62, 46–62 and 47–62. Exact eligible IDs, phase/timing exclusions, conference coverage and all denominators are in `prepared.json`. No raw downloads were added.

All three candidates improved both probability scores in 2023. **Net runs/game** won the locked selection: log loss 0.597439 versus Elo 0.618062; Brier 0.204943 versus 0.214033. Offense-only log loss was 0.609612 and prevention-only 0.606265. Selection training used 280 games; the final refit used 417. Net's initial beta/RMS were 0.234065877835/1.927262381896; refit values were 0.352052984422/1.873385820375. No parameters changed after results.

2024 retrospective validation, identical 133 games for every comparator (lower probability scores are better):

| Mode / model | Log loss | Brier | Winner accuracy |
|---|---:|---:|---:|
| Regular-only Elo | 0.603750 | 0.207800 | 93/133 (69.9%) |
| Regular-only Elo + net runs | 0.597991 | 0.206991 | 90/133 (67.7%) |
| Conference-inclusive Elo | 0.620988 | 0.215786 | 89/133 (66.9%) |
| Conference-inclusive Elo + net runs | 0.617736 | 0.215933 | 85/133 (63.9%) |
| Seed comparator (both modes) | 0.660503 | 0.229979 | 65.4%* |

*Seed accuracy awards half credit to exact 50/50 predictions, as in the unchanged benchmark.

The primary paired change is −0.005759 log loss and −0.000809 Brier, with three fewer correct winners. This is **mixed, inconclusive promotion evidence**, not a demonstrated bracket improvement. Regular-only regional Brier worsens by 0.002264 over 100 games; super-regional log loss/Brier worsen by 0.003949/0.001060 over 18 games. Much of the aggregate gain comes from twelve Omaha games (log-loss delta −0.061538). Only eight of sixteen regional groups improve either probability score. Conference-inclusive Brier is slightly worse overall (+0.000147). Calibration bins and grouped losses remain in the reproducible report; the small correlated samples do not justify a significance claim.

**Decision: retain Elo in the app.** Keep the locked candidate as a research result; do not tune it against 2024. Next, test its unchanged probabilities on historical regional advancement with selection-day routing and a locked scoring protocol. If that evidence is also mixed, close this candidate without promoting it. Component hitting/pitching inputs still require a separate bounded source decision; this result does not qualify them.

Verification: 192 external-data-free tests pass (152 scripts, 40 historical), including ten new cutoff, conservation, duplicate, fitting, symmetry and fallback checks. Baseline and v2 pipelines rebuilt successfully. Repeated preparation/evaluation outputs are byte-identical; protected baseline/v2 inputs and the app remain unchanged.
