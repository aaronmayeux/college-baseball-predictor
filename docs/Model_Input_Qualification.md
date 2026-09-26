# Focused model-input qualification

Milestone 6 has a focused qualification plan and offline hitting and pitching extractors, including retained team game logs verified September 26, 2026. No feature weights, quality-arm thresholds or prediction changes are selected. The [triage](Statistics_Discovery_and_Triage.md) owns the broader inventory; [SPEC](../historical/SPEC.md) owns cutoff and holdout rules.

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
| LSU 2025 | 55/55; 57/57 | Core counts plus team extra bases/HBP/sacrifices reconcile; PA checks against opposing BF pass in all 68 boxes | Core counts, BF components and explicit lineup starts now reconcile; per-player sacrifices and starts match cumulative targets, with two play-derived CI awards supplementing BF; HR allowed remains unqualified |
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

LSU’s cached StatCrew pitching qualification is now implemented below. The staged expansion below now defines the next work for the evaluation contract. Existing LSU 2021–2024 indexes/sample boxes are candidates, not qualified seasons. Qualify both sides of evaluation matchups; one school's seasons alone cannot validate a national feature. Reuse caches/shared boxes and resolve access scope for the exact selected source before requests. Broad discovery and bulk collection remain paused pending the exact-source access gate below.

## Pitcher BF, roles and workload pilot

`extract_pitching_inputs.py` is a separate offline extractor for Davidson 2024 and Missouri State 2022. All **112 boxes / 435 pitching appearances** pass: each pitcher’s BF equals AB+BB+HBP+SF+SH+catcher interference; summed BF agrees with the team pitching total and opposing batting PA components. Missing components block qualification rather than becoming zeros. These within-source checks are not independent-provider certification; no direct cumulative BF target is claimed.

The existing structured audit reconciles each pitcher’s starts, appearances and mapped counts against cumulative pitching targets. The new check requires binary pitching `gamesStarted` and exactly one pitching start per game. Generic lineup `gameStarted` and row order do not assign roles. Zero-out appearances remain included. Roles describe the eligible appearances only: starter-only, relief-only, or mixed, with each pitcher counted once. They do not label rotation talent, quality arms or aces.

| Team / mode | Games | Pitchers: starter-only / relief-only / mixed | Appearances | Outs | BF | Appearances with pitch counts |
|---|---:|---:|---:|---:|---:|---:|
| Davidson 2024, either mode | 52 | 1 / 9 / 8 | 212 | 1,311 | 2,168 | 194 |
| Missouri State 2022, regular-only | 51 | 1 / 4 / 8 | 190 | 1,321 | 2,062 | 44 |
| Missouri State 2022, conference-inclusive | 57 | 0 / 3 / 10 | 209 | 1,477 | 2,280 | 63 |

Each player summary includes outs, BF, starts, relief appearances, maximum appearance outs, unadjusted (SO−BB)/BF, ERA and RA9. Counts are summed before division; zero denominators yield null. Pitch totals are null if any appearance lacks a count; separately labeled known-pitch subtotals and coverage remain available. A missing/bad eligible game or failed season pitching check blocks the mode’s player summaries.

The Missouri State completion annotation is preserved along with original dates/issues; it does not establish actual pitcher work dates. Rest and availability remain unknown for both teams. Davidson’s existing batting omission remains visible and does not invalidate its independently checked pitching records. Final cumulative counts serve only as audit targets. Towson pitching BF/roles remain unqualified by this extractor. LSU’s separate adapter is described below; only one 2025 team has these descriptive inputs, so no nationwide predictive qualification is claimed. No quality/depth thresholds, weights, national validation or prediction adjustments are enabled.

### LSU StatCrew verification

With `--season-raw-dir`, the pitching extractor also checks all **68 LSU 2025 boxes / 274 appearances**. The explicit `LSU starters` lineup identifies the pitcher by position `p`; the label must match exactly one pitcher’s surname token suffix. It never uses pitching-table order. Each pitcher’s starts and appearances reconcile to cumulative APP-GS. Labels, source bytes/hashes and original timing issues remain in the output.

