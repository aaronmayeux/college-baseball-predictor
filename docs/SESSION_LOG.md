# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed

Planned the smallest staged expansion in [qualification](Model_Input_Qualification.md#multi-season-expansion-plan): start with the complete 2022 Stillwater regional (reuse Missouri State; three new team-seasons), then target the 2021–2024 NCAA fields for full-field testing. This is a coverage scope, not a statistical minimum or collection authorization. Training/selection/validation remains 2021–2022 / 2023 / 2024; 2025 is development and 2026 excluded.

Added an offline inventory command, `scripts/plan_model_expansion.py`; [DATA](DATA.md#offline-multi-season-expansion-inventory) owns reproduction. The four-season inclusive inventory has 14,175 team-game rows / 12,072 distinct D1 input games. These are not qualified boxes or request counts. No fitting, thresholds, fresh collection, model/app changes or new evidence archive.

## Verification

Restored exact-hash baseline and timing/seed checkpoints. All 154 existing tests pass (124 scripts, 30 historical). The new report repeats byte-for-byte, checks retained selection/timing evidence, and preserves all existing historical JSON/CSV and app HTML hashes. Scope/count assertions pass. Other evidence audits were not rerun; their prior findings remain unchanged.

## Next action and limits

Review exact-source access/volume and cached or permitted sample boxes for Oklahoma State, Arkansas and Grand Canyon 2022; complete the four-team preflight only after access clears. All registry bulk permissions remain unverified. No provider contact is authorized.

Before freezing the multi-season sample, qualify missing 2021 selection/seed evidence; its inventory is provisional. Before advancement validation, qualify historical routing (current routing is 2025-only). Preserve per-feature, both-team common samples and full Elo fallback. Do not tune on preflight outcomes or 2024. National predictive validation, actual work dates/rest and depth/ace thresholds remain unqualified. Broader audits, spreadsheet comparisons, UI changes and hosting migration stay deferred.
