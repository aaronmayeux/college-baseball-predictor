# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — HAVOC source route demonstrated

Aaron prioritized obtaining HAVOC inputs and explicitly authorized scraping public
D1Baseball historical stats, superseding the project’s reference-only rule.
[Source proof](Havoc_Source_Reconstruction.md): Virginia 2023 D1 batting rows load
in the browser, although direct HTTP returns 403. No date filter observed.
All eight postseason boxes linked from its schedule downloaded successfully.

Reconstruction removes every NCAA game from final-season batting counts: 65 → 57
games, batting K 418 → 368, BB 319 → 284, HBP 82 → 74, SB 83 → 71, CS 20 → 16.
Original HAVOC 1.358696; net-steals version 1.271739. These are input values,
not predictive results. No fitting, 2026 collection or app changes.

## Verification

Seven new data-free tests pass. Real parser checks both teams’ player sums, dates,
scores, hashes and all eight exclusions against retained Nolan games. D1 DOM sums
and final runs reconcile; offline output repeats byte-for-byte. Diff check passes.
Evidence ZIP and restoration instructions are in DATA.md; raw data is not committed.

## Next concrete step

Expand this verified route to a bounded 2021–2023 training/selection sample and
test original/net-steals HAVOC. Lock source windows and fallback coverage before
scoring. Final totals require complete subtraction; do not mix a full pre-NCAA
denominator with older NCAA numerator snapshots. One team is insufficient for
model testing. No broad coverage audit or open-ended school sweep.

Guillen and walks remain separate promising candidates awaiting fixed 2025
development confirmation. Do not combine or retune them after exposed results.
Elo remains in the app; closed candidates stay closed, individual pitchers deferred.
