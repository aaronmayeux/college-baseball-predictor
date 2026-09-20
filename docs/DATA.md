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

The stored source bytes retain their URLs, retrieval timestamps and SHA-256 hashes. Game dates are not certified completion or publication times. Three corrected 2023 games use official-school supplements. The original baseline retains two timing exclusions; the separate v2 extension below resolves them without overwriting that baseline. See the coverage report for the full source restrictions, gaps and holdout decision.

Original spreadsheets and reference PDFs remain in project sources, untouched. They are not runtime dependencies. No credentials are required for a cached rebuild.

## Timing and seed extension (v2)

Retain the original bundle above **and** `College_Baseball_Timing_Seed_Evidence_v2.zip` (about 1.6 MB). The add-on contains new source bytes, failed-access metadata and generated v2 outputs; repository code remains authoritative. SHA-256:

```text
9a9b2d059bc8858bfd127732ad848f87670a90769ecc3ed5d5c0ba961fd11376
```

After restoring/rebuilding the original baseline:

```sh
python3 scripts/restore_validation_data.py /absolute/path/to/College_Baseball_Timing_Seed_Evidence_v2.zip
python3 historical/test_validation_v2.py
python3 historical/validation_v2/run.py
```

The extension verifies source hashes, original coverage/correction gates, independent matches and seed eligibility before writing only `historical/validation_v2/output/`. Existing baseline files are fingerprinted and must remain unchanged. `evidence.py` can collect the named new sources if necessary, but only the preserved add-on reproduces this exact snapshot. Failed guessed NCAA article URLs are evidence of tested failures, not missing nationwide seed coverage. See [the v2 report](Timing_and_Seed_Validation.md) for scope and results.

## Statistics discovery evidence

`College_Baseball_Statistics_Discovery_Evidence.zip` is a small, independent research checkpoint, not a replacement for either baseline ZIP. It contains four ESPN historical summaries, four official LSU pages, URL/retrieval-time/hash metadata, and fingerprints of the five supplied references. No 2026 game feed was requested. Web-only source observations and current access limitations are recorded in the [triage report](Statistics_Discovery_and_Triage.md).

SHA-256: `ab47ff963eb3c7e3404b9066b7110506b4e3db2ffce3abb165a836dc5dad1960`.

Verify that hash before extracting into a new temporary directory. The archive has `raw/` and `reference_hashes.json` at its root. It does not contain or restore baseline outputs. Use current repository code:

```sh
sha256sum /absolute/path/to/College_Baseball_Statistics_Discovery_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Statistics_Discovery_Evidence.zip /tmp/baseball-statistics-discovery
python3 scripts/audit_statistics_sources.py --raw-dir /tmp/baseball-statistics-discovery/raw
```

After restoring the baseline, the same discovery checkpoint also supports the full LSU 2025 game-link inventory check:

```sh
python3 scripts/audit_official_season_inventory.py --raw-dir /tmp/baseball-statistics-discovery/raw
python3 scripts/test_official_season_inventory.py
```

This prints a reproducible per-game report with source/input hashes, strict join failures, cached-box presence and separate forecast-mode counts. It does not download boxes or certify appearances. A false `inventory_pass` is a reported coverage finding, not a script crash; callers must inspect it. Findings are in the [player coverage report](Historical_Player_Data_Coverage.md#full-season-inventory-gate-lsu-2025).

The offline audit verifies hashes and the fixed sample's event seasons, pitcher counts, pitch counts and outs. It never fetches data or modifies model inputs. These selected examples cannot estimate national coverage. Keep raw evidence private and outside Git, as with the earlier checkpoints.

## Historical player coverage evidence

`College_Baseball_Player_Coverage_Evidence.zip` retains 69 source responses with URL, UTC retrieval time and SHA-256 metadata, plus reproducible audit outputs. It is a separate checkpoint, not a replacement for the baseline or v2 archives. Includes exploratory empty-filter and populated probes as well as the fixed sample. No raw data belongs in Git.

SHA-256: `58fda46ad191c51a8fdb55be325c0a3c64421ab50a366bb43d26605ede74c8cd`.

Restore the original baseline first (no rebuild required for this audit), verify this ZIP's hash, then extract into a fresh temporary directory:

```sh
sha256sum /absolute/path/to/College_Baseball_Player_Coverage_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Player_Coverage_Evidence.zip /tmp/baseball-player-coverage
python3 scripts/audit_player_coverage.py --raw-dir /tmp/baseball-player-coverage/raw --output /tmp/baseball-player-coverage-rerun.json
python3 scripts/audit_official_player_sample.py --raw-dir /tmp/baseball-player-coverage/raw
python3 scripts/test_player_coverage.py
```

The ESPN audit records hashes of its ten preserved baseline roster/game inputs. Both audits are offline by default. The optional `--collect` flag is a bounded ESPN pilot, not a bulk importer or permission grant; cached failures are retained and never retried automatically. Official-source audit consumes retained bytes, including gzip-compressed responses. No full-season player import, feature fitting or baseline writes occur. [Coverage report](Historical_Player_Data_Coverage.md) owns findings and limitations.
