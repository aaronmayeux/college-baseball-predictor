# College Baseball Predictor

A Python research pilot for automated college baseball results collection and chronological game predictions. No interface or tournament simulator yet.

## Current checkpoint

- 2021–2025: **40,615 completed D1 games**, 310 internal team identities.
- Frozen pre-NCAA Elo: **68.9% winner accuracy** on 411 NCAA games in 2022–2024; **63.2%** in 2025 development data.
- These are retrospective matchup results, not bracket accuracy or an untouched holdout. The original baseline retains two timing exclusions; a separate v2 evaluation resolves them. 2026 is not certified untouched.

Read the [project brief](docs/College_Baseball_Predictor_Project_Brief.md), [specification](historical/SPEC.md), and [coverage and baseline report](docs/College_Baseball_Historical_Coverage_and_Elo_Report.md).

## Run the tests

Python 3.10+; standard library only. From the repository root:

```sh
python3 -m unittest discover -s historical -p 'test_*.py' -v
```

Tests use synthetic games and require no downloads. GitHub Actions runs the same tests.

## Restore data and reproduce the baseline

The public repository contains code, configuration and project-authored reports. Raw source pages, original spreadsheets, game-level exports, databases and the evidence ZIP are intentionally not tracked. Obtain the existing `College_Baseball_Historical_Baseline_Bundle.zip` from the project owner; there is no public dataset download.

```sh
python3 scripts/restore_data.py /path/to/College_Baseball_Historical_Baseline_Bundle.zip
python3 historical/run.py
```

The restore command verifies the pinned bundle checksum, restores data without replacing code or documents, and refuses to overwrite different local files. The default pipeline rebuilds from cache without network access. See [data restoration](docs/DATA.md) for details and limitations.

## Timing and seed extension

[Validation results](docs/Timing_and_Seed_Validation.md) cover resolved timing conflicts, expanded official checks and a fixed 2022–2025 seed comparator. Restore the separate add-on using [DATA.md](docs/DATA.md), then run `python3 historical/validation_v2/run.py`. Outputs remain separate from the original baseline.

## Layout

- `historical/`: original audited Python pipeline, season adapters, Elo and tests.
- `historical/cutoffs.json`: exact forecast cutoffs and recorded model assumptions.
- `scripts/restore_data.py`: restore the separately retained snapshot.
- `docs/`: brief, reports, data instructions and session log.

## Next work

Separate suspended-game start and completion events for daily forecasts, broaden independent phase coverage, and lock a prospective holdout protocol. Preserve the fixed baseline before tuning or adding richer features.

## Source boundaries

Do not automate D1Baseball access under an ordinary subscription: the project's recorded terms audit found an automation restriction. Source availability does not establish redistribution permission. Raw evidence stays outside this public repository. No license has been selected for this project; public visibility alone is not an open-source license.
