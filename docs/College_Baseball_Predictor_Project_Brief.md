# College Baseball Predictor — Project Brief

Current state: September 25, 2026.

## Purpose and current status

Build a college baseball tournament predictor whose primary use is **one run immediately before the NCAA tournament to fill out the entire bracket, from regionals through the national champion**. Automatically collect the eligible starting data, produce game and advancement probabilities, and explain the picks. Optional late-season conference-game comparisons are for fun; they are secondary to the complete bracket. Later pitching availability will be simulated from the initial snapshot; the first app uses team strength only.

The historical pilot covers **2021–2025: 40,615 completed D1 games, 1,520 team-season records and 310 stable team identities**. Records reconcile after documented corrections; three games use official-school supplements. V2 resolves two timing quarantines while preserving the original baseline. Provider agreement is not independent national certification.

Fixed neutral Elo selected 68.9% of NCAA winners across 411 games in 2022–2024 and 63.2% across 136 games in 2025 development. The historical report owns detailed metrics. These are retrospective matchup evaluations, not bracket accuracy or an untouched holdout.

Exact pre-NCAA cutoffs are now recorded: Wednesday 12:00 UTC before regionals, with a two-calendar-day assumed availability delay for date-only results. Regular-only and conference-inclusive inputs are separate. Point-in-time publication/completion is not certified. 2026 cannot be called untouched because prior probes exposed outcomes; discovery also encountered a default current-year player leaderboard. It was not used for model fitting or evaluation.

The preserved baseline and separate v2 evidence checkpoints are documented in DATA.md. V2 resolves the timing conflicts, checks 1,019 official schedule entries, and adds a cutoff-safe 2022–2025 seed benchmark. A complete team-only tournament engine and mobile-friendly browser app now use the retained 2025 field. Both frozen modes produce exact advancement odds, a full picked bracket, comparisons and CSV exports. A standalone HTML copy works offline; the first app is now privately hosted on Sites. Richer inputs follow after qualification. See [engine and app](Tournament_Engine.md).

## Working references

GitHub `main` is authoritative. `AGENTS.md` owns working rules; `historical/SPEC.md` owns evaluation rules.

- [Data restoration](DATA.md): restore the separately retained `College_Baseball_Historical_Baseline_Bundle.zip` with repository code. Ask for the ZIP if unavailable.
- [Historical coverage and Elo report](College_Baseball_Historical_Coverage_and_Elo_Report.md): detailed evidence, results and exclusions.
- [Timing and seed validation](Timing_and_Seed_Validation.md): resolved dates, broader independent checks, benchmark contract/results and remaining limits.
- [2025 coverage report](College_Baseball_2025_Coverage_Report.md): original 307-team, 8,418-game audit.
- Project attachments: original STATIC and DYNAMIC spreadsheets and research/design PDF. Keep originals untouched; they are references, not runtime dependencies or validated model specifications.

## Intended product

A mobile-friendly web app with an on-demand pre-tournament data import, one complete bracket, game/advancement/championship probabilities, short explanations and spreadsheet exports. Recurring refresh and live tournament updates are not required for the primary product. Include a selectable two-team radar chart like the DYNAMIC workbook's MATCHUPS chart: contact, power, speed, pitching and defense. Define comparable scales and explain each measure; the original formulas are not validated. Interface implementation is authorized; the first app uses plain HTML/JavaScript with a Python export, with private Sites hosting. Start with bracket picks, probabilities and comparisons from verified team-strength inputs. Add the radar dimensions when their inputs are qualified; do not invent values.

## Decisions to carry forward

