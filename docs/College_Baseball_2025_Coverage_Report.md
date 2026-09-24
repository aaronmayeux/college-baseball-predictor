# College baseball predictor — 2025 results audit

Historical analysis checkpoint. Repository setup is recorded in the current project brief and SESSION_LOG.md.

Prepared September 20, 2026 for Aaron Mayeux.

## Decision

The full **provider-listed 2025 results inventory is collected and internally reconciled**: 307 teams and 8,418 completed D1-versus-D1 games. Use this as the initial results foundation for an Elo baseline, subject to the remaining historical-season and cutoff checks below. No model, predictive accuracy claim, interface, scheduled job or deployment was created.

This establishes completeness against Warren Nolan's published 2025 roster and records, not independent certification of every NCAA game. Both teams' schedule pages are the same provider and may share the same upstream record.

## Fresh automated evidence

| Check | Result |
|---|---:|
| Team schedules parsed | 307 / 307 |
| Team win/loss/tie records matching the historical RPI table | 307 / 307 |
| Unique completed D1 games | 8,418 |
| Games with two consistent opposite-team observations | 8,418 / 8,418 |
| Score, date, team-ID or phase disagreements between those observations | 0 |
| Tied games retained | 2 |
| Explicit non-D1 completed observations excluded | 86 |
| Same-day, same-opponent groups retained as separate source game IDs | 641 |

Published totals sum to 8,416 wins, 8,416 losses and 4 team-level ties, implying 8,418 unique games. All downloaded raw payloads with hashes pass byte-level verification. A cached rerun of collection and normalization reproduced byte-identical games, observations and team-coverage JSON, without duplicate records. Canceled/postponed and other unscored rows stay in the observation ledger but are excluded from completed games. This audit does not prove every same-day pair's chronological order or independently verify every possible duplicate shared by both pages.

