# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — evidence-backed score corrections in candidate Elo exports

[Review contract and usage](Nolan_Refresh.md#reviewed-score-correction-acceptance).
`tournament.build --refresh <saved-version> --accept-corrections <review.json>
--output tournament/output/<name>/forecast.json` accepts explicitly reviewed score
corrections tied to every saved evidence hash and exact original/candidate row fingerprints.
The actual parser must reproduce agreeing reciprocal observations. Dates, identities,
phases, timing changes, new games and official overrides are not accepted by this path.
Unreviewed changes keep historical fallback; invalid approvals fail the export.

The candidate retains original rows, corrected fields, new provenance and review details.
The exporter independently checks original Elo against v2, then reports candidate
probability differences. Baseline evidence and app data remain unchanged. Both cutoff
modes and the two-day lag still apply; later corrections are retrospective, not certified
as available at historical forecast time. No new collection, coverage audit, cost, model
retuning, real correction acceptance or 2026 use.

## Verification

266 data-free tests pass (199 scripts, 67 historical). Six new tests cover saved raw
reciprocal pages through acceptance and real Elo/export integration (unrelated historical
gates/bracket layout mocked), deterministic changed probabilities, original-v2 gate,
provenance retention, stale/tampered reviews, invalid scores, ties, official protection,
mode separation and cutoff exclusion. Existing fallback/app-output protection tests pass.
`git diff --check` passes. No full-data scoring or new performance claim.

## Next concrete step

Use the offline review path when a genuine score correction is available; do not collect
more solely to find one. Fresh-year export remains a separate roster/cutoff task. The app
remains the preserved 2025 Elo demo. No broad audits, paid services, UI/hosting changes
or reopening closed model candidates.
