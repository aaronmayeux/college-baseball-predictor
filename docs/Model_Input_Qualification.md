# Focused model-input qualification

Milestone 6 now has a focused qualification plan and offline hitting and structured pitching extractors, verified September 25, 2026. No feature weights, quality-arm thresholds or prediction changes are selected. The [triage](Statistics_Discovery_and_Triage.md) owns the broader inventory; [SPEC](../historical/SPEC.md) owns cutoff and holdout rules.

## Smallest useful experiments

Aggregate eligible game counts first, then divide; do not average game rates. Zero denominators produce unavailable values, never zero quality. These are candidate definitions, not qualified model inputs.

| Experiment, in order | Minimum counts | Measure and purpose | Qualification still needed |
|---|---|---|---|
| Contact | Team strikeouts (SO), complete plate appearances (PA) | SO/PA; lower means fewer strikeouts, not measured swing contact | LSU PA components reconcile to opposing BF; qualify other teams against explicit totals, including interference/other awards. Never substitute AB |
| Power | AB, doubles, triples, HR | ISO = (2B + 2×3B + 3×HR)/AB; extra bases per at-bat | LSU and Missouri State pilot counts/rates now reconcile; national coverage and predictive validation remain open |
| HR frequency | HR and qualified PA | HR/PA, tested after ISO for added information | Same PA gate; this is frequency, **not the share of runs from homers** |
| Reaching base comparator | H, AB, BB, HBP, SF | OBP = (H+BB+HBP)/(AB+BB+HBP+SF) | Pilot counts complete for LSU/Missouri State; expand coverage. Avoid stacking overlapping OBP/BB features initially |
| Pitching quality | Per pitcher SO, BB, BF, outs; ER/R as diagnostics | (SO−BB)/BF; compare with ERA = 27×ER/outs and RA9 = 27×R/outs | Reconcile BF; validate sample-size adjustment on training data. Preserve individual versus team ER differences |
| Pitching depth and aces | Qualified quality estimate, outs, explicit pitching starts and relief appearances, school-season player identity | Count pitchers meeting both workload and quality requirements; mutually exclusive starter/relief/mixed summaries | Role audit and training-only workload/quality selection. Multiple aces or none; never label the best pitcher an ace automatically |

True HR dependence needs runs scored on HR plays divided by total runs. Preserve it as a separate later feature: neither HR/PA nor an assumed runs-per-HR multiplier answers that question. Park interactions and simulated later-round availability follow basic feature validation. Rest remains unknown.

## What the retained evidence actually supports

Rebuilt both appearance audits from hash-verified checkpoints and reran the separate exception annotations. All 234 sampled boxes parse (68+54+52+60). This is a selected feasibility sample, not a national coverage estimate.

| Team-season | Eligible boxes: regular / conference-inclusive | Hitting counts | Pitching counts and limits |
|---|---|---|---|
| LSU 2025 | 55/55; 57/57 | Core counts plus team extra bases/HBP/sacrifices reconcile; PA checks against opposing BF pass in all 68 boxes | Core counts reconcile; BF parsed but not independently reconciled to cumulative BF; pitching starts/roles and HR allowed unqualified |
| Towson 2024 | 54/54; 54/54 | Same six fields as LSU | Same core fields/BF limitation; starts/roles unqualified |
| Davidson 2024 | 52/52; 52/52 | Fourteen count fields exist, including extra bases/HBP/sacrifices; batting completeness still fails for the retained zero-PA substitute | Sixteen mapped counts reconcile, including starts and HR allowed; BF reconciles per appearance and against opposing PA; explicit pitching GS and observed roles qualified in the separate extractor |
| Missouri State 2022 | 51/51; 57/57 with separate completion annotation | Fourteen mapped counts reconcile; cutoff-specific ISO/OBP now extracted; PA-based rates remain unavailable | Sixteen mapped counts reconcile; BF and explicit pitching GS checks pass in the separate extractor. Original conference-inclusive strict join stays 56/57; annotation does not establish pitcher work dates |

