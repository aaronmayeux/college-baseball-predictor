# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed decision

**Close the net-runs/game candidate without promotion. Keep Elo in the app.** The [experiment report](Team_Run_Experiment.md) owns the locked protocol, complete source/coverage evidence and results.

Completed regional advancement validation with unchanged candidate settings and engine mechanics. Both modes cover all sixteen regionals in 2023 and 2024. Selection articles and retained season manuals qualify grouping, opening seeds and elimination rules; all 201 regional games form legal paths whose champions match the super-regional field. All 540 observed game probabilities match the original experiment.

2024 primary regional probability scores worsened: champion log loss 1.051040 → 1.133873; Brier 0.576852 → 0.589449. Both models picked 10/16 champions. Conference-inclusive probability scores also worsened and picks fell 10/16 → 9/16. Exploratory regional-cluster intervals include zero. 2023 improved but was selection-exposed, so it cannot justify promotion. No retuning or national-title expansion for this candidate.

## Verification

200 tests pass (152 scripts, 48 historical). Repeated forecasts/report are byte-identical; baseline/v2, original experiment, engine and app unchanged. No new collection, archive or raw-data commit. After original experiment reproduction via [DATA](DATA.md), run `historical/regional_validation.py prepare` then `evaluate`.

## Next

Make one bounded source/sample decision for dated team batting/pitching components across 2021–2024. Require coverage, cutoff support and access terms before batch collection. If no practical route qualifies, compare retaining Elo with licensed data; no purchase/contact authorization. Avoid open-ended school probes.

Preserve both modes, common samples and evaluation rules. 2025 remains development; 2026 excluded. Individual pitchers, Stillwater preflight, UI/hosting/spreadsheet work stay deferred.
