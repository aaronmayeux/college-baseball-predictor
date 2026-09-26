# College Baseball Predictor — Project Brief

Updated September 26, 2026.

## Purpose and current status

Build a predictor whose primary use is **one run immediately before the NCAA tournament to fill the entire bracket through the champion**. Automatically import eligible data, produce game/advancement probabilities and explain picks. Optional late-season conference comparisons are secondary.

The historical pilot covers **2021–2025: 40,615 completed D1 games, 1,520 team-season records and 310 stable team identities**. Records reconcile after documented corrections; three games use official-school supplements. V2 resolves two timing quarantines while preserving the original baseline. Provider agreement is not independent national certification.

Fixed neutral Elo selected 68.9% of NCAA winners across 411 games in 2022–2024 and 63.2% across 136 games in 2025 development. The historical report owns detailed metrics. These are retrospective matchup evaluations, not bracket accuracy or an untouched holdout.

Exact pre-NCAA cutoffs are now recorded: Wednesday 12:00 UTC before regionals, with a two-calendar-day assumed availability delay for date-only results. Regular-only and conference-inclusive inputs are separate. Point-in-time publication/completion is not certified. 2026 cannot be called untouched because prior probes exposed outcomes; discovery also encountered a default current-year player leaderboard. It was not used for model fitting or evaluation.

[DATA.md](DATA.md) owns the preserved checkpoints. V2 resolves timing conflicts, checks 1,019 official schedule entries and adds a cutoff-safe 2022–2025 seed benchmark. The [engine and app](Tournament_Engine.md) use the retained 2025 field in both frozen modes, with advancement odds, a complete bracket, comparisons and CSV exports. The app works offline or privately hosted on Sites.

## Working references

GitHub `main` is authoritative. `AGENTS.md` owns working rules; `historical/SPEC.md` owns evaluation rules.

- [Data restoration](DATA.md): restore the separately retained `College_Baseball_Historical_Baseline_Bundle.zip` with repository code. Ask for the ZIP if unavailable.
- [Historical coverage and Elo report](College_Baseball_Historical_Coverage_and_Elo_Report.md): detailed evidence, results and exclusions.
- [Timing and seed validation](Timing_and_Seed_Validation.md): resolved dates, broader independent checks, benchmark contract/results and remaining limits.
- [2025 coverage report](College_Baseball_2025_Coverage_Report.md): original 307-team, 8,418-game audit.
- Project attachments: original STATIC and DYNAMIC spreadsheets and research/design PDF. Keep originals untouched; they are references, not runtime dependencies or validated model specifications.

## Intended product

The mobile-friendly app needs on-demand pre-tournament import, a complete bracket, game/advancement/championship probabilities, short explanations and spreadsheet exports; no recurring refresh or live updates. The authorized first app uses HTML/JavaScript, a Python export and private Sites hosting. Add the DYNAMIC workbook-inspired two-team radar chart—contact, power, speed, pitching and defense—only after qualifying its inputs and defining comparable scales. Original chart formulas are not validated.

## Decisions to carry forward

1. Automate ingestion; retain raw source data and normalized records so results are reproducible.
2. Use probabilities, not just winner picks. Evaluate both individual games and advancement forecasts.
3. Model each tournament's actual rules. Regionals use four-team double elimination; super regionals use best-of-three series; Omaha has two four-team double-elimination groups followed by a best-of-three final. Verify the applicable year's rules before implementation.
4. Use common underlying team and player estimates across phases. Format, venue, rest, opponent, and available pitching alter the simulation. Separate independently trained models for each phase are not automatically necessary.
5. Benchmark a simple model before adding proposed differentiators.
6. Treat novelty as a research objective, not a reason to keep a feature that fails validation.

## Statistics discovery and joint triage

The [statistics inventory](Statistics_Discovery_and_Triage.md) owns candidate definitions, source findings, coverage, cutoff safety, thresholds and scaling alternatives, including both workbooks and the research PDF. Aaron prioritized hitting profiles and pitching quality/depth; individual features, thresholds and scaling remain unselected.

The [historical player audit](Historical_Player_Data_Coverage.md) and [2025 field map](Tournament_Source_Availability_2025.md) own detailed coverage gaps. Schedule inventories are not appearance histories; national player coverage remains unverified. The team-only fallback checks all 64 teams and pairings in both modes and reproduces v2 probabilities exactly. Engine checks establish bracket mechanics, not predictive calibration. Missing pitch counts/work dates limit availability modeling; final season totals are audit-only.