Sacrifice flies, sacrifice hits and catcher-interference awards are allocated along explicit play-by-play pitching changes. Pitch-code letters and repeated review commentary are excluded. Every pitcher’s BF must equal AB+BB+HBP+SF+SH+CI, and every game’s summed BF must equal opposing PA components. Allocated sacrifices also reconcile per player against cumulative SFA/SHA. The cumulative table lacks CI: two source-play awards (one each during Kade Anderson and Zac Cowan appearances) supplement its denominator; no direct cumulative BF/CI field is claimed. One pitching change enters another batting slot and explicitly removes the prior pitcher; this is verified rather than assuming “for” always names the prior pitcher.

| LSU mode | Games | Pitchers: starter-only / relief-only / mixed | Appearances | Outs | BF | Appearances with pitch counts |
|---|---:|---:|---:|---:|---:|---:|
| Regular-only | 55 | 2 / 11 / 5 | 233 | 1,406 | 2,046 | 232 |
| Conference-inclusive | 57 | 1 / 11 / 6 | 238 | 1,460 | 2,115 | 237 |

Both modes are complete. The original LSU–UCLA postseason date mismatch stays visible and excluded; it does not prevent count-only season reconciliation. A missing pitch count stays unknown. Actual work dates, rest, pitcher quality thresholds and national feature validation remain unqualified. This is within-source count/role verification, not evidence of improved predictions.

## Chronological evaluation contract

The retained pilots, including two additional 2022 team hitting logs, provide **no sufficient common chronological evaluation sample**. There is no 2023 player pilot, and only LSU covers the 2025 field. Do not fit on this convenience sample or claim improvement from it.

Target qualified training inputs from 2021–2022, development selection on 2023, and a fixed later comparison on 2024. Fit all scaling, opponent adjustment, sample-size shrinkage and thresholds within the earlier training period; refit through 2023 only after choosing the candidate. Prior published baseline metrics mean 2024 is retrospective validation, not an untouched holdout. If these seasons cannot be qualified, report the shortfall and revise the plan **before** inspecting candidate outcome metrics. 2025 remains a development diagnostic; 2026 stays excluded from this work.

Freeze eligibility and common game IDs before fitting. Score NCAA games whose two teams have qualified pre-NCAA features; record eligible games, teams, conferences and exclusions by season and mode. Compare unchanged Elo, seed benchmark and one-feature challengers on exactly those same games, and also report full-sample fallback coverage. Do not compare a selected-subset challenger against the published all-game 68.9% baseline.

Start with one added feature at a time, then only supported combinations. Primary measures: log loss and Brier score; also calibration, winner accuracy, and results by season. Report season/tournament-cluster uncertainty with the few-season limitation explicit. Retain an addition only when probability-quality evidence supports it without an unexplained material regression; otherwise keep Elo. Game-level gains do not establish bracket gains: evaluate advancement probabilities separately using the unchanged tournament engine before promotion. Freeze any future untouched test prospectively.

## Multi-season expansion plan

Planning decision, September 26, 2026: qualify a **four-team preflight**, then target **the 64 NCAA field teams in each of 2021–2024 (256 team-seasons)** for the full-field experiment. This restricts new player histories to tournament participants; keep the existing nationwide results for Elo. Do not recursively collect every opponent's season or build cross-season player identities. The 256 is a scope choice for complete tournament coverage, **not a statistically proven minimum or permission to collect**. A smaller predeclared subset could support exploratory matchup research, but cannot answer the full-field/advancement question. No collection or fitting is enabled by this plan.

### First bounded step

Use the **2022 Stillwater regional: Oklahoma State, Arkansas, Grand Canyon and Missouri State**. Missouri State's retained season makes this three new team-seasons, with additional qualification still needed for Missouri State. Selection is based on reusable evidence and a complete four-team group, not results or feature performance. Do not replace difficult schools with convenient winners or inspect challenger metrics in this preflight.

The cached inventory contains 215 regular-only team-game rows (213 distinct games), or 232 conference-inclusive rows (230 games). These are **result inventories**, not fresh-request counts or qualified feature rows. The group's seven NCAA games are potential matchup targets; the preflight is too narrow for national validation. Begin with access review and one representative permitted/cached box per new source, then complete histories only if the gate passes. Reuse shared boxes only when both sides independently pass their count/identity checks. A box containing an opponent does not qualify that opponent's season.

### Bounded expansion and verified volume

