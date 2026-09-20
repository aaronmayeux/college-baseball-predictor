# Historical player-data coverage

September 20, 2026. Hitting profiles and pitching quality/depth are approved priorities. **Coverage qualification remains incomplete; no features fitted.** Thresholds and scaling remain open in [statistics triage](Statistics_Discovery_and_Triage.md).

## Design and limits

Bounded ESPN pilot: first Tuesday and Friday of March and May in each season, 2021–2025 (20 requested dates). On each scoreboard, select the lowest SHA-256 event ID in each of two strata, before reading its box: games involving SEC/ACC/Big 12/Big Ten/Pac-12 schools, and games involving only other conferences. Use each season's preserved affiliation, including Oregon State's 2025 independent status. Exact names plus explicit aliases only; unmapped teams are not silently guessed. Four date/stratum cells had no mapped candidate, leaving 36 games, 56 teams and 21 conference labels. This is a deterministic feasibility sample, **not random national coverage**. Postseason stages and full team-season appearance reconciliation are still pending.

The 20 scoreboards returned 760 events; 694 were completed, season-accepted candidates: 565 major-involved, 39 other-only, 90 unmapped. Selected summaries all returned HTTP 200 and passed event/season/scoreboard team-score checks. Thirty-five join uniquely to the baseline on requested date, teams and score. Oregon State–Hawaii (`401751766`) has ESPN timestamp May 6, 2025 04:30 UTC but a matching baseline result on May 5; keep this date-boundary case unresolved in the strict join. Requested-date strata are not certified local game dates. Never replace baseline dates from this pilot.

An exploratory `groups=50` request returned an empty May 2, 2025 scoreboard; the same request without that filter returned 35 events. Preserve both. Empty payloads are not proof no games existed. The default feed is itself incomplete/selected: baseline date totals are shown as context, not matched-denominator coverage percentages.

## ESPN results

“Rows” means both teams have nonempty groups, not verified completeness. “Plays” means some records, not a complete sequence of plate appearances.

| Season | Scoreboard events / baseline games on requested dates | Sampled games | Batting rows | Pitching rows | Any plays |
|---|---:|---:|---:|---:|---:|
| 2021 | 94 / 291 | 6 | 2 | 2 | 2 |
| 2022 | 154 / 382 | 8 | 2 | 2 | 2 |
| 2023 | 171 / 399 | 7 | 3 | 3 | 3 |
| 2024 | 164 / 417 | 8 | 1 | 1 | 1 |
| 2025 | 177 / 426 | 7 | 1 | 1 | 1 |
| Total | 760 / 1,915 | 36 | 9 | 9 | 9 |

Nine of 20 major-involved samples had rows; zero of 16 other-only samples did. Do not infer that every smaller-conference game is unavailable. All 192 batting rows and 78 pitching rows carried provider player IDs; all 78 pitchers had positive pitch counts. IDs are present, **not validated as stable across seasons, transfers or providers**. Starter flags exist; season roles/depth require complete appearance histories.

| Required evidence | Observed in the nine populated games | Consequence |
|---|---|---|
| Player batting | AB, H, R, HR, BB, K; no individual HBP, SF, SH, 2B or 3B columns | Cannot qualify individual PA/OBP/ISO from these rows alone |
| Team batting totals | HBP, SF, SH, doubles, triples and other hitting counts on all 18 team sides | Candidate route to team profiles; presence does not certify correctness or complete PA (e.g. interference) |
| Player pitching | IP, H, R, ER, BB, K, HR, pitch counts on all 18 sides; no BF/HBP columns | Per-out rates may be possible after reconciliation; K/BF, BB/BF and FIP inputs remain incomplete |
| Plays and venue | Present in the populated sample; venue labels also occur without boxes | No play-sequence, actual-venue, completion/publication or workload-history certification |

