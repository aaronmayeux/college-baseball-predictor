# Current handoff

Updated September 20, 2026. Replace as work advances; Git history owns prior sessions.

## Latest work

Added a four-school historical source registry and a shared parser for newer SIDEARM pages. All 52 Davidson 2024 and 60 Missouri State 2022 boxes are parsed. Pitching appearances and 16 counts reconcile per player: Davidson 212; Missouri State 223. Fourteen batting counts and GP reconcile for listed players. Details: [Historical_Player_Data_Coverage.md](Historical_Player_Data_Coverage.md).

A coverage ledger preserves every requested team, including unknown/unregistered teams. It does not implement predictions or a fallback model.

## Verification

Eleven new tests and all 49 prior tests pass. New and prior audits reproduce byte-for-byte; baseline/cutoff data is unchanged. Source evidence is retained separately per DATA.md. Unused roster rows, zero-out pitchers, a fall exhibition and cancellations are handled explicitly. No interface, feature fitting or 2026 statistics collection.

## Next action and limitations

Resolve two audit exceptions, then map sources for the full 2025 development tournament field before broader collection:

- Davidson's Jake Dunagan pinch-running/CF appearance is missing from its batting cumulative list; retain it and fail batting completeness.
- Missouri State–Illinois State 9–4: three school sources say May 24, 2022; baseline says May 25. Preserve the baseline and verify independently before a versioned correction. Regular-only is complete; conference-inclusive remains 56/57 verified games.

Positive pitch counts: Davidson 194/212; Missouri State 72/223. Rest stays unknown. Actual-work/publication timing, cross-provider IDs and national permission/coverage remain unqualified. LSU–UCLA's overnight suspension remains unresolved for individual work dates.

One pre-NCAA run through champion remains primary. Simulate future workload; no live updates/scheduler required. Quality-arm/ace thresholds and scaling stay open; baseline/modes/holdout safeguards unchanged.
