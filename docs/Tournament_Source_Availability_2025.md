# 2025 tournament source availability

September 21, 2026. **All 64 selected teams are represented; this is a development-only availability map, not nationwide player qualification.** The preserved NCAA selection announcement independently fixes the field and regional seeds. `historical/tournament_sources_2025.json` records reviewed discovery URLs; `scripts/audit_tournament_sources.py` reproduces statuses from retained responses. No tournament box-score sweep was performed.

## What is established

- 63 historical schedule pages plus LSU's preserved complete-season audit: **64/64**. Availability alone does not verify full-season game joins; qualified inventories are listed below.
- 49 historical cumulative pages with batting/pitching groups plus LSU's preserved audit: **50/64**. Presence is not reconciliation, pre-cutoff eligibility or a usable feature.
- **Only LSU (1/64)** has reconciled core hitting and pitching counts in the current 2025 field. The other three completed pilot teams are different seasons and do not count toward this field.
- **0/64** have qualified recent workload or a production-validated fallback. **64/64** now have validated development team-only matchup mechanics, with unknown availability and uncalibrated uncertainty explicit. This is not a complete-bracket fallback engine. The source-map rows retain their original production-validation gate; the separate fallback audit owns the narrower mechanics result.
- Three additional pages (Cincinnati, UCLA, Arizona State) expose season-specific WMT links only; those links are not player groups or verified coverage.
- Bulk collection is disabled for every entry. No thresholds, scaling, model inputs, interface or simulator changed.

## Access gate

