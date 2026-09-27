# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — offensive HBP-rate experiment

[Locked protocol/results](Hit_By_Pitch_Experiment.md). Tested offensive
HBP/(AB+BB+HBP+SF+SH) as a single addition to conference-inclusive Elo using retained
NCAA reports. Fit on 2021–2022, select on 2023. It failed both probability scores:
log loss 0.628158 → 0.645132; Brier 0.218569 → 0.226878; winners 91/137 → 89/137.
Closed at selection, with no 2024 candidate scoring or post-result retuning.

The prior [walk-rate candidate](Walk_Rate_Experiment.md) stays locked and promising:
it improved 2024 game/regional probability scores and both fixed sensitivities.
Its uncertainty intervals cross zero and later-round regressions remain unresolved.
Elo remains in the app. No automatic stacking of features.

## Verification

281 data-free tests pass (199 scripts, 82 historical; eight new HBP tests).
Three HBP outputs reproduce byte-for-byte. Protected inputs, walk-rate code and
its five outputs, closed model code and app are unchanged. Failed-selection testing
ensures no validation/advancement scoring follows rejection. `git diff --check` passes.
No new provider collection, coverage audit, cost or 2025/2026 candidate evaluation.

## Next concrete step

Confirm the exact walk-rate model on 2025 development data under a protocol locked
before scoring. Use dated pre-NCAA walk counts, never final workbook totals. Retained
national reports cover 2021–2024; if needed, scope one free NCAA report acquisition,
not another coverage audit or school sweep. Review later-round behavior and bracket
implications before deployment. Preserve both cutoff modes and exact Elo fallback.
No failed-candidate reopening, 2024 retuning, individual-pitcher work or 2026 use.
Evidence-backed correction review remains available; no actual correction accepted.
Fresh-year export remains a separate roster/cutoff decision.