Internal checks compare player sums with provider team totals, including baseball outs (`6.2 IP = 20 outs`). They flag **two games**: Arkansas–Missouri State (`401394978`, May 3, 2022), with Arkansas batting R/BB and pitching H/R/ER/BB/K/HR/outs disagreements; and Towson–NC State (`401632674`, March 1, 2024), with a Towson pitching-outs disagreement. The official-school comparison below explains the missing Arkansas pitching appearance and Towson outs discrepancy; these remain flagged in the preserved ESPN payloads. Do not force every staff to 27 outs: walk-offs, shortened games and extra innings differ. Seven populated games pass the implemented sum checks; none is yet feature-qualified. Embedded cumulative AVG/ERA/OBP/SLG are excluded from feature use.

## Official-school fallback pilot

The [LSU archive](https://lsusports.net/bbstats/) linked all five historical indexes. Retained indexes list 63, 62, 71, 66 and 68 unique box links for 2021–2025, respectively, equal to baseline LSU game counts. **Equal counts are not game-by-game reconciliation and do not prove every link works.** Retrieved only the earliest listed box per season: all five expose a pitching BF header, HBP notation, pitches/strikes and narrative play-by-play. Those are schema-presence checks, not parsed/validated player counts. That initial check did not qualify a full season; the completed two-season audit below now reconciles counts.

These official boxes offer missing pitcher fields, but require school-specific parsing and player identity work. They are one school's sample, not a nationally viable fallback yet. Sources: [2021](https://static.lsusports.net/assets/docs/bb/21stats/lsu220.htm), [2022](https://static.lsusports.net/assets/docs/bb/22stats/lsu218.htm), [2023](https://static.lsusports.net/assets/docs/bb/23stats/lsu217.htm), [2024](https://static.lsusports.net/assets/docs/bb/24stats/lsu216.htm), [2025](https://static.lsusports.net/assets/docs/bb/25stats/lsu214.htm).

## Full-season inventory gate: LSU 2025

The offline `audit_official_season_inventory.py` now reconciles every dated game link in the retained discovery index against baseline identities and scores, rather than comparing counts alone. It rejects unknown identities, duplicate URLs, reused games, ambiguous same-score doubleheaders, malformed rows and wrong seasons. Three explicit source aliases are retained in the script; no fuzzy matching or baseline edits occur.

Of 68 index rows, **67 uniquely match on date, teams and score**. All 55 baseline-eligible regular-only games and all 57 conference-inclusive games match under the existing cutoff contract. These are game-inventory results, not player-data coverage. Only one linked box response is cached in the supplied discovery checkpoint; that checkpoint alone verifies no full-season appearance history. The cached count describes this checkpoint only, not all prior evidence or online availability.

The remaining row is LSU–UCLA, 9–5: the index says June 16; baseline game `wn:2025:51008` says June 17. LSU’s [suspension notice](https://lsusports.net/news/2025/06/16/lsu-ucla-game-suspended-will-resume-at-10-a-m-ct-tuesday) and [completion recap](https://lsusports.net/news/2025/06/17/baseball-defeats-ucla-9-5-to-advance-to-college-world-series-semifinal) explain start versus completion. These were verified through web search, not retained as new raw payloads. The strict inventory join remains blocked for this row; no date is silently replaced. This postseason game does not affect the two pre-NCAA inventory counts. Future workload imports must distinguish the actual day each pitcher worked; assigning the entire box to either date would be unsafe.

Eight new synthetic tests cover matching and failure cases; all 19 existing baseline, v2 and player-audit tests pass. The new audit reproduces offline from the baseline and discovery checkpoints already documented in DATA.md. No new evidence archive is needed. The two targeted smaller-conference boxes are now parsed below; complete season appearance reconciliation remains pending.

## Official pitching comparison: two smaller-conference sources

`audit_official_pitching.py` reads two retained official school boxes and the original ESPN summaries, with URL/hash, date, team and score checks. These are **targeted discrepancy cases, not a representative coverage estimate**. Towson’s 2024 and Missouri State’s 2022 schedules supplied the box links. Four new responses (two schedules, two boxes) are retained separately; all returned HTTP 200. No larger collection or bulk permission was established.

| Game / official school source | Verified finding | Remaining limitation |
|---|---|---|
| [Towson–NC State, March 1, 2024](https://towsontigers.com/sports/baseball/stats/2024/nc-state/boxscore/28316) | All seven pitchers match ESPN on outs, H, R, ER, BB and K. Towson recorded 25 outs (8.1 IP); ESPN’s team total says 24. Official individual rows and count totals reconcile. | Retain the aggregate conflict; do not discard the final 0.1-IP appearance or force 27 outs. |
| [Missouri State–Arkansas, May 3, 2022](https://missouristatebears.com/sports/baseball/stats/2022/arkansas/boxscore/5610) | Official box has 11 pitchers; ESPN has ten. Heston Tole’s missing 0.1-IP appearance accounts for 1 H, 2 R/ER, 1 BB and 1 K. All ten shared pitchers match on the six compared fields; official staff sums reconcile. | Official pitcher table lacks HR; individual HR attribution is not reconciled. All official NP values are zero and are normalized to unknown pitch counts, preserving raw zeros. |

Manual batting inspection also identifies Arkansas substitutes Kendall Diggs (1 R, 1 BB) and Zack Gregory (1 R) absent from ESPN’s batting rows. Those explain the batting R/BB sum differences. The automated comparison covers pitching only and does not claim every batting field is validated.

Across the four team sides, all **18 official pitcher rows** contain BF and HBP. Towson’s source also has positive pitch counts for all seven pitchers; Missouri State’s source has none. Positive ESPN counts are retained separately, not silently substituted into the official rows. Zero-out appearances are retained (including Nick Griffin); an appearance need not record an out. Team-total IP is blank on the official pages, so outs are summed from player rows rather than asserted from an absent total.

School roster links are present for home players, but cross-season/provider IDs remain unqualified. Comparison uses names only within each known game, with two explicit ESPN spelling aliases; it does not create stable player identities or infer roles from row order. Source bytes and both versions of conflicting counts remain untouched. No feature, workload threshold or rest rule was fitted.

Ten new synthetic tests cover missing appearances, unknown pitches, zero-out rows, baseball innings, aggregate conflicts, duplicate/unknown teams and names, and legacy HTML blank cells. All 27 prior tests still pass. Offline results repeat byte-for-byte. Reproduction and raw evidence: [DATA.md](DATA.md#official-pitching-comparison-evidence).

## Complete-season appearance pilot: LSU 2025 and Towson 2024

`audit_season_appearances.py` verifies retained source hashes, dated boxes, team/score identity, player counts and cumulative totals offline. `collect_season_appearances.py` is limited to these two historical seasons, caches responses/failures and makes at most one request per school host. This bounded pilot establishes tested access, **not permission for nationwide bulk collection**. No D1Baseball or 2026 statistics were requested.

| Check | LSU 2025 | Towson 2024 (CAA) |
|---|---:|---:|
| Official completed-game boxes retrieved and parsed | 68/68 | 54/54 |
| Strict date/team/score joins to preserved baseline | 67/68 | 54/54 |
| Pitchers / pitching appearances | 18 / 274 | 21 / 265 |
| Positive pitch counts / appearances | 273/274 | 238/265 |
| Zero-out pitching appearances retained | 16 | 6 |
| Batting leaderboard players / reconciled GP total | 20 / 875 | 17 / 601 |
| Regular-only eligible games / pitching appearances | 55 / 233 | 54 / 265 |
| Conference-inclusive eligible games / pitching appearances | 57 / 238 | 54 / 265 |

Every sampled pitcher's appearance count, outs, H/R/ER/BB/SO/WP/BK/HBP/AB matches the school's [LSU cumulative totals](https://static.lsusports.net/assets/docs/bb/25stats/teamcume.htm) or [Towson cumulative totals](https://towsontigers.com/sports/baseball/stats/2024). Every listed batting player's GP and AB/R/H/RBI/BB/SO also reconciles. This is within-school consistency, not independent certification. Final season totals are **audit targets only**; they include postseason where applicable and are never forecast features.

All 1,149 LSU and 854 Towson batting-table rows remain in the evidence. GP comparison excludes documented pitcher-only zero-batting rows: 274 LSU, 253 Towson. LSU excludes Dalton Beck's three pitcher-only appearances from batting GP; Towson includes Bobby Spencer's pitcher appearances in his batting GP because he also batted. These provider conventions are explicit and tested; unknown fielders are not silently discarded. No fuzzy player matching was needed; names remain scoped to one school-season, not stable cross-provider/transfer identities.

Blank, `--` and zero pitch counts remain unknown with original strings retained. BF is present throughout, but not independently reconciled to a cumulative BF total. Towson's April 14 box has 11 summed pitcher ER versus 9 team ER; these remain distinct, since team-unearned scoring can legitimately produce that difference ([StatCrew explanation](https://www.statcrew.com/sports/m-basebl/statc-m-basebl-body.html)). Individual ER still reconciles against each pitcher's cumulative total. Individual HR allowed, extra-base hitting/HBP/sacrifice inputs, starts/roles and play-by-play completeness remain unqualified. Full core-count reconciliation does not qualify every advanced metric.

The LSU–UCLA June 16–17 box now retains its suspension/resumption note as raw evidence. The strict June 16 source-date versus June 17 baseline-completion mismatch stays visible; no baseline correction or assumed individual appearance date is applied. LSU's April 22 box also notes a same-evening weather delay. Neither affects pre-NCAA game inventory completeness. **All eligible pre-NCAA games have parsed boxes in both forecast modes**, but source dates are not independently certified actual player-work dates or historical publication timestamps. Rest stays `unknown`; no missing appearance or missing pitch count becomes zero workload. No availability rule or model feature was fitted.

Twelve synthetic tests cover omitted HTML closing tags, zero-out/missing-count rows, wrong game identities/dates/scores, missing or duplicate boxes, unknown players, two-way-player conventions and conservative rest status. All 37 prior tests pass. Offline outputs reproduce byte-for-byte, with baseline/input hashes unchanged. Raw responses and audit output are retained in the separate season evidence checkpoint described in [DATA.md](DATA.md#complete-season-appearance-evidence).

## Expansion gate and next work

The next step is a **source registry and another small batch of whole team-seasons spanning different school publishing systems and smaller conferences**, using the same qualification checks. Do not extrapolate two schools' success to every tournament team.

1. Before nationwide collection, establish each provider's permitted automated use/volume or a licensed alternative. Record tested success separately from permission; do not automate D1Baseball under existing restrictions.
2. Build an explicit school/season source registry: schedule, all box links, cumulative audit totals, parser version, identities and failures. Inventory every completed official game, including non-D1 opponents for workload; baseline modeling exclusions must not erase physical pitching usage. Deduplicate shared opponent boxes and retain canceled/postponed/suspended games separately.
3. Qualify every team-season with game identity joins and every player's season appearance/count reconciliation, including zero-out appearances and substitutes. Preserve batting-GP conventions, missing pitch counts, ambiguous names and start/completion/appearance dates. Split eligible counts by the existing forecast contracts; audit-only postseason totals never enter pre-NCAA inputs.
4. At bracket lock, require an explicit coverage row for **every tournament team**, with separate hitting, season pitching-depth and recent-workload flags. No team may silently disappear because its player source failed. Where player detail remains unqualified, use a declared simpler team-level estimate with wider availability uncertainty; never label unknown arms rested. Validate that fallback before production.
5. Reconcile more schema samples before extending parsers nationally, then implement the approved hitting and pitching-quality/depth features on qualified chronological samples. Keep workload/quality/ace thresholds and scaling open. Simulate usage forward from the single frozen bracket snapshot; live updates and scheduling are unnecessary.

The preserved baseline, cutoff rules, forecast modes and holdout safeguards are unchanged. 2025 remains development; 2026 remains uncertified and unused. No interface or tournament simulator was built.
