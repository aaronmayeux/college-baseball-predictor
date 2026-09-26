# Historical team-component source decision

Reviewed September 26, 2026. Source qualification only; no new model experiment.

## Decision

**Use Aaron’s selected sources: Warren Nolan for the retained results backbone, NCAA for dated team batting/pitching reports, and D1Baseball for permitted reference use.** This is a personal, noncommercial, zero-budget project; [AGENTS.md](../AGENTS.md) owns those constraints. Elo stays; the net-run candidate stays closed and individual pitchers remain deferred.

A failed four-season mirror does not block a useful single-season access/schema check. NCAA’s public archive now provides a successful 2024 national sample. No feature or forecast mode is qualified by this discovery alone. The proposed SportsDataverse 2024 audit is superseded by this direct NCAA route; no paid inquiry or school sweep is queued.

## Direct NCAA sample: verified access and counts

The [official baseball statistics page](https://www.ncaa.org/championships/statistics-and-records/baseball/) links to the [historical archive](https://web1.ncaa.org/stats/StatsSrv/rankings?doWhat=archive&sportCode=MBA). Its public form accepts `sportCode=MBA`, `academicYear=2024`, `doWhat=display`. The returned menu offers Division I reporting dates, team categories and HTML/ASCII/PDF/CSV exports.

Two CSV POST responses succeeded from `https://web1.ncaa.org/stats/StatsSrv/rankings`, using `doWhat=showrankings`, `div=1`, `rptWeeks=90`, `rptType=CSV`, and team `statSeq` 589 (OBP) / 211 (ERA). The other three statistic selectors remain -1, as in the form. Both response headings confirm **through games May 26, 2024**; neither is a final-season report.

`scripts/audit_ncaa_archive.py` verifies retained hashes, request fields, response season/date/division/statistic, CSV schema, duplicate teams, counts, records and displayed rates. It handles the archive’s reclassifying section and trailing analytics HTML without treating either as missing data. The result:

- **305 source team names in each table**, including ten reclassifying rows; all names and game records agree between tables. These are source rows, not 305 certified eligible tournament teams.
- OBP includes AB, H, BB, HBP, SF and SH; all 305 displayed OBPs match the proper count formula at three decimals.
- ERA includes IP, R and team ER; all 305 displayed ERAs match 27×ER/outs at two decimals. Baseball `.1/.2` innings convert to one/two outs, not decimal fractions.
- The through-date passes the existing assumed two-day lag at the May 29 cutoff. Actual historical publication time, individual game inclusion and stable internal identities remain unverified.

The data likely include conference-tournament games and may include non-D1 opponents. Do not equate NCAA records with the D1-only Nolan inventory without reconciliation. Neither forecast mode is qualified yet. A regular-only feature needs eligible game components or proven team-specific snapshots/adjustments; one shared May 26 total cannot strip conference tournaments. Missing hitting SO/PA or pitching BF/K/BB means these two tables alone do not support contact or pitching strikeout-rate features.

Next: map the 2024 NCAA names to the retained 64-team field and reconcile games/cutoff/phase scope against Nolan. Then check the same public report route for 2021–2023; verify each year’s menu rather than reuse report IDs. Keep access/schema qualification separate from fitting. Preserve the evaluation contract and do not relabel conference-inclusive totals as regular-only.

[DATA.md](DATA.md#ncaa-dated-team-report-sample) owns the evidence checkpoint and offline reproduction. No automated D1 statistics collection occurred. A fresh terms-page web lookup failed; the existing documented prohibition remains, rather than assuming personal use grants automated access.

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

## Gate for any later free dataset

Require a 2021–2024 coverage manifest, stable team/game/opponent identities, dates/completion annotations, phase labels, provenance, explicit missing values and usable terms. Qualify team batting AB/H/2B/3B/HR/BB/HBP/SO/SF/SH/PA and team pitching outs/H/R/ER/BB/HBP/SO/HR/BF as needed by the exact selected feature. Missing PA/BF or interference components block dependent rates; do not invent zeros or average game rates. Team ER need not equal summed pitcher ER. Individual pitcher histories are unnecessary for this gate.

Reconcile eligible inventories and available count evidence. Apply unchanged [cutoffs](../historical/cutoffs.json), v2 completion corrections, two-day availability assumption and separate regular-only/conference-inclusive modes. Final totals are audit-only. Require complete selected-field feature coverage and common samples before a full-field experiment; no silent loss of teams.

The [qualification](Model_Input_Qualification.md#fitting-and-promotion-boundaries) and [SPEC](../historical/SPEC.md) own evaluation. Net-run remains closed; no new fitting, predictions or metrics occurred. Prior 2024 validation exposure must remain explicit, 2025 stays development, 2026 excluded, and individual pitchers remain deferred. The app continues with retained Elo while richer components are blocked; no paid approval is needed to keep using it.
