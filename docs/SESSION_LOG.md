# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed — schedule-aware OBP/ERA experiment

[Protocol/results](Schedule_Adjusted_Components.md); [reproduction](DATA.md#schedule-aware-component-extension).
Added game-weighted opponent Elo through each NCAA snapshot date to the raw OBP/ERA
model, with training-only weights/scaling and unchanged Elo offset. Trained 2021–2022,
selected 2023, refit through 2023, evaluated exposed 2024. No new sources or fallback gaps.

2024 game scores improve: log loss 0.620988 → 0.592047; Brier 0.215786 → 0.204155;
both pick 89/133. Primary advancement remains slightly worse, with 9/16 regional
champions versus Elo’s 10/16. Strict flagged-input fallback improves advancement,
so that conclusion is sensitive; do not promote this diagnostic after scoring.
**Keep Elo in the app.** Raw OBP/ERA and net-run remain closed.

Schedule-only diagnostic: better 2024 game and advancement scores (91/133 games,
10/16 champions), but worse than Elo in 2023. It is a research lead, not a selected model.

## Verification

237 tests pass. Five new outputs rerun byte-identically; prior raw experiment unchanged.
270 pairing comparisons match; all 32 regional paths qualify. Baseline/v2 gates pass;
app, cutoffs and evidence unchanged. No 2025 candidate evaluation or 2026 modeling.

## Next concrete step

Lock one schedule-only extension for **2025 development**, specifying chronological
fitting before scoring. Use existing Nolan results; no NCAA collection needed. Preserve
2024 exposure, 2025 development labeling, leakage checks, advancement comparison and
Elo fallback. No retuning on 2024, broad coverage audit, paid services, individual
pitchers/Stillwater, D1 automation or UI/hosting work.
