# Historical results pilot — session specification

Extends the recovered 2025 audit. Read `docs/College_Baseball_Predictor_Project_Brief.md` before work. The public repository contains code and reports; restore data using `scripts/restore_data.py`.

## Evidence and scope
- Retain source bytes, URL, UTC retrieval time, SHA-256 and source-specific season metadata.
- Historical RPI tables are roster/record reconciliation targets only; never feed final ratings or records into predictions.
- Collect 2021–2024; preserve the 2025 snapshot. No 2026 collection or evaluation in this session.
- No D1Baseball requests: inherited published automation prohibition remains binding for this pilot.
- Team roster presence is not tournament eligibility. Preserve each season's conference; never propagate the latest affiliation backward.
- School name changes require explicit aliases with evidence. Do not fuzzy-merge institutions.

## Forecast contract
- Primary product: one frozen pre-NCAA run produces the entire tournament bracket. Optional late-season conference matchups are secondary. Daily-updated evaluation remains a separate, deferred research mode; live updates and recurring refresh are not required for the primary product. Tournament workloads are simulated forward from bracket lock.
- Separate regular-season-only and conference-inclusive pre-NCAA strength.
- A recorded exact cutoff plus a strict date eligibility rule is required. Historical date-only results are reconstructed evidence, not point-in-time certified snapshots.
- Missing dates, score conflicts, non-D1 games, unscored results and unresolved phases must be excluded or block evaluation, with reasons retained.
- No arbitrary ordering of doubleheaders: predict all eligible games of a date from the preceding state, then update in a batch.
- Ties can update Elo as half a win but are excluded from binary accuracy/log-loss/Brier evaluation.
- Neutral model only. Venue/home designations remain unverified.
- The development team-only fallback preserves all selected teams. Missing eligible current-season results block a matchup rather than silently using a default rating; missing player histories never imply rest. Its numerical probabilities exclude player adjustments. Unmodeled availability and uncalibrated strength intervals remain explicit; matchup checks do not qualify a complete bracket.

## Modeling gate
Only evaluate Elo after collection, reciprocal-score checks, season-record reconciliation, identity collision checks and phase/cutoff checks pass for the evaluation sample. Report exclusions and sample coverage. Never imply independent national completeness from agreement within one provider.

## Evaluation
2021 initializes the history; chronological development/validation follows in 2022–2024; 2025 is explicitly development. Choose simple fixed Elo parameters before reading metrics; any later tuning requires a separate chronological plan. Compare with 50/50 and prior-game win-rate strength on identical games. Frozen pre-NCAA forecasts and daily updated predictions are different outputs. Keep the historical baseline unchanged. The project brief authorizes a separate team-only tournament engine and usable app using retained 2025 development inputs; full player-history qualification is not a prerequisite. Verify tournament structure and probability behavior before delivering a complete bracket. Do not describe unmodeled pitching availability as verified rest.

## Practical team-component experiment — current priority

Aaron explicitly accepts imperfect historical team data to advance the predictor. This contract supersedes earlier requirements for four complete seasons, exact game-total reconciliation and regular-only selection **for the new component experiment**, not the preserved baseline, closed net-run experiment or strict appearance extractors.

- Use usable dated pre-NCAA national batting/pitching reports, including conference-tournament totals. Label this conference-inclusive experiment separately; never call mixed totals regular-only. Retained OBP/ERA are the starting candidates. All-opponent NCAA counts may be tested alongside D1 Elo with scope disclosed; exact non-D1 subtraction is not a prerequisite.
- Small missing-game/count differences are warnings to quantify, not automatic whole-project blockers. Record snapshot dates/age, game-count differences, unresolved discrepancies and missing teams. State a reasonable inclusion/fallback rule before scoring and assess sensitivity to flagged rows; do not declare every discrepancy harmless or repair unknown counts with invented zeros. Identity ambiguity, invalid denominators and future-data contamination still block the affected input.
- Use the supported seasons and available reports; older snapshots are permissible when dated and their omitted results are disclosed. Do not require full 2021–2024 coverage before a useful experiment. Keep all bracket teams via Elo fallback when richer inputs are unavailable; report feature-covered and fallback cases explicitly.
- Lock a small candidate set and chronological train/evaluation plan before fitting. Fit scaling/weights only on training seasons and compare with the matching Elo mode on identical games. Prior 2024 exposure must remain explicit; new results are retrospective/development evidence, not untouched validation. 2025 remains development; 2026 excluded.
- Retain log loss, Brier score, calibration and secondary accuracy; assess sensitivity to material data gaps. Preserve future-data/cutoff safeguards and advancement checks before app promotion. No requirement to improve or replace Elo; retain it if gains are inconclusive.

The next deliverable is an actual batting/pitching comparison, with these bounded checks integrated into it. Earlier-window feasibility planning and further broad archive/school audits are not prerequisites. No model was fitted or promoted when this policy was recorded.

## Holdout decision
2026 cannot be certified untouched: recovered SESSION_RECORD.md says an earlier ESPN sample included 2026 and its original raw evidence was lost. Exact exposed games and whether outcomes informed choices are unknown. Do not collect or evaluate 2026 under an untouched-holdout claim. Reserve a future season prospectively after locking code, cutoffs and metrics; 2027 is the earliest candidate, not yet a committed test.

Additional holdout exposure: requesting Columbia's official 2021 schedule silently returned 2026 scored rows. The season guard rejects the payload from historical checks and all modeling. It is retained as raw failed-access evidence only. No 2026 fit or metrics were run. A later Conference USA 2025 statistics page linked to DBU’s default 2026 schedule; the season guard rejected that response. The explicit 2025 selector was used instead. The retained wrong-year page is failed-discovery evidence only.

## Versioned timing/seed extension

`validation_v2/run.py` is a separate frozen-forecast evaluation; it never rewrites baseline games, predictions or metrics. Its contract and evidence are in [the v2 report](../docs/Timing_and_Seed_Validation.md). Original quarantine rules remain part of v1 reproduction; v2 applies verified timing resolutions to copies. Completion dates drive the unchanged two-day result-availability assumption. Do not feed suspended-game completion dates into a new daily prediction target: model start and completion events separately first.

The seed comparator uses cutoff-eligible NCAA selection announcements and a fixed regional-seed odds rule, with no fitting or national-seed inputs. Both published and modified timestamps must precede the forecast cutoff. Require complete identity mappings and compare on identical samples. Preserve development/holdout labels and reconstruction caveats.

## Separate team-run challenger

[Team_Run_Experiment.md](../docs/Team_Run_Experiment.md) owns the locked score-based challenger protocol and results. It uses 2021–2022 frozen NCAA matchups for coefficient training, 2023 selection, and 2024 retrospective validation, with training-only scaling and an unchanged Elo offset. This does not alter 2021's initialization role or any metrics in the preserved baseline. No 2025 candidate evaluation or 2026 modeling; no promotion without separate advancement validation. Component-count qualification and individual pitcher work remain separate.

## Separate preflight selection evidence

The 2021 school-hosted NCAA selection PDF and dated school article now pass a separate retrospective eligibility/identity check; see [qualification](../docs/Model_Input_Qualification.md#verified-preflight-september-26-2026). This does not change v1 or v2 seeds, predictions, metrics or the initialization label. The expansion planner accepts this evidence optionally; future seed scoring must retain common samples and cutoff rules.

September 26 discovery/search results exposed incidental 2026 scores and current-year summaries while locating historical sources. They were not ingested as features or used for fitting, selection or evaluation; the existing no-untouched-2026 decision remains binding.
