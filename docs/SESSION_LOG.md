# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — bounded versioned Nolan refresh

[Usage/results](Nolan_Refresh.md); [evidence/reproduction](DATA.md#versioned-nolan-refresh-evidence).
`python3 -m ingestion.nolan_refresh` imports 1–8 explicitly named schedules into
immutable ignored versions. It supports live requests and verified cached replay,
checks season/team/URL/hash, retains failures without automatic retries, and stops
on access/rate-limit responses. No redirects, crawling, D1 requests or paid services.

Live LSU/Florida/Tennessee 2024 check: 207 schedule entries, all matching retained
normalized rows; 195 game IDs, ten with both requested sides, nine regular-only and
ten conference-inclusive eligible games. The 185 missing counterpart pages reflect
bounded scope. Partial imports remain staged, not supplied to Elo. New evidence is
retained separately; historical corrections and app are untouched.

## Verification

252 data-free tests pass (185 scripts, 67 historical). Ten new checks cover source
integrity, wrong-year/team rejection, duplicates, reciprocal conflicts, phase/cutoff
rules, failure caching, request bounds and redirects. Network-disabled rerun is
byte-identical. Baseline/v2 preservation gates pass. No 2026 collection or modeling.

## Next concrete step

Connect staged versions to the existing Elo export through a candidate dataset adapter.
Reuse verified unchanged history/corrections with provenance; explicitly handle changed,
conflicting and missing rows, retaining the verified snapshot as fallback. Verify all
64 teams and both modes before changing app data. No collection to fill out this
bounded sample, broad audits, UI/hosting work or paid services.

Elo remains the app model. Schedule-only failed the 2025 development probability
checks and is closed, as are prior failed candidates. No retuning on exposed 2024/2025.
