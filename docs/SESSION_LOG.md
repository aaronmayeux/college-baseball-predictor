# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — refresh connected to full Elo export

[Usage/results](Nolan_Refresh.md#connected-candidate-forecast-export).
`tournament.build --refresh <saved-version> --output tournament/output/<name>/forecast.json`
reparses saved raw bytes, checks input/code hashes and staged rows, then connects
unchanged corroborated results to the full historical dataset. Changed, new,
conflicting, unpaired and missing results keep explicit historical fallback. Official
corrections and original provenance survive. Candidate outputs cannot overwrite app data.
No model changes, new collection, scoring experiment or 2026 use.

The saved LSU/Florida/Tennessee 2024 refresh confirms ten games; 185 unpaired games
retain baseline history. No requested-team baseline game is missing. Both full 2025
cutoff-mode forecasts preserve all 64 teams and match baseline advancement/bracket picks.
This is historical refresh integration, not certified nationwide or fresh-year support.

## Verification

260 tests pass (193 scripts, 67 historical). Eight new adapter tests include evidence
and generated-row tampering, changed scores/dates/phases, official correction preservation,
missing/conflicting/new rows and app-output protection. All 4,032 ordered matchups per
mode match exactly; candidate reruns are byte-identical. Baseline/v2 gates pass.
Reproduce with `python3 scripts/check_refresh_export.py <saved-version>`.

## Next concrete step

Add evidence-backed acceptance of genuinely changed rows into candidate forecasts while
preserving baseline history. Use synthetic fixtures; do not collect more to find changes.
Until qualified, actual changed rows remain flagged with historical fallback. No broad
audits, paid services, UI/hosting changes or retuning the closed model candidates.
