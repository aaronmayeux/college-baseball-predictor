# Historical team-component source decision

Reviewed September 26, 2026. This is a source decision, not a data qualification or model experiment.

## Decision and stop rule

**Keep Elo and do not start component-stat collection. Select College Splits as the single prospective licensed-sample route.** Its role supplying FanGraphs and its advertised NCAA event data make it a better targeted inquiry than another school sweep. This is an engineering judgment, not verified coverage, an available license, or a purchase recommendation.

No reviewed route currently establishes all three requirements: complete 2021–2024 team components, reconstruction of both forecast modes, and permitted acquisition/use. Stop public-source discovery here. Do not retry NCAA access, expand school probes, buy a FanGraphs membership for this purpose, or implement a speculative importer. Reopen only on a provider response or an authorized supplied dataset meeting the requirements below. No provider contact, account signup, purchase or authenticated sample request occurred.

## Evidence and limits

Public documentation was read through web retrieval; these are documentation observations, not retained API payloads or measured coverage. URLs below are the provenance for this decision. No new raw source bytes or game exports were downloaded into the project; existing evidence remains unchanged. General searches returned substantial irrelevant material, which was not used. No 2026 game feed or model inputs were collected.

| Route | Evidence reviewed | Decision |
|---|---|---|
| College Splits | Its [About page](https://collegesplits.com/about) advertises NCAA event-level data and data-distribution services. FanGraphs identifies it as its college supplier. No delivered sample, historical completeness matrix, price or applicable license was obtained. | Sole prospective sample/license inquiry; unqualified for ingestion. |
| FanGraphs | [March 2025 announcement](https://blogs.fangraphs.com/weve-got-college-data/) advertises D1 history from 2021 and member exports. It does not establish dated team-game exports, both project phase filters or our automated-use rights. | Do not infer forecast-safe availability from season coverage or membership. Approach the upstream supplier instead. |
| Highlightly | [API documentation](https://highlightly.net/mlb-api/documentation/) describes team match statistics as MLB and warns fields can be absent. Its wider NCAA offering does not establish this endpoint's NCAA coverage in 2021–2024. No authenticated sample tested. | Not selected: extra coverage/schema uncertainty. |
| Highlightly terms | [Published terms](https://highlightly.net/terms/), updated July 24, 2026, allow application data storage/use but restrict API resale, competing databases and gambling/gaming operations. | Bracket-product suitability would need clarification; no license-fit conclusion. |
| NCAA, ESPN, schools, D1Baseball | Existing [source findings](Statistics_Discovery_and_Triage.md#sourceaccess-findings): NCAA access unresolved, ESPN historical gaps, school-specific work, D1 automation prohibition. No fresh endpoint probes. | Not reopened. Retained examples do not establish a national component feed. |

These findings mean **not qualified**, not that historical data do not exist. Source quality, licensing and cost remain distinct questions.

## One bounded provider sample

This specification is ready for an authorized inquiry; it has not been sent. Ask College Splits whether it can deliver:

1. A coverage manifest for all 64 NCAA tournament teams in each of 2021–2024 (256 team-seasons): stable provider/team IDs, dated game inventory, available batting/pitching fields, missing games and known corrections. Request inventory metadata before bulk stats.
2. One machine-readable sample package containing complete dated team batting and team pitching logs for **LSU and Towson in each of 2021–2024** (eight team-seasons), including conference-tournament games where played. These contrast programs/conferences, reuse existing reference experience, and are selected without candidate outcomes. They test schema and season coverage, not national completeness or predictive performance. No substitution of a more convenient school/year and no sequential school requests; missing sample history is a reported failure. Include postseason rows only as exclusion/audit checks.
3. Counts, definitions and explicit missing values: batting AB, H, 2B, 3B, HR, BB, HBP, SO, SF, SH, PA and interference/other PA awards; team pitching outs, H, R, ER, BB, HBP, SO, HR and BF. Provide team ER directly rather than assuming summed pitcher ER equals it. Do not require individual pitcher histories, roles, pitch counts or availability.
4. Game ID, opponent ID, season, game date/time and timezone, completion/resumption information, status, phase, source provenance and correction policy. Unavailable historical publication times must be disclosed; retrieval today never proves availability then.
5. Written permitted delivery/automation, local raw-cache retention and reproducible model-research rights, plus use of derived predictions/stat summaries in Aaron's bracket app. Clarify duration, historical package price, future on-demand updates and restrictions. Do not request player histories or a recurring live feed. No price or budget is assumed.

Acceptance: reconcile the sample against retained result inventories and any existing independent count evidence; explicitly disclose where only within-provider checks are possible. Reject duplicates, unresolved identities/dates, missing eligible games and invented zeros. Aggregate counts before rates, validate innings as outs, and check PA/BF including interference. A missing denominator blocks its rate, not every unrelated count. Final-season totals are audit-only.

Apply unchanged [cutoffs.json](../historical/cutoffs.json), v2 completion corrections and two-calendar-day availability assumption; keep regular-only and conference-inclusive separate. A generic provider “regular season” label is insufficient until conference-tournament classification agrees. Snapshots must independently support both modes and their exact eligible game sets; a single pre-NCAA total cannot replace dated logs. Eight passing histories would clear only the sample gate. Require manifest reconciliation and complete selected-field component coverage before a full-field experiment; no partial rows silently changing the common sample.

## Retain Elo versus licensed data

| Choice | Benefit | Cost / remaining limit |
|---|---|---|
| Retain Elo now (selected) | Usable full-field app and established evaluations; no new acquisition needed | Does not distinguish component hitting/pitching styles. Fresh production ingestion remains separately unqualified. |
| College Splits sample, only after authorization | One centralized delivery could make component testing practical | Price, permissions, sample delivery and all-field completeness unknown; even qualified data may not improve predictions. |

Next concrete step is Aaron's decision whether to authorize **one College Splits sample-and-license inquiry**, using the scope above, with no purchase commitment. Otherwise retain Elo and leave component acquisition paused; do not replace this decision with another open-ended source search.

The net-run candidate stays closed. [SPEC](../historical/SPEC.md) and [qualification](Model_Input_Qualification.md#fitting-and-promotion-boundaries) retain evaluation authority. No fitting or metrics were run. Any later component experiment must lock its recipe before fitting, retain common samples and advancement validation, and acknowledge 2024's prior validation exposure; it is not a fresh untouched holdout. 2025 remains development, 2026 excluded, and individual pitchers remain deferred.
