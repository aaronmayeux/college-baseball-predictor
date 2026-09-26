# Project instructions

Read `docs/College_Baseball_Predictor_Project_Brief.md` and `historical/SPEC.md` before changes. Review relevant code. Explain material choices in concise plain English.

- Preserve chronological cutoffs, provenance, raw evidence, known exclusions and original fields on corrections.
- Keep regular-only, conference-inclusive and daily-updated forecasts separate.
- Treat 2025 as development and 2026 as not certified untouched.
- Do not automate D1Baseball collection under the current source restrictions.
- Never commit raw downloads, game-level exports, databases, evidence ZIPs, credentials or the original spreadsheets. Do not use `git add -f` to bypass these exclusions.
- Keep tests runnable without external data. Use the separately retained bundle for full pipeline checks.
- Keep `docs/SESSION_LOG.md` as a short rolling handoff: latest meaningful change, verification, unresolved blockers and next action. Replace stale entries instead of appending a diary.
- Aaron authorized the tournament engine and first usable interface. Follow the build order in the project brief; broad player-data/access audits must not block the team-only app. This repository is separate from the bridge game.

- Current model-improvement priority is team-level hitting and pitching. Follow the brief’s team-level-first plan; individual pitcher histories and the unfinished Stillwater preflight are deferred, not prerequisites. Avoid open-ended school-by-school collection.

## Standing rule: keep context lean

- Documentation describes current truth. Update existing sections in place; remove superseded decisions, repeated summaries, obsolete plans and routine execution chatter.
- Use Git history for past decisions and changes. Do not copy deleted narrative into new archive files or append a dated note for every edit.
- Give each fact or rule one authoritative home and link to it elsewhere. Keep the brief focused on the product, current state, material constraints and next work. Read detailed reports only when relevant to the task.
- Aim for a brief under 2,000 words and a rolling handoff under 300 words; consolidate before growing either. Preserve a necessary active constraint rather than cutting it solely to meet a word target.
- Preserve raw evidence, provenance, reproducibility, audit findings and unresolved caveats. Concision applies to working narrative, not destruction of research evidence. Keep detailed evidence in its existing reports/data rather than duplicating it in startup documents.
- Before committing documentation, remove duplication and stale statements and check that current requirements remain clear. This rule applies to all repository edits and future sessions.
