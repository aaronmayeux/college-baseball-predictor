# Current handoff

Updated September 20, 2026. Replace this summary as work advances; use Git history for prior sessions.

## Latest change

Established the standing documentation rule in `AGENTS.md`: current state, concise working files, no accumulating decision diary. Consolidated the brief, removed obsolete setup instructions and repeated historical checkpoints, and retained the requested radar chart in the product requirements.

## Verification

This change only edits documentation. Reviewed the diff for preserved constraints, active requirements and correct repository paths. Code, data, audit reports and model behavior are unchanged; runtime tests were not rerun.

Last runtime verification (repository setup): all six offline tests passed, 3,212 data files restored, and the full cached pipeline passed SQLite integrity/foreign-key checks. Predictions, metrics and eligibility matched the saved bundle byte-for-byte. These are prior verified results, not new test runs.

## Next action and blockers

Resolve the two excluded 2023 timing conflicts, broaden independent date/phase checks, then add a cutoff-safe seed benchmark. Follow the brief and specification for evaluation constraints. Full reproduction requires the separately retained data bundle; see `DATA.md`. No interface work yet.