Carry these product requirements forward:

- Quality-arm counts require both meaningful workload and quality cutoffs; distinguish rotation, bullpen and mixed roles without double-counting. Identify multiple aces or none. Separate season depth from arms available after recent usage; thresholds remain open.
- Power, contact and HAVOC can coexist. Test HR dependence and park/opponent interactions without assuming power is bad. Measure reaching base, efficient stealing and advancement separately.
- Evaluate z-scores and alternatives for modeling; consider percentiles for comparison charts. Adjust for sample size, opponents and parks before interpreting standardized numbers as quality. Neither scaling nor chart formulas are settled.
- Compare additions against the preserved baseline on common chronological samples. Qualify data before implementing the approved priority families; review other additions jointly.

## Spreadsheet cautions and research hypotheses

The research PDF and discovery report own the workbook audit. Postseason-contaminated totals, uncertain advanced-stat provenance, inconsistent weights, cached errors, flawed DIRTY_DER/HAVOC definitions and incorrect series logic preclude treating workbook results as forecast evidence. Keep originals untouched.

Retain the hypotheses of home/park effects, power sensitivity, opponent-specific HAVOC, and tournament pitching depletion. Distinguish actual home park from host selection and batting last. Do not infer spin or contact quality from batted-ball labels, or universal recovery rules from pitcher workload. Implement only after the relevant coverage and evaluation gates.

## Data-source strategy

| Candidate | Intended role | Unresolved issue |
|---|---|---|
| NCAA statistics and official school schedules/box scores | Independent checks; expanded results and phase coverage in the v2 validation report | Nationwide coverage, access restrictions, parsing differences and snapshot timing remain unresolved |
| ESPN scoreboards and game summaries | Game IDs, results, box scores, play-by-play and pitch counts when available | Undocumented interfaces and uneven historical coverage; validate venue flags |
| Boyd's World | ISR and historical ratings research | Accessible archives, cutoff dates, and permitted automated use |
| Warren Nolan plus targeted official-school corrections | 2021–2025 results pilot: 40,615 games; all 1,520 team-season records reconcile after documented corrections | Independent national completeness, precise historical timing, broader phase verification, ongoing access/usage terms; original workbook attribution remains uncertain |
| D1Baseball | Potential separately licensed source; direct public HTML retrieval tested successfully | Published terms prohibit automated monitoring/mining/copying; supported feed, license, historical completeness and price are unverified |
| FanGraphs college leaderboards | Advanced-stat comparisons and possible inputs | Export access, historical coverage, definitions, and usage terms |
| Commercial providers | Prior research only; paid acquisition out of scope | Zero-budget rule in AGENTS.md |

National player-data coverage remains unverified. baseballr is an access tool, not an independent source. MLB-derived metrics require college-specific validation.

Every normalized record should retain provider, provider ID, stable internal team/player ID where available, season, game timestamp, venue, retrieval timestamp, and raw-record reference. Handle missing data explicitly. Cache responses, avoid duplicate games, validate baseball innings notation, and make reruns safe. On-demand ingestion supports the one-run workflow; scheduled refresh is out of scope.

## Build milestones and acceptance criteria

| Milestone | Deliverable | Done when |
|---|---|---|
| 1. Coverage audit | Representative season/date/team coverage table and selected sources | Results, box scores, player data, and play-by-play availability are quantified separately; fallbacks and access limits documented |
| 2. Data pipeline | Repeatable import command, raw cache, normalized database, cutoff-aware features | A representative regular-season dataset loads without manual stat copying; reruns do not duplicate records; key totals reconcile |
| 3. Baseline | Simple game model, such as regularized logistic regression or Elo | Evaluated chronologically against simple benchmarks; probabilities and limitations reported |
| 3a. Statistics discovery and triage | Broad candidate inventory and prioritized shortlist | Follow the statistics discovery contract above; Aaron and assistant review priorities before feature implementation |
| 4. Tournament engine | Regionals, supers, Omaha groups, final series | Reset games, series stopping rules, advancement, and shared simulation state behave correctly; probabilities reconcile |
| 5. First usable app | Mobile-friendly bracket, probabilities, team comparisons, explanations and export | Aaron can open and use a complete 64-team development bracket through the champion; model/data versions, cutoffs and limitations are visible |
| 6. Richer inputs and production readiness | Qualified hitting profiles, pitching depth/aces and availability; reliable fresh import | Validate additions against the baseline chronologically; qualify source access and coverage for inputs actually used |

