# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — Guillen tested; HAVOC input gap isolated

[Protocol/results](Guillen_Havoc_Experiment.md). Aaron authorized original Guillen
and HAVOC benchmarks plus a fixed caught-stealing HAVOC alternative. This supersedes
the inventory's earlier skip recommendation. Ten free dated NCAA reports acquired:
2021–2024 HR/runs pairs, and 2023 SB/CS plus batting-average samples. No school sweep.

Guillen = 1.6×HR/runs. Fit 2021–2022, select 2023, refit through 2023, evaluate
exposed 2024. Positive fitted coefficient favors higher HR/run ratios, not a power
penalty. 2024: 92/133 winners versus Elo's 89; log loss 0.620988 → 0.593697;
Brier 0.215786 → 0.203279. Regional loss 1.157268 → 1.031633; Brier
0.636643 → 0.574031; both pick 10/16. Both fixed sensitivities retain gains.
Supers regress slightly; retrospective gains need confirmation. App remains Elo.

HAVOC remains untested: SB/CS are available, but batting K is absent from tested
reports. Pitching K cannot substitute. No changed denominator or invented counts.

## Verification

293 data-free tests pass (202 scripts, 91 historical; twelve new).
Five outputs repeat byte-for-byte; 270 matchup checks and 32 regional paths pass.
Protected inputs, prior models/outputs and app unchanged; diff check passes.
New raw evidence/outputs retained separately per DATA.md; none committed to Git.

## Next concrete step

Lock 2025 development confirmation of Guillen and walks as separate fixed models,
using dated pre-NCAA inputs. No post-hoc combinations or 2024/2025 refitting.
A focused dated batting-K source can enable HAVOC, but must not block usable
candidates or start school/coverage sweeps. Preserve cutoff modes and Elo fallback.
No failed-candidate reopening, individual pitchers or 2026 use. Fresh-year export
remains a separate roster/cutoff decision.
