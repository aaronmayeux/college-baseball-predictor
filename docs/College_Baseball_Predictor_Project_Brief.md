# College Baseball Predictor — Project Brief

Current state as of September 20, 2026. Git history preserves earlier revisions.

## Purpose and current status

Build a college baseball tournament predictor using automatically collected regular-season data. Produce calibrated game probabilities, advancement probabilities, and a predicted bracket from regionals through the national championship. Explain the main reasons behind predictions.

The historical pilot covers **2021–2025: 40,615 completed D1 games, 1,520 team-season records and 310 stable team identities**. Records reconcile after documented corrections; three games use official-school supplements. V2 resolves two timing quarantines while preserving the original baseline. Provider agreement is not independent national certification.

Fixed neutral Elo selected 68.9% of NCAA winners across 411 games in 2022–2024 and 63.2% across 136 games in 2025 development. The historical report owns detailed metrics. These are retrospective matchup evaluations, not bracket accuracy or an untouched holdout.

Exact pre-NCAA cutoffs are now recorded: Wednesday 12:00 UTC before regionals, with a two-calendar-day assumed availability delay for date-only results. Regular-only and conference-inclusive inputs are separate. Point-in-time publication/completion is not certified. 2026 cannot be called untouched because prior probes exposed outcomes; discovery also encountered a default current-year player leaderboard. It was not used for model fitting or evaluation.

The preserved baseline and separate v2 evidence checkpoints are documented in DATA.md. V2 resolves the timing conflicts, checks 1,019 official schedule entries, and adds a cutoff-safe 2022–2025 seed benchmark. No tournament simulator, interface, hosting, scheduled refresh or paid feed exists. Broad statistics discovery is documented; joint priority review is next, before feature implementation.

## Working references

GitHub `main` owns current code and documents. Read `AGENTS.md` for working rules and `historical/SPEC.md` for the evaluation contract. This brief describes current state; edit it in place rather than appending session histories.

- [Data restoration](DATA.md): restore the separately retained `College_Baseball_Historical_Baseline_Bundle.zip` with repository code. Ask for the ZIP if unavailable.
- [Historical coverage and Elo report](College_Baseball_Historical_Coverage_and_Elo_Report.md): detailed evidence, results and exclusions.
- [Timing and seed validation](Timing_and_Seed_Validation.md): resolved dates, broader independent checks, benchmark contract/results and remaining limits.
- [2025 coverage report](College_Baseball_2025_Coverage_Report.md): original 307-team, 8,418-game audit.
- Project attachments: original STATIC and DYNAMIC spreadsheets and research/design PDF. Keep originals untouched; they are references, not runtime dependencies or validated model specifications.

## Intended product

A mobile-friendly web app with automated data refresh, tournament brackets, game/advancement/championship probabilities, short explanations and spreadsheet exports. Include a selectable two-team radar chart like the DYNAMIC workbook's MATCHUPS chart: contact, power, speed, pitching and defense. Define comparable scales and explain each measure; the original formulas are not validated. Interface tools and hosting remain undecided. No interface implementation is authorized yet.

## Decisions to carry forward

1. Automate ingestion; retain raw source data and normalized records so results are reproducible.
2. Use probabilities, not just winner picks. Evaluate both individual games and advancement forecasts.
3. Model each tournament's actual rules. Regionals use four-team double elimination; super regionals use best-of-three series; Omaha has two four-team double-elimination groups followed by a best-of-three final. Verify the applicable year's rules before implementation.
4. Use common underlying team and player estimates across phases. Format, venue, rest, opponent, and available pitching alter the simulation. Separate independently trained models for each phase are not automatically necessary.
5. Benchmark a simple model before adding proposed differentiators.
6. Treat novelty as a research objective, not a reason to keep a feature that fails validation.

## Statistics discovery and joint triage

The [statistics inventory and proposed triage](Statistics_Discovery_and_Triage.md) owns candidate definitions, source/access findings, overlap, reliability, coverage, cutoff safety, cost/effort, pitching thresholds and scaling alternatives. It reviews both original workbooks and the research PDF, and extends beyond them. Recommendations await Aaron's review; no features or thresholds have been selected or fitted.

Proposed first tests: compact hitting components, pitcher quality and qualifying-arm depth/aces, opponent-adjusted scoring/prevention, then simple baserunning/defense challengers. Research current arm availability, park/HR dependence, fuller HAVOC and matchup interactions next. The report includes a reproducible four-game ESPN feasibility sample and an official-box cross-check; these do not establish national coverage.