Python and SQLite implement the pipeline and baseline. Build order remains engine → usable app → richer inputs. Aaron accepts the first app’s appearance and behavior. Move to milestone 6 with focused input qualification; broad collection/access audits remain paused unless needed for a selected feature. This does not certify fresh nationwide ingestion or player features.

## Evaluation rules

- Split by season in chronological order. Fit preprocessing and tune features using only training data. Keep a final period untouched until evaluation.
- Use the recorded Wednesday 12:00 UTC pre-NCAA cutoffs and two-calendar-day assumed availability rule from cutoffs.json. Regular-only is primary; conference-inclusive is separately labeled. Daily in-tournament updates are a separate mode. These are retrospective date-based reconstructions, not point-in-time-certified snapshots.
- Use log loss and Brier score to assess probability quality, plus calibration: events assigned roughly 60% should happen roughly 60% of the time. Report winner accuracy as a secondary measure.
- Compare against simple team-strength and seed baselines. Compare only on common evaluation samples when a feature reduces coverage.
- Evaluate game and advancement probabilities; uncertainty intervals should respect clustering by season/tournament. Omaha's small annual sample limits conclusions.
- Measure features one at a time and in meaningful combinations. Do not optimize thresholds against the same bracket used to advertise performance.
- Represent uncertainty about team strength and availability separately from game randomness. Carry a consistent team-strength draw through a simulated tournament when using that approach.
- A synthetic fair four-team regional should give each team a 25% initial title chance. A fixed independent 60% game favorite wins a best-of-three series 64.8% of the time. Use such checks alongside actual format edge cases.

## Next work

Reproduction: [DATA.md](DATA.md).

[App](https://aaron-college-baseball-predictor.aaronmayeux.chatgpt.site) unchanged.

**Team-level-first plan:** defer individual pitcher roles, workload, depth/aces, availability and the Stillwater preflight. Prioritize practical team data and measured prediction comparisons.

The [team-run experiment](Team_Run_Experiment.md) tested retained Nolan results and official/v2 corrections across all 256 tournament team-seasons in 2021–2024. Its net-runs/game candidate failed regional advancement validation and is **closed without promotion; Elo remains in the app**. No 2024 retuning, 2025 candidate evaluation or 2026 modeling occurred.

Aaron selected **Warren Nolan, NCAA and D1Baseball**, for personal, noncommercial use with no spending. The [source report](Team_Component_Source_Decision.md) records populated national NCAA OBP/ERA snapshots for 2021–2024 (293/301/305/305 teams). The latest tested 2021/2022 dates are empty; populated earlier dates omit later eligible games. In 2024 all 64 field identities map, 63 records and 59 runs-allowed totals reconcile after accounting for retained non-D1 games; five discrepancies remain. Conference-tournament and non-D1 scope prevent regular-only qualification. Neither mode has qualified component features.

The national date/phase planner rules out a complete four-season solution using one cumulative snapshot per team: known empty dates leave regular-only coverage at 50/64 in 2021 and 61/64 in 2022. Army and Columbia also played a regular game after their 2022 conference tournaments, so no single snapshot isolates their full regular-only totals. 2023/2024 are date-feasible, not component-qualified.

Next: assess a separately defined earlier regular-season feature window and quantify omitted results before collection or fitting. This alternative is not adopted; preserve the existing forecast/mode rules, all 64 teams and non-D1 limitations. No school sweep or paid detour; D1 stays reference-only.

[Input qualification](Model_Input_Qualification.md) retains the richer-count extractors and gaps. Pitcher thresholds remain open.

Preserve all 64 teams and both cutoff-separated modes; retain the existing team-only fallback where richer inputs are unqualified. Spreadsheet comparisons, interface redesign, Cloudflare migration and daily updates remain deferred. The app remains a 2025 development demo; [Tournament_Engine.md](Tournament_Engine.md) owns reproduction.

## Open decisions

- Future production execution environment; Cloudflare is Aaron’s preferred future hosting option, with migration deferred. Development app hosting remains Sites. Repository: https://github.com/aaronmayeux/college-baseball-predictor (public).
- Further training-season expansion beyond the implemented 2021–2025 pilot; assess scoring-environment changes before adding complexity.
- A future prospectively reserved holdout; 2026 is not certified untouched. Current exact cutoffs and regular-only/conference-inclusive rules are settled in cutoffs.json.
- A qualifying free source for dated team components; paid acquisition is out of scope.
- Bracket scoring system if optimizing a contest entry rather than simply reporting the most likely outcomes.
