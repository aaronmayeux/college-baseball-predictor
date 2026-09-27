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

**Both formulas failed the locked 2023 selection screen; this specification is
closed without promotion.** All six priority exclusions are complete. Seventeen
of the fixed 24 team-seasons qualify. Neither the sample nor the minimum changed.

| Season | Final tables | Eligible teams | Covered NCAA games | Elo fallback |
|---|---:|---|---:|---:|
| 2021 training | 8/8 | Arizona State, Fairfield, Texas | 4/139 | 135 |
| 2022 training | 8/8 | All eight locked teams | 12/141 | 129 |
| 2023 selection | 8/8 | Auburn, Penn, Sam Houston, Samford, Southern Miss, Tulane | 8/137 | 129 |

The 16 training games meet the four-per-year requirement; selection meets eight.
Fit uses only 2021–2022. Training RMS scales are 0.306026656 (original) and
0.270956655 (net steals); fitted coefficients are −0.500097894 and −0.352623772.
Those signs are fitted results, not a causal claim or permission to reverse signs.
2023 is previously exposed retrospective selection, not an untouched holdout.

### 2023 common-sample comparisons

Lower log loss and Brier are better. Every unsupported pair uses the exact original
Elo probability. Full-field accuracy is 91/137 for all three methods.

| Method | Full-field log loss | Full-field Brier | Covered log loss | Covered Brier | Covered winners |
|---|---:|---:|---:|---:|---:|
| Elo | 0.628158 | 0.218569 | 0.610390 | 0.209997 | 5/8 |
| Elo + original HAVOC | 0.632914 | 0.220862 | 0.691837 | 0.249261 | 5/8 |
| Elo + net-steals HAVOC | 0.631495 | 0.220160 | 0.667539 | 0.237236 | 5/8 |

Original HAVOC worsens full-field loss/Brier by +0.004756/+0.002293;
net steals worsens them by +0.003337/+0.001591. Routing flagged selection pairs
to Elo gives identical results because none of the eight covered selection games
has a flagged input. Training retains the predeclared small discrepancies,
including Fairfield 2021, Dallas Baptist 2022 and UCLA 2022; no totals were repaired.
Calibration bins for full-field, covered and fixed-sensitivity comparisons are
retained in the reproducible report. Eight selection games are too few to establish
national effectiveness or stable calibration. No later-year scoring, advancement
test, app promotion, sign reversal, combination or post-result tuning was performed.

## Completed evidence and safeguards

The six completed game IDs are wn:2022:42130, wn:2022:44006, wn:2022:44009,
wn:2023:46020, wn:2023:45018 and wn:2023:45022. Original failed HTTP and DOM
attempts remain intact; no unavailable value became zero.

Three games—not the two previously identified—have official start dates one day
before Nolan's completion dates. Reviewed official recaps bind exact identities,
scores, original game rows, source URLs and hashes:

| Game | Box start | Completion | Official completion evidence |
|---|---|---|---|
| Auburn–UCLA | 2022-06-05 | 2022-06-06 | [UCLA recap](https://uclabruins.com/news/2022/6/6/baseball-ucla-falls-to-auburn-11-4-in-regional-final) |
| Sam Houston–Tulane | 2023-06-03 | 2023-06-04 | [Tulane recap](https://tulanegreenwave.com/news/2023/6/4/baseball-green-wave-bearkats-halted-in-seventh) |
| Southern Miss–Tennessee | 2023-06-10 | 2023-06-11 | [Tennessee recap](https://utsports.com/news/2023/6/11/baseball-vols-battle-back-but-fall-short-in-super-regional-opener-at-southern-miss) |

The adapter accepts reviewed start dates only for these bound exclusions, wholly
after the forecast cutoff, with a one-day start/completion difference. Original
Nolan dates, outcomes, cutoff rules and Elo inputs are unchanged. Unreviewed boxes
still require an exact date match.

Auburn's current official pages embed WMT composite tables with explicit SB/CS/HBP.
Their composite SO column contains pitching strikeouts, despite its batting-table
placement. The adapter therefore joins explicit K from the separate Hitting view
by exact player name. Both views must agree on every player's AB/R/H/BB, each
used column must sum to its published total, and opposing pitching totals must
match AB/R/H/BB/K/HBP. Composite SO is preserved but never used as batting K.
Official embedding URLs and both original DOM views are retained and hash-bound.
The other three exclusions use complete Sidearm composite tables, with explicit
zeros and verified player totals. Supplemental links are stored separately from
the earlier checkpoint registry.

## Verification and disposition

28 focused data-free tests pass, including WMT batting-versus-pitching strikeouts,
player joins, schema/sum conflicts, provenance, date-review tampering, original
cutoff exclusion, chronological gates and exact fallback. Real prepare/evaluate
runs repeat byte-for-byte. All earlier checkpoint files remain byte-identical;
baseline/v2 preservation gates pass. Code fingerprints now include the adapter.

[DATA.md](DATA.md) owns checkpoint restoration. Current output is
`output/bounded-v3-final`, including the locked selection result; earlier outputs
are preserved. Stop this specification after its failed screen. The next model
work is separate locked 2025 development confirmation of the already-promising
Guillen and walk-rate candidates, without refitting or combining them. Elo remains
the deployed model; no further broad HAVOC collection is required.
