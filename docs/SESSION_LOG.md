# Current handoff

Updated September 25, 2026. Git history owns prior sessions.

## Completed

Published the first usable app privately for Aaron: https://aaron-college-baseball-predictor.aaronmayeux.chatgpt.site

GitHub remains authoritative. `.openai/hosting.json` retains the Site identity; reuse it. Added pinned Vite preview tooling and `scripts/build_static_app.py` to stage only HTML/forecast data in ignored `dist/`. Forecast loading errors now use plain language. Hosting reproduction and detailed checks: [Tournament_Engine.md](Tournament_Engine.md).

## Verification

Restored baseline and timing/seed checkpoints and rebuilt both 64-team forecasts offline. All 121 tests pass. Chrome checked both modes, every stage, game details, comparisons, same-team guard and the 64-team table. Downloaded CSVs parsed correctly: 64 team rows and 126 bracket-game rows, correct mode/cutoff. Desktop/phone-width visuals inspected; narrow iframe controls and no-overflow checks passed at 320/390/768 px nominal widths, including the expanded small-phone odds table. These are viewport checks, not physical-phone/Safari tests. Sites confirmed deployment succeeded.

## Next action and limits

Aaron accepts the app’s appearance and behavior. Begin milestone 6 in a new chat: follow the project brief’s focused model-improvement path. First reuse triage/coverage findings to specify and qualify the smallest cutoff-safe hitting and pitching quality/depth inputs, with field gaps and a chronological evaluation plan. Then test qualified additions against the preserved baseline; later-round pitcher availability follows basic quality/depth. Thresholds/scaling remain open.

Spreadsheet comparisons, redesign, Cloudflare migration and daily updates remain deferred. Aaron has a Cloudflare account; hosting migration is separate. Preserve all 64 teams, both forecast modes and the existing fallback. Current limits remain: no certified fresh nationwide import, qualified player adjustments, bracket calibration or untouched holdout. This closeout changes documentation only; no new collection or model tuning.