An offline plan rebuilt from the hash-verified baseline and timing/seed checkpoints gives:

| Season / use | Field teams | Eligible team-game rows, regular / inclusive | Distinct input games, regular / inclusive | Potential NCAA targets |
|---|---:|---:|---:|---:|
| 2021 training; baseline initialization year | 64 | 3,118 / 3,309 | 2,668 / 2,825 | 139 |
| 2022 training | 64 | 3,395 / 3,621 | 2,894 / 3,086 | 141 |
| 2023 candidate selection | 64 | 3,399 / 3,643 | 2,878 / 3,072 | 137 |
| 2024 locked retrospective comparison | 64 | 3,387 / 3,602 | 2,907 / 3,089 | 133 |

Across the four seasons, conference-inclusive inputs cover 14,175 team-game rows in 12,072 distinct result games. The modes overlap; do not add their volumes. Actual requests also depend on cache reuse, two-sided parsing, schedules, cumulative audit targets, failed sources and full-season reconciliation. Non-D1 appearances must be retained for physical workload/audit purposes even when excluded from D1 quality features; these inventory counts do not include them. Final-total reconciliation may require postseason boxes, which remain audit-only and outside forecast features. The current extractors require full-season checks; do not silently weaken that gate to meet the smaller pre-cutoff count.

Only Missouri State 2022 among these 256 has a completed retained appearance pilot. Its ISO/OBP and pitching summaries can be reused, but PA remains unqualified. LSU 2021–2024 indexes and one sample box per season are leads, not complete histories. Towson/Davidson 2024 are outside the NCAA field. LSU 2025 remains a parser regression/development reference, outside this experiment.

### Gates before expansion or fitting

1. **Exact access scope:** record source host, historical paths, redirect destinations, terms/robots evidence, acceptable automated use/volume, cache coverage and proposed request budget. Existing successful probes and robots pacing do not establish bulk permission. All retained player-source registry entries still have unverified bulk permission; no fresh full-season sweep is presently cleared. Use permitted school/conference/opponent sources if available; record failures without bypassing restrictions. Do not contact providers without Aaron's authorization. D1Baseball remains excluded. If no route qualifies, report the blocker before collection.
2. **2021 field and comparators:** the separate selection check below now qualifies all 64 regional seeds for retrospective use. The optional preflight input replaces provisional result-participant membership in the expansion planner. Frozen v2 seed metrics still cover 2022–2025; integrating/scoring the new 2021 comparator remains future work. Preserve 2021's initialization label and fixed Elo state; its richer-input training role does not rewrite published baseline results.
3. **Per-feature qualification:** reconcile every required eligible game and cumulative audit target. Start with ISO, OBP as the comparator, and an aggregate staff (SO−BB)/BF challenger derived by summing qualified pitcher counts. Contact and HR/PA require separately qualified PA. Depth/aces follow only after quality, sample-size handling and roles qualify; choose workload/quality thresholds on training data only. Zero/missing denominators never become zero quality. Work dates/rest, park interactions and depletion remain deferred.
4. **Freeze before outcome scoring:** write a versioned manifest with source/code hashes, all planned teams and season-specific conferences, feature/mode qualification, both-team common game IDs, seeds and explicit exclusions. Decide missing-data and experiment rules before candidate metrics. Different feature packages need their own common-sample baseline; combinations use their intersection. A failed optional PA field need not invalidate ISO, but missing eligible ISO counts block ISO. Keep excluded teams in the app with unchanged Elo fallback. A coverage shortfall cannot silently redefine the full-field experiment: revise this plan before scoring.

### Verified preflight, September 26, 2026

`audit_expansion_preflight.py` replays bounded source probes offline. Sample choice is each school's earliest listed 2022 game, not a favorable result. No full-season box sweep or feature fitting occurred.

| School | Result inventory | Eligible regular / inclusive inventory | First-box qualification |
|---|---|---|---|
| Oklahoma State | 64/64 exact matches | 54/54; 59/59 | Both sides pass batting/pitching sums, pitcher BF components, opposing PA and explicit pitching GS; six pitchers total |
| Grand Canyon | 62/62 exact matches | 56/56; 60/60 | Same two-sided checks pass; seven pitchers total |
| Arkansas | 66/67 strict; 67/67 with separate completion annotation | 54/54; 56/56 after annotation | Both sides pass core batting/pitching counts; ten pitchers total. Extra-base/PA components and explicit roles not yet qualified |

