# Current handoff

Updated September 26, 2026. Git history owns prior sessions.

## Completed

Extended the shared StatCrew adapters to a named team while preserving LSU defaults. Both sides of the retained Arkansas–Illinois State first box now pass hitting/PA, pitcher BF components and explicit lineup starter checks (ten pitchers). Fixed a defensive catcher-to-pitcher throw being mistaken for a substitution.

The preflight report now records cache coverage and distinguishes links from retained bytes. Arkansas's index links to dated counts and season totals, but those reports are absent. The preflight cache has one box per new school; it cannot qualify their season pitcher histories or Arkansas season hitting. The existing Oklahoma State/Grand Canyon hitting inputs remain qualified and unchanged.

[Qualification](Model_Input_Qualification.md#arkansas-retained-evidence-limit-and-sample-qualification) owns findings; [DATA](DATA.md#multi-season-preflight-evidence) owns reproduction. No new requests or ZIP, fitting, outcome metrics, model/app change or 2026 evaluation.

## Verification

All 182 tests pass (152 scripts, 30 historical). Seven new regressions cover named teams, lineup identity, defensive throws, replay spacing and cache failures. All 68 LSU hitting outputs and complete pitching report match the previous adapters exactly. Structured hitting results remain unchanged. Two preflight runs are byte-identical; 3,249 preserved data/app hashes remain unchanged.

## Next action and limits

Review acceptable access for the two exact linked Arkansas reports (`teamgbg.htm`, `teamcume.htm`), then retrieve/reconcile them if permitted. Full-season box scope remains unverified; no provider contact is authorized. Finish remaining four-team pitching/appearance qualification before candidate scoring.

Preserve 2021–2022 training / 2023 selection / 2024 retrospective validation, common both-team samples and Elo fallback. No sufficient chronological feature sample exists. Rest/depth thresholds and historical routing remain unqualified. UI/hosting/spreadsheet work stays deferred.
