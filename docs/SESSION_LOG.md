# Current handoff

Updated September 25, 2026. Git history owns prior sessions.

## Completed

Extended the offline pitching extractor with `lsu_pitching_inputs.py` and optional `--season-raw-dir`. All 68 LSU 2025 boxes / 274 appearances reconcile explicit lineup starts, per-pitcher BF components and cumulative starts/appearances/sacrifices. Two catcher-interference plays supplement cumulative BF components; one different-batting-slot pitching change requires explicit prior-pitcher removal. No table-order starter inference. [Qualification](Model_Input_Qualification.md) owns results; [DATA](DATA.md#offline-pitching-input-pilot) owns commands.

Together with Davidson/Missouri State, the pilot covers 180 boxes / 709 pitching appearances. Model, app, baseline, existing appearance audits and hitting extractor remain unchanged. No weights, thresholds, fresh collection or 2026 evaluation.

## Verification

All 154 tests pass (124 scripts, 30 historical), including eight new LSU regressions. Full three-team extraction repeats byte-for-byte; baseline/config hashes stay unchanged and previous structured-team outputs match. LSU has 55/55 regular-only and 57/57 conference-inclusive games. Pitch counts cover 232/233 and 237/238 appearances respectively. Actual work dates/rest remain unknown. The LSU–UCLA postseason date mismatch and Missouri State completion annotation remain visible.

## Next action and limits

Define the smallest permitted multi-season expansion covering both teams in evaluation matchups, following the qualification report’s 2021–2022 training / 2023 selection / 2024 retrospective validation plan before collection or fitting. Existing LSU historical indexes/sample boxes are candidates, not qualified seasons. Do not tune depth/ace thresholds on the convenience sample.

National predictive validation remains unsupported; preserve all 64 teams and unchanged Elo fallback. Broader access audits, spreadsheet comparison, app redesign, Cloudflare migration and daily updates remain deferred. The unavailable conference-archive checkpoint is unnecessary for current extraction.
