# Project instructions

Read `docs/College_Baseball_Predictor_Project_Brief.md` and `historical/SPEC.md` before changes. Review relevant code. Explain material choices in concise plain English.

- Preserve chronological cutoffs, provenance, raw evidence, known exclusions and original fields on corrections.
- Keep regular-only, conference-inclusive and daily-updated forecasts separate.
- Treat 2025 as development and 2026 as not certified untouched.
- Do not automate D1Baseball collection under the current source restrictions.
- Never commit raw downloads, game-level exports, databases, evidence ZIPs, credentials or the original spreadsheets. Do not use `git add -f` to bypass these exclusions.
- Keep tests runnable without external data. Use the separately retained bundle for full pipeline checks.
- Record changes, verification, limitations and the next concrete step in `docs/SESSION_LOG.md`.
- Do not build an interface until that milestone is authorized. This repository is separate from the bridge game.
