# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — distinct offensive walk-rate experiment

[Locked protocol, results and reproduction](Walk_Rate_Experiment.md).
Tested BB/(AB+BB+HBP+SF+SH) from retained NCAA reports as one addition to
conference-inclusive Elo. Fit 2021–2022, selected on 2023, refit through 2023,
then scored previously exposed 2024 without retuning. Source preparation reuses
existing qualifications only; no closed candidate was rescored or modified.

2024: 90/133 winners versus Elo's 89; game log loss 0.620988 → 0.616370 and
Brier 0.215786 → 0.213651. Regional champion log loss 1.157268 → 1.117877 and
Brier 0.636643 → 0.613727; both pick 10/16 champions. Both fixed sensitivities
retain probability-score gains. This is promising retrospective evidence, not
certified improvement: intervals cross zero and supers/finals regress.

## Verification

273 data-free tests pass (199 scripts, 74 historical; seven new tests).
Baseline/v2 rebuilds succeed. Five experiment outputs reproduce byte-for-byte;
270 matchup equivalence checks and 32 regional paths pass. Source/protected inputs,
old candidate code and app unchanged. `git diff --check` passes. No new collection,
coverage audit, cost, 2025/2026 candidate evaluation or app promotion.

## Next concrete step

Lock this exact model for a 2025 development confirmation, before scoring.
The retained national reports cover 2021–2024; use dated pre-NCAA 2025 walk counts,
never final workbook totals. If needed, separately scope a bounded free NCAA report
acquisition, not another coverage audit or school sweep. Review later-round behavior
and bracket implications before deployment. Keep Elo, both cutoff modes and fallback.
No 2024 retuning, failed-candidate reopening, individual-pitcher work or 2026 use.
Evidence-backed score-correction review remains implemented; no actual correction
has been accepted. Fresh-year export remains a separate roster/cutoff decision.