Primary source: [Warren Nolan 2025 RPI table](https://www.warrennolan.com/baseball/2025/rpi-live). Per-team URLs, retrieval timestamps and raw hashes are retained in the database and JSON records. Final RPI/records are reconciliation targets, **not model inputs**.

## Independent school checks

- [Columbia official 2025 schedule](https://gocolumbialions.com/sports/baseball/schedule/2025): all 49 scored games match by opponent, date and score, with explicit name aliases.
- [Oregon State official 2025 schedule](https://osubeavers.com/sports/baseball/schedule/2025): all 65 scored games match by opponent, date and score, including the tie.
- [LSU official 2025 schedule](https://lsusports.net/sports/bsb/schedule/season/2025/): the displayed 53–15 record matches. Full per-game official reconciliation was not performed for LSU this turn.
- [Southern official 2025 schedule](https://gojagsports.com/sports/baseball/schedule/2025): the displayed 24–27 all-opponent record matches the 51 scored provider rows. One is non-D1 Dillard; exclude that win for the D1-only comparison. Full official per-game reconciliation was not performed this turn.

These four programs span different coverage situations but are not a random national sample. Official and aggregator sites may themselves share upstream data.

**Correction to earlier audit:** Oregon State's previous count of 64 only counted wins/losses. The correct scored-game inventory has 65 including a tie. The previous parser was incomplete on ties; the current parser and official check correct it.

## Separate regular season and tournament results

| Source-derived phase | Unique games |
|---|---:|
| regular season | 7,963 |
| conference tournament | 319 |
| regional | 102 |
| super regional | 20 |
| omaha | 12 |
| championship series | 2 |

Phase labels use explicit schedule event headings for conference tournaments, regionals, supers, Omaha and championship series. Ordinary unlabeled games are inferred regular season; this is a classification method, not independent national phase verification. Opposite-team phase labels agree throughout.

Columbia–Holy Cross played two games on May 24. The official Columbia structured schedule marks both type R, conference false, tournament null. Those two late games are explicitly classified regular season and the evidence is recorded. A universal cutoff at the start of conference-tournament week would incorrectly discard them.

The [2024–25 NCAA prechampionship manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2024-25D1MBA_PreChampsManual.pdf) schedules selection for May 26 and regionals for May 30–June 2. It confirms regional double elimination, super-regional best-of-three and Omaha bracket/series structure. Read the applicable year's manual before building simulations; this report does not implement them.

**Proposed forecast policy:** freeze regular-season strength separately from conference-tournament-inclusive strength. Choose and record an exact forecast timestamp before model evaluation. No cutoff has been silently selected in the database. End-season scores are reconstructed historical outcomes; their current corrections are not guaranteed to match the originally published version.

## Source assessment: tested versus advertised

| Source | Evidence status | Role |
|---|---|---|
| Warren Nolan | Fresh: national 2025 roster, all schedules, final records and reciprocal games parsed | Selected pilot backbone; long-term refresh/rights and older seasons unverified |
| Official school schedules | Fresh: four pages downloaded; two full game-by-game comparisons, two aggregate record comparisons | Reconciliation and targeted fallback |
| ESPN | Earlier chat observations only; original raw evidence lost | Optional IDs/player boxes; prior sparse requests rule out assuming complete team schedules |
| NCAA statistics | Earlier chat observations: landing page readable, dated snapshot challenged | Historical statistics snapshots remain unverified |
| Boyd's World / ISR | Earlier probes failed | Optional benchmark, not a baseline requirement |
| FanGraphs | Earlier visible season controls and members-only export; no export tested | Optional advanced-stat comparison |
| D1Baseball | Fresh: direct public HTML requests succeeded; browser fetches returned 403 | Potential licensed source; not selected for automated collection |

D1Baseball's [published terms](https://d1baseball.com/terms-of-service/) expressly prohibit automated monitoring/data mining/copying. A normal subscription is not sufficient evidence of a permitted automated feed. No documented supported feed, historical export completeness, pre-tournament snapshots or price for our use was verified. No subscription was bought and no one was contacted. Their [contact page](https://d1baseball.com/contact/) is the route for a future licensing inquiry about full D1 game history, daily team/player logs, pitch counts, permitted storage/use and sample files.

The first lost audit attempted 53 selected ESPN summaries across 2015, 2019, 2021, 2023–2026: 52 returned results, 34 had some player rows, 33 had both teams' pitcher rows, 32 had positive counts for every listed pitcher, and 33 had play records. These are **inherited small-sample observations**, not current independently reproduced evidence or coverage estimates. See SESSION_RECORD.md. The current inventory does not add player boxes or play-by-play.

## Minimum baseline contract

Keep season, stable provisional team IDs, played date, result/status, scores, phase and provenance. Retain ties and non-D1 exclusions explicitly. Date-only records do not establish exact completion time or doubleheader order. For a results-only Elo baseline, same-day updates should use a documented batch rule unless game ordering is verified; exclude ties from binary win/loss evaluation or use an explicit tie update rule.

Venue text and provider home/away designations are retained in source observations, but actual home-park advantage and batting last are not inferred to be interchangeable. Actual home-team IDs remain unknown. Begin a neutral team-strength comparator; add a home term only after venue verification.

The pilot uses Python standard-library collection/parsing and SQLite, with immutable raw snapshot hashes. No special stats, ISR, paywall, hand-copied routine numbers or player feed is required for this baseline. Team slugs are provisional provider IDs; a cross-provider identity map and renamed/transitional-school handling remain necessary for multi-season use.

## Remaining limitations and next concrete work

1. Independently reconcile the national team universe and broaden school checks across conferences. The NCAA preseason manual lists UTRGV under WAC while this provider's 2025 roster places it in Southland, illustrating why preseason lists cannot silently override season-specific affiliation data. No affiliation correction was inferred from memory.
2. Review phase classifications and choose exact forecast cutoffs, preserving regular-only and conference-inclusive modes.
3. Collect and reconcile earlier seasons, starting with 2021–2024, before fitting a chronological baseline. Do not report 2025 as an untouched test year: prior design work used its outcomes.
4. Test sustained collection/retry behavior and correction handling before scheduling refresh. Successful one-time downloads establish access, not a provider service guarantee or redistribution license.
5. Re-run stratified player/box/play-by-play coverage only when pursuing power, HAVOC and pitching features. Missing data must not become zeros.

**Session outcome:** the 2025 results portion of the coverage milestone is complete against the selected provider, with a reproducible inventory and explicitly limited independent checks. Historical player coverage remains inherited, and broader historical/independent verification is pending. Earlier-season collection, cutoff validation and Elo are covered in the historical and timing reports; the project brief owns the current build order.

## Conference reconciliation

The figures below use the provider's season-specific conference labels. Every team is checked against its published D1 win/loss/tie record; conference totals count team observations, so a game between two conference members appears twice in that conference's observation ledger.

| Conference | Teams | Records matching |
|---|---:|---:|
| ACC | 16 | 16 |
| ASUN | 12 | 12 |
| America East | 7 | 7 |
| American Athletic | 10 | 10 |
| Atlantic 10 | 12 | 12 |
| Big 12 | 14 | 14 |
| Big East | 8 | 8 |
| Big South | 9 | 9 |
| Big Ten | 17 | 17 |
| Big West | 11 | 11 |
| Coastal Athletic | 12 | 12 |
| Conference USA | 10 | 10 |
| Horizon League | 6 | 6 |
| Independent | 1 | 1 |
| Ivy League | 8 | 8 |
| MAAC | 13 | 13 |
| Mid-American | 11 | 11 |
| Missouri Valley | 10 | 10 |
| Mountain West | 8 | 8 |
| Northeast | 11 | 11 |
| Ohio Valley | 10 | 10 |
| Patriot League | 6 | 6 |
| SEC | 16 | 16 |
| SWAC | 12 | 12 |
| Southern | 8 | 8 |
| Southland | 11 | 11 |
| Sun Belt | 14 | 14 |
| The Summit League | 6 | 6 |
| West Coast | 9 | 9 |
| Western Athletic | 9 | 9 |

## Reproducibility and files

The evidence bundle contains collector/parser scripts, original response bytes and SHA-256 metadata, source observations, unique games, exclusions, team/conference checks, the official-school comparisons, validation results and a portable SQLite database. The brief receives a dated session note. The earlier SESSION_RECORD.md is an explicitly inherited checkpoint, not a substitute for raw evidence.
