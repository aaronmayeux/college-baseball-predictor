# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Verified progress

Reconciled the NCAA May 26, 2024 OBP/ERA sample against the verified tournament field and v2 Nolan results: **64/64 identities, 63/64 records, 59/64 runs-allowed totals**. Seven retained non-D1 games explain some differences without entering model inputs. Five residual discrepancies remain; 62 teams have conference-tournament games. Neither forecast mode is qualified.

Checked earlier NCAA menus and national reports. Populated pairs: **2021 May 23 (293 teams), 2022 May 25 (301), 2023 May 28 (305)**. Later tested 2021 May 28/30 and 2022 May 30 reports explicitly return no rankings. All populated rates/records reconcile internally. Earlier 2021/2022 snapshots omit later eligible results; no national completeness claim.

The [source report](Team_Component_Source_Decision.md) owns scope, discrepancy table and source decisions. [DATA](DATA.md#ncaa-dated-team-report-sample) owns the combined evidence ZIP and offline reproduction. Code derives report IDs from season menus, distinguishes empty reports from zero data, and retains strict identity/count checks.

## Verification

215 tests pass (167 scripts, 48 historical). Offline reconciliation repeats byte-identically; baseline/v2 gates pass. No model fitting, candidate metrics, app changes or 2026 ingestion. Raw evidence remains outside Git; all access was free.

## Next

Plan a bounded national-archive test of team-specific pre-conference snapshots across seasons. Compare available dates to retained Nolan phase inventories and all 64 field teams before fetching more categories. Carry five 2024 count discrepancies and 2021/2022 timing gaps as blockers; no school sweep.

Keep Elo; net-run stays closed. Preserve evaluation/advancement rules and prior 2024 exposure. 2025 remains development; 2026 excluded. Individual pitchers, Stillwater, UI/hosting/spreadsheet work remain deferred. D1 reference-only; no paid detours.