1. Automate ingestion; retain raw source data and normalized records so results are reproducible.
2. Use probabilities, not just winner picks. Evaluate both individual games and advancement forecasts.
3. Model each tournament's actual rules. Regionals use four-team double elimination; super regionals use best-of-three series; Omaha has two four-team double-elimination groups followed by a best-of-three final. Verify the applicable year's rules before implementation.
4. Use common underlying team and player estimates across phases. Format, venue, rest, opponent, and available pitching alter the simulation. Separate independently trained models for each phase are not automatically necessary.
5. Benchmark a simple model before adding proposed differentiators.
6. Treat novelty as a research objective, not a reason to keep a feature that fails validation.

## Statistics discovery and joint triage

The [statistics inventory and proposed triage](Statistics_Discovery_and_Triage.md) owns candidate definitions, source/access findings, overlap, reliability, coverage, cutoff safety, cost/effort, pitching thresholds and scaling alternatives. It reviews both original workbooks and the research PDF, and extends beyond them. Aaron approved prioritizing hitting profiles and pitching quality/depth. Individual features, quality-arm/ace thresholds and scaling are not selected or fitted.

The [historical player audit](Historical_Player_Data_Coverage.md) covers four sampled team-seasons. The [2025 field map](Tournament_Source_Availability_2025.md) has 64 schedule sources and 50 player-group sources, but only LSU has reconciled core appearances. Schedule-result inventories are not appearance histories; detailed gaps remain in those reports. The team-only fallback checks all 64 teams and every pairing in both modes, reproducing v2 probabilities exactly; availability uncertainty remains unmodeled; the separate engine now verifies complete-bracket mechanics, not predictive calibration. Missing pitch counts and actual-work dates limit workload modeling. Final season totals are audit targets only.

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
| Commercial provider if needed | More consistent coverage | Verify sample coverage and terms before considering cost |

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

Python and SQLite implement the existing pipeline and baseline. Remaining audit gaps do not block milestones 4–5 using retained 2025 development data. Build order is engine → usable app → richer inputs. Aaron accepts the first app’s appearance and behavior. Move to milestone 6 with focused input qualification; broad collection/access audits remain paused unless needed for a selected feature. This does not certify fresh nationwide ingestion or player features.

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

Use [DATA.md](DATA.md); cached entry point: `python3 historical/run.py`.

Aaron confirmed the [hosted app](https://aaron-college-baseball-predictor.aaronmayeux.chatgpt.site) looks and works fine. No redesign is needed now. Next is focused prediction-model improvement:

The [focused input qualification plan](Model_Input_Qualification.md) now records the minimum features, verified pilot coverage and chronological evaluation gate. The four retained season audits reproduce, but none supplies a sufficient national training/validation sample. No prediction changes are qualified yet.

Next: extend the **cached LSU box parser** for extra-base hits and plate-appearance components, produce separate cutoff-specific counts/rates, and cross-check ISO on Missouri State's structured boxes. Then qualify pitcher BF and explicit roles using the same cache. The plan owns exact gates and subsequent multi-season expansion; thresholds/scaling remain open.

Preserve all 64 teams and both cutoff-separated modes; retain the existing team-only fallback where richer inputs are unqualified. Spreadsheet comparisons, interface redesign, Cloudflare migration and daily updates remain deferred. Aaron has a Cloudflare account and prefers it as a future hosting option; migration is separate from model work. The current app remains a 2025 development demo. See [Tournament_Engine.md](Tournament_Engine.md) for reproduction and [DATA.md](DATA.md) for retained evidence.

## Open decisions

- Future production execution environment; Cloudflare is Aaron’s preferred future hosting option, with migration deferred. Development app hosting remains Sites. Repository: https://github.com/aaronmayeux/college-baseball-predictor (public).
- Further training-season expansion beyond the implemented 2021–2025 pilot; assess scoring-environment changes before adding complexity.
- A future prospectively reserved holdout; 2026 is not certified untouched. Current exact cutoffs and regular-only/conference-inclusive rules are settled in cutoffs.json.
- Whether a paid source becomes necessary after testing free coverage.
- Bracket scoring system if optimizing a contest entry rather than simply reporting the most likely outcomes.
