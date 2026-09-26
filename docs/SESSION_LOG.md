# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed

Added an offline team game-log hitting extractor using the existing preflight checkpoint. Oklahoma State 2022 (64 games) and Grand Canyon 2022 (62) reconcile all ten batting fields against season footer/individual totals; available overall counts and retained first boxes also match. All 126 games pass opposing PA/BF component checks, including interference. Both cutoff modes now qualify ISO, OBP, strikeout rate and HR/PA. The exact Oklahoma State self-name alias is scoped and documented.

This qualifies descriptive team hitting, not player appearance histories or predictive improvement. Missouri State retains its prior ISO/OBP inputs; Arkansas hitting and remaining pitching/PA gaps stay open. Final totals remain audit-only. No new requests, fitting, outcome metrics, bulk permission, model/app change or 2026 evaluation.

[Qualification](Model_Input_Qualification.md#retained-team-hitting-logs) owns results and limitations. [DATA](DATA.md#retained-team-game-log-hitting) owns the offline command; no new ZIP is needed.

## Verification

All 175 tests pass (145 scripts, 30 historical). Twelve new synthetic tests cover missing/duplicate/wrong-year rows, count and denominator failures, identity aliases and qualification gates. Two full extraction reports repeat byte-for-byte; 3,249 preserved data/app JSON, CSV and HTML hashes remain unchanged.

## Next action and limits

Test whether retained Arkansas evidence can qualify team hitting, then finish the four-team preflight's remaining pitching/appearance reconciliation. Source-specific bulk scope remains unverified; no provider contact is authorized.

Preserve 2021–2022 training / 2023 selection / 2024 retrospective validation, common both-team samples and Elo fallback. No sufficient chronological feature sample exists yet. Rest/depth thresholds and historical advancement routing remain unqualified. Spreadsheet comparisons, UI changes and hosting migration stay deferred.
