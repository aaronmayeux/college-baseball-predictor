# Statistics discovery and proposed triage

Reviewed September 20, 2026. **Aaron approved prioritizing hitting profiles and pitching quality/depth; individual features remain unqualified.** No new model, weights, thresholds, simulator or interface was implemented. Forecast and holdout rules remain in [SPEC](../historical/SPEC.md).

## Recommendation for joint review

The active [team-component source decision](Team_Component_Source_Decision.md) supersedes this inventory’s original player-first ordering: keep Elo, defer individual pitchers, and use retained/free sources only under Aaron’s zero-budget rule. The table below preserves candidate research priorities, not authorization to resume collection. Baserunning, defense, availability and park interactions remain future proposals.

| Priority | Proposed work | Reason |
|---|---|---|
| Test now, 1 | Hitting OBP, K%, BB%, ISO and HR/PA; compare a smaller combination with adjusted run scoring | Separates reaching base, contact and power without inheriting workbook weights |
| Test now, 2 | Pitcher K%, BB%, HBP%, HR rate, ERA/RA9; qualifying starter/reliever counts and ace candidates | Directly addresses quality arms; workload and quality must both qualify |
| Test now, 3 | Opponent-adjusted scoring/prevention versus preserved Elo; verify actual home venues | Broadest existing data; establish whether extra detail adds anything |
| Test now, 4 | Stealing attempts and success; basic error/fielding measures as challengers | Cheap when boxes are complete, but narrower than full HAVOC or defense |
| Research further | Available arms after recent use, exact HR-run share, advancement, park and handedness interactions, wOBA/FIP alternatives | Potentially valuable; histories, denominators or permissions need work |
| Defer | Tracking-derived contact/pitch quality, full defensive runs, weather/travel effects, coach policy and detailed depletion simulation | High effort or unverified historical access; revisit after simpler features |
| Skip as model inputs | Legacy HAVOC/DIRTY_DER formulas, assumed HR-run share, fixed style bonuses, pitcher wins/saves, clutch labels | Defective, redundant or weakly supported; raw evidence remains preserved |

“Test now” means proposed experiments **after data qualification and approval of the relevant family**. Hitting and pitching quality/depth have priority approval; the remaining families remain proposals. None is already proven predictive. The current plan prioritizes team-level counts; individual pitching coverage work remains deferred.

## Original references inspected

- STATIC: all eight sheet names and the Raw_Stats/Data_Master/Solver_Control/Style_Control inputs and formulas inspected. Raw_Stats has 64 teams and 75 columns. It already includes conventional offense, pitching, batted-ball rates, wOBA/wRC+, FIP/xFIP/SIERA and custom metrics. This inventory extends it with player roles/depth, uncertainty, actual availability, opportunities and matchup context.
- Confirmed `Raw_Stats!Y2=(1-AF2)-(X2*0.4)`: own offensive BABIP feeds DIRTY_DER. `Z2=((V2*2)+T2+S2)/U2` omits caught stealing and opportunities. `AA2=(Q2*1.6)/M2` assumes HR run value. Data_Master standardizes within the 64-team field. These are unsuitable inherited definitions, not validated features.
- DYNAMIC: inspected original XLSB shared strings and chart XML. Labels include CONTACT/POWER/SPEED/PITCHING/DEFENSE, the same advanced-stat families, and the original style classifications. Binary formula execution was not repeated; the prior PDF owns its detailed formula/cache audit. No workbook was modified or recalculated.
- Read all 12 pages of `CWS_Predictor_Research_and_Design.pdf`. Retain its opponent adjustment, tournament resource and evidence-first hypotheses. Repository cutoffs and holdout decisions supersede its older proposed season range. Original advanced-stat attribution remains unresolved; a metric label is not source provenance.

## Source/access findings

