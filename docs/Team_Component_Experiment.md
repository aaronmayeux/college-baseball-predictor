# Practical OBP/ERA experiment

## Locked protocol — before scoring

Conference-inclusive only; preserve Elo, both app modes and the closed net-run candidate.
Use retained NCAA all-opponent OBP/ERA through May 23, 2021; May 25, 2022;
May 28, 2023; May 26, 2024. Dates must pass the recorded two-day availability
assumption and precede NCAA games. These are retrospective reports, not certified
publication-time snapshots. No 2025 or 2026 candidate evaluation.

Train on 2021–2022 NCAA matchups; select on 2023; refit the selected specification
on 2021–2023; evaluate once on previously exposed 2024. All results are development/
retrospective evidence. Three candidates: OBP, negative ERA, both. Use exact count-derived
rates, differences between opponents, training-only RMS scaling, fixed Elo log-odds
offset, no intercept, ridge 0.01 per coefficient. No hyperparameter search. Select only
if both log loss and Brier improve on identical 2023 games; break ties by log loss,
Brier, then name. Otherwise select Elo. Persist selection before 2024 scoring.

Input inclusion: explicit identity, non-reclassifying row, valid rate/count arithmetic,
matching batting/pitching records, at least 20 source games, snapshot at most 14 days
old at cutoff, no included NCAA/future/ineligible D1 games. Keep missing/invalid inputs
on exact Elo fallback for the entire matchup; never insert zero stats. Relative to
D1 plus retained non-D1 results through the snapshot, allow up to two games/wins/losses/
ties and ten runs discrepancy. Larger unexplained discrepancies use fallback. This
practical bound is fixed before scoring, not proof every difference is harmless.
Count eligible games omitted after the snapshot and disclose all-opponent scope.
2021 participant identities are retrospective; no seed claim is made for that year.

Report common full-field and feature-covered game metrics, seed comparator where
available, calibration bins, stage and regional-group differences, coverage and all
fallback reasons. Sensitivity (no reselection): (1) Elo fallback on any matchup with
record/run discrepancy, known non-D1 input, or omitted eligible games; (2) fit the
same selected candidate without 2021, to examine older-snapshot dependence. These
are diagnostics, not alternate models eligible for promotion.

For 2023/2024, enumerate regional advancement with the existing exact engine, opening
1–4 and 2–3. Freeze probabilities before scoring; reuse validated historical result-path
checks and require champions to match the super-regional field. Report champion log
loss, four-class summed Brier, top-pick accuracy, calibration and paired regional
bootstrap (5,000 draws; seed 20240926), exploratory within-season only. Promotion
requires improvement in both 2024 game and advancement probability scores, no material
unexplained stage/sensitivity regression, and a separate reviewed deployment step.
No automatic app change; one correlated validation season cannot certify future gains.

## Reproduction

Restore baseline and v2 per [DATA](DATA.md), plus the combined NCAA archive checkpoint.
From repository root:

```sh
python3 historical/team_components.py prepare --evidence-dir /absolute/path/to/ncaa
python3 historical/team_components.py evaluate --evidence-dir /absolute/path/to/ncaa
```

Outputs and locks are ignored under `historical/team_component_output/`. No downloads,
raw data, game exports or model changes to the app are committed.

## Results — September 26, 2026

**Completed; retain Elo.** The combined OBP/ERA model won 2023 selection but failed
2024 game and regional-advancement comparisons. Close this raw-rate specification
without promotion or 2024 retuning. This does not establish that all batting/pitching
models fail; it tests these unadjusted all-opponent rates added to D1 Elo.

### Usable inputs and retained gaps

| Season | Snapshot age at cutoff | Usable teams | Feature-covered NCAA games | Elo-fallback games | Eligible games omitted per team |
|---|---:|---:|---:|---:|---:|
| 2021 | 10 days | 60/64 | 127/139 | 12 | 0–6 |
| 2022 | 7 days | 63/64 | 139/141 | 2 | 0–6 |
| 2023 | 3 days | 64/64 | 137/137 | 0 | 0 |
| 2024 | 3 days | 64/64 | 133/133 | 0 | 0 |

2021 fallback identities: South Florida, Southern, Norfolk State, Presbyterian College.
2022: Alabama State. These are unresolved exact report-name mappings, not proof that
NCAA lacks their rows. No fuzzy join or further school collection was attempted.
All 64 teams remain represented in every season. 2021/2022 omit eligible late games
for 62/60 teams. Retained non-D1 games affect 4/2/4/4 teams by year.

