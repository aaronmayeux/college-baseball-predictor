# Focused model-input qualification

This is milestone 6's first deliverable: a feature/data plan checked against retained evidence on September 25, 2026. No feature weights, quality-arm thresholds or prediction changes are selected. The [triage](Statistics_Discovery_and_Triage.md) owns the broader inventory; [SPEC](../historical/SPEC.md) owns cutoff and holdout rules.

## Smallest useful experiments

Aggregate eligible game counts first, then divide; do not average game rates. Zero denominators produce unavailable values, never zero quality. These are candidate definitions, not qualified model inputs.

| Experiment, in order | Minimum counts | Measure and purpose | Qualification still needed |
|---|---|---|---|
| Contact | Team strikeouts (SO), complete plate appearances (PA) | SO/PA; lower means fewer strikeouts, not measured swing contact | Verify PA against explicit totals or AB+BB+HBP+SF+SH plus interference/other awarded appearances; never substitute AB |
| Power | AB, doubles, triples, HR | ISO = (2B + 2×3B + 3×HR)/AB; extra bases per at-bat | Parse and reconcile extra-base counts in LSU's retained boxes; structured pilot already supports these counts |
| HR frequency | HR and qualified PA | HR/PA, tested after ISO for added information | Same PA gate; this is frequency, **not the share of runs from homers** |
| Reaching base comparator | H, AB, BB, HBP, SF | OBP = (H+BB+HBP)/(AB+BB+HBP+SF) | Complete eligible counts; avoid stacking overlapping OBP/BB features initially |
| Pitching quality | Per pitcher SO, BB, BF, outs; ER/R as diagnostics | (SO−BB)/BF; compare with ERA = 27×ER/outs and RA9 = 27×R/outs | Reconcile BF; validate sample-size adjustment on training data. Preserve individual versus team ER differences |
| Pitching depth and aces | Qualified quality estimate, outs, explicit pitching starts and relief appearances, school-season player identity | Count pitchers meeting both workload and quality requirements; mutually exclusive starter/relief/mixed summaries | Role audit and training-only workload/quality selection. Multiple aces or none; never label the best pitcher an ace automatically |

True HR dependence needs runs scored on HR plays divided by total runs. Preserve it as a separate later feature: neither HR/PA nor an assumed runs-per-HR multiplier answers that question. Park interactions and simulated later-round availability follow basic feature validation. Rest remains unknown.

## What the retained evidence actually supports

Rebuilt both appearance audits from hash-verified checkpoints and reran the separate exception annotations. All 234 sampled boxes parse (68+54+52+60). This is a selected feasibility sample, not a national coverage estimate.

| Team-season | Eligible boxes: regular / conference-inclusive | Hitting counts | Pitching counts and limits |
|---|---|---|---|
| LSU 2025 | 55/55; 57/57 | AB/H/R/RBI/BB/SO reconcile; normalized extra-base/HBP/sacrifice counts absent | Core counts reconcile; BF parsed but not independently reconciled to cumulative BF; pitching starts/roles and HR allowed unqualified |
| Towson 2024 | 54/54; 54/54 | Same six fields as LSU | Same core fields/BF limitation; starts/roles unqualified |
| Davidson 2024 | 52/52; 52/52 | Fourteen count fields exist, including extra bases/HBP/sacrifices; batting completeness still fails for the retained zero-PA substitute | Sixteen mapped counts reconcile, including starts and HR allowed; BF denominator and role semantics need qualification |
| Missouri State 2022 | 51/51; 57/57 with separate completion annotation | Fourteen mapped counts reconcile; ISO is feasible for an isolated extraction check | Sixteen mapped counts reconcile; BF/role checks remain. Original conference-inclusive strict join stays 56/57; annotation does not establish pitcher work dates |

Names are scoped to school-season; cross-season player matching is unnecessary for initial team summaries. Never merge transfers by name. Source publication times remain uncertified even where count reconciliation passes.

