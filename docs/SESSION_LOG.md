# Current handoff

Updated September 25, 2026. Git history owns prior sessions.

## Completed

Added the separate offline pitching extractor (`extract_pitching_inputs.py`, `pitching_inputs.py`). All 112 Davidson 2024/Missouri State 2022 boxes and 435 pitching appearances pass BF component/opponent-PA/team-total checks. Explicit pitching GS and cumulative per-player starts support mutually exclusive observed starter-only, relief-only and mixed summaries. Both modes produce complete workload summaries; partial pitch-count coverage stays explicit. [Qualification](Model_Input_Qualification.md) owns results; [DATA](DATA.md#offline-pitching-input-pilot) owns restoration/commands.

Model, app, baseline, existing appearance audits and hitting extractor are unchanged. No thresholds, fitting, fresh collection or 2026 evaluation. The existing field checkpoint supplies all new extraction evidence.

## Verification

All 146 tests pass (116 scripts, 30 historical), including 12 pitching regression tests. Full cached extraction repeats byte-for-byte; baseline/config fingerprints remain unchanged. Davidson: 52/52 games in both modes. Missouri State: 51/51 regular-only, 57/57 conference-inclusive with the existing separate completion annotation. Actual pitcher work dates and rest remain unknown. Davidson’s batting omission remains visible.

## Next action and limits

Extend BF and explicit pitching-start verification to LSU’s cached StatCrew boxes. Its original parser lacks per-game GS; investigate explicit lineup/play evidence and reconcile against cumulative APP-GS, never use table order. Then follow the qualification report’s targeted multi-season expansion and chronological evaluation plan. No national predictive validation is supported yet; preserve all 64 teams and unchanged Elo fallback.

Depth/ace thresholds remain open. Broader collection/access audits, spreadsheet comparison, app redesign, Cloudflare migration and daily updates remain deferred. The unavailable conference-archive checkpoint is unnecessary for this step.
