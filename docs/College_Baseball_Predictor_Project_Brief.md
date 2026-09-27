# College Baseball Predictor — Project Brief

Updated September 27, 2026.

## Purpose and current status

Build a predictor whose primary use is **one run immediately before the NCAA tournament to fill the entire bracket through the champion**. Automatically import eligible data, produce game/advancement probabilities and explain picks. Optional late-season conference comparisons are secondary.

The 2021–2025 pilot retains 40,615 completed D1 games, 1,520 team-seasons and
310 identities. Documented corrections reconcile provider records; three games use
official supplements. This is not independent national certification.

Neutral Elo picked 68.9% of 411 NCAA winners in 2022–2024 and 63.2% of 136 in
2025 development: retrospective matchup accuracy, not bracket accuracy or a holdout.

Frozen cutoffs are Wednesday 12:00 UTC before regionals, with a two-calendar-day
assumed availability delay. Regular-only and conference-inclusive modes remain separate;
publication/completion timing is not certified. Prior outcome exposure disqualifies
2026 as untouched; it has not been used for fitting or evaluation here.

[DATA.md](DATA.md) owns restoration. V2 resolves two timing quarantines, checks 1,019
official schedule entries and adds eligible 2022–2025 seed benchmarks while preserving
the original baseline. The [engine/app](Tournament_Engine.md) provide the 2025 field
in both modes, advancement odds, a full bracket, comparisons and CSV exports, offline
or privately hosted on Sites.

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

The [player audit](Historical_Player_Data_Coverage.md) and [field map](Tournament_Source_Availability_2025.md) own coverage gaps. National player coverage remains unverified. The fallback preserves all 64 teams and v2 probabilities in both modes. Engine checks establish mechanics, not calibration; missing workload limits availability modeling. Final totals are audit-only.

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
| D1Baseball | Public historical batting tables plus linked official postseason boxes; Aaron authorized collection | One 2023 team reconstructed; no date filter observed; broader historical coverage and consistent access unverified |
| FanGraphs college leaderboards | Advanced-stat comparisons and possible inputs | Export access, historical coverage, definitions, and usage terms |
| Commercial providers | Prior research only; paid acquisition out of scope | Zero-budget rule in AGENTS.md |

National player coverage remains unverified. baseballr is an access tool. MLB-derived metrics need college-specific validation.

Normalized records retain source/team/player identities, season, game time, venue, retrieval time and raw references. Preserve missingness, cache responses, deduplicate games and validate baseball innings. Imports are on demand; scheduled refresh is out of scope.

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

Python/SQLite implement the pipeline. Aaron accepts the first app. Milestone 6 prioritizes focused experiments; broad audits remain paused. Fresh nationwide ingestion and player features remain unqualified.

## Evaluation rules

- Split by season in chronological order. Fit preprocessing and tune features using only training data. Keep a final period untouched until evaluation.
- Use the recorded Wednesday 12:00 UTC pre-NCAA cutoffs and two-calendar-day assumed availability rule from cutoffs.json. The preserved baseline keeps both modes; the new component experiment prioritizes explicitly labeled conference-inclusive inputs under the practical contract in SPEC. Daily in-tournament updates are a separate mode. These are retrospective date-based reconstructions, not point-in-time-certified snapshots.
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

The [net-run](Team_Run_Experiment.md) and [raw OBP/ERA](Team_Component_Experiment.md)
candidates failed validation and are closed. The [schedule-aware OBP/ERA
extension](Schedule_Adjusted_Components.md) improved 2024 game scores but failed its
primary regional-advancement check. Strict fallback changed that conclusion; no
post-scoring diagnostic was promoted. Detailed metrics and limitations stay in those
reports. The [source report](Team_Component_Source_Decision.md) retains NCAA samples,
snapshot gaps and unresolved count discrepancies.

The [schedule-only 2025 development test](Schedule_Only_Development.md) is also
closed without promotion: it picked one extra game and regional champion but worsened
both probability scores. A fixed missing-game diagnostic did not change the conclusion.
Do not retune closed candidates on exposed 2024/2025. **Elo remains in the app.**

**Nolan refresh and evidence-backed corrections are connected to candidate Elo exports:**
[usage and review contract](Nolan_Refresh.md). Saved-byte replay preserves historical
fallback and official overrides. Explicit reviews bind source hashes and exact
original/replacement rows; unsupported changes keep baseline values. Synthetic tests
cover raw-to-Elo integration, provenance and cutoff separation. The retained bounded
refresh matches the original forecasts; no actual correction has been approved and
no prediction gain is claimed. App data remains unchanged.

**Promising candidates:** [Guillen](Guillen_Havoc_Experiment.md) and
[walk rate](Walk_Rate_Experiment.md) each improve 2024 game/regional scores and fixed
sensitivities. Guillen favors higher HR/run ratios; it is not a power penalty. Both
need later confirmation. [Standalone HBP](Hit_By_Pitch_Experiment.md) failed selection.
HAVOC's original and caught-stealing formulas are now authorized benchmarks, superseding
the inventory's earlier skip recommendation, and remain untested. The [D1Baseball reconstruction pilot](Havoc_Source_Reconstruction.md) recovered all pre-NCAA HAVOC counts for Virginia 2023 by subtracting eight postseason boxes from final totals.

**Next:** obtain enough HAVOC inputs through the verified D1Baseball/postseason-subtraction
route to test the original/net-steals formulas. Lock the source windows and bounded
training/selection sample before fitting. Unsupported pairs retain Elo; no broad
coverage audit. Final totals alone are ineligible.

Guillen and walks separately await a locked 2025 development confirmation, without
refitting or post-hoc combinations. No 2024 retuning, 2026 use or failed-candidate
reopening. Follow the [practical contract](../historical/SPEC.md#practical-team-component-experiment--current-priority)
and accept small documented gaps. D1 collection authorization is in AGENTS.md.
Fresh-year export remains a separate roster/cutoff task; the app remains Elo.

[Input qualification](Model_Input_Qualification.md) retains the richer-count extractors and gaps. Pitcher thresholds remain open.

Preserve all 64 teams and both cutoff-separated modes; retain the existing team-only fallback where richer inputs are unqualified. Spreadsheet comparisons, interface redesign, Cloudflare migration and daily updates remain deferred. The app remains a 2025 development demo; [Tournament_Engine.md](Tournament_Engine.md) owns reproduction.

## Open decisions

- Future production execution environment; Cloudflare is Aaron’s preferred future hosting option, with migration deferred. Development app hosting remains Sites. Repository: https://github.com/aaronmayeux/college-baseball-predictor (public).
- Further training-season expansion beyond the implemented 2021–2025 pilot; assess scoring-environment changes before adding complexity.
- A future prospectively reserved holdout; 2026 is not certified untouched. Current exact cutoffs and regular-only/conference-inclusive rules are settled in cutoffs.json.
- Fresh-year NCAA input availability and schedule/park adjustments; retained reports are usable for the documented experiment, not certified nationwide production ingestion.
- Bracket scoring system if optimizing a contest entry rather than simply reporting the most likely outcomes.