Names are scoped to school-season; cross-season player matching is unnecessary for initial team summaries. Never merge transfers by name. Source publication times remain uncertified even where count reconciliation passes.

For the 2025 field, only **1/64 (LSU)** has reconciled core appearance histories; **0/64** currently have a fully qualified hitting-plus-pitching feature package. The other 63 need eligible appearance/count qualification. The [field map](Tournament_Source_Availability_2025.md) retains each team's specific gap: 64 schedule sources and 50 player-total groups do not constitute 64 feature histories. The three earlier pilot seasons cannot fill 2025 gaps. Keep the existing team-only fallback for every unqualified team, in both modes.

## Implemented extraction and next work

`extract_hitting_inputs.py` rebuilds the existing audits from source bytes and writes a separate ignored JSON report. The new LSU adapter reads inning play-by-play, checks extra-base/HBP/sacrifice/interference counts against the game summary, checks inning hits/runs against the box, and compares PA components against opposing pitcher BF. It excludes pitch notation and repeated replay commentary from event counts. All 68 games parse; all ten extracted season-count fields match cumulative audit targets. The original LSU–UCLA postseason date issue remains visible and excluded from both forecast modes.

The Missouri State adapter sums already reconciled structured batting rows and preserves the evidence-checked May 24/25 completion annotation. All 60 boxes support ISO/OBP; PA and interference are explicitly null, so strikeout rate and HR/PA remain null. Davidson's failed batting gate is unchanged. Final totals verify extraction only; cutoff rates sum eligible games, never final totals or averages of game rates.

| Team-season / mode | Games | ISO | OBP | Strikeouts/PA | HR/PA |
|---|---:|---:|---:|---:|---:|
| LSU 2025 regular-only | 55 | .218152 | .417004 | 18.2384% | 3.9591% |
| LSU 2025 conference-inclusive | 57 | .214551 | .411996 | 18.4416% | 3.8961% |
| Missouri State 2022 regular-only | 51 | .200898 | .386654 | Unqualified | Unqualified |
| Missouri State 2022 conference-inclusive | 57 | .216608 | .388818 | Unqualified | Unqualified |

These are unadjusted descriptive inputs, **not evidence of improved predictions**. Both team/mode inventories are complete. A missing or invalid eligible game blocks that mode's rates; a PA mismatch blocks PA-based rates while retaining reconciled power counts. Failed full-season count checks also block rates. Input hashes, source metadata, game exclusions and original date annotations remain in the output. No player-level hitting features or weights are enabled.

Next, extend BF and explicit pitching-start verification to LSU’s cached StatCrew boxes; its existing pitching parser has no per-game GS field, so table order must not supply starts. Investigate explicit lineup or play evidence and reconcile against cumulative APP-GS, retaining unknown roles where evidence is insufficient. Then identify the smallest permitted multi-season expansion needed for the evaluation contract below. Existing LSU 2021–2024 indexes/sample boxes are candidates, not qualified seasons. Qualify both sides of evaluation matchups; one school's seasons alone cannot validate a national feature. Reuse caches/shared boxes and resolve access scope for the exact selected source before requests. Broad discovery and bulk collection remain paused.

## Pitcher BF, roles and workload pilot

`extract_pitching_inputs.py` is a separate offline extractor for Davidson 2024 and Missouri State 2022. All **112 boxes / 435 pitching appearances** pass: each pitcher’s BF equals AB+BB+HBP+SF+SH+catcher interference; summed BF agrees with the team pitching total and opposing batting PA components. Missing components block qualification rather than becoming zeros. These within-source checks are not independent-provider certification; no direct cumulative BF target is claimed.

The existing structured audit reconciles each pitcher’s starts, appearances and mapped counts against cumulative pitching targets. The new check requires binary pitching `gamesStarted` and exactly one pitching start per game. Generic lineup `gameStarted` and row order do not assign roles. Zero-out appearances remain included. Roles describe the eligible appearances only: starter-only, relief-only, or mixed, with each pitcher counted once. They do not label rotation talent, quality arms or aces.