Small count discrepancies were **included**, not treated as blockers: four 2021 teams
have a one-run difference; 2022 has none among mapped rows. In 2023 Santa Clara has
−5 runs, Washington −9 runs, and Eastern Illinois +1 game/+1 win relative to the
retained comparison. The five previously documented 2024 differences remain unchanged
([source report](Team_Component_Source_Decision.md#2024-tournament-field-reconciliation)).
No counts were repaired, games invented or final-season totals substituted. Source
hashes, dates, team reasons, differences and omitted game IDs remain in ignored outputs.

### Selection and fitted model

Training uses 266 covered 2021–2022 matchups. All 137 2023 games are common to each comparison.

| 2023 selection model | Log loss ↓ | Brier ↓ | Correct winners |
|---|---:|---:|---:|
| Conference-inclusive Elo | 0.628158 | 0.218569 | 91/137 |
| Elo + OBP | 0.627307 | 0.218164 | 92/137 |
| Elo + ERA | 0.616261 | 0.213243 | 94/137 |
| Elo + OBP and ERA — selected | 0.615965 | 0.213107 | 94/137 |

Refit on 403 covered 2021–2023 matchups: OBP coefficient 0.1033892917 with RMS
0.0263141771; negative ERA coefficient 0.2398353845 with RMS 1.1568685177. These
multiply scaled matchup differences on top of Elo log odds; no Elo coefficient,
intercept or candidate threshold is tuned. The selection lock was written before
2024 candidate scoring; the regional forecast lock precedes advancement scoring.

### 2024 retrospective evaluation

| Game model, same 133 NCAA games | Log loss ↓ | Brier ↓ | Correct winners |
|---|---:|---:|---:|
| Conference-inclusive Elo | 0.620988 | 0.215786 | 89/133 |
| Elo + OBP and ERA | 0.630395 | 0.221404 | 88/133 |
| Fixed regional-seed benchmark | 0.660503 | 0.229979 | 65.4%* |

*Seed accuracy gives half credit to exact 50/50 predictions, as in the preserved benchmark.
The candidate worsens log loss by **0.009407** and Brier by **0.005618**. Regional-game
loss/Brier worsen by 0.013296/0.007680 (100 games); supers worsen by 0.029224/0.014057
(18). Omaha improves by −0.050245/−0.022762 (12), insufficient to offset the regressions.
The three championship games change little. Detailed calibration bins, stage metrics,
common covered/fallback samples and regional-group game differences are reproduced.

| Regional advancement, same 16 regionals | Champion log loss ↓ | Multiclass Brier ↓ | Champions picked |
|---|---:|---:|---:|
| Elo | 1.157268 | 0.636643 | 10/16 |
| Elo + OBP and ERA | 1.284373 | 0.683499 | 9/16 |
| Seed benchmark | 1.429963 | 0.637239 | 10/16 |

Only 6/16 regional groups improve either advancement probability score. Candidate-minus-Elo
exploratory 95% paired-regional intervals are **[−0.014139, +0.274212]** for log loss and
**[−0.020333, +0.114965]** for Brier. These include zero and are not future-season confidence
intervals. 2023 selection-exposed advancement improves (log loss 1.065144 → 0.971002;
Brier 0.598209 → 0.544431; both pick 9/16), but does not override the later failure.

### Sensitivity and verification

| 2024 diagnostic | Game log-loss delta | Game Brier delta | Advancement log-loss delta | Advancement Brier delta |
|---|---:|---:|---:|---:|
| Primary | +0.009407 | +0.005618 | +0.127105 | +0.046856 |
| Flagged matchups use Elo | +0.008206 | +0.004657 | +0.108935 | +0.039695 |
| Same specification fitted without 2021 | +0.010349 | +0.006490 | +0.149271 | +0.035492 |

Positive means worse than matching Elo. Strict fallback changes 21/133 games in 2024
(and 16/137 in 2023). Its `covered` subset means source availability, not whether the
sensitivity actually applies an adjustment. Excluding 2021 from fitting retains the
older 2022 snapshot, so it is not a complete snapshot-age control. Neither diagnostic
reverses the 2024 conclusion. The flagged rows are therefore not a persuasive reason
to postpone the decision for a coverage cleanup. Unobserved common source errors and
opponent/park confounding remain possible; these checks do not prove gaps harmless.

**230 data-free tests pass** (175 scripts, 55 historical; seven new experiment tests).
The baseline/v2 rebuild succeeds. Preparation, selection, regional forecasts, predictions
and report reproduce byte-for-byte. All 270 observed 2023/2024 probabilities agree with
the hypothetical pairing implementation; 32 regional result paths qualify and their
champions match the super-regional fields. Source/protected-input hashes remain unchanged
during the experiment. The app and both Elo modes are unchanged; no 2025 candidate or
2026 modeling occurred. No new downloads, paid services or evidence archives were needed.

Next: a separately locked, bounded test of **schedule-adjusted team components**, using
the retained opponents/Elo histories to address a plausible weakness of raw all-opponent
rates. Define that adjustment and a chronological development comparison before fitting;
2024 is already exposed and must not become a new holdout or tuning success claim.
Reuse these inputs and fallbacks; no broad source audit or individual-pitcher work.
