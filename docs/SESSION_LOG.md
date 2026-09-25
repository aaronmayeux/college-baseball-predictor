# Current handoff

Updated September 25, 2026. Git history owns prior sessions.

## Completed

Published the first usable app privately for Aaron: https://aaron-college-baseball-predictor.aaronmayeux.chatgpt.site

GitHub remains authoritative. `.openai/hosting.json` retains the Site identity; reuse it. Added pinned Vite preview tooling and `scripts/build_static_app.py` to stage only HTML/forecast data in ignored `dist/`. Forecast loading errors now use plain language. Hosting reproduction and detailed checks: [Tournament_Engine.md](Tournament_Engine.md).

## Verification

Restored baseline and timing/seed checkpoints and rebuilt both 64-team forecasts offline. All 121 tests pass. Chrome checked both modes, every stage, game details, comparisons, same-team guard and the 64-team table. Downloaded CSVs parsed correctly: 64 team rows and 126 bracket-game rows, correct mode/cutoff. Desktop/phone-width visuals inspected; narrow iframe controls and no-overflow checks passed at 320/390/768 px nominal widths, including the expanded small-phone odds table. These are viewport checks, not physical-phone/Safari tests. Sites confirmed deployment succeeded.

## Next action and limits

Get Aaron’s phone usability feedback and address concrete issues. Spreadsheet comparisons and richer inputs remain deferred. Preserve the existing engine and cutoff-separated modes. This is still a 2025 development demo: no fresh nationwide import, player availability, venue adjustments, strength uncertainty or qualified radar inputs. Predictive bracket calibration and untouched holdout remain unestablished. No new collection or model tuning occurred.
