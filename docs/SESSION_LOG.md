# Current handoff

Updated September 27, 2026. Git history owns prior sessions.

## Completed — bounded HAVOC checkpoint, not a model test

[Locked protocol/results](Havoc_Chronological_Experiment.md) target eight teams in each
of 2021–2023: first two regionals alphabetically. Fourteen complete final batting
tables retained. Texas and Louisiana Tech 2022 now have complete pre-NCAA subtractions
(69→61 and 64→61 games), supplementing the separately retained Virginia 2023 pilot.
Twenty-nine official box requests are cached: 16 HTTP 200, nine 404, four certificate
502 responses. Failed/missing/unsupported boxes remain explicit exclusions.

D1Baseball repeatedly showed Cloudflare browser verification. One normal reload
recovered an earlier page; collection stopped when verification returned. No bypass.
The evidence checkpoint preserves successes, failures and exact remaining game IDs.

## Verification and limitations

21 focused data-free tests pass. Offline preparation/report repeat byte-for-byte;
baseline/v2 preservation gates pass. Only one 2022 matchup and no 2021/2023 matchups
qualify. The coverage gate correctly stops before fitting or scoring either formula.
**HAVOC is still untested, not rejected.** Elo and the app remain unchanged.
Reproduction and checkpoint identity: DATA.md. New code: scripts/havoc_inputs.py and
historical/havoc.py. Tests need no external data.

## Next concrete step

Resume the same fixed sample when public D1 access permits; finish missing captures
and named excluded-game boxes using the saved checkpoint. Do not retry cached failures
automatically, replace teams or start a broad coverage audit. Once chronological
minimums pass, test both authorized formulas under the locked protocol. No later-year
scoring or deployment is authorized by this preliminary screen alone.

Guillen and walks still await separate locked 2025 confirmation; no combinations,
2024 retuning, 2026 use or reopening failed candidates. Individual pitchers deferred.
