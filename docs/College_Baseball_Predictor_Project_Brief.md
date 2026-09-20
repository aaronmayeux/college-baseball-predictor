# College Baseball Predictor — Project Brief

Prepared September 20, 2026. Repository edition.

## Purpose and current status

Build a college baseball tournament predictor using automatically collected regular-season data. Produce calibrated game probabilities, advancement probabilities, and a predicted bracket from regionals through the national championship. Explain the main reasons behind predictions.

The historical results pilot now covers **2021–2025: 40,615 completed D1 games, 1,520 provider team-season records and 310 stable internal team identities**. The 2021–2024 extension adds 32,197 games. All season records reconcile after evidence-backed 2023 corrections; three games are official-school supplements rather than independent reciprocal provider records. Two 2023 date-conflict games remain in the inventory but are excluded from modeling. Provider-defined completeness is not independent national certification.

A fixed chronological neutral Elo baseline has been implemented and evaluated. Frozen regular-only ratings selected 68.9% of NCAA game winners across 411 games in 2022–2024; 2025 development accuracy is 63.2% across 136 games. Probability scores and all comparison modes are in College_Baseball_Historical_Coverage_and_Elo_Report.md. These are retrospective matchup evaluations, not bracket accuracy or an untouched holdout.

Exact pre-NCAA cutoffs are now recorded: Wednesday 12:00 UTC before regionals, with a two-calendar-day assumed availability delay for date-only results. Regular-only and conference-inclusive inputs are separate. Point-in-time publication/completion is not certified. 2026 cannot be called untouched because prior ESPN probes and a wrong-season official response exposed outcomes; it was not used for model fitting or evaluation.

The current reproducible handoff is College_Baseball_Historical_Baseline_Bundle.zip, containing Python standard-library scripts, raw evidence, provenance, corrections, cutoff eligibility, tests, predictions and a combined SQLite database. The dedicated public repository is https://github.com/aaronmayeux/college-baseball-predictor. No tournament simulator, interface, hosting, scheduled refresh or paid feed exists. Next: resolve timing exceptions, broaden date/phase checks, add a cutoff-safe seed benchmark, and reserve a future holdout prospectively.

## Project instructions — copy this section into project instructions

Build a college baseball bracket predictor. Explain choices in concise, plain English, define technical terms when needed, preserve settled decisions, and keep a durable record of progress.

Read College_Baseball_Predictor_Project_Brief.md and the current repository specification before starting work. Review relevant source files when making implementation changes. Update the brief/specification when decisions change. At the end of a substantial work session, record what changed, what was verified, remaining limitations, and the next concrete step.

The goal is automated data collection and credible predictions across regionals, super regionals, Omaha bracket play, and the championship series. Original spreadsheets are reference material, not a specification that must be preserved. Keep originals untouched. No routine copying and pasting of stats should be required.

Research current sources and tournament rules rather than relying solely on memory. Cite sources for factual research claims. Distinguish verified findings, inherited audit findings, assumptions, proposed features, and hypotheses. Never claim a novel idea is unprecedented or predictive until evidence supports that claim.

Start with source coverage, a reproducible data pipeline, and a simple prediction baseline. Add complexity only when it addresses a measured limitation or improves evaluation on unseen seasons. Do not start with a polished interface. Proposed architecture is Python for data and modeling, followed by a mobile-friendly interface and spreadsheet exports; the exact tools and hosting are not yet settled.

Prevent future information from entering historical predictions. Store source, retrieval time, game date, and forecast cutoff. Separate pre-tournament forecasts from forecasts updated during the tournament. Do not substitute final-season statistics for regular-season snapshots.

Use a shared game-probability model with separate tournament-format simulators. Treat power, HR dependence, contact, and HAVOC as separate attributes that can coexist. Investigate home-field advantage, park effects, opponent matchups, and pitcher availability. Learn adjustments from data rather than imposing arbitrary style bonuses.

