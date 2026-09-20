# Current handoff

Updated September 20, 2026. Replace as work advances; Git history owns prior sessions.

## Latest work

Full-season appearance audit now parses all 68 LSU 2025 boxes and 54 Towson 2024 boxes. Every listed player's core season counts reconcile: 274 LSU and 265 Towson pitching appearances, plus batting GP and six core batting counts. Provider-specific pitcher-only batting rows are retained and explained. See [Historical_Player_Data_Coverage.md](Historical_Player_Data_Coverage.md).

## Verification

All 55/57 LSU regular-only/conference-inclusive pre-NCAA games and all 54 Towson games have verified boxes. Pitch counts are positive for 273/274 LSU and 238/265 Towson appearances; other counts remain unknown. Zero-out appearances survive. Twelve new synthetic tests and all 37 prior tests pass. Offline audit repeats byte-for-byte; preserved baseline and cutoff hashes are unchanged. The separate season evidence ZIP is documented in DATA.md.

## Next action and limitations

Expand a school/season source registry and qualify another small whole-season batch across publishing systems/smaller conferences; establish permissions before national collection. Require coverage or an explicit validated simpler fallback for every tournament team. Do not infer rest from missing appearances.

LSU–UCLA still has source start June 16 versus baseline completion June 17; retained box notes confirm suspension. Individual actual-work dates, historical publication timing, cross-provider IDs, starts/roles, advanced batting fields and pitcher HR attribution remain unqualified. Final season totals only audit completeness.

Primary product remains one pre-NCAA run through the champion with simulated future workloads. No interface, feature fitting, live updates or scheduler. Quality-arm/ace thresholds and scaling stay open; baseline/modes/holdout safeguards unchanged. 2025 is development; 2026 is uncertified and unused.
