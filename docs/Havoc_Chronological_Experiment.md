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

**Blocked before fitting; both formulas remain untested.** All 24 final Overall
batting tables are now retained. Twelve team-seasons have complete verified
pre-NCAA subtractions, up from two in the original checkpoint:

| Season | Complete final tables | Eligible teams | Covered NCAA games | Elo fallback games |
|---|---:|---|---:|---:|
| 2021 training | 8/8 | Arizona State, Fairfield, Texas | 4/139 | 135 |
| 2022 training | 8/8 | Air Force, Dallas Baptist, Florida State, Louisiana Tech, Southeastern Louisiana, Texas | 6/141 | 135 |
| 2023 selection | 8/8 | Auburn, Penn, Samford | 2/137 | 135 |

Training has 10 of the required 16 covered games, with at least four in each year.
Selection has two of eight. No coefficient, candidate score, winner or promotion
was produced. This is missing evidence, not a rejected predictive hypothesis.
Elo, all 64 bracket teams, prior models and app outputs remain unchanged.

The fixed sample now retains 88 official HTTP responses: 45 status 200, 19 status
404, 14 transport failures, six 403 and four 502. Successful access alone does not
qualify a box. Additional browser DOM captures preserve document titles, team
headings and complete batting tables; they do not claim an observed HTTP status.
Empty/truncated extraction attempts are retained separately. The latest browser
attempt showed a box score but failed DOM extraction and click dispatch, so it
was not admitted. No security control was bypassed or failed URL automatically retried.

The parser now recognizes legacy composite-table team captions. Supplemental
official links retain discovery provenance and are restricted to already-needed
excluded game IDs. Original failed responses stay intact; rendered sources are
separate. Both-sided identity, exact date, score, required columns, player sums and
body hashes remain mandatory. Conflicting valid HTTP/rendered counts fail preparation.
No absent steal, caught-stealing or hit-by-pitch count is inferred as zero.

Small final-run discrepancies remain flags, including eligible Fairfield 2021 −9
and Dallas Baptist 2022 −1. Southern 2021 +11 remains ineligible under the unchanged
tolerance. Other incomplete teams' flags and every unresolved game ID remain in
the evidence report. No source total or game date was silently corrected.

## Verification and continuation

23 focused data-free tests pass, including caption identity, rendered provenance,
failed-HTTP fallback, conflicting sources, exact dates, hashes, player sums, immutable
locks, exact Elo fallback and the two chronological evaluation paths. Real preparation
and report repeat byte-for-byte; baseline/v2 preservation gates pass. All original
checkpoint files were verified unchanged against their original manifest.

[DATA.md](DATA.md) owns restoration and checkpoint identity. The original output is
preserved; the resumed run is `output/bounded-v2`. Use the same 24-team-season sample.
The shortest evidenced continuation is six excluded games:

| Game ID | Required evidence | Remaining issue |
|---|---|---|
| wn:2022:42130 | Auburn–UCLA regional final | Complete table and documented June 5 start / June 6 completion reconciliation |
| wn:2022:44006 | Auburn–Stanford, June 20 | Complete batting table; replacement page lacks usable counts |
| wn:2022:44009 | Arkansas–Auburn, June 21 | Retained legacy box lacks supported explicit SB/CS columns |
| wn:2023:46020 | Southern Miss–Tennessee opener | Complete rendered table; saved extraction was empty |
| wn:2023:45018 | Sam Houston–Tulane | Complete table and documented June 3 start / June 4 completion reconciliation |
| wn:2023:45022 | Oregon State–Sam Houston, June 4 | Complete rendered table; saved extraction was empty |

If these qualify under unchanged checks, Auburn/UCLA 2022 and Southern Miss,
Sam Houston/Tulane 2023 can supply the missing coverage. This is a collection
priority, not permission to relax dates or counts. The full report retains other
fixed-sample exclusions. Do not replace teams, launch a broad audit, fit below the
minimum, or score later years. Reuse saved successes and explicit source links.
