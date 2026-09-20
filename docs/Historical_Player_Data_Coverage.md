# Historical player-data coverage — initial audit

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

Internal checks compare player sums with provider team totals, including baseball outs (`6.2 IP = 20 outs`). They flag **two games**: Arkansas–Missouri State (`401394978`, May 3, 2022), with Arkansas batting R/BB and pitching H/R/ER/BB/K/HR/outs disagreements; and Towson–NC State (`401632674`, March 1, 2024), with a Towson pitching-outs disagreement. These are unresolved source inconsistencies, not evidence that one side is correct. Do not force every staff to 27 outs: walk-offs, shortened games and extra innings differ. Seven populated games pass the implemented sum checks; none is yet feature-qualified. Embedded cumulative AVG/ERA/OBP/SLG are excluded from feature use.

## Official-school fallback pilot

The [LSU archive](https://lsusports.net/bbstats/) linked all five historical indexes. Retained indexes list 63, 62, 71, 66 and 68 unique box links for 2021–2025, respectively, equal to baseline LSU game counts. **Equal counts are not game-by-game reconciliation and do not prove every link works.** Retrieved only the earliest listed box per season: all five expose a pitching BF header, HBP notation, pitches/strikes and narrative play-by-play. Those are schema-presence checks, not parsed/validated player counts. No full season of appearances has been certified.

These official boxes offer missing pitcher fields, but require school-specific parsing and player identity work. They are one school's sample, not a nationally viable fallback yet. Sources: [2021](https://static.lsusports.net/assets/docs/bb/21stats/lsu220.htm), [2022](https://static.lsusports.net/assets/docs/bb/22stats/lsu218.htm), [2023](https://static.lsusports.net/assets/docs/bb/23stats/lsu217.htm), [2024](https://static.lsusports.net/assets/docs/bb/24stats/lsu216.htm), [2025](https://static.lsusports.net/assets/docs/bb/25stats/lsu214.htm).

## Full-season inventory gate: LSU 2025

The offline `audit_official_season_inventory.py` now reconciles every dated game link in the retained discovery index against baseline identities and scores, rather than comparing counts alone. It rejects unknown identities, duplicate URLs, reused games, ambiguous same-score doubleheaders, malformed rows and wrong seasons. Three explicit source aliases are retained in the script; no fuzzy matching or baseline edits occur.

Of 68 index rows, **67 uniquely match on date, teams and score**. All 55 baseline-eligible regular-only games and all 57 conference-inclusive games match under the existing cutoff contract. These are game-inventory results, not player-data coverage. Only one linked box response is cached in the supplied discovery checkpoint; zero full-season appearance histories are verified. The cached count describes this checkpoint only, not all prior evidence or online availability.

The remaining row is LSU–UCLA, 9–5: the index says June 16; baseline game `wn:2025:51008` says June 17. LSU’s [suspension notice](https://lsusports.net/news/2025/06/16/lsu-ucla-game-suspended-will-resume-at-10-a-m-ct-tuesday) and [completion recap](https://lsusports.net/news/2025/06/17/baseball-defeats-ucla-9-5-to-advance-to-college-world-series-semifinal) explain start versus completion. These were verified through web search, not retained as new raw payloads. The strict inventory join remains blocked for this row; no date is silently replaced. This postseason game does not affect the two pre-NCAA inventory counts. Future workload imports must distinguish the actual day each pitcher worked; assigning the entire box to either date would be unsafe.

Eight new synthetic tests cover matching and failure cases; all 19 existing baseline, v2 and player-audit tests pass. The new audit reproduces offline from the baseline and discovery checkpoints already documented in DATA.md. No new evidence archive is needed. Smaller-conference boxes, the two ESPN inconsistencies and complete appearance reconciliation remain pending.

## Gate and next work

**Do not implement model features from this pilot.** Next qualify official boxes for a smaller-conference school alongside LSU, reconcile every dated appearance for selected team-seasons, and resolve the two ESPN disagreements against official boxes. Expand to conference tournaments, regionals, supers and Omaha as coverage strata only; respect forecast-mode cutoffs when later building inputs. Keep missing games distinct from rested/unused arms, and incomplete player totals distinct from zero performance.

Before larger collection, establish permitted automation volume and a viable fallback. ESPN is an undocumented interface; public responses do not establish a feed license. School bulk permission remains unverified. D1Baseball was not requested; its prohibition remains binding. No 2026 stats requested. Do not infer historical publication times from retrieval timestamps. Suspended-game start/completion separation, phase verification and prospective holdout locking remain open under [SPEC](../historical/SPEC.md).

Reproduction and raw evidence are in [DATA.md](DATA.md#historical-player-coverage-evidence). The baseline was restored solely as a read-only audit reference; no baseline, cutoff, v2, forecast mode or model output was changed.
