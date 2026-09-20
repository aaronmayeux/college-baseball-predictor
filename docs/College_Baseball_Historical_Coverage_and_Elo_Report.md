# College Baseball Predictor — Historical Coverage and Elo Baseline

> Preserved v1 baseline report. Timing exclusions are resolved only in the separate [v2 validation](Timing_and_Seed_Validation.md); the results below remain unchanged.
Historical analysis checkpoint. Repository setup is recorded in the current project brief and SESSION_LOG.md.

Prepared September 20, 2026. Reproducible research pilot; no interface or deployment.

## Outcome

Collected and reconciled **32,197 completed D1 games from 2021–2024**, extending the recovered 2025 audit to **40,615 games**. All 1,520 provider team-season records reconcile after documented source corrections. There are 310 stable internal team identities. Three 2023 games are official-school supplements; they are not two independent provider observations. Two other 2023 games are quarantined from modeling because their dates conflict across sources.

A fixed chronological Elo baseline passed the pipeline's coverage and eligibility gates. With strength frozen before NCAA tournament play, it selected **68.9% of winners across 411 NCAA games in 2022–2024**, versus **61.9%** for a smoothed prior-results win-rate benchmark. In 2025 development data it selected **63.2%**, versus **59.2%**. These are **retrospective matchup evaluations, not untouched-holdout results or simulated bracket accuracy**.

## Coverage

| Season | Provider-listed teams | Teams with completed D1 games | Corrected games | Team records reconciled |
|---|---:|---:|---:|---:|
| 2021 | 302 | 293 | 7,185 | 302/302 |
| 2022 | 301 | 301 | 8,244 | 301/301 |
| 2023 | 305 | 305 | 8,377 | 305/305 |
| 2024 | 305 | 305 | 8,391 | 305/305 |
| 2025 | 307 | 307 | 8,418 | 307/307 |

The nine 2021 provider 0–0 records are Bethune-Cookman, Brown, Columbia, Cornell, Dartmouth, Harvard, Maryland Eastern Shore, Princeton and Yale. They remain in the team universe and are not treated as missing downloaded pages. Causes of each zero season were not independently researched here.

All season roster/schedule requests succeeded and are cached. Successful access means tested retrieval, not a guarantee of continued service or a redistribution license. National completeness remains relative to the provider's season rosters and record totals, with limited independent sampling. Newly listed programs receive their own identities; no tournament eligibility is inferred from roster presence.