Work in manageable milestones. Use judgment for reversible implementation choices; explain material tradeoffs without repeatedly reopening settled decisions. Keep code in a dedicated GitHub repository once one is established. Do not confuse this project with Aaron's separate bridge-building game repository.

## Reference files

- NEW_2025_12232025xSTATIC.xlsx — original static workbook.
- NEW_2025_12232025xDYNAMIC.xlsb — original dynamic workbook.
- CWS_Predictor_Research_and_Design.pdf — detailed research and design report from the originating conversation.
- College_Baseball_2025_Coverage_Report.md — current national results audit and limitations.
- College_Baseball_2025_Audit_Bundle.zip — reproducible scripts, raw responses, provenance, normalized data and SQLite database.
- College_Baseball_Historical_Coverage_and_Elo_Report.md — current multi-season results, source corrections, cutoff policy and fixed baseline evaluation.
- College_Baseball_Historical_Baseline_Bundle.zip — current reproducible code, raw evidence, crosswalk, predictions, tests and combined SQLite inventory.
- SPEC.md — current implementation/evaluation contract inside the historical bundle.
- SESSION_RECORD.md — inherited sample-audit findings whose original raw files were lost; retained inside the recovered 2025 directory.
- This brief — the current project handoff and decision record; use this standalone revision over the older copy inside the audit bundle.

Attach the actual reference files to the project. Their filenames here do not provide access to their contents in a new conversation.

## Decisions to carry forward

1. Automate ingestion; retain raw source data and normalized records so results are reproducible.
2. Use probabilities, not just winner picks. Evaluate both individual games and advancement forecasts.
3. Model each tournament's actual rules. Regionals use four-team double elimination; super regionals use best-of-three series; Omaha has two four-team double-elimination groups followed by a best-of-three final. Verify the applicable year's rules before implementation.
4. Use common underlying team and player estimates across phases. Format, venue, rest, opponent, and available pitching alter the simulation. Separate independently trained models for each phase are not automatically necessary.
5. Benchmark a simple model before adding proposed differentiators.
6. Treat novelty as a research objective, not a reason to keep a feature that fails validation.

## Findings from the original spreadsheet audit

These findings were established in the originating conversation. Reinspect the original files if implementing a repair or needing exact cell-level evidence.

| Area | Finding | Implication |
|---|---|---|
| ISR | Raw_Stats column E contains ISR. Static composite assigns it 35% weight. | Retain as a candidate baseline/input, subject to historical availability. |
| Source attribution | No documented source URLs were found. Aaron recalls Warren Nolan. ISR originates with Boyd Nation/Boyd's World. Advanced fields resemble FanGraphs offerings but provenance is unconfirmed. | Do not assert every input came from a specific provider. |
| Data cutoff | Some records include postseason results; LSU's row reflects 68 games and a 53–15 record. | Original data cannot establish honest pre-tournament accuracy. |
| Static weights | 45% DIRTY_DER, 35% ISR, 10% wRC+, 10% inverse SIERA. | These are existing choices, not validated optimal weights. |
| Dynamic score | Weight/feature alignment differs; original binary cached composite results contain errors. | Rebuild explicitly named features rather than reproducing positional formulas. |
| DIRTY_DER | Uses offensive BABIP where opponent BABIP was intended; error penalty in formula is 10 times the comment's stated penalty. | Do not reuse this defensive metric unchanged. |
| GUILLEN | HR × 1.6 / runs scored. | Estimates HR scoring share using a fixed runs-per-homer assumption. |
| HAVOC | (2 × SB + BB + HBP) / K. | Ignores caught stealing and mixes rates/opportunities; low K can dominate. |
| Style labels | Static sheet classifies 54 of 64 teams as GLASS CANNON; some thresholds/references are inconsistent. | Labels do not currently discriminate well. |
| Tournament logic | Supers/finals are represented as single games; some runner-up/random rerun logic is problematic. | Build and verify format simulators independently. |
| Data quality | Name punctuation and game-total discrepancies exist. | Use stable team IDs and reconciliation checks. |

