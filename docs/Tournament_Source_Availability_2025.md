# 2025 tournament source availability

September 21, 2026. **All 64 selected teams are represented; this is a development-only availability map, not nationwide player qualification.** The preserved NCAA selection announcement independently fixes the field and regional seeds. `historical/tournament_sources_2025.json` records reviewed discovery URLs; `scripts/audit_tournament_sources.py` reproduces statuses from retained responses. No tournament box-score sweep was performed.

## What is established

- 58 historical schedule pages plus LSU's preserved complete-season audit: **59/64**. These are accessible indexes, not verified full-season game joins.
- 47 historical cumulative pages with batting/pitching groups plus LSU's preserved audit: **48/64**. Presence is not reconciliation, pre-cutoff eligibility or a usable feature.
- **Only LSU (1/64)** has reconciled core hitting and pitching counts in the current 2025 field. The other three completed pilot teams are different seasons and do not count toward this field.
- **0/64** have qualified recent workload or a production-validated fallback. Every row requires a validated team-level fallback/uncertainty policy until feature coverage is qualified. The baseline Elo exists, but is not yet a validated complete-bracket fallback engine.
- Bulk collection is disabled for every entry. No thresholds, scaling, model inputs, interface or simulator changed.

## Access gate

46 school pages link [SIDEARM's terms](https://sidearmsports.com/sports/2022/12/7/terms-of-service). They permit personal-use copying subject to notices, but this review establishes neither a bulk automation volume nor permission to redistribute source content. This is not an asserted blanket automation ban. The other 18 entries retain unverified provider terms. A successful response or permissive robots rule alone is not permission.

Little Rock's robots file disallows all paths; no schedule was requested. Dallas Baptist's robots request returned 502; collection stopped there. The Presto terms request returned 403; its terms remain unverified. Existing D1Baseball restrictions remain binding and no requests were made to it. For each provider, establish acceptable automated use/volume or a licensed feed before collecting complete player histories. Do not contact providers without Aaron's authorization.

The primary path remains official-school archives where permitted. Opponent/conference boxes and a licensed provider are potential alternatives, not certified fallbacks. Historical cumulative totals are audit targets only. Never replace missing pitch counts or appearances with zero workload, and never infer that an unknown pitcher is rested.

## Per-team map

**Index** = historical schedule page found; **audit** = preserved LSU reconciliation. **Groups** = historical batting/pitching groups present, not validated counts. **Gap** = not yet verified, not proof data does not exist. Links point to the tested schedule when available; otherwise the candidate origin. **S** = linked SIDEARM personal-use terms, bulk volume unverified; **U** = terms unverified. Every row has unknown recent workload and requires a validated fallback. These flags apply to both forecast modes; only LSU has completed box coverage in both (55 regular-only, 57 conference-inclusive).

| Team | Schedule | Player totals | Access | Remaining work |
|---|---|---|---|---|
| [Louisville](https://gocards.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [East Tennessee State](https://etsubucs.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Vanderbilt](https://vucommodores.com) | Gap | Gap | U | Two candidate paths returned 404; locate archive |
| [Wright State](https://wsuraiders.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Texas](https://texassports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Houston Christian](https://hcuhuskies.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [UTSA](https://goutsa.com/sports/baseball/schedule/season/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [Kansas State](https://kstatesports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Arkansas](https://arkansasrazorbacks.com) | Gap | Gap | U | Two candidate paths returned 404; locate archive |
| [North Dakota State](https://gobison.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Kansas](https://kuathletics.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Creighton](https://gocreighton.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [North Carolina State](https://gopack.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Stetson](https://gohatters.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Auburn](https://auburntigers.com/sports/baseball/schedule/season/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [Central Connecticut](https://ccsubluedevils.com/sports/bsb/2024-25/schedule) | Index | Gap | U | Locate/qualify historical player totals |
| [North Carolina](https://goheels.com/sports/baseball/schedule/2025) | Index | Groups | U | Reconcile permitted game/player histories |
| [Holy Cross](https://goholycross.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Oklahoma](https://soonersports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Nebraska](https://huskers.com/sports/baseball/schedule/season/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [LSU](https://lsusports.net/sports/bsb/schedule/season/2025/) | Audit | Audit | U | Actual work dates, feature/fallback validation |
| [Little Rock](https://lrtrojans.com) | Gap | Gap | U | Robots disallow; permitted alternative needed |
| [Dallas Baptist](https://dbupatriots.com) | Gap | Gap | U | Robots 502; access unresolved |
| [Rhode Island](https://gorhody.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Georgia](https://georgiadogs.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Binghamton](https://bubearcats.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Duke](https://goduke.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Oklahoma State](https://okstate.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [TCU](https://gofrogs.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [USC](https://usctrojans.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Oregon State](https://osubeavers.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Saint Mary's College](https://smcgaels.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Florida State](https://seminoles.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Bethune-Cookman](https://bcuathletics.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Northeastern](https://nuhuskies.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Mississippi State](https://hailstate.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Georgia Tech](https://ramblinwreck.com/sports/m-basebl/schedule/season/2024-25/) | Index | Gap | U | Locate/qualify historical player totals |
| [Western Kentucky](https://wkusports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Ole Miss](https://olemisssports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Murray State](https://goracers.com/sports/baseball/schedule/2025) | Index | Gap | S | Cumulative includes mixed-year rows; review exhibition/season scope |
| [West Virginia](https://wvusports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Kentucky](https://ukathletics.com/sports/baseball/schedule/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [Clemson](https://clemsontigers.com) | Gap | Gap | U | 2025 URL returned 2026; rejected; alternate 404 |
| [South Carolina Upstate](https://upstatespartans.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Arizona](https://arizonawildcats.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Cal Poly](https://gopoly.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Oregon](https://goducks.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Utah Valley](https://gouvu.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Florida](https://floridagators.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [East Carolina](https://ecupirates.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Coastal Carolina](https://goccusports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Fairfield](https://fairfieldstags.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Wake Forest](https://godeacs.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Cincinnati](https://gobearcats.com/sports/baseball/schedule/2025) | Index | Gap | U | Embedded EmptyRef parser gap |
| [Tennessee](https://utsports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Miami (OH)](https://miamiredhawks.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [UCLA](https://uclabruins.com/sports/baseball/schedule/2025) | Index | Gap | U | Embedded EmptyRef parser gap |
| [Fresno State](https://gobulldogs.com/sports/baseball/schedule/2025) | Index | Groups | U | Reconcile permitted game/player histories |
| [UC Irvine](https://ucirvinesports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Arizona State](https://thesundevils.com/sports/baseball/schedule/2025) | Index | Gap | U | Embedded EmptyRef parser gap |
| [Alabama](https://rolltide.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Miami (FL)](https://miamihurricanes.com/sports/baseball/schedule/season/2024-25/) | Index | Gap | U | Locate/qualify historical player totals |
| [Southern Miss](https://southernmiss.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Columbia](https://gocolumbialions.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |

## Reproducibility and next gate

Retain raw response bytes, URL, retrieval time, SHA-256 and failed-request metadata in the separate checkpoint described in [DATA.md](DATA.md#full-field-source-map-and-exception-evidence). Availability describes the retrieved snapshot, not a promise of current access. Legacy pages are screened by historical title and group labels; embedded cumulative pages additionally require the requested historical payload path and explicit game years. Schema checks deliberately do not certify player identities, every box link or all game dates. Unhandled source conventions remain gaps.

The Clemson 2025-26 response is quarantined discovery evidence only; no 2026 outcome was used for modeling or evaluation, and 2026 remains uncertified. Final cumulative pages include postseason and must never become pre-NCAA features. Preserve regular-only and conference-inclusive cutoffs.

Next establish provider access, resolve the listed archive/parser gaps, then reconcile each team-season and validate a simpler fallback before any all-team feature or bracket claim. Prioritize the shared SIDEARM route because it covers most discovered pages, while retaining the five schedule gaps explicitly. No live refresh or scheduler is needed.