Primary source pages: [2021](https://www.warrennolan.com/baseball/2021/rpi-live), [2022](https://www.warrennolan.com/baseball/2022/rpi-live), [2023](https://www.warrennolan.com/baseball/2023/rpi-live), [2024](https://www.warrennolan.com/baseball/2024/rpi-live). Final ratings/records are reconciliation targets only, never model inputs.

## Corrections and independent evidence

- The 2021 source uses older HTML/CSS and different table columns. The adapter now reads its scores and reference records correctly without changing raw bytes.
- Oregon–Arizona on May 25, 2022 was labeled “Final” without a result score. The labeled line-score table supplies Arizona 8, Oregon 6, independently confirmed by [Oregon's recap](https://goducks.com/news/2022/5/25/baseball-ducks-drop-pac-12-tournament-opener.aspx). The parser recovers this automatically.
- Three February 19, 2023 source game entries were absent from the schools' official schedules: NC State–Missouri State, East Carolina–Saint Joseph's, and Kent State–Evansville. Both schools' official schedules show other opponents that day. The six original observations remain in the exclusion ledger, with correction evidence attached.
- Three actual February 19 games were missing: Dallas Baptist 13–1 Fordham, Bowling Green 10–4 Tennessee Tech, and Southern Indiana 5–4 Western Illinois. They are supplemented from [Fordham](https://fordhamsports.com/sports/baseball/schedule/2023), [Bowling Green](https://bgsufalcons.com/sports/baseball/schedule/2023), and [Southern Indiana](https://usiscreamingeagles.com/sports/baseball/schedule/2023). Each supplement uses one official record represented from both teams' perspectives. This is explicitly not independent reciprocal confirmation. DBU's own schedule requests returned HTTP 502.
- Charlotte–Lipscomb, June 3, 2023: both provider scorelines said Charlotte 9–2 but their W/L labels were reversed. [Charlotte's official schedule](https://charlotte49ers.com/sports/baseball/schedule/2023) confirms Charlotte won. Corrected outcomes retain the original labels and evidence.
- Kent State–Ohio State, 2023: [Kent State](https://kentstatesports.com/sports/baseball/schedule/2023) says April 25; [Ohio State](https://ohiostatebuckeyes.com/sports/baseball/schedule/2023) and the provider say April 26. The scores agree. The game is retained but excluded from all baseline inputs and evaluation.
- Columbia–Dartmouth, 14–13 in 2023: [Columbia](https://gocolumbialions.com/sports/baseball/schedule/2023) dates it April 22, while the provider says April 23. A resumed game is possible but not verified; quarantine rather than choose a date.

Fresh full-season school comparisons cover Oregon State 2021–2024 and Columbia 2022–2024: **387 of 388 scored rows match opponent, date and score**, with the remaining Columbia game quarantined as above. Explicit name aliases are recorded. This is a targeted convenience sample, not a random national audit. The inherited 2025 comparisons of 114 school games remain separately labeled as recovered evidence.

Columbia's requested 2021 schedule returned **2026** data. The season guard rejects it. A successful HTTP response does not establish correct-year access. Guessed 2021 NCAA manual URLs returned 404; accessible 2022–2024 manuals were downloaded, hashed and inspected. No browser challenge was bypassed.

## Team identities and affiliations

The crosswalk maps 1,520 season-specific provider rows to 310 permanent internal IDs. Exact provider-slug continuity is the default; name changes use explicit aliases: Houston Baptist → Houston Christian, and Dixie State → Utah Tech. Official institutional histories support continuity: [Houston Christian](https://hc.edu/about-hcu/history/), [Utah Tech](https://about.utahtech.edu/history/). No fuzzy matching merges similar names; Houston and Houston Christian remain distinct.

Season-specific conference labels are preserved, including conference changes and the Colonial/Coastal naming difference. Provider roster additions/removals are stored in `membership_changes.json`; reasons for every entry/exit and NCAA postseason eligibility have not all been independently verified. No NCAA numeric identity crosswalk or nationwide affiliation certification is claimed. These gaps do not enter the neutral results-only model as predictors.

## Exact forecast cutoffs and eligible inputs

Each pre-NCAA forecast is frozen on Wednesday at 12:00 UTC before regionals. A result becomes *assumed available* two calendar days after its source game date at 00:00 UTC. This includes the final regular-season weekend while adding a buffer for date-only records. Conference tournaments enter only the separately labeled inclusive mode.

| Season | Forecast cutoff (UTC) | Regular-only eligible games | Conference-inclusive eligible games |
|---|---|---:|---:|
| 2021 | 2021-06-02T12:00:00+00:00 | 6,791 | 7,046 |
| 2022 | 2022-06-01T12:00:00+00:00 | 7,780 | 8,103 |
| 2023 | 2023-05-31T12:00:00+00:00 | 7,912 | 8,238 |
| 2024 | 2024-05-29T12:00:00+00:00 | 7,928 | 8,258 |
| 2025 | 2025-05-28T12:00:00+00:00 | 7,963 | 8,282 |

Every completed D1 game's decision and exclusion reason are saved in `forecast_eligibility.csv`, including the two quarantined date conflicts. Unscored, canceled, suspended, non-D1 and known erroneous source entries remain in the season observation/exclusion ledgers, outside the completed D1 table. Ties stay in the inventory and count as half a win for Elo updates, but do not enter binary metrics.

The NCAA opening windows are checked against the [2022 manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2021-22D1MBA_PreChampsManual.pdf), [2023 manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2022-23D1MBA_PreChampsManual.pdf), [2024 manual](https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/2023-24D1MBA_PreChampsManual.pdf), inherited 2025 audit/manual and the official 2021 Oregon State NCAA schedule. No tournament simulator is implemented here.

**Limit:** source dates do not prove exact game-completion or publication times. A two-day delay does not eliminate unknown resumed games or later score corrections. `point_in_time_certified` is false for every eligibility record. Phases come from provider event labels, with unlabeled pre-NCAA games inferred regular season; this is not an independent national phase audit. The current result is an honest date-based reconstruction with known exceptions excluded, not a certified replay of what was published at each historical instant.

## Baseline and results

Elo is a rating that moves up or down after a result, accounting for opponent strength. This fixed baseline starts each new team at 1500, uses K=20 and scale 400, and carries half of the previous season's rating differences into the new season. These are engineering starting values, fixed before metrics were read, not optimized parameters. No home advantage, run-margin adjustment, final ranking or player statistic enters the model.

2021 initializes ratings. 2022–2024 provide chronological fixed-parameter validation; 2025 is development. All games on the same source date update together, so a doubleheader's unverified ordering cannot change results. Daily forecasts use the two-day delay and earlier results only. Frozen regular-only and conference-inclusive models retain their own histories and stay fixed through that year's NCAA matchups.

| Season | NCAA games | Elo winner accuracy | Win-rate accuracy | Elo log loss | Win-rate log loss | Elo Brier score |
|---|---:|---:|---:|---:|---:|---:|
| 2022 | 141 | 66.0% | 57.4% | 0.6262 | 0.6555 | 0.2187 |
| 2023 | 137 | 70.8% | 68.2% | 0.6181 | 0.6380 | 0.2140 |
| 2024 | 133 | 69.9% | 60.2% | 0.6037 | 0.6420 | 0.2078 |
| 2025 | 136 | 63.2% | 59.2% | 0.6592 | 0.6735 | 0.2321 |

Lower log loss and Brier score mean better probability forecasts. A 50/50 benchmark scores 0.6931 log loss and 0.2500 Brier. Equal-probability winner guesses receive half-credit rather than an arbitrary alphabetical pick. Across 2022–2024, regular-only Elo scores **0.6162 log loss / 0.2136 Brier**, versus **0.6453 / 0.2273** for win rate. All benchmarks use the same evaluation rows. Season-by-season calibration bins and every prediction are saved; the sample is too small to claim precise calibration or superiority across future seasons.

Separate modes, NCAA-game log loss:

| Season | Frozen regular-only | Frozen conference-inclusive | Daily updated |
|---|---:|---:|---:|
| 2022 | 0.6262 | 0.6341 | 0.6283 |
| 2023 | 0.6181 | 0.6281 | 0.6291 |
| 2024 | 0.6037 | 0.6210 | 0.6164 |
| 2025 | 0.6592 | 0.6610 | 0.6638 |

Do not interpret these few seasons as proof that conference-tournament results should always be ignored. The regular-only objective was selected before these measurements. Daily updated forecasts answer a different question. These scores use actual realized opponents and do not evaluate bracket advancement, tournament simulation or a contest entry. A seed benchmark is still missing.

## Holdout decision

**2026 cannot be certified untouched.** The inherited session record reports ESPN probes including 2026, with original raw evidence lost and exact exposed games unknown. This session also encountered 2026 outcomes through Columbia's wrong-season response. No 2026 model fit, tuning or metrics were run. Do not present 2026 as a pristine holdout. A future season—2027 is the earliest candidate—must be reserved prospectively after the protocol is locked.

## Reproducibility, access restrictions and remaining work

The bundle includes raw bytes and SHA-256 provenance, parsers, corrected and excluded observations, the identity crosswalk, exact cutoff contract, predictions, calibration, metrics, tests and SQLite. `python3 run.py` rebuilds from cache; `--collect` adds missing downloads. Source corrections are in `2023/corrections.py`, with machine-checked official evidence. Tests cover future-result leakage, same-day order, frozen ratings, cutoff boundaries, ties and renamed/distinct schools. See `rerun_validation.json` for deterministic rerun evidence and `research_hash_validation.json` for supplemental-source hash checks.

No D1Baseball requests were made. Its automation prohibition is inherited from the prior terms audit; a normal subscription still does not establish permission for automated collection. ESPN, NCAA statistics, Boyd's World, FanGraphs, nationwide player data and play-by-play capabilities were not newly tested here. No advertised feature is being counted as collected data. No dedicated repository, interface, hosting, scheduled refresh or paid feed exists.

**Next concrete step:** resolve the two timing exceptions using box scores/recaps; broaden date/phase checks beyond the current school sample; add a cutoff-safe seed benchmark. Preserve this fixed baseline before experimenting with parameters or richer features. Establish a dedicated repository and prospectively lock a genuinely unseen evaluation season before claiming out-of-sample performance.
