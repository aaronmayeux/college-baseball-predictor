# Frozen batting candidates — 2025 development confirmation

## Locked protocol — before scoring

Confirm Guillen (`1.6*HR/R`) and offensive walk rate (`BB/(AB+BB+HBP+SF+SH)`)
separately against conference-inclusive neutral Elo. This is exposed 2025 development,
not untouched validation. No fitting, combinations, threshold search, 2024 retuning,
2026 use or automatic deployment. Elo remains in both app modes.

Use the original 2021–2023 final models, with full precision frozen in code:

| Candidate | Matchup RMS scale | Coefficient | Training games |
|---|---:|---:|---:|
| Guillen | 0.10032947177598207 | 0.25322391361463914 | 403 |
| Walk rate | 0.022077761145654972 | 0.16776241190324512 | 403 |

Guillen matches the retained selection lock (SHA-256
`241329828e0c9f9bf9cddfa0cc86384c5dcfb9998d89b7f5b259eaf0f1c04884`).
Walk's full precision was reproduced using only the original 2021–2023 prepared
sample and unchanged fitting function; no 2024/2025 observation enters that recovery.
Both equal the coefficients previously reported to ten decimals.

Bounded acquisition: one free NCAA 2025 menu and its latest eligible non-final
OBP, ERA, HR and runs reports. IDs must come from the menu; cache requests,
failures, exact forms, UTC times and hashes. No school sweep. May 25 is the selected
through-date; the cutoff is May 28 at 12:00 UTC with the unchanged two-day delay.
Keep all-opponent NCAA scope alongside D1 Elo and label these reconstructed snapshots.
Publication timing is not certified.

Apply original component qualification: exact/reviewed identities, matching OBP/ERA
records, valid counts/rates, at least 20 games, snapshot age 2–14 days, record
difference at most two and runs-allowed difference at most ten. Guillen also needs
matching HR/run/batting records and runs-scored difference at most ten. Retain
small discrepancies, known non-D1 games and omitted eligible games as flags;
never repair source counts. Invalid/missing features give exact Elo for the whole
matchup. Freeze all 64 teams and regional forecasts before scoring outcomes.

Report each candidate's full, covered and fallback game samples, stage/regional
breakdowns, log loss, Brier, calibration and secondary picks against identical Elo
and seed samples. Use the exact four-team engine, legal regional result paths and
super-field reconciliation. Report regional champion log loss, summed four-class
Brier, picks, calibration and 5,000 paired regional bootstrap draws (seed 20240926).
The fixed sensitivity sends every flagged matchup to Elo; no new sensitivity fitting.
A candidate passes the probability screen only if both game and regional scores
improve. Any unexplained stage/sensitivity regressions remain deployment concerns;
passing is not promotion. No improvement claim if all features fall back.

## Results

**Neither frozen candidate passed; keep Elo.** No post-result retuning or deployment.
All four national reports parsed. Walk rate qualifies all 64 teams/136 games;
Guillen qualifies 63 teams/134 games. Bethune-Cookman's runs-scored discrepancy
is −11, beyond the existing ten-run limit; its two games receive exact Elo.
All team records reconcile; small runs-allowed differences affect five teams.
Twelve Guillen teams and seven walk-rate teams have at least one flag, including
known non-D1 games. No eligible D1 game is omitted by the May 25 snapshot.

Lower probability scores are better. Picks include fractional seed ties.

| Model | Game log loss | Game Brier | Correct /136 | Regional log loss | Regional Brier | Champions /16 |
|---|---:|---:|---:|---:|---:|---:|
| Elo | 0.660978 | 0.233853 | 86 | 1.132374 | 0.633688 | 7 |
| Guillen | 0.672018 | 0.238461 | 88 | 1.208696 | 0.669473 | 8 |
| Walk rate | 0.670583 | 0.237120 | 84 | 1.132127 | 0.633723 | 9 |
| Seed benchmark | 0.658747 | 0.228176 | 89.5 | 1.131484 | 0.613595 | 9 |

On Guillen's 134 covered games, log loss/Brier are 0.676973/0.240767 versus
Elo 0.665768/0.236090. Its two fallback predictions equal Elo exactly.
Walk rate has no primary fallback games. Both candidates worsen game log loss
and Brier in regionals, supers and Omaha; their two-game final-series gains do
not compensate. Better Guillen winner picks do not imply better probabilities.

The fixed flagged-to-Elo sensitivity retains worse aggregate game scores for
both: Guillen 0.665177/0.235729; walk rate 0.667030/0.235566. Guillen also
worsens both regional scores. Walk's sensitivity slightly improves both regional
scores (1.132357/0.632946), but still fails the game check. No sensitivity promoted.

Exploratory 95% paired regional bootstrap intervals for candidate-minus-Elo:

| Candidate | Log-loss interval | Brier interval |
|---|---:|---:|
| Guillen | [−0.024823, 0.182329] | [−0.028652, 0.105092] |
| Walk rate | [−0.072893, 0.068567] | [−0.045616, 0.040489] |

Both cross zero. One exposed season and 16 regional clusters cannot establish
future performance. These fixed candidates failed confirmation; preserve their
2024 results as historical findings, without promoting or retuning them on 2025.

## Verification and reproduction

Six new data-free tests cover frozen models, symmetry, exact missing/flagged Elo
fallback, stale locks, source tampering, snapshot timing and invalid denominators.
Existing Guillen/walk/engine tests also pass. Real preparation and evaluation repeat
byte-for-byte. All 16 regional paths match the super field; 272 observed/hypothetical
probability checks per candidate pass. Baseline/v2 input preservation gates pass.
The evidence retains full source provenance, features, calibration, stage/regional
breakdowns and predictions; no raw data or game exports are committed.

Restore baseline/v2 and the separate archive in [DATA.md](DATA.md), then run:

```sh
python3 historical/batting_confirmation.py prepare --raw-dir /absolute/evidence/raw
python3 historical/batting_confirmation.py evaluate --raw-dir /absolute/evidence/raw
python3 -m unittest discover -s historical -p 'test_batting_confirmation.py'
```

`collect` is explicit and bounded; matching cached requests make no network calls.
Changed source/code/protocol rejects the old lock. Outputs are ignored under
`historical/batting_confirmation_output/`. App forecasts and both modes are unchanged.
