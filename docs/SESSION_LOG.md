# Current handoff

Updated September 21, 2026. Git history owns prior sessions.

## Latest work

Mapped all 64 NCAA-selected 2025 teams: 59 historical schedules/preserved audits; 48 historical player-group pages/preserved audits. Only LSU has reconciled core counts in this field. All teams retain unknown workload and a required validated fallback. Bulk collection remains disabled pending provider access/volume. See [full-field source map](Tournament_Source_Availability_2025.md).

Duke independently confirms Jake Dunagan's PR/CF appearance; Davidson lists him in pitching/fielding but omits batting. Batting completeness remains false. Illinois State confirms the Missouri State game started May 24 and finished May 25, 2022. Baseline completion date is correct. Separate exception annotations qualify Missouri State conference-inclusive box joins at 57/57 without assigning pitcher work dates.

Recovered all 117 raw responses and metadata from the truncated source-expansion ZIP via CRC and SHA checks; rebuilt its derived audit. DATA.md documents recovery and the new checkpoint.

## Verification

70 tests pass. LSU/Towson audit repeats byte-for-byte. New audits reproduce offline. All 3,212 baseline files remain identical. No model fitting, thresholds, scaling, interface or simulator changes. One pre-NCAA run through champion remains primary; no scheduler/live updates required.

## Next action and limitations

Establish provider access/volume, resolve five schedule gaps plus player-source/parser gaps, then qualify additional team-seasons and validate fallback behavior. SIDEARM personal-use copying is not a verified bulk-volume grant. Little Rock robots disallow; Dallas Baptist robots failed. A Clemson historical URL returned 2026 content and was rejected; 2026 remains uncertified and unused for modeling. Preserve cutoffs, separate forecast modes and unknown rest.