Carry these product requirements forward:

- Quality-arm counts require both meaningful workload and quality cutoffs; distinguish rotation, bullpen and mixed roles without double-counting. Identify multiple aces or none. Separate season depth from arms available after recent usage; thresholds remain open.
- Power, contact and HAVOC can coexist. Test HR dependence and park/opponent interactions without assuming power is bad. Measure reaching base, efficient stealing and advancement separately.
- Evaluate z-scores and alternatives for modeling; consider percentiles for comparison charts. Adjust for sample size, opponents and parks before interpreting standardized numbers as quality. Neither scaling nor chart formulas are settled.
- Compare additions against the preserved baseline on common chronological samples. Review the shortlist jointly before implementation.

## Spreadsheet cautions and research hypotheses

The original weights, styles and formulas are not validated. The research PDF owns the inherited audit; the discovery report records current reference inspection. Postseason-contaminated totals, uncertain advanced-stat provenance, inconsistent weights, cached errors, flawed DIRTY_DER/HAVOC definitions and incorrect series logic preclude treating workbook results as forecast evidence. Keep originals untouched.

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

Fresh discovery probes reproduced populated and empty ESPN boxes; retained evidence is separate from the earlier lost probes. National player-data coverage remains unverified. baseballr is an access tool, not an independent source. MLB-derived metrics such as SIERA require college-specific validation.

Every normalized record should retain provider, provider ID, stable internal team/player ID where available, season, game timestamp, venue, retrieval timestamp, and raw-record reference. Handle missing data explicitly. Cache responses, avoid duplicate games, validate baseball innings notation, and make reruns safe. Scheduled refresh comes after a reliable manual command; no scheduler has been configured.

## Build milestones and acceptance criteria

| Milestone | Deliverable | Done when |
|---|---|---|
| 1. Coverage audit | Representative season/date/team coverage table and selected sources | Results, box scores, player data, and play-by-play availability are quantified separately; fallbacks and access limits documented |
| 2. Data pipeline | Repeatable import command, raw cache, normalized database, cutoff-aware features | A representative regular-season dataset loads without manual stat copying; reruns do not duplicate records; key totals reconcile |
| 3. Baseline | Simple game model, such as regularized logistic regression or Elo | Evaluated chronologically against simple benchmarks; probabilities and limitations reported |
| 3a. Statistics discovery and triage | Broad candidate inventory and prioritized shortlist | Follow the statistics discovery contract above; Aaron and assistant review priorities before feature implementation |
| 4. Tournament engine | Regionals, supers, Omaha groups, final series | Reset games, series stopping rules, advancement, and shared simulation state behave correctly; probabilities reconcile |
| 5. Added features | Measured home/park effects, power/HAVOC, then pitching availability | Each addition is compared with the baseline on unseen seasons and retained only with a justified benefit |
| 6. Interface and refresh | Mobile-friendly bracket, explanations, exports, refresh status | Real predictions trace to model/data versions and timestamps; missing data and uncertainty are visible |

Python and SQLite implement the results pipeline, cutoff reconstruction, Elo and separate seed benchmark. Milestones 1–3 remain partial: broader coverage, exact timing, player data and advancement evaluation are incomplete. Statistics discovery is documented; joint triage is pending. Milestones 4–6 have not started. Hosting remains undecided.

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

## Next work

Use repository code, `historical/SPEC.md` and [DATA.md](DATA.md); the cached pipeline entry point is `python3 historical/run.py`. Do not run older bundled scripts over the current handoff.

Timing/seed work is complete in `historical/validation_v2/`; baseline preservation and recovery are documented in the v2 report and DATA.md. Next review the proposed statistics priorities with Aaron, then qualify historical player-data coverage before feature fitting. Start/completion separation for daily forecasts, broader independent phase checks and prospective holdout locking remain outstanding; none should be silently dropped.

## Open decisions

- Eventual execution/hosting environment. Repository: https://github.com/aaronmayeux/college-baseball-predictor (public).
- Further training-season expansion beyond the implemented 2021–2025 pilot; assess scoring-environment changes before adding complexity.
- A future prospectively reserved holdout; 2026 is not certified untouched. Current exact cutoffs and regular-only/conference-inclusive rules are settled in cutoffs.json.
- Whether a paid source becomes necessary after testing free coverage.
- Bracket scoring system if optimizing a contest entry rather than simply reporting the most likely outcomes.
