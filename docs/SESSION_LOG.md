# Current handoff

Updated September 20, 2026. Replace this summary as work advances; Git history owns prior sessions.

## Latest change

Added separate `historical/validation_v2/` evaluation. Official recaps resolve Kent State–Ohio State (April 26) and Columbia–Dartmouth (April 22 start, April 23 completion). Broader checks also resolve Fordham–Richmond’s suspended game and four delayed regional openers. Original baseline code, inputs, predictions and metrics remain unchanged.

Checked 1,019 official schedule observations across 18 school-seasons: 1,016 independent, three reused supplement sources. Verified 59 explicit tournament-phase observations and 128 opening regional fixtures. Added cutoff-eligible seeds for all 256 tournament team-seasons in 2022–2025. Contract, results and caveats: [v2 report](Timing_and_Seed_Validation.md).

## Verification

All 13 offline tests pass. Full original pipeline rebuild succeeded; original predictions, metrics and eligibility match the baseline ZIP byte-for-byte. Ten v2 outputs reproduce byte-for-byte. Exact-checksum add-on restoration verified. Raw evidence and game-level outputs remain excluded from GitHub.

## Next action and limitations

Use both separately retained checkpoints; restoration commands and hashes are in [DATA.md](DATA.md). Next separate start/completion events for daily suspended-game forecasts, broaden independent phase checks, and lock a prospective holdout protocol. V2 currently emits frozen forecasts only. Publisher dates support retrospective cutoff reconstruction, not point-in-time certification. 2025 remains development; 2026 remains uncertified untouched and unused for modeling. No interface built.