Search scope: original references, repository reports/code, official LSU historical statistics, NCAA access and baseballr documentation, ESPN historical summaries, FanGraphs college/glossary pages, Boyd's World, SABR PING, Driveline cWAR, Highlightly documentation/prices/terms, and scaling documentation. This is a broad first inventory, not an exhaustive survey or nationwide player-data audit. A general web search returned irrelevant results and was discarded; verified primary pages below support this report. No D1Baseball requests, paid purchases or provider contacts were made.

| Source | Tested now versus advertised/inherited | Coverage, automation and cost implications |
|---|---|---|
| **R: existing results** | Repository audit records 2021–2025 results coverage; not rerun here | Already retained, no new purchase. Date-based reconstruction only; verified scores do not establish player-stat coverage. [Historical report](College_Baseball_Historical_Coverage_and_Elo_Report.md) owns counts |
| **B: official boxes** | [LSU 2025 index](https://static.lsusports.net/assets/docs/bb/25stats/teamstat.htm), [May 16 box](https://static.lsusports.net/assets/docs/bb/25stats/sc-55.htm) and [special reports](https://static.lsusports.net/assets/docs/bb/25stats/teamspec.htm) readable; source bytes retained | Sample box has BF, HBP, pitches/strikes, inherited runners and narrative plays. Season reports include postseason and cannot directly feed pre-NCAA forecasts. [Archive](https://lsusports.net/bbstats/) links 2021–2025 and older years; links alone do not verify them. Public sample access costs $0; bulk permission and school-by-school reliability unverified. Medium/high collection effort |
| **E: ESPN** | Four fixed historical summaries returned HTTP 200; two contain pitching rows, two contain empty arrays. See sample below | Undocumented endpoint; no supported feed/license established. Public probes cost $0, historical completeness unknown. Medium ingestion effort; high effort for complete recent-workload histories |
| **N: NCAA / baseballr** | `stats.ncaa.org` unavailable through web tool. [Function documentation](https://billpetti.github.io/baseballr/reference/ncaa_team_player_stats.html) readable, describes batting/pitching/fielding and bot protection | Wrapper functionality is advertised, not a successful data fetch. Documentation mixes an old 2013–2017 range with a 2023 example; verify real season coverage. No paid plan identified. High access risk; no challenge circumvention |
| **F: FanGraphs college** | [College board](https://www.fangraphs.com/leaders/college) readable, 2021–2026 selectors and members-only export visible. A `?season=2025` request failed in web tool; no export tested | Historical selector is not a cutoff-safe snapshot or completeness proof. Paid export membership price/license for our use unverified. Automation and redistribution rights unresolved. Default board exposed 2026 player stats; nothing imported or evaluated |
| **I: Boyd's World / ISR** | Data index and attempted 2025 ISR page failed in web tool | Access failure, not proof data do not exist. Cutoff archives, automation permission, price and historical completeness unverified. Do not substitute final ISR. [PING paper](https://sabr.org/journal/article/the-ping-ratings-a-model-for-rating-ncaa-baseball-teams/) distinguishes ISR from Warren Nolan NPI |
| **M: methodology** | [Driveline cWAR](https://drivelinebaseball.com/blogs/blog/an-introduction-to-cwar) describes college-season coefficients and park/SOS adjustment, with approximate fielding/baserunning | Supports candidate design, not a working current feed. Its inherited data sources do not grant us collection rights; complete modern coverage unknown |
| **C: commercial** | [Highlightly API docs](https://highlightly.net/mlb-api/documentation/) advertise NCAA boxes, player stats and lineups. [Pricing](https://highlightly.net/mlb-api/) shows $0/100 requests daily, $7.99/7,500, $18.99/25,000, $44.99/65,000 monthly labels | No key, payload, historical coverage or checkout tested. Marketing alternates “every” and “most” NCAA coverage. [Terms](https://highlightly.net/terms/) permit application data storage/distribution but restrict API pass-through, competing databases and gambling/gaming use. Check fit if bracket contests become a product objective. No service guarantee; not selected |
| **Restricted/unexplored** | D1Baseball prohibition remains as recorded in the [2025 report](College_Baseball_2025_Coverage_Report.md#source-assessment-tested-versus-advertised); no fresh request | D1 licensing/feed price unverified. National tracking, injury archives and other commercial vendors were not tested; classify as unexplored, not unavailable |

Fresh ESPN feasibility sample (selected prior examples, **not a random coverage estimate**):

| Event ID / date | Matchup | Pitcher rows | Positive pitch counts | Play records |
|---|---|---:|---:|---:|
| 401749148 / 2025-05-16 | LSU–South Carolina | 8 | 8/8 | 301 |
| 401750347 / 2025-03-04 | Kennesaw State–Georgia Tech | 0 | Unknown | 0 |
| 401653540 / 2024-05-16 UTC | South Alabama–Louisiana | 0 | Unknown | 0 |
| 401778093 / 2025-06-15 | Coastal Carolina–Oregon State | 7 | 7/7 | 581 |

Endpoint: `https://site.api.espn.com/apis/site/v2/sports/baseball/college-baseball/summary?event=ID`. All eight May 16 pitcher pitch counts agree with the official school box on inspection. Each populated team's pitching outs total 27. Play counts include pitch/inning events; they are not counts of completed plate appearances. ESPN's sampled pitcher groups omit BF and HBP columns; do not manufacture either from incomplete batting totals. Embedded ERA/AVG/OBP/SLG fields are not certified as-of totals; reconstruct from individual events instead. The June sample is for schema coverage only, never a pre-NCAA input.

## Candidate inventory

Source codes above supply access, cost and historical coverage for every row. **R** alone has an established multi-season inventory. **B/E** mean isolated successful 2024/2025 examples, national 2021–2025 coverage unknown. **N/F/I/C** are prospective alternatives, not verified imports. No paid source is required by the proposed first tests. Effort includes normalization: **L** low once eligible counts exist, **M** moderate joins/adjustment, **H** substantial new histories/parsing.

Cutoff classes: **G** aggregate only eligible dated games, with mode/lag rules from SPEC; **P** reconstruct eligible plays/appearances, including completion/publication uncertainty; **S** requires a dated pre-cutoff snapshot (final totals invalid); **K** requires information actually known at forecast time. All statistical adjustments and learned weights are training-only. Reliability below is a research assessment, not a measured forecasting result.

| Candidate / definition | Usefulness and overlap | Reliability / missing evidence | Sources; cutoff; effort | Triage |
|---|---|---|---|---|
| OBP, BB/PA, HBP/PA | Reaching base and patience; overlap wOBA/OPS/HAVOC | OBP needs its proper AB+BB+HBP+SF denominator; HBP sparse | B/E/N/F; G; M | Test now |
| Batting K/PA | Contact proxy and opponent matchup; overlaps old HAVOC | Not swing-contact%; adjust opponent pitching and sample size | B/E/N/F; G; M | Test now |
| ISO=SLG−AVG; HR/PA; doubles/triples per PA | Extra-base power and HR frequency; related but not identical | Triples and HR fluctuate with park and opportunities | B/E/N/F; G; M | Test now; triples secondary |
| Actual runs scored on HR plays / total runs | True HR dependence distinct from power | Need scoring plays; low total runs destabilize ratio; no automatic power penalty | B/E; P; H | Research further |
| wOBA / adjusted run creation (wRC+-like) | Compact event-value alternative to several offense columns | College weights and adjustment provenance required; no final-season constants for earlier forecasts | B/N/F/M; G or S; H | Research further |
| Base Runs; adjusted runs per offensive out | Sequencing-resistant challenger; overlaps wOBA/run differential | Base Runs coefficients need college validation; offensive outs required for rate | B/E/M; G; M | Research further |
| AVG, SLG, OPS, RBI, raw hits/HR/runs | Useful display/check fields; substantial component overlap | Counting totals mix ability and opportunities; RBI depends on teammates | B/E/N/F; G; L | Skip as extra independent drivers |
| BABIP; GB/LD/FB/PU and HR/FB rates | Contact shape and park hypotheses | BABIP mixes defense/contact/luck; batted-ball classification uncertain. GO/FO counts are outs, not GB/FB rates | B/F; P or S; H | Research further |
| Pitches per PA, long-PA frequency | Offensive workload pressure on opponent | Requires full PA/pitch histories; K and BB already explain some | B/E; P; H | Research further |
| Swing contact%, chase%, whiff%, exit velocity, hard-hit/barrel%, spray, expected wOBA | Potential contact/pitch matchup detail | National historical tracking/access untested; do not infer from K% or fly-ball outs | Licensed tracking unexplored; P/K; H, price unknown | Defer |
| Pitcher K/BF, BB/BF, HBP/BF, (K−BB)/BF | Core control/dominance; compare components with K−BB, not all as independent evidence | Need BF; shrink short samples toward role/league. Avoid unstable K:BB when BB≈0 | B/N/F; G; M | Test now |
| ERA=27×ER/outs; RA9=27×R/outs; HR/BF | Run prevention and HR susceptibility | ERA affected by fielders/scorer; RA9 includes defense; HR noisy/park-sensitive | B/E/N/F; G; M | Test now as comparators |
| WHIP=(H+BB)/IP; K/9, BB/9, K:BB | Familiar diagnostics, fallback denominators | WHIP omits HBP; per-inning rates not equivalent to BF rates; overlap core metrics | B/E/N/F; G; L | Skip as stacked extra drivers |
| FIP; xFIP; SIERA | Alternative pitching quality estimators | FIP needs HR/HBP/K/BB and college constant; xFIP needs fly balls and expected HR/FB; SIERA needs validated college relationships | B/F/M; G or S; M/H | Research FIP first; defer xFIP/SIERA |
| Starter, relief and mixed-role qualifying-arm counts | How many pitchers meet both workload and quality thresholds | Role-specific workloads; avoid one-inning stars and double-counting mixed roles | B/E/N; G; M | Test now, coverage gate |
| Ace candidates: sustained elite quality + starter workload | Distinguishes teams with multiple aces or none | League/role benchmark and uncertainty needed; team rank alone insufficient | B/E/N; G; M | Test now, threshold review |
| Starter outs/start; long-relief capacity; top-arm share of staff outs | Rotation durability, concentration and fallback depth | Coach/opponent/game context matters; counts alone omit usable innings | B/E/N; P; M | Test now, coverage gate |
| Expected available quality outs after recent usage | Game-specific resources beyond season depth | Need every recent appearance, rest, pitches/BF/outs; missing game ≠ rested | B/E/C; P/K; H | Research further, high priority |
| Inherited runners scored/received; relief entry context | Relief effectiveness beyond charged ERA | Tiny samples, inherited difficulty and sequencing; overlaps quality estimates | B/E; P; H | Research further |
| Pitch type, velocity, movement, location, platoon arsenal fit | Potential starter-lineup interaction | Historical national tracking and license untested | Tracking unexplored; P/K; H, price unknown | Defer |
| Pitcher W/L, saves, shutouts, complete games | Roles/descriptive workload clues | Decisions depend heavily on offense/opportunity; CG overlaps outs/start | B/E/N; G; L | Skip as quality scores |
| SB/(SB+CS); attempts/PA as a labeled proxy | Stealing efficiency plus aggressiveness | Low attempts uncertain; PA not actual steal opportunity; pickoffs separate | B/N/F; G; M | Test now |
| Attempts/eligible steal opportunities; advancement on hits/outs, baserunning outs, pickoffs | Fuller HAVOC and runs gained/lost | Define base/out opportunity and double steals; needs runner events; overlaps speed/OBP | B/E; P; H | Research further |
| Bunt attempts/success, sacrifice outcomes, GDP/opportunity | Small-ball choices and avoidance of wasted outs | Strategy/score dependent; successful sacrifices alone omit failures | B/E; P; H | Research further, lower priority |
| FPCT=(PO+A)/(PO+A+E); E/chances | Routine execution challenger, limited defensive display | Scorer bias, position mix and range missing; both measures redundant | B/N; G; M | Test now, low priority |
| Outs on eligible balls in play / eligible balls in play; ROE rate | Team conversion and pressure on defense | Define HR/sacrifice/DP treatment explicitly; opponent BABIP alone is not pure defense | B/E; P; H | Research further |
| Catcher CS/attempts, passed balls; pitcher WP/BF and pickoffs | HAVOC prevention interaction | Separate catcher/pitcher attribution and opportunities; catching changes | B/E/N; P; H | Research further |
| Defensive runs, range, framing, pop time | More complete defense/catching | Tracking coverage not established; estimated cWAR fielding not observed range | M/tracking; P/K; H, price unknown | Defer |
| Elo; adjusted runs scored/allowed; opponent strength | Core team strength and offensive/pitching context | Results available; scoring affected by blowouts/short games. Fit opponents jointly using prior games | R/B/M; G; L/M | Test adjusted scoring versus Elo |
| RPI/SOS/ISR/NPI, seed, win%, Pythagorean expectation/residual | Benchmarks/context; overlap Elo/run strength | Only dated ratings; final schedules contaminate SOS. Pyth exponent unvalidated; residual not a fixed “luck” bonus | R/I/N; G or S; M | Research ISR; keep existing seed comparator; skip stacked rankings |
| True home venue, batting last, host status | Separate site effect from strong teams being selected hosts | Existing venue flags unverified; visitors can bat last at neutral sites | R/B/E; K; M | Test after venue audit |
| Park run/HR factors; HR dependence × park | Tests glass-cannon hypothesis directly | Estimate multi-year factors with opponent adjustment/shrinkage; pre-cutoff only, renovations tracked; Omaha small sample | R/B/E/M; G/K; H | Research further |
| Pitcher/lineup handedness, platoon splits; contact × K, GB × defense, speed × catcher | Specific matchup explanations | Tiny splits, probable lineups uncertain; single main effects first, few continuous interactions | B/E/N/F; P/K; H | Research further |
| Recency, lineup turnover, transfers, injuries, probable starters | Current personnel more informative than streak labels | Only announcements/history known then; final actual lineup leaks; roster identities unresolved | B/E/C; K; H | Research personnel; defer broad injury model |
| Weather, wind, travel, time zones, rest, series/game number | Environment and schedule context | Historical observations ≠ historical forecasts; confounds venue/opponents | B/E plus weather archive unexplored; K; H, price unknown | Defer weather/travel; research rest |
| RISP/2-out BA, late-close record, clutch/hot streaks | Descriptive situational performance | Small selection-biased samples; overlaps general talent and opponent mix | B/E; P; M | Skip fixed bonuses |

## Pitching depth and aces: proposed definitions to choose together

Count a pitcher only if **eligible workload ≥ W AND estimated quality meets Q**. Retain the name, outs/BF, role, quality estimate and uncertainty. W and Q remain open. Use starters, relievers and mixed roles as mutually exclusive summary groups; count each person once in total staff depth. Within-role appearance splits can still describe dual use.

For discussion only, a sensitivity grid could compare relief minima of 10/20/30 IP and starter minima of 30/40/50 IP at pre-NCAA lock, with above-average/top-third quality. These are illustrative test settings, not recommended final cutoffs. Review schedule-length and BF-based alternatives before choosing. A reliever should not need starter innings to qualify. Compare raw ERA screens with shrunk K/BB/HBP/HR-based estimates and adjusted run prevention; choose on chronological validation, not which labels flatter 2025 teams.

An **ace candidate** must clear a stricter D1 starter-quality standard plus sustained starter workload (illustratively top 10–15% and 40–60 IP for review). There can be zero, one or several. Use a separate “elite reliever” label instead of treating one short dominant relief stint as an ace. Show borderline/insufficient evidence rather than pretending thresholds remove uncertainty. Compare hard counts with expected qualifying counts and quality-weighted expected outs, which avoid abrupt changes at a cutoff.

Season depth describes the roster's demonstrated capacity. Availability describes what it can plausibly supply next: last appearance, pitches/BF/outs in recent days, consecutive-day use, rest, role and expected stint length. Record uncertainty about injuries and coach choice. Do not invent a universal recovery rule or treat workload estimates as medical clearance.

Keep talent inputs within each forecast mode. A proposal to use known conference-tournament workload with regular-only talent must be a separately named availability overlay, reviewed before changing the strict existing mode. Bracket-lock forecasts simulate future usage; daily updates may use only already observed usage. Start/completion separation for suspended games remains a prerequisite. Opponent depletion benefits require a future shared tournament ledger; defer that implementation.

## Scaling and reliability: candidates, not decisions

First establish eligible counts and sample size; estimate opponent/park/season effects and shrink noisy rates toward a suitable population. Then compare scaling options. Shrinkage means giving a ten-inning sample less influence than a sixty-inning sample. A z-score alone does none of this.

| Choice | Recommended experiment | Limit |
|---|---|---|
| Z-score: subtract training mean, divide by training SD | First candidate for a regularized linear/logistic model | Keeps relative distances; sensitive to outliers; does not make data normal or establish quality |
| Median/interquartile-range scaling | Challenger when heavy tails materially distort fitting | More resistant to extremes; still needs reliable inputs and a zero-spread rule |
| Log or smoothed log-odds transform then scale | Consider for skewed positive rates/counts or bounded probabilities | Handle zeros explicitly; estimate smoothing/transform parameters on training only |
| Raw units / exposure-aware count models | Compare where modeling events with PA/BF/outs; tree models usually need no standard scaling | Model choice matters; counts require exposure, not merely a different scale |
| Percentiles | Preferred candidate for comparison charts: “better than 80% of the comparison group” | Hides size of gaps; tied ranks and direction need definition; not a win probability |
| Min-max or rank-to-normal transforms | Lower priority challengers | Extrema unstable; rank transforms discard magnitude information |

Technical support: [scikit-learn preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html). This table is our proposed evaluation design, not a claim that one scaler is universally best. In regularized models scaling affects the penalty; it is not itself an accuracy improvement.

Fit preprocessing within each chronological training fold and freeze it for evaluation. Compute any current-season context only from data available at that cutoff under a rule fixed in advance. Never normalize with final-season totals or future tournament participants. Prefer all-D1, same-role comparison groups with minimum evidence; show tournament-field percentiles only as a clearly labeled alternate view. Chart percentiles must use the same known-at-cutoff population and display the underlying rate/workload. A contact/power/speed chart describes style; higher aggression or HR dependence is not automatically better. Chart-axis formulas remain open.

Avoid double-counting: compare OBP+ISO+K% with wOBA alternatives; K/BB components with K−BB or FIP alternatives; ERA with defense-aware prevention; and stealing with ordinary offensive talent. Add one family at a time and compare on identical covered games against Elo/seed baselines. Score log loss, Brier and calibration across seasons/conferences, report missingness and uncertainty, and retain complexity only for credible incremental benefit. No predictive tests were run in this discovery session.

A larger outfield is not evidence of easier stealing. Separate outfield-hit/advancement effects from pitcher/catcher control of steals; do not award a generic Omaha HAVOC bonus.

## Coverage gate after priority approval

Hitting profiles and pitching quality/depth are the approved priorities. The [initial historical player audit](Historical_Player_Data_Coverage.md) owns current results, missing fields, source disagreements and the next coverage steps. Thresholds, ace-label details, scaling and other proposed families remain open. No feature fitting is authorized by a coverage success alone.

Before fitting, establish permissions for intended collection volume and a viable fallback, then review workload/quality threshold sensitivity. Timing/phase verification and prospective holdout locking remain outstanding under SPEC.

Original discovery raw-probe recovery and its offline audit command remain in [DATA.md](DATA.md#statistics-discovery-evidence). That selected four-game sample is feasibility evidence, not national completeness or predictive validation.