| Team / mode | Games | Pitchers: starter-only / relief-only / mixed | Appearances | Outs | BF | Appearances with pitch counts |
|---|---:|---:|---:|---:|---:|---:|
| Davidson 2024, either mode | 52 | 1 / 9 / 8 | 212 | 1,311 | 2,168 | 194 |
| Missouri State 2022, regular-only | 51 | 1 / 4 / 8 | 190 | 1,321 | 2,062 | 44 |
| Missouri State 2022, conference-inclusive | 57 | 0 / 3 / 10 | 209 | 1,477 | 2,280 | 63 |

Each player summary includes outs, BF, starts, relief appearances, maximum appearance outs, unadjusted (SO−BB)/BF, ERA and RA9. Counts are summed before division; zero denominators yield null. Pitch totals are null if any appearance lacks a count; separately labeled known-pitch subtotals and coverage remain available. A missing/bad eligible game or failed season pitching check blocks the mode’s player summaries.

The Missouri State completion annotation is preserved along with original dates/issues; it does not establish actual pitcher work dates. Rest and availability remain unknown for both teams. Davidson’s existing batting omission remains visible and does not invalidate its independently checked pitching records. Final cumulative counts serve only as audit targets. LSU and Towson pitching BF/roles are still unqualified by this extractor; no 2025 field coverage gain is claimed. No quality/depth thresholds, weights, national validation or prediction adjustments are enabled.

## Chronological evaluation contract

The current four team-seasons provide **no sufficient common chronological evaluation sample**. There is no 2023 player pilot, and only LSU covers the 2025 field. Do not fit on this convenience sample or claim improvement from it.

Target qualified training inputs from 2021–2022, development selection on 2023, and a fixed later comparison on 2024. Fit all scaling, opponent adjustment, sample-size shrinkage and thresholds within the earlier training period; refit through 2023 only after choosing the candidate. Prior published baseline metrics mean 2024 is retrospective validation, not an untouched holdout. If these seasons cannot be qualified, report the shortfall and revise the plan **before** inspecting candidate outcome metrics. 2025 remains a development diagnostic; 2026 stays excluded from this work.

Freeze eligibility and common game IDs before fitting. Score NCAA games whose two teams have qualified pre-NCAA features; record eligible games, teams, conferences and exclusions by season and mode. Compare unchanged Elo, seed benchmark and one-feature challengers on exactly those same games, and also report full-sample fallback coverage. Do not compare a selected-subset challenger against the published all-game 68.9% baseline.

Start with one added feature at a time, then only supported combinations. Primary measures: log loss and Brier score; also calibration, winner accuracy, and results by season. Report season/tournament-cluster uncertainty with the few-season limitation explicit. Retain an addition only when probability-quality evidence supports it without an unexplained material regression; otherwise keep Elo. Game-level gains do not establish bracket gains: evaluate advancement probabilities separately using the unchanged tournament engine before promotion. Freeze any future untouched test prospectively.

## Reproduction and boundaries

[DATA.md](DATA.md#offline-hitting-input-pilot) owns restoration and both extraction commands. Repeated outputs are byte-identical. All **146 tests** pass (116 scripts, 30 historical), including 13 hitting tests for count formulas, unknown denominators, interference, replay comments, pitch-code confusion, missing/duplicate events, incomplete modes and chronological exclusions. Twelve pitching tests cover BF/interference, role flags versus generic lineup starts/order, missing counts, zero-out appearances, rates, incomplete modes and cutoff exclusions. Tests need no external data.

The original LSU/Towson audit remains unchanged; the new extractor calls it without modifying its output contract. Input/config fingerprints remain unchanged during extraction. No fresh collection, 2026 evaluation, model/app change or raw-data commit occurred. The unavailable conference-archive checkpoint is unnecessary for these pilots; its newer field/access results were not rerun. Spreadsheet comparison, UI changes and hosting migration remain deferred.
