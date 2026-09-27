# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — HAVOC tested and closed

Latest main fetched; baseline/v2 restored and rebuilt. All six priority postseason
exclusions now pass, including three documented start/completion date reconciliations.
WMT official embedded tables require batting K from the Hitting view; composite SO
is pitching strikeouts. Adapter verifies player joins, sums, both scores, opposing
pitching counts, source hashes and exact official embedding provenance.

The fixed sample has 17 usable team-seasons; covered NCAA games are 4/12/8 in
2021/2022/2023. Both locked formulas were fit on 16 training games and tested on
eight 2023 selection games with 129 exact Elo fallback games. Both worsened log loss
and Brier and added no correct picks. **HAVOC closed without promotion; Elo remains.**
[Chronological report](Havoc_Chronological_Experiment.md) owns metrics and limitations.

## Verification

28 focused data-free tests pass. Actual preparation/evaluation repeat byte-for-byte;
baseline/v2 preservation gates pass. Earlier checkpoint bytes remain unchanged.
[DATA.md](DATA.md) owns the updated evidence archive and `output/bounded-v3-final`
selection lock. No 2024–2026 candidate scoring, cutoff relaxation or app change.

## Next concrete step

Lock a separate 2025 development confirmation protocol for the existing Guillen
and walk-rate candidates, then evaluate their frozen models with game and advancement
checks when their retained inputs qualify. No refitting, combinations, 2024 retuning,
2026 use, failed-candidate reopening or broad audits. Individual pitchers deferred.
