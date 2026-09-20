# Current handoff

Updated September 20, 2026. Replace as work advances; Git history owns prior sessions.

## Latest work

Primary scope: one pre-NCAA run fills the complete bracket through the champion; optional late-season matchups are for fun. Simulate tournament usage forward. Daily-mode research stays separate and deferred.

Added an offline official-school pitching parser/comparison for Towson–NC State (2024) and Missouri State–Arkansas (2022). The official boxes explain both flagged ESPN pitching discrepancies: one missing Arkansas appearance (Heston Tole), and a Towson aggregate innings total one out short. Original records remain untouched. Detailed findings: [Historical_Player_Data_Coverage.md](Historical_Player_Data_Coverage.md).

## Verification

18 official pitcher appearances expose BF/HBP; ten shared pitchers in the Arkansas game and all seven in the Towson game match on outs/H/R/ER/BB/K. Official count totals reconcile. Missouri State box pitch counts are all zero, retained as raw values but treated as unknown. Manual inspection explains Arkansas’s missing batting substitutes; batting automation and individual HR reconciliation remain incomplete.

Ten new tests plus all 27 prior tests pass; comparison output repeats byte-for-byte. Restored original player coverage evidence passed its hash and offline audits. Four new school responses and report are preserved in the official pitching evidence ZIP documented in DATA.md. Baseline files remain unchanged.

## Next action and limitations

Reconcile complete appearance histories for sampled LSU and smaller-conference team-seasons. Fixed-box success does not establish season completeness, stable IDs, bulk permission or historical publication timing. Keep missing appearances distinct from rested arms. Preserve appearance/start/completion dates, phase checks and prospective holdout locking.

Quality-arm/ace thresholds and scaling remain open. 2025 is development; 2026 remains uncertified and unused. No features fitted or interface authorized.
