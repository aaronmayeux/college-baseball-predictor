# Historical team-component source decision

Reviewed September 26, 2026. Source qualification only; no new model experiment.

## Decision

**Use Aaron’s selected sources: Warren Nolan for the retained results backbone, NCAA for dated team batting/pitching reports, and D1Baseball for permitted reference use.** This is a personal, noncommercial, zero-budget project; [AGENTS.md](../AGENTS.md) owns those constraints. Elo stays; the net-run candidate stays closed and individual pitchers remain deferred.

The direct NCAA route supplies populated national OBP/ERA samples in all four seasons, but **not yet complete, cutoff-qualified features**. Earlier dated snapshots are necessary in 2021/2022. The proposed SportsDataverse audit is superseded; no paid inquiry or school sweep is queued.

## Direct NCAA archive: verified access and counts

The [official baseball statistics page](https://www.ncaa.org/championships/statistics-and-records/baseball/) links to the [historical archive](https://web1.ncaa.org/stats/StatsSrv/rankings?doWhat=archive&sportCode=MBA). Its public POST form accepts `sportCode=MBA`, `academicYear=<season>`, `doWhat=display`. The returned Division I menu pairs report dates with IDs. CSV POSTs to the same route use `doWhat=showrankings`, `div=1`, `rptType=CSV`, the menu-derived `rptWeeks`, and team `statSeq` 589 (OBP) / 211 (ERA), with the other three selectors -1.

`scripts/audit_ncaa_archive.py` verifies retained hashes, menu/request scope, response season/date/division/statistic, CSV schema, duplicate teams, records, counts and rate arithmetic. Each populated pair has matching names and records; every OBP and ERA reconciles. OBP supplies AB/H/BB/HBP/SF/SH; ERA supplies IP/R/team ER. Innings `.1/.2` mean one/two outs. These are source rows, not counts of tournament-eligible teams.

| Season | Through date | Report ID | OBP / ERA rows | Reclassifying rows per table | Finding |
|---|---|---:|---:|---:|---|
| 2021 | May 30 | 73 | 0 / 0 | 0 | Both explicitly return “No rankings for this category” |
| 2021 | May 28 | 72 | 0 / 0 | 0 | Same explicit empty response |
| 2021 | May 23 | 67 | 293 / 293 | 7 | Populated earlier weekly snapshot; later eligible games omitted |
| 2022 | May 30 | 75 | 0 / 0 | 0 | Both explicitly empty |
| 2022 | May 25 | 72 | 301 / 301 | 8 | Populated; stops during conference tournaments |
| 2023 | May 28 | 75 | 305 / 305 | 10 | Populated pre-NCAA date; field/game reconciliation pending |
| 2024 | May 26 | 90 | 305 / 305 | 10 | Populated; 64-team reconciliation below |

All tested through-dates pass the existing two-day availability assumption. That does not certify publication time or individual component-game inclusion. Empty reports are preserved as source availability findings, never zero-valued team data. The bounded earlier checks show that an empty latest menu option does **not** establish an empty season. No full archive sweep occurred. Missing SO/PA and pitching BF/K/BB also prevent dependent contact/strikeout-rate features.

## 2024 tournament-field reconciliation

`scripts/reconcile_ncaa_archive.py` rechecks baseline/v2 gates and the dated selection sources, reuses the verified selection-name mappings, and joins all **64 of 64** tournament teams to both tables. Only straight/curly apostrophe normalization is added; no fuzzy institution matching. None maps to a reclassifying row. It compares G/W/L/T and runs allowed against v2-corrected Nolan results, retaining game IDs, non-D1 source rows and fingerprints. Ties remain ties.

- **63/64 records and 59/64 runs-allowed totals agree** after adding seven explicitly retained non-D1 games for four teams. **59/64 agree on all five checks.** This is reconciliation evidence, not certification of component completeness.
- Non-D1 evidence: Grambling–Wiley (one), Nicholls–Dillard/Southeastern Baptist (four), Northern Kentucky–Miami-Hamilton (one), Western Michigan–Goshen (one). These remain excluded from the D1 model; no baseline edits.
- **62/64 teams have conference-tournament games** in the inclusive inventory. UC Irvine and UC Santa Barbara have none. No field team has a cutoff-eligible D1 result after May 26. The snapshot is conference-inclusive in scope, not a regular-only feature source.

Residual differences below are **NCAA minus Nolan D1 plus retained non-D1 totals**. No source is silently declared correct:

| Team | Record difference | Runs allowed difference |
|---|---|---:|
| Southeast Missouri State | None | -1 |
| Evansville | None | -5 |
| VCU | None | +5 |
| Northern Kentucky | +1 game, +1 win | +3 |
| Western Michigan | None | -4 |

Northern Kentucky's extra game is unexplained by the retained non-D1 row. The other four discrepancies persist despite identical records. Team totals alone cannot identify the conflicting game or distinguish scoring corrections from statistical exclusions. No school requests were made to resolve them. OBP components, earned runs and pitching outs have not been independently reconciled game by game.

**Neither forecast mode is qualified.** All-opponent NCAA counts cannot silently replace D1-only features; known non-D1 scores cannot subtract unknown AB/H/BB/ER/outs. A shared cumulative snapshot cannot remove conference tournaments. The older 2021/2022 snapshots introduce additional timing gaps, and no new fitting or evaluation is authorized by this access check.

## National snapshot date/phase feasibility

`scripts/plan_ncaa_snapshots.py` compares every retained NCAA Division I menu date with the v2-corrected Nolan inventory for all 256 tournament team-seasons. A compatible date must include **every** eligible D1 result for that mode and **no** excluded D1 result. It rejects final reports, respects the unchanged two-day delay, and keeps missing dates, timing conflicts and mixed phases blocking. Existing empty reports are removed from possible dates; unrequested options remain untested. No new source requests or metrics were run.

| Season | Regular-only menu-feasible teams | After excluding known empty reports | Compatible retained populated date* | Inclusive after excluding known empty reports |
|---|---:|---:|---:|---:|
| 2021 | 64/64 | 50/64 | 43/64 | 7/64 |
| 2022 | 62/64 | 61/64 | 22/64 | 4/64 |
| 2023 | 64/64 | 64/64 | 1/64 | 64/64 |
| 2024 | 64/64 | 64/64 | 2/64 | 64/64 |

*Date compatibility only: a populated national table does not yet establish a mapped, reconciled row for each counted team. These columns are not qualified feature coverage. The 2021 field uses retained NCAA result participants for planning, matching the existing expansion planner; the optional dated 2021 selection checkpoint is not consumed here. No seed evaluation is performed.

**Structural exception:** Army and Columbia played one retained regular-season game against each other on May 29, 2022, after their conference tournaments. A pre-conference snapshot misses it; a later snapshot includes tournament statistics. This prevents a single cumulative snapshot per team from reproducing the full regular-only scope, even if every menu option were populated. Original phase labels and results are unchanged.

The minimum date sets below cover only the date-feasible teams after removing known empty reports, not the complete field in the first two seasons:

| Season | Regular-only report dates | Compatible teams covered |
|---|---|---:|
| 2021 | May 13, 19, 24 | 50/64 |
| 2022 | May 18, 23 | 61/64 |
| 2023 | May 11, 18, 22, 28 | 64/64 |
| 2024 | May 8, 20, 26 | 64/64 |

The planner computes the smallest number of dates covering the compatible intervals, not the smallest number of new requests. No listed untested date is claimed populated. Known non-D1 games occur before the last target result for 3/2/4/4 regular-only field teams respectively (4/2/4/4 inclusive); those component-scope gaps also remain. The seven retained national sample pairs are insufficient for complete four-season features in either mode.

**Decision:** stop treating one cumulative pre-conference snapshot per team as a complete four-season solution. Do not download the date sets merely to produce a known-incomplete training matrix, and do not drop Army/Columbia or relabel conference totals. Elo remains the usable model.

**Current product decision:** Aaron accepts small documented gaps and explicitly conference-inclusive pre-NCAA stats. The earlier-window planning proposal is superseded by an actual OBP/ERA experiment using usable reports, supported seasons and Elo fallback. The strict date/phase findings above remain valid for exact full-season reconstruction; they no longer block practical model testing. Follow the [practical experiment contract](../historical/SPEC.md#practical-team-component-experiment--current-priority), including scope disclosure and sensitivity checks.
[DATA.md](DATA.md#ncaa-dated-team-report-sample) owns evidence checkpoints and reproduction. D1 remains reference-only under its recorded automation prohibition; no paid source or provider contact is involved.

## Warren Nolan sample

Its [2024 stats menu](https://www.warrennolan.com/baseball/2024/stats) links to public runs, hits, hits allowed and errors tables. The [hits table](https://www.warrennolan.com/baseball/2024/stats-off-hits-per-game) and [hits-allowed table](https://www.warrennolan.com/baseball/2024/stats-def-hits-per-game) were readable and state D1-only scope. These season tables have not been established as pre-cutoff snapshots; no counts were imported. Reuse the audited dated results for reconciliation and Elo. Do not substitute final RPI, SOS or vendor Elo for the project’s cutoff-safe strength.

## Verified free-source evidence

Inspected the public `sportsdataverse/baseballr-data` repository at commit **e2800f16906104b771210c1aba4eeb975baad202**, using GitHub metadata and source files, not game data. These immutable references allow rechecking the decision without retaining new raw downloads:

- [Team-stat manifest](https://github.com/sportsdataverse/baseballr-data/blob/e2800f16906104b771210c1aba4eeb975baad202/ncaa/team_stats/manifest.csv), Git blob `6ab6378f00d58107299cd224ce45b267095cf470`.
- [Dataset builder](https://github.com/sportsdataverse/baseballr-data/blob/e2800f16906104b771210c1aba4eeb975baad202/python/ncaa_baseball_data_build/builders.py), Git blob `3adf8dcb970e01768a4b29ca6add0b113781b802`.
- [License](https://github.com/sportsdataverse/baseballr-data/blob/e2800f16906104b771210c1aba4eeb975baad202/LICENSE.md) and [runbook](https://github.com/sportsdataverse/baseballr-data/blob/e2800f16906104b771210c1aba4eeb975baad202/RUNBOOK.md).

| Season | Published team-stat row count | Qualification |
|---|---:|---|
| 2021 | 0 | No team-stat table rows |
| 2022 | 0 | No team-stat table rows |
| 2023 | 0 | No team-stat table rows |
| 2024 | 5,614,266 | Advertised manifest count only; unique games, completeness and denominators not verified |

The builder explicitly says its legacy 2012–2023 payloads have empty team/player/linescore/situational families. Historical play-by-play and schedule existence therefore does not establish a ready team-component table. Reconstructing and qualifying every count from play text would be separate substantial work, not a simple bulk import. The builder also notes missing legacy division information; counts must not be presented as verified D1 game coverage.

The MIT file covers software and associated documentation; it is not blanket certification of upstream data rights. The public loader/release path is a practical free access mechanism, but coverage already fails before an ingestion decision. No upstream NCAA collector, proxy workflow or live school request was run. The repository's backfill instructions are not project instructions.

The separate [ncaa_bbStats provenance page](https://collegebaseballstatspackage.readthedocs.io/en/latest/data_provenance.html) advertises season-level NCAA team tables. It does not establish dated game components or both cutoff modes. Its default player cache also discloses FanGraphs-export provenance; no such data were acquired. Final totals cannot become pre-tournament inputs merely because download access is free.

## Other source findings retained

| Route | Evidence / limit | Current decision |
|---|---|---|
| College Splits / FanGraphs | [College Splits](https://collegesplits.com/about) advertises NCAA event data; [FanGraphs](https://blogs.fangraphs.com/weve-got-college-data/) names it as supplier and advertises history from 2021/member exports. Dated sample, complete fields and rights unverified. | Paid path removed; no inquiry queued. |
| Highlightly | [Docs](https://highlightly.net/mlb-api/documentation/) describe team match stats as MLB, with possible missing fields; historical NCAA support unverified. [Terms](https://highlightly.net/terms/) constrain gaming use. | Not selected; no signup or paid plan. |
| NCAA, ESPN, schools, D1Baseball | [Existing findings](Statistics_Discovery_and_Triage.md#sourceaccess-findings): access gaps, uneven histories, school-specific work and D1 automation prohibition. | Nolan/NCAA focus above supersedes the earlier pause; no school sweep. |

The mirror findings above were documentation/metadata checks only; the direct NCAA sample is separately retained. Search/provenance pages exposed incidental current-year metadata; no 2026 games or features were ingested or evaluated.

## Input checks for the practical experiment

The [practical experiment contract](../historical/SPEC.md#practical-team-component-experiment--current-priority) supersedes the earlier four-season/full-field exact-reconciliation prerequisite. Preserve source bytes, dates, identities, denominators, missing values and provenance. Qualify only fields required by the selected candidate; no need to acquire every proposed statistic first. Missing PA/BF still prevents dependent rates; OBP/ERA use their own retained denominators.

Use the existing pre-NCAA cutoffs and availability assumption. Dated, older reports and all-opponent counts can be tested with scope/gaps disclosed; final/post-cutoff totals cannot become historical predictors. Use common comparison games and explicit Elo fallback instead of silently dropping bracket teams. Quantify flagged discrepancies and their sensitivity rather than stopping for minor imperfections.

Net-run remains closed. Prior 2024 exposure stays explicit, 2025 development, 2026 excluded, individual pitchers deferred. The app remains Elo pending measured improvement and promotion checks; no new fitting occurred in this documentation update.
