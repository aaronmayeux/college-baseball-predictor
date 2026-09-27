# Bounded HAVOC chronological experiment

## Protocol locked before collection and scoring

Use the eight participants in the first two regional names alphabetically per
season: Austin/Columbia (2021), Auburn/Austin (2022), Auburn/Baton Rouge (2023).
This 24-team-season convenience sample is selected by location name, not results
or HAVOC. It cannot establish national effectiveness. Do not replace unavailable
teams or enlarge the sample after viewing model scores.

Reconstruct conference-inclusive counts through the existing pre-NCAA cutoff
and two-calendar-day availability rule. Collect public D1Baseball Overall final
batting tables and schedule-linked official boxes for every excluded game.
Retain source bytes/captures, URLs, retrieval times and hashes. Verify identities,
season, complete table schemas, player totals, both game scores and complete
excluded-game inventory. Final totals alone never qualify. Disclose non-D1 scope
and count discrepancies. Require matching final game counts; final run differences
up to ten remain flagged and uncorrected, with a fixed sensitivity routing flagged
pairs to Elo. Larger run differences, unresolved scope or missing subtraction mean fallback.
Keep source windows identical for every HAVOC numerator and denominator.

Compare exactly two separate additions to unchanged conference-inclusive Elo:
`(2*SB+BB+HBP)/batting_K` and `(2*(SB-CS)+BB+HBP)/batting_K`.
Fit 2021–2022 only with training RMS difference scaling, no intercept, fixed Elo
log-odds offset and ridge 0.01. Select on already-exposed 2023 only. Require at
least 16 covered training games, at least 4 from each training year, and 8 covered
selection games; otherwise report insufficient data and do not fit. No tuning,
combination, sign reversal or alternative formula after results.

Report identical full-field NCAA samples with exact pairwise Elo fallback plus
covered-only comparisons: log loss, Brier, calibration and secondary accuracy.
A candidate passes this preliminary screen only if both 2023 probability scores
improve; order qualifying candidates by log loss, Brier, name. Lock sources and
coverage before fitting and selection before any later scoring. No 2024/2025/2026
candidate scoring or app promotion in this bounded first test. A positive screen
requires a separately locked later-season and advancement assessment; a negative
screen stops this specification. Preserve prior candidates and app outputs.

## Results

**Blocked before fitting; both formulas remain untested.** Fourteen complete final
batting captures were retained (eight 2021, six 2022). The bounded collection reached
2023 but D1Baseball repeatedly presented Cloudflare browser verification. One ordinary
reload recovered an earlier page; collection stopped when verification returned.
No paywall, authentication or security control was bypassed. Incidental current-year
navigation was excluded; no 2026 inputs entered preparation or fitting.

Twenty-nine distinct linked official box URLs were requested once and cached:
16 returned HTTP 200, nine returned 404 and four returned certificate-related 502
responses. Successful HTTP access alone does not qualify a box. Unsupported legacy
formats, missing links and failed responses remain explicit exclusions. No broad
coverage audit or replacement-team search was performed.

**Two additional teams now have complete verified pre-NCAA counts:**

| 2022 team | Final → eligible games | BB | HBP | Batting K | SB | CS | Original HAVOC | Net-steals HAVOC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Louisiana Tech | 64 → 61 | 270 | 99 | 516 | 62 | 18 | 0.955426 | 0.885659 |
| Texas | 69 → 61 | 288 | 70 | 484 | 47 | 15 | 0.933884 | 0.871901 |

Both include conference tournaments through May 29, before the June 1 cutoff under
the existing two-day rule. Their full game counts and runs agree with retained Nolan
results. Ten distinct verified boxes cover their eleven excluded team-game appearances;
their shared regional box is reused. Both teams' dates, identities, scores and batting
player sums are checked in every subtraction. These are input values, not predictions.
The earlier Virginia 2023 pilot remains separately preserved and outside this locked sample.

| Season | Complete final tables | Reconstructed eligible teams | Covered NCAA games | Elo fallback games |
|---|---:|---:|---:|---:|
| 2021 training | 8/8 | 0/8 | 0/139 | 139 |
| 2022 training | 6/8 | 2/8 | 1/141 | 140 |
| 2023 selection | 0/8 | 0/8 | 0/137 | 137 |

The chronological minimum fails before either coefficient is fitted or any candidate
score is computed. This is **missing evidence, not a failed predictive hypothesis**.
No winner comparison, advancement claim or app promotion is justified. All 64 bracket
teams and existing Elo/app outputs remain intact.

Small final run discrepancies remain uncorrected flags: Fairfield 2021 −9, Old Dominion
2021 −1, DBU 2022 −1 and UCLA 2022 −3. Southern 2021 +11 exceeds the locked tolerance.
None of these teams qualifies yet because complete verified subtraction is also missing.
Full per-team reasons, missing game IDs, source hashes and failed captures are retained
in the separate evidence checkpoint, not duplicated in Git.

## Verification and continuation

Twenty-one focused data-free tests pass, covering the original pilot plus new identity,
season/split, loading/blank-cell parsing, count validation, cutoff/non-D1 handling,
both-sided box verification, hashes, exact Elo fallback, chronological fitting,
immutable locks, both candidate evaluation paths and refusal to fit an inadequate sample.
The real blocked report and prepared inputs reproduce byte-for-byte. Baseline/v2 gates
pass; earlier model code and app files are unchanged.

Restore the new checkpoint and baseline/v2 per [DATA.md](DATA.md). Continue only the
same 24-team-season sample: recover missing D1 captures when access permits and obtain
working official evidence for the named missing exclusions. Reuse cached successes;
do not automatically retry failures, replace teams or enlarge the sample. Then rerun
qualification and, only when its chronological minimum passes, compare both formulas.
The failed session is a checkpoint, not completion of the requested model test.
