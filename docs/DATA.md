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

## Official pitching comparison evidence

`College_Baseball_Official_Pitching_Evidence.zip` contains four new school responses with URL/retrieval-time/SHA-256 metadata and the derived comparison report. It supplements the original player-coverage checkpoint; neither archive replaces the other. SHA-256:

```text
1e071c3d118921b9adbc5efc875eb2ad469bc41e7c9201003dd9a6fad7c48590
```

Verify the hash, extract into a fresh temporary directory, and use current repository code:

```sh
sha256sum /absolute/path/to/College_Baseball_Official_Pitching_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Official_Pitching_Evidence.zip /tmp/baseball-official-pitching
python3 scripts/audit_official_pitching.py --official-raw-dir /tmp/baseball-official-pitching/raw --espn-raw-dir /tmp/baseball-player-coverage/raw
python3 scripts/test_official_pitching.py
```

The comparison is offline, verifies both source hashes/URLs and game identity, and never writes baseline data or changes original counts. Only these two boxes are supported. Schedules retain discovery provenance; they are not qualified full-season imports. Findings and remaining gaps belong in the [coverage report](Historical_Player_Data_Coverage.md#official-pitching-comparison-two-smaller-conference-sources).

## Complete-season appearance evidence

`College_Baseball_Season_Appearance_Evidence.zip` (about 3.7 MB) contains the 126 required source responses (two indexes, two cumulative audit targets and 122 boxes), their URL/UTC-retrieval/SHA-256 metadata, and the derived audit. Reused bytes come from the supplied prior checkpoints; new responses cover LSU 2025 and Towson 2024 only. SHA-256:

```text
4f481828e3d7d16d47ccd5d46c1e1d7735dfd9ca3f3ad1cc8996a061b70ded71
```

Restore the original baseline, verify this hash, then extract to a fresh directory:

```sh
sha256sum /absolute/path/to/College_Baseball_Season_Appearance_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Season_Appearance_Evidence.zip /tmp/baseball-season-appearances
python3 scripts/audit_season_appearances.py --raw-dir /tmp/baseball-season-appearances/raw --output /tmp/season-appearance-rerun.json
cmp /tmp/season-appearance-rerun.json /tmp/baseball-season-appearances/audit.json
python3 scripts/test_season_appearances.py
```

The audit is offline and never modifies baseline/model inputs. Full season totals only reconcile counts. Inspect per-game issues, `season_counts_reconciled`, per-mode box coverage and the separate timing/rest flags; a completed command does not certify workload availability. [Coverage report](Historical_Player_Data_Coverage.md#complete-season-appearance-pilot-lsu-2025-and-towson-2024) owns results, provider-specific GP conventions and expansion gates.

The optional bounded collector can reproduce access attempts into a new evidence directory, reusing the three earlier extracted raw directories:

```sh
python3 scripts/collect_season_appearances.py --evidence-dir /tmp/new-season-pilot --source-raw-dirs /tmp/baseball-statistics-discovery/raw /tmp/baseball-player-coverage/raw /tmp/baseball-official-pitching/raw
```

Fresh downloads are a different snapshot and may change. The collector is hard-limited to these two inventories, caches failures without automatic retries, and never requests 2026. This is not a nationwide importer or a grant of bulk-source permission. Keep all raw and game/player-level outputs outside Git.

## Structured-source expansion evidence

`College_Baseball_Source_Expansion_Evidence.zip` (about 12.1 MB) retains 117 responses with URL/UTC-retrieval/SHA-256 metadata: two schedules, two cumulative pages, 112 season boxes, and the excluded Missouri State–Drury fall exhibition box. It also contains the complete derived audit. It supplements the earlier checkpoints; no raw/player/game exports belong in Git.

SHA-256:

```text
33fb20a46b46c81cc372865aa28baec8e51701b89d72b9803c2bcf3ae7973a6f
```

Restore the original baseline and use the exact-hash recovery command below. This supplied archive is truncated within its final `audit.json` and lacks a ZIP central directory. All 234 raw/metadata members are complete; the recovery script verifies ZIP CRCs and source SHA-256 values before writing. The original attachment is preserved, and the partial derived audit is discarded and rebuilt:

```sh
sha256sum /absolute/path/to/College_Baseball_Source_Expansion_Evidence.zip
python3 scripts/restore_source_expansion.py /absolute/path/to/College_Baseball_Source_Expansion_Evidence.zip /tmp/baseball-source-expansion
python3 scripts/audit_player_source_expansion.py --raw-dir /tmp/baseball-source-expansion/raw --output /tmp/source-expansion-rerun.json
python3 scripts/test_player_source_expansion.py
```

The audit verifies hashes, historical payload paths, season labels, game identities, participation flags and mapped player counts. Inspect `comparisons`, per-game `issues`, and mode-specific completeness. The original audit retains Davidson's batting-list omission and Missouri State's May 24/25 date conflict. Separate exception annotations below resolve only the result-date join; they never overwrite this audit. Cumulative season values are audit targets only. [Coverage report](Historical_Player_Data_Coverage.md#structured-source-expansion-davidson-2024-and-missouri-state-2022) owns detailed findings.

`historical/player_sources.json` is source configuration, not raw data. Its four entries retain original season/conference identity and parser families. The optional `python3 scripts/collect_player_source_expansion.py --evidence-dir /tmp/new-source-expansion` command collects only the two reviewed embedded-SIDEARM entries, one request per host, caching failures without automatic retries. A fresh collection is a new snapshot; it does not establish bulk permission. The prior LSU/Towson collector and checkpoint remain separate and reproducible.

## Full-field source map and exception evidence

`College_Baseball_Field_Source_Evidence.zip` retains the new bounded discovery responses, failed-request metadata, full-field availability audit and separate exception annotations. It also contains all 117 recovered source-expansion responses/metadata plus the rebuilt expansion audit, so the truncated prior ZIP is not needed to read those bytes. Keep the original baseline, timing/seed and season-appearance checkpoints. No raw evidence belongs in Git.

SHA-256: `37eccf733470e236ae5a5d721c19b256db43e7a30b20999aae004941f99216cd`.

After restoring the baseline and timing/seed checkpoints, verify that hash and extract into a fresh directory. Restore the season-appearance checkpoint as above; use repository code:

```sh
python3 -m zipfile -e /absolute/path/to/College_Baseball_Field_Source_Evidence.zip /tmp/baseball-field
python3 scripts/audit_player_source_expansion.py --raw-dir /tmp/baseball-field/expansion/raw --output /tmp/expansion-rebuilt.json
python3 scripts/audit_player_exceptions.py --original-audit /tmp/baseball-field/expansion/audit.json --raw-dir /tmp/baseball-field/field/raw --output /tmp/exceptions-rebuilt.json
cmp /tmp/exceptions-rebuilt.json /tmp/baseball-field/field/exception_annotations.json
python3 scripts/test_tournament_sources.py
```

These commands are offline. Adding reviewed archive entries changes the expansion audit’s registry fingerprint; all original player/game findings are unchanged. Compare the current expansion output against the conference-archive checkpoint below; the prior archived audit remains intact. The original 59-schedule source map is retained as historical evidence; current repository code/registry use the follow-up checkpoint below for the expanded map. The registry lists exact tested URLs and retains failures; it is not a national downloader or a permission grant. No collection command is added for the full field. The [source map](Tournament_Source_Availability_2025.md) owns access/coverage limits. The exception annotations preserve original records and unknown work dates. The original strict audit remains reproducible; there is no baseline correction.

## Access and parser follow-up evidence

`College_Baseball_Access_Parser_Evidence.zip` contains the prior field-map raw directory plus bounded follow-up responses: Vanderbilt/Arkansas historical schedules and robots files, Clemson’s separate StatCrew index/cumulative page and missing robots response, another failed DBU robots check, and rechecked SIDEARM terms. It includes the rebuilt 62-schedule map and offline collection-volume plan. No season box sweep occurred. It supersedes only the source-map raw directory/output, not the field checkpoint’s exception/expansion evidence or the baseline.

SHA-256: `54cf90c2b0fd357a2bb07db6fe1c399f0a48647d64b462dd70d2772d806e5285`.

This checkpoint preserves the 62-schedule intermediate snapshot. Current code/registry reproduction uses the conference-archive checkpoint below. To inspect the retained intermediate evidence, verify the hash and extract to a fresh directory:

```sh
sha256sum /absolute/path/to/College_Baseball_Access_Parser_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Access_Parser_Evidence.zip /tmp/baseball-access-followup
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m unittest discover -s historical -p 'test_*.py'
```

Source URL, retrieval time, bytes/hash and failed-request metadata remain preserved. The WMT link classifications derive entirely from previously retained bytes; destination pages were not fetched. Murray State’s mixed-year row remains a gap; Clemson cumulative qualification now uses the conference-archive audit below. The plan counts known D1 games by the existing cutoff rules, keeps all 64 teams, and never enables collection or converts unknown workload into rest. Findings and access constraints belong in the [field report](Tournament_Source_Availability_2025.md).

## Conference archive qualification evidence

`College_Baseball_Conference_Archive_Evidence.zip` contains the prior access/source-map raw directory plus bounded OVC, Conference USA, WMT access/discovery responses, one Clemson box and Florida State’s independent suspension recap. Includes current field, StatCrew archive, access and collection-plan audits, plus the expansion audit with its updated registry fingerprint. No full-season box sweep occurred. Keep the baseline, timing/seed, season-appearance and field/expansion checkpoints for their distinct inputs. This ZIP supersedes the access checkpoint’s source-map raw/output; it does not replace the other archives.

SHA-256: `3cc0765168b0ecc9ea74bef5ef5dcd20bcf505c496f71d452f89f779468a967f`.

After restoring baseline, timing/seed and season-appearance inputs, verify the hash and extract to a fresh directory. Use current repository code:

```sh
sha256sum /absolute/path/to/College_Baseball_Conference_Archive_Evidence.zip
python3 -m zipfile -e /absolute/path/to/College_Baseball_Conference_Archive_Evidence.zip /tmp/baseball-conference
python3 scripts/audit_tournament_sources.py --raw-dir /tmp/baseball-conference/raw --lsu-audit /tmp/baseball-season-appearances/audit.json --output /tmp/field_audit.json
cmp /tmp/field_audit.json /tmp/baseball-conference/field_audit.json
python3 scripts/audit_statcrew_archives.py --raw-dir /tmp/baseball-conference/raw --output /tmp/archive_audit.json
cmp /tmp/archive_audit.json /tmp/baseball-conference/archive_audit.json
python3 scripts/audit_source_access.py --raw-dir /tmp/baseball-conference/raw --output /tmp/access_audit.json
cmp /tmp/access_audit.json /tmp/baseball-conference/access_audit.json
python3 scripts/plan_tournament_collection.py --field-audit /tmp/field_audit.json --output /tmp/collection_plan.json
cmp /tmp/collection_plan.json /tmp/baseball-conference/collection_plan.json
python3 scripts/audit_player_source_expansion.py --raw-dir /tmp/baseball-field/expansion/raw --output /tmp/expansion_audit.json
cmp /tmp/expansion_audit.json /tmp/baseball-conference/expansion_audit.json
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m unittest discover -s historical -p 'test_*.py'
```

The [field report](Tournament_Source_Availability_2025.md#conference-alternatives-and-archive-qualification) owns findings and limitations. All 64 source entries remain unqualified for production features/fallback; only LSU has full core appearance reconciliation. StatCrew inventories and cumulative additive checks are not appearance-history certification. Clemson’s completion annotation is separate from the strict source row and assigns no pitcher work dates. WMT Games’ HTML robots response and CUSA’s default 2026 DBU schedule are retained failed-discovery evidence; the latter is rejected from historical qualification and all modeling.


## Offline scope, inventory and fallback checks

No new checkpoint is needed: these checks use the retained conference archive plus baseline and timing/seed inputs above. The season/field checkpoints remain necessary for their original appearance and exception audits. After restoration, use current repository code:

```sh
python3 scripts/audit_collection_scope.py --raw-dir /tmp/baseball-conference/raw --field-audit /tmp/baseball-conference/field_audit.json --output /tmp/collection_scope.json
python3 scripts/audit_retained_inventories.py --raw-dir /tmp/baseball-conference/raw --field-audit /tmp/baseball-conference/field_audit.json --output /tmp/inventory_audit.json
python3 scripts/audit_team_fallback.py --field-audit /tmp/baseball-conference/field_audit.json --output /tmp/fallback_audit.json
```

All commands are offline and leave baseline/v2 outputs unchanged. Outputs include source/input fingerprints; keep their game/matchup-level records outside Git. The fallback checks baseline gates, independent schedules, timing evidence and the NCAA field before comparing probabilities. It never uses season player totals as predictors. The [field report](Tournament_Source_Availability_2025.md#retained-source-expansion-and-team-only-fallback) owns results and remaining limitations. Tests remain runnable without the evidence bundles.

The nine additional schedule identity reviews can also be reproduced with the earlier access/parser checkpoint (hash above), whose retained pages contain all nine schedules. After restoring the baseline and extracting that checkpoint to `/tmp/baseball-access`:

```sh
python3 scripts/audit_retained_inventories.py --raw-dir /tmp/baseball-access/raw --field-audit /tmp/baseball-access/field_audit.json --output /tmp/inventory_audit.json
```

Expected summary: 11 reconciled, 21 unresolved joins, 16 parser/inventory gaps, 16 unsupported schedules. The output fingerprints the reviewed alias configuration as well as source and baseline inputs. This older field audit is sufficient for these inventory checks only; it does not reproduce the later full source/access map. No new raw checkpoint is required.

## Offline hitting-input pilot

Restore the baseline, season-appearance checkpoint and field checkpoint using the exact hashes above. No additional evidence archive or fresh downloads are needed. The field checkpoint supplies both structured boxes (`expansion/raw`) and independent timing evidence (`field/raw`). Run:

```sh
python3 scripts/extract_hitting_inputs.py \
  --season-raw-dir /tmp/baseball-season-appearances/raw \
  --expansion-raw-dir /tmp/baseball-field/expansion/raw \
  --exception-raw-dir /tmp/baseball-field/field/raw
python3 -m unittest discover -s scripts -p 'test_hitting_inputs.py'
```

Output: ignored `historical/model_inputs/hitting_inputs.json`. Custom JSON output paths are restricted to that directory to prevent overwriting sources/baseline inputs. The command verifies source bytes via the existing audits and records input/code fingerprints, source metadata, count checks and cutoff-specific game IDs/rates. Check each team's `full_season_check.pass_counts`, each mode's `complete` and `PA_complete`, and per-game issues; successful execution can report unqualified inputs. Failed checks never publish partial-season rates. Missouri State PA-based rates remain null. Cumulative totals are audit targets only; model and app outputs are untouched. Definitions, results and limits: [focused qualification](Model_Input_Qualification.md).

## Offline pitching-input pilot

Uses the same restored baseline and field checkpoint as the hitting pilot. No new downloads or evidence ZIP are needed:

```sh
python3 scripts/extract_pitching_inputs.py \
  --expansion-raw-dir /tmp/baseball-field/expansion/raw \
  --exception-raw-dir /tmp/baseball-field/field/raw
python3 -m unittest discover -s scripts -p 'test_pitching_inputs.py'
```

Output: ignored `historical/model_inputs/pitching_inputs.json`; custom outputs must also be JSON files under that directory. Check `full_season_pass`, per-mode `complete`, and per-game `BF_check`/`issues`. Source metadata, original timing annotations, scoped player names, raw appearance counts and input/code hashes are retained. Repeated runs are byte-identical. Missing pitch counts stay null; known-pitch subtotals are explicitly partial. Work dates/rest remain unknown. Results and role definitions belong in [qualification](Model_Input_Qualification.md#pitcher-bf-roles-and-workload-pilot). No model/app input is replaced.
