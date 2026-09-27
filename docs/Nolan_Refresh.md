# On-demand Nolan refresh

The refresh command imports a **bounded, separately versioned schedule snapshot**.
It does not overwrite historical evidence, update the app, fit models or substitute
partial schedules for the verified Elo inputs. This is the import/staging step of
fresh-data support; automatic nationwide ingestion and fresh-year bracket export
are not yet qualified.

## Use

From the repository root, after restoring the historical baseline:

```sh
python3 -m ingestion.nolan_refresh --season 2024 \
  --teams LSU Florida Tennessee --version my-refresh-001
```

One invocation accepts 1–8 exact roster slugs. It requests only those schedule URLs,
sequentially, with at least two seconds between request starts, a 30-second timeout
and a 5 MB response limit. No discovery crawl, paid service, provider contact,
D1Baseball request or automatic retry is performed. Redirects are not followed;
401/403/429 responses stop the batch. Successful HTTP access does not establish
permission for a nationwide collection volume.

The version name is immutable. Repeating the same command reuses saved pages and
failures without network access. Use a new version for a deliberately fresh attempt;
do not delete failed evidence to make a version retry. A partial interrupted write
may require a new version. Outputs are ignored under `ingestion/output/<version>/`:
source HTML/metadata, request/code fingerprints, observations, staged games,
exclusion reasons and summary.

Offline replay requires no network:

```sh
python3 -m ingestion.nolan_refresh --season 2024 \
  --teams LSU Florida Tennessee --version retained-replay-001 \
  --cached-raw historical/2024/raw
python3 -m unittest discover -s scripts -p 'test_nolan_refresh.py'
```

## Qualification and preservation

- Only existing reviewed season rosters and cutoffs are accepted (2021–2025).
  2026/future imports are disabled until a distinct roster/cutoff decision; no claim
  of an untouched 2026 holdout is allowed. The bounded live check used 2024.
- Exact requested season/team headings, source URLs and saved SHA-256 hashes are
  checked. Empty/changed formats and duplicate game IDs fail rather than silently
  replacing valid schedules. Roster identities are exact; no fuzzy merging.
- The parser is adapted from the preserved 2024 parser, without modifying it.
  Dates, scores, labels, timing warnings, original source fields and provenance
  remain available. Final source rankings/records are never model features.
- Every staged game needs two agreeing observations, including teams, scores,
  date and phase. Missing counterpart pages are reported, not silently accepted.
  Unscored/non-D1/unknown-opponent rows remain explicit exclusions.
- Existing regular-only and conference-inclusive phase lists and the two-day
  availability rule determine separate eligibility. NCAA outcomes never qualify
  as pre-NCAA inputs. Timing-review rows remain blocked. Historical date-only
  source data is not certified as published or complete at the forecast cutoff.
- Official supplements and v2 corrections are **not** automatically applied to
  changed source bytes. Their applicability must be checked during integration.
  No partial staged sample is passed to Elo; the app retains its verified snapshot.

## Verified September 27, 2026

A live three-page request for LSU, Florida and Tennessee 2024 succeeded: **207
schedule observations**, including two unscored rows, and **195 distinct completed
D1 game IDs**. Ten games have both sides inside the requested set. Nine qualify
regular-only; ten qualify conference-inclusive. The other 185 games lack the
counterpart page in this deliberately bounded batch. This is not missing national
history or a reason for another coverage audit; it is explicit partial-import scope.

All 207 normalized date/identity/status/score/phase/timing rows match the retained
snapshot and the legacy parser. Source bytes and retrieval timestamps are preserved
separately even where normalized results match. A mocked network prohibition proves
that a repeated live-version command makes no new requests; every output is
byte-identical. Existing baseline/v2 preservation gates pass. **252 data-free tests
pass** (185 scripts, 67 historical), including ten new import checks.

Source evidence: [DATA.md](DATA.md#versioned-nolan-refresh-evidence). No game-level
outputs or raw pages are committed. No model probabilities, app assets, previous
experiments or cutoffs changed; no 2026 collection or model scoring occurred.

## Next integration step

Connect a staged version to the existing Elo export through an explicit candidate
dataset adapter. Reuse verified unchanged history and corrections with their provenance;
report changed/conflicting/missing rows and preserve the original snapshot as fallback.
Verify full-field probabilities and both cutoff modes before changing the app's data.
Do not expand collection merely to finish this three-team sample, or label this
bounded importer as certified nationwide/fresh-year support.
