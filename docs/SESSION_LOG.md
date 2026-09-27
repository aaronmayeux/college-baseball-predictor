# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed — schedule-only 2025 development test

[Protocol/results](Schedule_Only_Development.md); [reproduction](DATA.md#schedule-only-2025-development).
Locked one conference-inclusive schedule correction before scoring 2025: fixed ridge,
training-only scaling/weight from 417 games in 2021–2023, no 2024 fitting. Full eligible
Nolan schedules replace earlier NCAA snapshot restrictions; all 64 teams qualify.
2024 only supplies eligible Elo carry; 2025 remains development, not a holdout.

**Failed; close without promotion or retuning. Keep Elo in the app.**
Games: 87/136 versus Elo’s 86, but log loss/Brier worsen
0.660978/0.233853 → 0.675974/0.237253. Regional champions: 8/16 versus 7,
but advancement loss/Brier worsen 1.132374/0.633688 → 1.240951/0.677750.
The predeclared one-missing-appearance diagnostic leaves the decision unchanged.
Raw OBP/ERA, net-run and schedule-aware primary remain unpromoted; no new sources.

## Verification

242 tests pass. Five outputs rerun byte-identically; 136 matchup comparisons match;
all 16 regional paths qualify. Baseline/v2 gates and protected fingerprints pass.
App, both baseline modes, raw evidence and prior experiments unchanged. No 2026 modeling.

## Next concrete step

Implement a bounded, free, on-demand Nolan refresh into a separate dataset version,
using the verified Elo model and existing cutoff/fallback rules. Preserve the offline
demo; fresh-year import is not yet production-certified. No broad coverage audit,
paid services, D1 automation, individual pitchers, UI redesign or hosting migration.
Any further model candidate needs a distinct hypothesis and new chronological lock;
do not keep trying weights on exposed 2024/2025.