The existing structured parser reads Oklahoma State's 16 pitching / 18 batting cumulative rows and Grand Canyon's 15 / 21. These are parsing checks, not season appearance reconciliation. The StatCrew core box reader now takes an explicit team name; its LSU wrapper retains identical output. Three boxes cover 23 pitching and 82 batting rows across six sides, not six complete team-seasons. Scoped source aliases are recorded in code and verified against dated reciprocal scores; no fuzzy team merging.

Arkansas's index dates the 11–6 Vanderbilt game May 14; the baseline correctly dates completion May 15 (`wn:2022:36425`). [Arkansas's suspension notice](https://arkansasrazorbacks.com/game-two-between-arkansas-vanderbilt-suspended-in-sixth-inning/) and [Vanderbilt's completion recap](https://vucommodores.com/arkansas-holds-on-to-even-series/) support the separate annotation. The strict row, null join and original issue remain intact. No baseline correction or pitcher-work-date assignment occurs.

**Access:** all three tested stats paths are allowed by the retained robots rules for the declared research agent. Oklahoma State/Grand Canyon specify 30 seconds between requests; Arkansas specifies no delay. Both structured sites link [SIDEARM terms](https://sidearmsports.com/terms-of-service), whose personal-use copying provision does not establish bulk automation scope or redistribution rights. Arkansas's linked privacy page supplies no collection license; archive terms remain unverified. No season-wide collection is cleared. Initial SIDEARM robots-to-cumulative probes were about 23 seconds apart, shorter than the discovered 30-second delay; later requests exceeded 30 seconds. Future requests must enforce the full delay, including redirects and discovery. No provider was contacted.

**2021 selection evidence:** `selection_2021.py` checks South Alabama's [May 31 announcement](https://usajaguars.com/news/2021/5/31/baseball-jags-to-compete-at-ncaa-gainesville-regional-as-no-3-seed.aspx) and its linked NCAA selection-bracket filename against the school-hosted PDF. All 64 identities, sixteen seed sets and 32 June 4 opening matchups pass. The PDF is a blank advancement bracket, visually checked; South Carolina's host marker is correctly attached to regional seed 2, not automatically seed 1. National seeds and team records are not model inputs.

The article reports publication 13:42 and modification 13:50:31 on May 31 without a timezone; even the conservative UTC−12 interpretation precedes the June 2 cutoff. PDF creation/modification metadata are May 31 08:48:20 UTC−04. This supports retrospective eligibility, not point-in-time certification. The article link and school-hosted filename match; its historical redirect chain was not observed. A guessed NCAA article returned 404; search also encountered an NCAA challenge page, which was not bypassed. Existing v2 seeds/metrics and historical routing remain unchanged. The planner's default without the new checkpoint still labels 2021 provisional; use its optional preflight directory to enable this evidence.

Next: qualify Arkansas's retained team hitting evidence if sufficient, then finish the remaining four-team pitching/appearance gates. Establish acceptable source-specific season scope before any additional collection. The structured team-log result below does not qualify pitcher histories or weaken appearance gates.

### Retained team hitting logs

`extract_retained_hitting.py` qualifies Oklahoma State and Grand Canyon 2022 **team hitting only**, with no new source requests. All 64 and 62 dated rows respectively join the preserved result inventory by exact date, mapped teams and reciprocal scores. Box URLs uniquely identify rows, including doubleheaders; row order never determines identity.

Ten batting fields sum exactly to both the game-log footer and cumulative individual batting sums; six available overall team counts also agree. Each school's retained first box independently parses to the same ten game counts. These are within-source consistency checks, not independent-provider certification. This separate team-level adapter meets full-season count reconciliation using complete dated logs; it does not replace or relax player appearance checks.

Every game's AB, hits, walks, strikeouts, extra bases, HBP, sacrifices and catcher interference agree with the matching opponent pitching row. PA components sum to explicit opposing BF in **126/126 games** and both season footers. Three Oklahoma State and one Grand Canyon interference awards are retained. Eight Oklahoma State opponent rows use the exact self-name `Oklahoma St.`; an explicit scoped alias is reviewed against matching box URLs, dates and reversed scores. Unreviewed aliases fail; no fuzzy identity matching.

| Team / mode | Eligible games | ISO | OBP | Strikeouts/PA | HR/PA |
|---|---:|---:|---:|---:|---:|
| Oklahoma State regular-only | 54 | .191591 | .389388 | 21.3268% | 3.3393% |
| Oklahoma State conference-inclusive | 59 | .186706 | .389187 | 21.4227% | 3.2706% |
| Grand Canyon regular-only | 56 | .173320 | .384071 | 15.4183% | 2.9347% |
| Grand Canyon conference-inclusive | 60 | .168004 | .384013 | 15.7423% | 2.7732% |

Both modes sum eligible game counts before division, using the unchanged cutoff and availability rule. Full-season/postseason totals are audit targets only. Missing counts, a failed season/sample check or an incomplete inventory blocks rates. An unqualified PA denominator blocks strikeout rate and HR/PA separately, preserving otherwise reconciled ISO/OBP. Source hashes, exact aliases, per-game failures, eligible IDs and code/input fingerprints remain in the ignored report.

These are unadjusted descriptive inputs, not predictive improvement. The four-team preflight now has power/OBP for three teams (including the existing Missouri State box-derived inputs), and PA-based hitting rates for two. Arkansas hitting remains unqualified; Missouri State PA and the new schools' pitcher histories remain separate gaps. No feature fitting, outcome metrics, national qualification, new bulk permission or app adjustment follows from this result. [DATA.md](DATA.md#retained-team-game-log-hitting) owns reproduction; no new evidence ZIP is needed.

### Fitting and promotion boundaries

Follow the chronological contract above: train on 2021–2022, select on 2023, lock the candidate and preprocessing/refit recipe, then refit through 2023 and compare once on 2024. Regular-only decides selection; conference-inclusive is a separately reported sensitivity run using the same selected feature recipe, not extra independent observations. Lock the exact small candidate/threshold grid before fitting; this planning step chooses no numerical cutoffs, weights, shrinkage or scaling. Start with one added input at a time; postpone opponent-adjusted player features requiring more opponent histories. Existing Elo remains the team-strength control, not proof the raw input is opponent-adjusted.

Use paired log-loss/Brier differences on the frozen common games, calibration and secondary accuracy. Report each season and tournament grouping; one retrospective validation season cannot supply a credible multi-season uncertainty estimate. Do not treat two modes, repeated team appearances or all games as independent replicates. No minimum gain or sample size is certified here. Inconclusive probability-quality evidence means retain Elo, not tune on 2024. No 2025/2026 expansion is required; 2025 stays development and 2026 excluded.

Advancement validation is a separate promotion gate. `tournament/field.py` currently hard-codes 2025 routing: qualify historical selection-day routing for the tested years before using the unchanged engine mechanics. A complete four-team group can test regional advancement; it cannot validate national title probabilities. Full-field paired game gains alone do not authorize changing the app.

## Reproduction and boundaries

[DATA.md](DATA.md#offline-hitting-input-pilot) owns restoration and both extraction commands. Repeated outputs are byte-identical. All **175 tests** pass (145 scripts, 30 historical; twelve new retained-log regressions), including 13 hitting tests for count formulas, unknown denominators, interference, replay comments, pitch-code confusion, missing/duplicate events, incomplete modes and chronological exclusions. Twelve pitching tests cover BF/interference, role flags versus generic lineup starts/order, missing counts, zero-out appearances, rates, incomplete modes and cutoff exclusions. Eight LSU tests additionally check explicit starter matching, ambiguity, event allocation, batting-slot changes, BF mismatches and cumulative interference/start reconciliation. Tests need no external data.

The LSU/Towson audit output contract remains unchanged; the generic StatCrew core reader preserves the LSU wrapper behavior. Input/config fingerprints remain unchanged during extraction. The input-extractor pilots used retained evidence; the bounded preflight requests above are a separate checkpoint. No 2026 evaluation, model/app change or raw-data commit occurred. The unavailable conference-archive checkpoint is unnecessary for these pilots; its newer field/access results were not rerun. Spreadsheet comparison, UI changes and hosting migration remain deferred.
