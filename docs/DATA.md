# Data restoration and provenance

The data checkpoint is `College_Baseball_Historical_Baseline_Bundle.zip` (66.8 MB compressed), retained separately in the project sources. It is not committed to GitHub or published as a release asset.

SHA-256:

```text
8be5c804aeadc593faa11441f12e82b75e32adaa778b2aacdb00a70fe9f40e63
```

From the repository root, run:

```sh
python3 scripts/restore_data.py /absolute/path/to/College_Baseball_Historical_Baseline_Bundle.zip
python3 historical/run.py
```

The restore command requires this exact snapshot. It verifies the archive before writing, rejects unsafe paths, skips Python and Markdown files, and refuses to replace differing local data. Existing identical data is reused. About 1.2 GB of free space is needed for restored evidence and derived outputs; allow additional space for rebuilding SQLite.

The pipeline reads cached 2021–2024 raw pages and the preserved 2025 normalized inventory. It verifies official correction evidence, reconciles records and identities, records cutoff eligibility, runs tests, evaluates fixed Elo, and rebuilds SQLite. Derived data remains ignored by Git. `python3 historical/check_rerun.py` checks deterministic outputs after an initial successful run.

2025 is an inherited frozen input. Its legacy collector, report generator and D1Baseball probe script are intentionally not included in this repository. Their original versions remain in the private evidence bundle, but are not needed for the current cached pipeline.

`python3 historical/run.py --collect` requests only missing Warren Nolan season pages after the required official evidence is available. It is not a complete fresh-from-the-internet bootstrap. Do not assume a current download reproduces a past source snapshot. Use a separate dataset version for later corrections; preserve raw provenance and do not silently change the audited baseline.

The stored source bytes retain their URLs, retrieval timestamps and SHA-256 hashes. Game dates are not certified completion or publication times. Three corrected 2023 games use official-school supplements, and two date conflicts remain excluded from modeling. See the coverage report for the full source restrictions, gaps and holdout decision.

Original spreadsheets and reference PDFs remain in project sources, untouched. They are not runtime dependencies. No credentials are required for a cached rebuild.