For the 2025 field, only **1/64 (LSU)** has reconciled core appearance histories; **0/64** currently have a fully qualified hitting-plus-pitching feature package. The other 63 need eligible appearance/count qualification. The [field map](Tournament_Source_Availability_2025.md) retains each team's specific gap: 64 schedule sources and 50 player-total groups do not constitute 64 feature histories. The three earlier pilot seasons cannot fill 2025 gaps. Keep the existing team-only fallback for every unqualified team, in both modes.

## Concrete next implementation

1. Extend the retained LSU StatCrew box parser for team 2B/3B/HR, HBP and sacrifices. Reconcile each new count against explicit box totals/summary events and full-season audit targets. Check interference before claiming PA completeness. Do this offline; missing/ambiguous fields remain unavailable. The first deliverable is separate cutoff-specific **count/rate output**, not changed probabilities.
2. Use Missouri State's structured boxes as a second-format ISO check. Retain Davidson's failed batting gate. Add focused tests for missing fields, double-counted events, zero denominators, excluded postseason games and differences between forecast modes. Hash inputs; keep game/player exports outside Git.
3. Check pitcher BF and explicit starts in the same cached boxes. Do not infer starters from table order or generic lineup-start flags. Then summarize workload by role without choosing quality-arm/ace cutoffs yet.
4. Only after the small extractor works, identify the smallest permitted multi-season expansion needed for evaluation. Existing LSU 2021–2024 indexes and sample boxes are candidates, not qualified seasons. Qualify both sides of evaluation matchups; one school's seasons alone cannot validate a national feature. Reuse caches/shared boxes. Resolve access scope for the exact selected source before requests; do not restart all-field discovery or run a bulk sweep.

A failed extraction gate should report the missing field and affected games, not trigger a nationwide search. No new source requests are needed for steps 1–3.

## Chronological evaluation contract

The current four team-seasons provide **no sufficient common chronological evaluation sample**. There is no 2023 player pilot, and only LSU covers the 2025 field. Do not fit on this convenience sample or claim improvement from it.

Target qualified training inputs from 2021–2022, development selection on 2023, and a fixed later comparison on 2024. Fit all scaling, opponent adjustment, sample-size shrinkage and thresholds within the earlier training period; refit through 2023 only after choosing the candidate. Prior published baseline metrics mean 2024 is retrospective validation, not an untouched holdout. If these seasons cannot be qualified, report the shortfall and revise the plan **before** inspecting candidate outcome metrics. 2025 remains a development diagnostic; 2026 stays excluded from this work.

Freeze eligibility and common game IDs before fitting. Score NCAA games whose two teams have qualified pre-NCAA features; record eligible games, teams, conferences and exclusions by season and mode. Compare unchanged Elo, seed benchmark and one-feature challengers on exactly those same games, and also report full-sample fallback coverage. Do not compare a selected-subset challenger against the published all-game 68.9% baseline.

Start with one added feature at a time, then only supported combinations. Primary measures: log loss and Brier score; also calibration, winner accuracy, and results by season. Report season/tournament-cluster uncertainty with the few-season limitation explicit. Retain an addition only when probability-quality evidence supports it without an unexplained material regression; otherwise keep Elo. Game-level gains do not establish bracket gains: evaluate advancement probabilities separately using the unchanged tournament engine before promotion. Freeze any future untouched test prospectively.

## Reproduction and boundaries

Use [DATA.md](DATA.md) for exact hashes and restoration. Rebuilt `audit_season_appearances.py` from the season-appearance checkpoint (byte-identical output), `audit_player_source_expansion.py` from the field checkpoint's `expansion/raw`, and `audit_player_exceptions.py` from its original audit plus `field/raw` (byte-identical annotations). The expansion audit uses the current registry fingerprint. Inspect normalized `appearances[*].counts`, comparisons and per-mode gates for the matrix above.

All 121 existing tests pass (91 scripts, 30 historical). No new model test or accuracy claim is implied. No fresh collection, 2026 evaluation, model/app change or raw-data commit occurred. The unavailable conference-archive checkpoint is unnecessary for these four pilots; its newer field/access results were not rerun. Spreadsheet comparison, UI changes and hosting migration remain deferred.