47 field entries have pages linking [SIDEARM's terms](https://sidearmsports.com/sports/2022/12/7/terms-of-service). They permit personal-use copying subject to notices, but this review establishes neither a bulk automation volume nor permission to redistribute source content. This is not an asserted blanket automation ban. The other 17 entries retain unverified provider terms. A successful response or permissive robots rule alone is not permission.

Little Rock’s school robots file disallows all paths; its school schedule was not requested. Its conference’s own 2025 archive supplies results and player totals, but redirects to `static.ovcsports.com`; rules for that destination remain unverified. Dallas Baptist’s school robots request returned 502; its Conference USA schedule supplies the historical index instead. Clemson’s separate data host returned robots 404 (missing file); its two bounded archive probes succeeded, without establishing bulk terms. The Presto terms request returned 403; its terms remain unverified. Existing D1Baseball restrictions remain binding and no requests were made to it. For each provider, establish acceptable automated use/volume or a licensed feed before collecting complete player histories. Do not contact providers without Aaron's authorization.

The SIDEARM terms were rechecked and retained in the access checkpoint; no numeric automated collection allowance was established. The primary path remains official-school archives where permitted. Opponent/conference boxes and a licensed provider are potential alternatives, not certified fallbacks. Historical cumulative totals are audit targets only. Never replace missing pitch counts or appearances with zero workload, and never infer that an unknown pitcher is rested.

## Per-team map

**Index** = historical schedule page found; **audit** = preserved LSU reconciliation. **Groups** = historical batting/pitching groups present, not validated counts. **Gap** = not yet verified, not proof data does not exist. Links point to the tested schedule when available; otherwise the candidate origin. **S** = linked SIDEARM personal-use terms, bulk volume unverified; **U** = terms unverified. Every row has unknown recent workload and requires a validated fallback. These flags apply to both forecast modes; only LSU has completed box coverage in both (55 regular-only, 57 conference-inclusive).

| Team | Schedule | Player totals | Access | Remaining work |
|---|---|---|---|---|
| [Louisville](https://gocards.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [East Tennessee State](https://etsubucs.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Vanderbilt](https://vucommodores.com/sports/baseball/schedule/season/2024-25/) | Index | Gap | U | Historical archive found; qualify totals and box parser |
| [Wright State](https://wsuraiders.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Texas](https://texassports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Houston Christian](https://hcuhuskies.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [UTSA](https://goutsa.com/sports/baseball/schedule/season/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [Kansas State](https://kstatesports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Arkansas](https://arkansasrazorbacks.com/sport/m-basebl/schedule/?season=2024-25) | Index | Gap | U | Historical archive found; qualify totals and box parser |
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
| [Little Rock](https://ovcsports.com/custompages/stats/baseball/2025/lr.htm) | Index | Groups | U | OVC archive: 61 result joins; player appearance histories still unverified |
| [Dallas Baptist](https://conferenceusa.com/schedule.aspx?schedule=4255) | Index | Gap | S | Conference archive found; qualify player totals and boxes |
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
| [Murray State](https://goracers.com/sports/baseball/schedule/2025) | Index | Gap | S | Cumulative has a 5/4/2024 Southern Ill. row; preserve date conflict |
| [West Virginia](https://wvusports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Kentucky](https://ukathletics.com/sports/baseball/schedule/2025) | Index | Gap | U | Locate/qualify historical player totals |
| [Clemson](https://data.clemsontigers.com/Stats/Baseball/2025/teamstat.htm) | Index | Groups | U | 63 result joins including separate suspension annotation; appearance histories unverified |
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
| [Cincinnati](https://gobearcats.com/sports/baseball/schedule/2025) | Index | Gap | U | Historical WMT stats link extracted; destination untested |
| [Tennessee](https://utsports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Miami (OH)](https://miamiredhawks.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [UCLA](https://uclabruins.com/sports/baseball/schedule/2025) | Index | Gap | U | Historical WMT stats link extracted; destination untested |
| [Fresno State](https://gobulldogs.com/sports/baseball/schedule/2025) | Index | Groups | U | Reconcile permitted game/player histories |
| [UC Irvine](https://ucirvinesports.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Arizona State](https://thesundevils.com/sports/baseball/schedule/2025) | Index | Gap | U | Historical WMT stats link extracted; destination untested |
| [Alabama](https://rolltide.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Miami (FL)](https://miamihurricanes.com/sports/baseball/schedule/season/2024-25/) | Index | Gap | U | Locate/qualify historical player totals |
| [Southern Miss](https://southernmiss.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |
| [Columbia](https://gocolumbialions.com/sports/baseball/schedule/2025) | Index | Groups | S | Reconcile permitted game/player histories |

## Reproducibility and next gate

Retain raw response bytes, URL, retrieval time, SHA-256 and failed-request metadata in the separate checkpoint described in [DATA.md](DATA.md#full-field-source-map-and-exception-evidence). Availability describes the retrieved snapshot, not a promise of current access. Legacy pages are screened by historical title (or explicit schedule heading) and group labels; embedded cumulative pages additionally require the requested historical payload path and explicit game years. Schema checks deliberately do not certify player identities, every box link or all game dates. Unhandled source conventions remain gaps.

Nuxt empty refs now decode without turning missing values into workload zeros. For WMT-linked pages, retained same-host redirect, payload path, baseball season and destination ID must agree. The historical roster is selected explicitly; default/current roster metadata is not used. These pages contain destination links, not the destination statistics. Murray State’s mixed-year cumulative row remains rejected; no date correction is inferred.

The Clemson 2025-26 response and Conference USA’s default DBU 2026 schedule link are quarantined discovery evidence only; no 2026 outcome was used for modeling or evaluation, and 2026 remains uncertified. Final cumulative pages include postseason and must never become pre-NCAA features. Preserve regular-only and conference-inclusive cutoffs.

Next resolve provider scope and redirect-host rules, remaining player-source/parser gaps and full appearance histories. Extend the mechanically checked fallback with validated uncertainty/tournament behavior before any complete-bracket claim. All schedule sources are now identified; most game inventories and nearly all player histories remain unverified. No live refresh or scheduler is needed.

## Collection volume (offline planning only)

`plan_tournament_collection.py` sizes the preserved D1 results inventory across all 64 teams; it does not fetch, authorize requests, qualify a fallback or change model inputs. The [conference-archive checkpoint](DATA.md#conference-archive-qualification-evidence) preserves its inputs and output hashes.

| Scope | Team-game sides | Distinct games touching field teams |
|---|---:|---:|
| Full-season count reconciliation | 3,852 | 3,159 |
| Regular-only, existing pre-NCAA cutoff | 3,396 | 2,865 |
| Conference-inclusive, same cutoff | 3,580 | 3,023 |

These are known D1 game counts, **not a certified request budget**. A shared box can save a second download only after both team sides are qualified. Non-D1 physical workload, missing sources, indexes/totals, separate PDFs and validation requests add work; retained cache can reduce fresh downloads. Conference-game physical workload is still relevant at bracket lock even when strength features use regular-only inputs. All 64 retain explicit unknown workload and unvalidated fallback status. No full-season box sweep occurred. Clemson and Little Rock result inventories and cumulative sum checks are qualified separately below; their appearance histories are not reconciled.

## Conference alternatives and archive qualification

The [shared StatCrew audit](../scripts/audit_statcrew_archives.py) reads retained Clemson and Little Rock archives through the source registry, verifies explicit report years and source identities, joins results, and compares listed player sums with team totals. Full-season totals remain audit targets only.

| Check | Clemson 2025 | Little Rock 2025 |
|---|---:|---:|
| Strict result joins | 62/63 | 61/61 |
| Result joins including separately evidenced completion | 63/63 | 61/61 |
| Regular-only eligible result inventory | 56/56 | 51/51 |
| Conference-inclusive eligible result inventory | 60/60 | 56/56 |
| Listed batters / summed GP | 16 / 652 | 18 / 655 |
| Listed pitchers / summed appearances | 22 / 279 | 18 / 241 |

Mapped additive core counts match team totals. Individual pitcher ER sums are 316 versus Clemson’s team 310 and 378 versus Little Rock’s team 376; retain these separately because team-unearned scoring can produce this distinction. Summed player GP/appearances are not team game counts. These checks cannot reveal an omitted zero-count player, establish stable player IDs or qualify pre-cutoff features. No new complete appearance history is claimed.

Florida State’s retained [May 4 recap](https://seminoles.com/news/2025/5/4/baseball-series-evened-as-no-5-fsu-edged-by-no-3-clemson-in-suspended-game) confirms the 6–3 Clemson game began May 3 and finished May 4 after an overnight suspension. A separate result annotation preserves the strict May 3 source row and links the existing May 4 baseline result. The baseline stays unchanged and individual work dates remain unknown.

The [OVC archive](https://ovcsports.com/custompages/stats/baseball/2025/lr.htm) contains Little Rock’s results and cumulative player groups. Conference USA’s 2025 statistics page linked to a default 2026 DBU schedule; that response was rejected. Its season selector explicitly identifies [2025 schedule 4255](https://conferenceusa.com/schedule.aspx?schedule=4255). No outcome from the rejected response was used in modeling.

`audit_source_access.py` reproduces the access findings from retained bytes. OVC and Conference USA robots allow the tested archive paths for our declared research agent with a **five-second crawl delay**; this is pacing guidance, not verified bulk-use permission. WMT Games’ robots URL returned an HTML application shell, so access rules remain unknown and no historical stats destination was requested. WMT Digital allows crawling, but its tested terms candidate returned 404 and the retained homepage linked only privacy/contact information. Rules on WMT Digital do not authorize WMT Games. No provider contact or license grant occurred.


## Retained-source expansion and team-only fallback

`audit_retained_inventories.py` applies the shared embedded schedule parser to the retained full-field pages. Louisville joins **66/66** results and Mississippi State **59/59**. Their regular-only / conference-inclusive inventories reconcile **55/56** and **54/55** games, respectively. These are result inventories only; **LSU remains the sole field team with fully reconciled core appearances**.

Louisville's completed May 11 Georgia Tech loss retains “Postponed to 5/11.” The parser accepts only this explicit rescheduling form when its destination matches the source row date, retaining the original label. Canceled, suspended and conflicting-date labels still fail. Louisville's five opponent aliases are scoped to its retained website/location metadata; “Miami” requires the Coral Gables/Hurricanes record, never a global name guess. With the additional scoped identity reviews below, this audit yields 11 reconciled inventories, 21 unresolved result joins, 16 parser/inventory gaps and 16 without a supported embedded schedule. These statuses do not erase existing LSU/StatCrew qualifications. No additional boxes were downloaded or appearances certified.

The reviewed configuration in `historical/schedule_aliases_2025.json` resolves nine more embedded schedules using exact source titles, school websites and locations. Each mapping applies only to its named 2025 schedule. Changed metadata, unreviewed title variants, missing reviewed records, unknown targets and identity collisions block qualification; date, score and duplicate checks remain strict. Raw labels are preserved. No global “Miami” alias is added.

| Additional reconciled team | Full-season games | Regular-only eligible | Conference-inclusive eligible |
|---|---:|---:|---:|
| Texas | 58 | 53 | 54 |
| Kansas | 60 | 56 | 58 |
| North Carolina | 61 | 51 | 54 |
| Duke | 62 | 54 | 56 |
| TCU | 59 | 54 | 57 |
| Ole Miss | 64 | 55 | 59 |
| Cal Poly | 62 | 53 | 58 |
| Oregon | 58 | 54 | 56 |
| UC Irvine | 60 | 52 | 56 |

All expected results match in each displayed scope. This expansion was reproduced using the supplied access/parser checkpoint; its 64-team field audit represents the older 62-schedule discovery snapshot, not a replacement for the current 64-source map. The conference checkpoint was not supplied this session, so the current field/access/StatCrew audits were not rerun. No sources were fetched, and no player appearances, actual work dates or collection permissions were newly qualified.

`audit_collection_scope.py` reviews each retained probe path and robots-host root separately. It distinguishes explicit robots denials, missing/error/HTML responses, unresolved pattern/precedence handling and personal-use terms. Bot-specific exclusions are not applied to unrelated agents. Retained redirects to static OVC, Binghamton, Texas and Kansas State origins remain separately flagged; origin rules cannot be transferred. The current SIDEARM terms still state personal-use copying, with no numeric automation allowance found. This is not a blanket automation prohibition. **Zero new bulk requests is the project's current gate, not a provider-declared quota.** No provider contact occurred. Further nationwide scope remains unresolved.

`audit_team_fallback.py` reconstructs the unchanged fixed neutral Elo using the separate v2 timing evidence and existing frozen cutoffs. It retains all 64 teams, reports coverage per team, and checks all **2,016 possible pairings per mode**. Both modes reproduce v2 probabilities for all **136 observed 2025 NCAA games**, with zero numerical difference. The existing 63.2% winner accuracy is unchanged, not a new improvement or bracket score. Missing eligible team results block a matchup; missing player information does not drop a team or alter its rating.

Every fallback row retains unknown recent workload, no available-pitcher list, no player adjustment and a null, explicitly uncalibrated strength interval. These checks validate development matchup mechanics only. Numeric availability uncertainty, tournament state, advancement probabilities and complete-bracket behavior remain unimplemented. No thresholds/scaling were selected; 2026 was not used. Reproduction uses the existing checkpoints in [DATA.md](DATA.md#offline-scope-inventory-and-fallback-checks).