## Research hypotheses

### Home-field advantage

Separate playing at one's actual home park, being a selected host, batting last, travel, and crowd effects. Hosts are generally strong teams; raw host advancement rates do not isolate a home-field effect. Control for team and opponent quality. Verify venue independently because an ESPN sample incorrectly marked an Omaha game as non-neutral. Do not turn a reported host advancement percentage into a per-game win probability.

### Power and glass cannon

Test whether HR dependence, high strikeout rate, and limited alternative offense make a team more sensitive to a change in park or opponent. Power itself is not a weakness. A powerful team can also have strong contact, walks, and baserunning.

Prefer actual runs scored on HR plays divided by total runs when play-by-play is complete. Count all runners scoring on the homer, not just the batter. Keep the workbook's fixed 1.6 estimate clearly labeled if used as a fallback. Also measure HR per plate appearance, strikeout rate, walks, and non-HR production; dependence alone does not measure overall offensive quality.

Estimate offense in the destination park relative to its regular-season environment, controlling for opposition. For Omaha, consider dimensions, wind direction relative to the field, temperature, and batted-ball tendencies when data permits. Public historical exit velocity and spray data are not assumed available. A bigger outfield may also allow gap hits and protect a team's own pitchers; apply venue effects to both sides.

### HAVOC

Measure components separately: reaching base, stealing efficiently, taking extra bases, and capitalizing on mistakes. Include caught stealing and opportunity denominators. Walk/HBP rates and steal attempts/success are feasible starting points; extra-base advancement and wild-pitch/passed-ball opportunities need coverage assessment.

Test interactions with opposing pitcher control, strikeout ability, catcher throwing, holding runners, and defense when available. A larger outfield does not automatically help steal attempts. Power and HAVOC should coexist as continuous scores rather than mutually exclusive categories. Test incremental value beyond existing offensive metrics to avoid counting walks/contact twice.

### Pitching resources and bracket path

Explore expected starters, quality of remaining pitchers, recent workload, and rest. Update availability as simulated games consume pitching. Sample uncertain starter choices when announcements are unavailable. Do not invent a precise universal recovery rule.

Potential differentiator: a team can lose while forcing its opponent to use valuable bullpen arms, benefiting a third team later in the bracket. Test whether this effect adds predictive value. This is a proposed feature, not a claim of unprecedented research.

## Data-source strategy

| Candidate | Intended role | Unresolved issue |
|---|---|---|
| NCAA statistics and official school schedules/box scores | Independent checks; 114 games matched across two official school schedules | Nationwide coverage, access restrictions, parsing differences and snapshot timing remain unresolved |
| ESPN scoreboards and game summaries | Game IDs, results, box scores, play-by-play and pitch counts when available | Undocumented interfaces and uneven historical coverage; validate venue flags |
| Boyd's World | ISR and historical ratings research | Accessible archives, cutoff dates, and permitted automated use |
| Warren Nolan plus targeted official-school corrections | 2021–2025 results pilot: 40,615 games; all 1,520 team-season records reconcile after documented corrections | Independent national completeness, precise historical timing, broader phase verification, ongoing access/usage terms; original workbook attribution remains uncertain |
| D1Baseball | Potential separately licensed source; direct public HTML retrieval tested successfully | Published terms prohibit automated monitoring/mining/copying; supported feed, license, historical completeness and price are unverified |
| FanGraphs college leaderboards | Advanced-stat comparisons and possible inputs | Export access, historical coverage, definitions, and usage terms |
| Commercial provider if needed | More consistent coverage | Verify sample coverage and terms before considering cost |

The earlier research successfully inspected individual ESPN examples with pitch counts and play-by-play, but other sampled games lacked box scores. This was a feasibility probe, not a completed coverage study. Those original raw files were lost; these player-data findings are inherited, not freshly reproduced by the 2025 results audit. The baseballr package documents NCAA/ESPN access functions but is an access tool, not an independent source of truth. MLB-derived metrics such as SIERA require validation before assuming equivalent college performance.

