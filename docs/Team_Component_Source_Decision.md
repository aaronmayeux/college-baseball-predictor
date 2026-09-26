# Historical team-component source decision

Reviewed September 26, 2026. Source qualification only; no new model experiment.

## Decision

**Keep Elo and use only retained or free data. No component source qualifies for the planned 2021–2024 test yet.** Aaron's zero-budget instruction supersedes the prospective College Splits inquiry; budget authority is in [AGENTS.md](../AGENTS.md). No provider inquiry, purchase, subscription or chargeable trial is queued.

A bounded free-source check found SportsDataverse's published NCAA archive, but its pinned team-stat manifest has zero rows for 2021–2023. Do not acquire its 2024 data alone for a four-season experiment or reopen piecemeal school collection. Stop this search after the evidence below. Reopen component acquisition only when a free dated dataset demonstrably fills the required years; otherwise retain Elo. This is not a claim that no suitable free dataset can ever exist.

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
| NCAA, ESPN, schools, D1Baseball | [Existing findings](Statistics_Discovery_and_Triage.md#sourceaccess-findings): access gaps, uneven histories, school-specific work and D1 automation prohibition. | No new probes or school sweep. |

Source facts above were read from public documentation/metadata. No API game payload, historical stat table or new evidence archive was acquired. Search/provenance pages exposed incidental current-year metadata; no 2026 games or features were ingested or evaluated.

## Gate for any later free dataset

Require a 2021–2024 coverage manifest, stable team/game/opponent identities, dates/completion annotations, phase labels, provenance, explicit missing values and usable terms. Qualify team batting AB/H/2B/3B/HR/BB/HBP/SO/SF/SH/PA and team pitching outs/H/R/ER/BB/HBP/SO/HR/BF as needed by the exact selected feature. Missing PA/BF or interference components block dependent rates; do not invent zeros or average game rates. Team ER need not equal summed pitcher ER. Individual pitcher histories are unnecessary for this gate.

Reconcile eligible inventories and available count evidence. Apply unchanged [cutoffs](../historical/cutoffs.json), v2 completion corrections, two-day availability assumption and separate regular-only/conference-inclusive modes. Final totals are audit-only. Require complete selected-field feature coverage and common samples before a full-field experiment; no silent loss of teams.

The [qualification](Model_Input_Qualification.md#fitting-and-promotion-boundaries) and [SPEC](../historical/SPEC.md) own evaluation. Net-run remains closed; no new fitting, predictions or metrics occurred. Prior 2024 validation exposure must remain explicit, 2025 stays development, 2026 excluded, and individual pitchers remain deferred. The app continues with retained Elo while richer components are blocked; no paid approval is needed to keep using it.
