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

## Holdout decision
2026 cannot be certified untouched: recovered SESSION_RECORD.md says an earlier ESPN sample included 2026 and its original raw evidence was lost. Exact exposed games and whether outcomes informed choices are unknown. Do not collect or evaluate 2026 under an untouched-holdout claim. Reserve a future season prospectively after locking code, cutoffs and metrics; 2027 is the earliest candidate, not yet a committed test.

Additional holdout exposure: requesting Columbia's official 2021 schedule silently returned 2026 scored rows. The season guard rejects the payload from historical checks and all modeling. It is retained as raw failed-access evidence only. No 2026 fit or metrics were run. A later Conference USA 2025 statistics page linked to DBU’s default 2026 schedule; the season guard rejected that response. The explicit 2025 selector was used instead. The retained wrong-year page is failed-discovery evidence only.

## Versioned timing/seed extension

`validation_v2/run.py` is a separate frozen-forecast evaluation; it never rewrites baseline games, predictions or metrics. Its contract and evidence are in [the v2 report](../docs/Timing_and_Seed_Validation.md). Original quarantine rules remain part of v1 reproduction; v2 applies verified timing resolutions to copies. Completion dates drive the unchanged two-day result-availability assumption. Do not feed suspended-game completion dates into a new daily prediction target: model start and completion events separately first.

The seed comparator uses cutoff-eligible NCAA selection announcements and a fixed regional-seed odds rule, with no fitting or national-seed inputs. Both published and modified timestamps must precede the forecast cutoff. Require complete identity mappings and compare on identical samples. Preserve development/holdout labels and reconstruction caveats.

## Separate preflight selection evidence

The 2021 school-hosted NCAA selection PDF and dated school article now pass a separate retrospective eligibility/identity check; see [qualification](../docs/Model_Input_Qualification.md#verified-preflight-september-26-2026). This does not change v1 or v2 seeds, predictions, metrics or the initialization label. The expansion planner accepts this evidence optionally; future seed scoring must retain common samples and cutoff rules.

September 26 discovery/search results exposed incidental 2026 scores and current-year summaries while locating historical sources. They were not ingested as features or used for fitting, selection or evaluation; the existing no-untouched-2026 decision remains binding.