Every normalized record should retain provider, provider ID, stable internal team/player ID where available, season, game timestamp, venue, retrieval timestamp, and raw-record reference. Handle missing data explicitly. Cache responses, avoid duplicate games, validate baseball innings notation, and make reruns safe. Scheduled refresh comes after a reliable manual command; no scheduler has been configured.

## Build milestones and acceptance criteria

| Milestone | Deliverable | Done when |
|---|---|---|
| 1. Coverage audit | Representative season/date/team coverage table and selected sources | Results, box scores, player data, and play-by-play availability are quantified separately; fallbacks and access limits documented |
| 2. Data pipeline | Repeatable import command, raw cache, normalized database, cutoff-aware features | A representative regular-season dataset loads without manual stat copying; reruns do not duplicate records; key totals reconcile |
| 3. Baseline | Simple game model, such as regularized logistic regression or Elo | Evaluated chronologically against simple benchmarks; probabilities and limitations reported |
| 4. Tournament engine | Regionals, supers, Omaha groups, final series | Reset games, series stopping rules, advancement, and shared simulation state behave correctly; probabilities reconcile |
| 5. Added features | Measured home/park effects, power/HAVOC, then pitching availability | Each addition is compared with the baseline on unseen seasons and retained only with a justified benefit |
| 6. Interface and refresh | Mobile-friendly bracket, explanations, exports, refresh status | Real predictions trace to model/data versions and timestamps; missing data and uncertainty are visible |

Python standard-library scripts and SQLite implement the reversible 2021–2025 research pilot. Results coverage, reconstructed cutoff eligibility and a fixed Elo comparator are implemented; broader independent coverage, exact historical completion/publication times, player data, seed benchmarking and advancement evaluation remain incomplete. Milestones 1–3 are therefore partial at the wider project level. Milestones 4–6 have not started. The dedicated public GitHub repository is established; no deployment destination is selected.

## Evaluation rules

- Split by season in chronological order. Fit preprocessing and tune features using only training data. Keep a final period untouched until evaluation.
- Use the recorded Wednesday 12:00 UTC pre-NCAA cutoffs and two-calendar-day assumed availability rule from cutoffs.json. Regular-only is primary; conference-inclusive is separately labeled. Daily in-tournament updates are a separate mode. These are retrospective date-based reconstructions, not point-in-time-certified snapshots.
- Use log loss and Brier score to assess probability quality, plus calibration: events assigned roughly 60% should happen roughly 60% of the time. Report winner accuracy as a secondary measure.
- Compare against simple team-strength and seed baselines. Compare only on common evaluation samples when a feature reduces coverage.
- Evaluate game and advancement probabilities; uncertainty intervals should respect clustering by season/tournament. Omaha's small annual sample limits conclusions.
- Measure features one at a time and in meaningful combinations. Do not optimize thresholds against the same bracket used to advertise performance.
- Represent uncertainty about team strength and availability separately from game randomness. Carry a consistent team-strength draw through a simulated tournament when using that approach.
- A synthetic fair four-team regional should give each team a 25% initial title chance. A fixed independent 60% game favorite wins a best-of-three series 64.8% of the time. Use such checks alongside actual format edge cases.

## Research starting points

These links were used in the prior research. Recheck current access, coverage, and applicable-year rules before relying on them in production.

