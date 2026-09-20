# Timing and seed validation — v2

The original dataset, Elo code, predictions and metrics remain unchanged. This separately versioned extension re-admits two resolved 2023 games to frozen forecasts and compares the same fixed Elo against a seed benchmark. Run/recovery commands and checkpoint hashes live in [DATA.md](DATA.md).

## Timing resolutions

| Game | Start | Completion | Evidence and treatment |
|---|---|---|---|
| Kent State 10–5 Ohio State, `30070` | April 26, 2023 | April 26 | Both [Kent](https://kentstatesports.com/news/2023/4/26/baseball-fly-the-flag-flashes-double-up-buckeyes-10-5) and [Ohio State](https://ohiostatebuckeyes.com/news/2023/4/26/buckeyes-split-home-and-home-series-against-kent-state) describe Wednesday’s completed game. Kent’s April 25 schedule entry is stale. |
| Columbia 14–13 Dartmouth, `28465` | April 22, 2023 | April 23 | [Suspension report](https://gocolumbialions.com/news/2023/4/22/baseball-defeats-dartmouth-in-game-one-game-two-called-due-to-darkness) records 11–11 after nine; [completion recap](https://gocolumbialions.com/news/2023/4/23/baseball-sweeps-dartmouth-with-two-wins-on-senior-day) confirms Sunday’s 12-inning finish. |
| Fordham 12–9 Richmond, `28885` | April 22, 2023 | April 23 | Newly detected by broader checks. [Updated recap](https://fordhamsports.com/news/2023/4/22/baseball-game-suspended-in-9th-rams-lead-12-9.aspx) and [Sunday recap](https://fordhamsports.com/news/2023/4/23/baseball-falls-in-finale-at-richmond.aspx) confirm Sunday completion. Already included on the correct completion date in v1; no rating-input change. |

Original fields and evidence references remain in each v2 resolution. The two-calendar-day availability assumption runs from completion date; Columbia’s final result cannot enter ratings before April 25 at 00:00 UTC. Exact completion/publication times remain uncertified. This extension emits frozen forecasts only: daily forecasts for suspended games require separate start-time prediction and completion-time update events.

## Independent checks

- 1,019 scored schedule observations across 18 school-seasons and 13 schools, using cached official evidence for 2021–2024. Of these, **1,016 are independent of the result source**, covering 988 distinct D1 games; three recheck the same school evidence used for existing supplements.
- 59 explicit phase observations: 35 conference tournament and 24 regional. Missing event labels remain unverified, rather than being treated as proof of regular-season play.
- All 128 opening regional fixtures in 2022–2025 match the selection-announced pairings and phase. 124 match the planned opening date; four completion exceptions have additional school evidence: two 2022 Coral Gables games, Georgia Southern–UNCG in 2022, and Kansas State–Louisiana Tech in 2024. The [Louisiana Tech recap](https://latechsports.com/news/2024/6/1/baseball-diamond-dogs-season-ends-in-the-fayetteville-regional) confirms the 19–4 game finished Saturday after a 13-hour weather delay.
- Columbia’s purported 2021 page still returns 2026 and is rejected. Missouri State’s 2023 page contains one explicitly identified October 2022 fall exhibition against Drury, retained as outside-season evidence and excluded from comparison.

These are targeted checks, not independent national completeness certification. Opponent aliases are explicit; dates, scores and phases must match uniquely. Raw bytes, retrieval timestamps, URLs and hashes are retained; unresolved matches block v2 evaluation.

## Seed benchmark contract

256 team-season seed records cover all tournament teams in 2022–2025. Sources are the NCAA’s dated selection announcements: [2022](https://www.ncaa.com/news/baseball/article/2022-05-30/2022-ncaa-di-baseball-championship-bracket-announced), [2023](https://www.ncaa.com/news/baseball/article/2023-05-29/2023-ncaa-division-i-baseball-championship-bracket-announced), [2024](https://www.ncaa.com/news/baseball/article/2024-05-27/2024-ncaa-division-i-baseball-championship-bracket-announced), [2025](https://www.ncaa.com/news/baseball/article/2025-05-26/2025-ncaa-di-baseball-championship-bracket-announced). Article metadata identifies publication on May 30, 2022; May 30, 2023; May 27, 2024; and May 26, 2025. Both publication and modification timestamps must precede the recorded forecast cutoff. The 2023 URL date is not used as its publication timestamp.

Only original regional seeds 1–4 enter the comparator. Each one-step better seed doubles the odds: `P(A wins) = 1 / (1 + 2 ** (seed_A - seed_B))`. Equal seeds yield 50%; national seeds and later bracket results are unused. This fixed, untuned heuristic is not a calibrated seed model. Equal-seed picks receive half-credit for accuracy. Seeds reflect committee information, including conference tournaments; they do not become regular-only Elo inputs.

Every season must have 16 complete four-team regions and 64 unique mapped identities. Missing or late seeds cannot silently reduce supported-season coverage. The 2021 initialization season has no seed benchmark. All comparisons use identical game samples; results are retrospective matchup tests, not bracket predictions or untouched validation. Current pages with pre-cutoff publisher metadata are reconstructed evidence, not archived point-in-time certification.

## Results

Lower log loss and Brier score indicate better probabilities. This table uses regular-only frozen Elo; the generated metrics also contain conference-inclusive results and each NCAA phase.

| Period | Games | Model | Accuracy | Log loss | Brier |
|---|---:|---|---:|---:|---:|
| 2022–2024 | 411 | Preserved Elo | 68.9% | 0.616226 | 0.213630 |
| 2022–2024 | 411 | Timing-resolved Elo | 68.9% | 0.616232 | 0.213632 |
| 2022–2024 | 411 | Seed heuristic | 63.7% | 0.647538 | 0.227645 |
| 2025 development | 136 | Preserved Elo | 63.2% | 0.659165 | 0.232052 |
| 2025 development | 136 | Timing-resolved Elo | 63.2% | 0.659168 | 0.232053 |
| 2025 development | 136 | Seed heuristic | 65.8% | 0.658747 | 0.228176 |

Resolving the two quarantined games changes probabilities slightly through chronological rating carryover, but no winner picks. Elo beats this seed heuristic in pooled 2022–2024; seeds do better in 2025 development. These descriptive differences do not establish statistical superiority, and no tuning followed these results. 2026 remains uncertified as untouched and unused for modeling.

## Verification and next work

Six original and seven new offline tests pass. The original pipeline rebuilt successfully; original predictions, metrics and eligibility match the baseline bundle byte-for-byte. All ten v2 outputs reproduced byte-for-byte on a cached rerun. The evidence add-on restores without overwriting different local files.

Next: implement separate start/completion events for daily forecasts, extend independent phase coverage beyond the targeted sample, and lock a prospective holdout protocol before model or bracket-engine expansion. No interface was built.
