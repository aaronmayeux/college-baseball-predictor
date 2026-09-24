# Current handoff

Updated September 24, 2026. Git history owns prior sessions.

## Completed

Built the full 2025 tournament engine and first browser app using existing frozen team Elo. Verified NCAA format and placement. Regionals/Omaha handle reset games; supers/final stop at two wins. Exact advancement probabilities integrate all possible opponents; a separate game-by-game favorites path fills the entire bracket. Both forecast modes retain all 64 teams.

The app has round navigation, conditional game odds, overall advancement/title odds, team comparisons and CSV exports. `python3 -m tournament.build --standalone /absolute/path/College_Baseball_Predictor.html` creates an offline browser copy. Code, contracts and reproduction: [Tournament_Engine.md](Tournament_Engine.md). No public hosting yet.

## Verification

121 tests pass. All elimination paths, fair-team probabilities, the 60%/64.8% series benchmark, stopping and routing are covered. The retained-data build matches v2 matchup probabilities for 136 games per mode within 1.12e-16; stage totals reconcile to 16/8/2/1. Original baseline and v2 checkpoint data are byte-identical. JavaScript syntax and standalone DOM checks pass for stage/mode controls, comparisons and both CSV exports. Actual visual/browser layout verification remains pending: the browser binary was unavailable and its download failed.

## Next action and limits

Finish real-browser phone/desktop checks and provide hosted access, then get Aaron’s feedback. The standalone copy is a development preview, not a deployed site. Continue engine → usable app → richer inputs; do not resume broad player/access audits. No fresh nationwide import, player availability, venue adjustments, strength uncertainty or unqualified radar dimensions. Predictive bracket calibration and untouched holdout remain unestablished. Source restrictions and cutoff separation are unchanged.
