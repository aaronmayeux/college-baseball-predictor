# Current handoff

Updated September 25, 2026. Git history owns prior sessions.

## Completed

Implemented the separate offline hitting extractor in `scripts/extract_hitting_inputs.py` and `hitting_inputs.py`. LSU's 68 boxes reconcile extra-base hits, HBP, sacrifices and PA against play-by-play, box summaries, opposing BF and cumulative count targets. Missouri State's 60 structured boxes provide a second-format power/OBP check; its PA-based rates stay null. Both cutoff modes produce complete pilot outputs. Definitions/results: [qualification report](Model_Input_Qualification.md). Restore/run command: [DATA.md](DATA.md#offline-hitting-input-pilot).

Predictions, app, baseline and original appearance-audit output contracts are unchanged. No feature weights or thresholds selected. New output is ignored, separate from model inputs used by the app.

## Verification

All 134 tests pass (104 scripts, 30 historical), including 13 new synthetic failure/cutoff checks. Extraction repeats byte-for-byte; input/config fingerprints remain unchanged. LSU eligible coverage is 55/55 regular-only and 57/57 conference-inclusive; Missouri State is 51/51 and 57/57 using the existing completion annotation. Original LSU postseason date mismatch and unknown player work dates remain visible. No new source requests or 2026 evaluation.

## Next action and limits

Qualify pitcher BF and explicit starter/relief roles using these same cached boxes, then summarize workload before choosing depth/ace thresholds. Follow the documented chronological plan before targeted multi-season collection or fitting. Current pilots do not support national predictive validation; retain all 64 teams, both modes and unchanged Elo fallback.

No broader collection/access audit is needed now. The conference-archive checkpoint remains unavailable and unnecessary for this step. Spreadsheet comparisons, app redesign, Cloudflare migration and daily updates remain deferred. Hosting reproduction remains in [Tournament_Engine.md](Tournament_Engine.md).
