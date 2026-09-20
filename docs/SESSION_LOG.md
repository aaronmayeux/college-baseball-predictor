# Current handoff

Updated September 20, 2026. Replace as work advances; Git history owns prior sessions.

## Latest work

Aaron approved prioritizing hitting profiles and pitching quality/depth. Initial historical coverage audit is in [Historical_Player_Data_Coverage.md](Historical_Player_Data_Coverage.md). No features, thresholds, scaling choices or interface implemented.

## Verification

Twenty ESPN date queries across 2021–2025 yielded a deterministic 36-game sample covering 56 teams. Nine games had batting/pitching rows; none of 16 other-only conference samples did. Two populated games failed internal totals checks. All selected event/season/scoreboard identities passed; one requested-date baseline join remains unresolved at a UTC/local-date boundary. Five LSU indexes and earliest-game boxes passed archive/schema checks, not full-season reconciliation.

Evidence hashes and offline reruns verified; six new synthetic guard tests and 13 existing baseline/v2 tests passed. Authenticated GitHub confirmed write access. Baseline restored for read-only comparisons; preserved baseline inputs verified unchanged. V2 bundle was unnecessary; v2 code, cutoffs and forecast modes unchanged. Raw evidence recovery is in DATA.md.

## Next action and limitations

Qualify smaller-conference official boxes alongside LSU, reconcile every appearance for sampled team-seasons, resolve ESPN inconsistencies, then extend coverage sampling to postseason stages. National coverage, stable player identities, historical publication timing and bulk-source permissions remain unverified. Missing appearances cannot mean rested arms.

Quality-arm/ace thresholds and scaling remain open. Preserve daily start/completion handling, broader phase checks and prospective holdout locking. 2025 is development; 2026 remains uncertified and unused. No interface authorized.