- [SABR: The PING Ratings](https://sabr.org/journal/article/the-ping-ratings-a-model-for-rating-ncaa-baseball-teams/) — existing opponent-adjusted college ratings research; distinguishes ISR and Warren Nolan's ratings.
- [D1Baseball Terms of Service](https://d1baseball.com/terms-of-service/) — automation restrictions checked during the 2025 audit; any licensed feed requires separate verification.
- [Warren Nolan](https://www.warrennolan.com/) and [Boyd's World](http://boydsworld.com/) — candidate ratings sources.
- [FanGraphs college leaderboards](https://www.fangraphs.com/leaders/college) and [SIERA definition](https://library.fangraphs.com/pitching/siera/).
- [Driveline: introduction to cWAR](https://drivelinebaseball.com/blogs/blog/an-introduction-to-cwar) — prior college-specific park/schedule-adjusted work.
- [Official Charles Schwab Field information](https://charlesschwabfieldomaha.com/plan-your-visit/stadium-information/) — venue dimensions.
- [2025–26 NCAA pre-championship manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2025-26D1MBA_PreChampsManual.pdf).
- [Study of batting last in NCAA tournament baseball](https://pubmed.ncbi.nlm.nih.gov/16195017/) — narrower question than total home-field advantage.
- [baseballr function reference](https://billpetti.github.io/baseballr/reference/index.html).
- [LSU 2025 official schedule](https://lsusports.net/sports/bsb/schedule/season/2025/) — example official historical source.

## Next-session starting point

Read this standalone brief and College_Baseball_Historical_Coverage_and_Elo_Report.md. Restore College_Baseball_Historical_Baseline_Bundle.zip, read its root SPEC.md and README.md, and use root run.py for a cached rebuild. Do not restart the 2025 audit or run its legacy report generator over the new handoff.

Preserve the fixed baseline and all correction evidence. The next data-quality work is resolving the 2023 Kent State–Ohio State and Columbia–Dartmouth date/completion discrepancies, then broadening independent date/phase checks and adding a cutoff-safe seed benchmark. Keep the two timing-conflict games excluded until resolved. Any new corrections must preserve original fields and source provenance.

Keep 2025 labeled development; do not claim 2026 is untouched. Reserve a future season prospectively after locking the evaluation protocol. Do not build an interface. Use this dedicated repository for code and documents; retain data outside Git. This project is separate from the bridge game.

## Open decisions

- Eventual execution/hosting environment. Repository: https://github.com/aaronmayeux/college-baseball-predictor (public).
- Further training-season expansion beyond the implemented 2021–2025 pilot; assess scoring-environment changes before adding complexity.
- A future prospectively reserved holdout; 2026 is not certified untouched. Current exact cutoffs and regular-only/conference-inclusive rules are settled in cutoffs.json.
- Whether a paid source becomes necessary after testing free coverage.
- Bracket scoring system if optimizing a contest entry rather than simply reporting the most likely outcomes.

Current fixed-parameter results use recorded date-based eligibility. Broader exact-time and independent national verification remain limitations; no precise historical publication-time claim is made.


## Historical checkpoint — September 20, 2026: national 2025 results inventory

The status and next-step statements in this checkpoint are superseded by the historical-extension update below; retained as the original decision record.

The latest deliverables are `College_Baseball_2025_Coverage_Report.md` and `College_Baseball_2025_Audit_Bundle.zip`. The bundle contains fresh raw responses with provenance/hashes, Python collector/parser scripts, audit JSON and `College_Baseball_2025.sqlite`. No dedicated GitHub repository, trained model, UI, deployment or scheduled refresh has been established.

### Verified this session

- Discovered and parsed all 307 teams in Warren Nolan's 2025 RPI roster. All 307 parsed D1 win/loss/tie records match the provider's published records.
- Collected 8,418 unique completed D1-versus-D1 games. All have two consistent opposite-team observations; no score/date/team/phase conflicts were found. This is internal reconciliation of one provider, not independent national certification.
- Source-derived stages: 7,963 regular season; 319 conference tournament; 102 regional; 20 super regional; 12 Omaha bracket games; 2 championship-series games.
- Cached collection/normalization rerun reproduced byte-identical games, observations and team-coverage JSON without duplicates.
- Retained two ties. Excluded 86 explicitly non-D1 completed team observations and 489 canceled/postponed observations from the D1 completed-game table. Retained 641 same-day matchup groups without collapsing their source game IDs.
- Independent school-page comparisons match opponent, date and score for all 49 Columbia and all 65 Oregon State games. LSU's official 53–15 and Southern's official 24–27 all-opponent records were checked at aggregate level only.
- Corrected the earlier audit's Oregon State 64-game count: that parser omitted its tie. Current scored-game total is 65.
- May 24 Columbia–Holy Cross games are explicitly regular season based on the official Columbia schedule; do not use the start of conference-tournament week as a blanket regular-season cutoff.
- D1Baseball direct public HTML access succeeded here, unlike earlier browser-fetch 403 responses. Its published Terms of Service prohibit automated monitoring/data mining/copying. Treat it as a potential separately licensed feed; a subscription alone is not sufficient for our automated use. No supported feed, licensed terms, historical completeness or price was verified. No purchase or outbound message was made.

### Decisions and remaining limits

Use the 2025 results inventory as the initial data foundation and Elo as the proposed simple comparator. Python standard-library scripts plus SQLite were chosen as reversible pilot implementation choices. No model has been trained. The default objective remains regular-season-based forecasts, with conference-inclusive forecasts separately labeled.

Exact forecast cutoff is still unselected. Phase labels largely derive from provider headings; unlabeled ordinary games are inferred regular season. Scores retrieved now may include corrections not available historically. Exact completion timestamps, suspended-game timing, doubleheader order, actual home-park advantage and batting-last designation remain unverified. Provider team slugs are provisional IDs pending a multi-source/multi-season crosswalk.

The team universe is provider-defined. Independent national roster/affiliation reconciliation and broader official-school sampling remain open. NCAA preseason manual affiliations differ from the provider in the UTRGV/WAC/Southland placement; preserve source-specific season metadata until independently resolved. Successful retrieval is not a long-term service guarantee or a redistribution license.

The earlier sample audit's raw files were lost in an environment disconnect; its player/box/play-by-play observations are inherited chat findings, not reverified evidence in this bundle. They are preserved in SESSION_RECORD.md. The new national collection contains results, not new nationwide player or play-by-play coverage.

### Next concrete step

Reconcile earlier seasons beginning with 2021–2024 and confirm forecast cutoff/phase rules. Then evaluate a simple chronological Elo baseline using only prior eligible games; retain 2025 as development material because prior design already used its outcomes. Assess 2026 holdout eligibility before evaluating it. Add richer team/pitching features only after a separate coverage study and measured improvement. No interface work yet.


## Session update — September 20, 2026: historical extension and fixed Elo baseline

This update supersedes prior current-status and next-step statements in the dated 2025 session note above.

### Completed and verified

- Restored the 2025 audit ZIP; all 317 recovered raw response hashes matched. Its 307 teams and 8,418 games remain intact.
- Fresh corrected inventories: 2021 — 302 provider teams, 293 with D1 games, 7,185 games; 2022 — 301 teams, 8,244 games; 2023 — 305 teams, 8,377 games; 2024 — 305 teams, 8,391 games. All 1,520 team-season records reconcile across 2021–2025.
- Adapted the older 2021 HTML. Recovered the 2022 Oregon–Arizona Final-only result from its labeled line score, confirmed by Oregon's recap.
- For 2023, excluded three erroneous February 19 matchups and supplied three missing actual games from official school schedules. The supplement observations explicitly share one official record per game; they are not independently reciprocal evidence. Corrected reversed Charlotte–Lipscomb W/L labels while preserving original fields.
- Kept 2023 Kent State–Ohio State and Columbia–Dartmouth date conflicts in the inventory, quarantined from every model input and evaluation sample. Do not silently choose one source's date.
- Fresh full-season independent comparisons: 387 of 388 official scored rows matched across Oregon State 2021–2024 and Columbia 2022–2024; the remaining date conflict is quarantined. These are selected samples, not national certification.
- Built 310 stable internal IDs across 1,520 season records, with explicit Houston Baptist/Houston Christian and Dixie State/Utah Tech aliases and source-specific annual conferences. No NCAA-ID or postseason-eligibility certification is claimed.
- Recorded exact Wednesday-before-regionals 12:00 UTC cutoffs, separate regular-only/conference-inclusive eligibility and exclusions. A two-calendar-day availability delay is an assumption for date-only data, not observed completion time.
- Implemented fixed neutral Elo (1500 initial rating, K=20, scale 400, 50% annual carry), same-day batch updates, tie handling, 50/50 and smoothed prior-win-rate benchmarks. 2021 initializes; 2022–2024 validate fixed parameters chronologically; 2025 remains development. No parameter tuning was performed.
- Frozen regular-only 2022–2024 NCAA results: 411 games, 68.9% winner accuracy, 0.6162 log loss and 0.2136 Brier. Win-rate comparator: 61.9%, 0.6453 and 0.2273. 2025 development: 63.2% accuracy over 136 NCAA games. Full modes, calibration bins and individual predictions are saved.
- Tests cover future-result leakage, same-day order, frozen-mode isolation, cutoff boundaries, ties and name aliases. Cached rerun evidence is saved in rerun_validation.json; database integrity and foreign keys are checked during rebuild.

### Limits and holdout decision

2026 cannot be certified untouched: inherited ESPN coverage probes included it, and this session's Columbia 2021 URL silently returned 2026 results. That response is rejected by the year guard and retained only as access-failure evidence. No 2026 fitting, tuning or evaluation occurred. A future season, earliest candidate 2027, must be reserved after locking the protocol.

Scores retrieved now may contain later corrections. Unlabeled pre-NCAA games are inferred regular season; phase/completion-date verification remains limited. Actual venue advantage, player/box/play coverage, a seed benchmark, bracket simulation, advancement calibration and a prospectively untouched evaluation remain open. National team completeness and every conference affiliation are not independently certified.

D1Baseball was not queried; the inherited automation restriction remains in force. Successful Warren Nolan retrieval does not create an automated-feed guarantee or redistribution license. No interface, repository, deployment, scheduler, purchase or outbound contact was created.

### Durable deliverables and next step

College_Baseball_Historical_Baseline_Bundle.zip and College_Baseball_Historical_Coverage_and_Elo_Report.md are the current handoff. Root run.py rebuilds cached normalized data, evidence checks, eligibility, tests, baseline and SQLite. Preserve this baseline before richer features. Next: resolve the two timing exceptions, broaden independent date/phase checks and add a cutoff-safe seed benchmark; then establish the dedicated repository and lock a future holdout.


## Repository setup — September 20, 2026

The public repository is `aaronmayeux/college-baseball-predictor`. Code, tests, cutoff configuration, specification and project-authored reports are tracked. The large evidence bundle, raw responses, SQLite databases, generated game-level outputs and original spreadsheets remain outside Git. `scripts/restore_data.py` verifies the saved bundle checksum and restores data without overwriting code. See `docs/DATA.md`.

This repository edition supersedes earlier statements about a repository not yet existing. Historical session notes remain as dated records. No modeling parameters, source restrictions or evaluation claims changed during repository setup. Next data/model work remains resolving the two timing exceptions, broadening checks and adding a seed benchmark.


## Interface requirement — September 20, 2026

Aaron requests graphs like the original spreadsheet. Preserve the two-team radar (spider) comparison from the DYNAMIC workbook MATCHUPS sheet, with CONTACT, POWER, SPEED, PITCHING and DEFENSE axes. The inspected chart caches Coastal Carolina and LSU as its example teams. The future app should allow selecting two teams and comparing their profiles. Define comparable scales and explain the metrics when implemented; preserve the visual concept without treating the original formulas as validated. This is a recorded requirement for the later interface milestone, not authorization to build it now.
