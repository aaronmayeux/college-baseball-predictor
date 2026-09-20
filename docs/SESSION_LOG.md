# Session log

## September 20, 2026 — Public repository setup

Repository: https://github.com/aaronmayeux/college-baseball-predictor

### Changes

Imported the current historical pipeline and six chronology tests from the supplied baseline ZIP. Added the README, project instructions, current brief, specification, audit reports, data-restoration instructions and a checksum-verified restoration command. Added Git exclusions for raw evidence, databases, generated data and original workbooks. Added a GitHub Actions workflow for offline tests. The cached pipeline gives a clear restoration instruction when data is missing.

Public files contain code, configuration and project-authored documentation. The evidence bundle remains separate. Legacy 2025 scripts, including its historical D1Baseball probe, are not included. No model parameters or prediction rules changed.

### Verification

- All six offline chronology tests passed in the repository.
- Restored 3,212 data files from the pinned ZIP without replacing code or documents.
- Full cached pipeline completed; SQLite contains 40,615 games and passed its integrity/foreign-key checks.
- Predictions, baseline metrics and cutoff eligibility reproduced the audited ZIP byte-for-byte.
- Reviewed the staged file list: no raw responses, databases, game-level exports, workbooks or archives are tracked; checked for common credential/private-key patterns.

### Limits and next step

Data is not publicly redistributed; full reproduction requires the existing bundle from the project owner. No license has been selected. The current baseline remains retrospective, 2025 remains development, and 2026 is not certified untouched. Next: resolve the two 2023 date conflicts, broaden independent date/phase checks and add a seed benchmark. No interface work.


## September 20, 2026 — Spreadsheet-style graphs requested

Recorded Aaron’s request for graphs in the future app. Inspected the original DYNAMIC workbook chart XML: MATCHUPS uses a two-series radar chart with contact, power, speed, pitching and defense axes. Added the requirement to the brief. Original spreadsheets, code, data and model are unchanged. Verification was limited to the source chart definition and documentation diff; no runtime tests were needed. Next data/model work remains the two timing conflicts, broader independent checks and a cutoff-safe seed benchmark. Interface implementation remains deferred.
