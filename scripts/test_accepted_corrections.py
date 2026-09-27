"""Synthetic evidence and full export checks; no collection or historical data."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_candidate_refresh as fixtures
from test_candidate_refresh import game, fresh, staged
from ingestion import candidate as c
from ingestion import nolan_refresh as n
from tournament import build as b


def approval(history, bundle):
    return dict(schema=1, season=2024, refresh_version=bundle['version'],
        refresh_sha256=deepcopy(bundle['source_sha256']), corrections=[dict(
            game_id=bundle['games'][0]['game_id'], reason='Reviewed reciprocal saved scorelines.',
            baseline_sha256=c.fingerprint(history[2024][0]),
            candidate_sha256=c.fingerprint(bundle['games'][0]))])


class AcceptedCorrections(unittest.TestCase):
    def inputs(self):
        history={2024:[game()]}
        bundle=staged([dict(fresh(),runs_a=0)])
        return history,bundle,approval(history,bundle)

    def test_accept_preserves_full_original_and_is_deterministic(self):
        history,bundle,review=self.inputs();before=deepcopy(history)
        result,report=c.merge_verified(history,bundle,review)
        self.assertEqual(history,before)
        row=result[2024][0]
        self.assertEqual(row['runs_a'],0)
        self.assertEqual(row['refresh_correction']['original_game'],before[2024][0])
        self.assertEqual(row['refresh_correction']['observation_refs'],bundle['games'][0]['observation_refs'])
        self.assertEqual(report['counts'],{'accepted_score_correction':1})
        self.assertTrue(report['numerical_inputs_changed'])
        self.assertEqual(report['decisions'][0]['correction']['original_game'],before[2024][0])
        self.assertEqual(report['decisions'][0]['accepted_fields']['runs_a'],0)
        self.assertEqual((result,report),c.merge_verified(history,bundle,review))

    def test_stale_evidence_baseline_and_candidate_fail_closed(self):
        for target in ('refresh','baseline','candidate','version','reason','duplicate','absent'):
            history,bundle,review=self.inputs()
            if target=='refresh':bundle['source_sha256']['raw']='changed'
            if target=='baseline':history[2024][0]['observation_refs']=[]
            if target=='candidate':bundle['games'][0]['runs_a']=9
            if target=='version':review['refresh_version']='other'
            if target=='reason':review['corrections'][0]['reason']=' '
            if target=='duplicate':review['corrections']*=2
            if target=='absent':review['corrections'][0]['game_id']='absent'
            with self.subTest(target=target),self.assertRaises(ValueError):
                c.merge_verified(history,bundle,review)

    def test_unsafe_or_unqualified_reviews_cannot_override_fallback(self):
        for change in ({'game_date':'2024-05-21'},{'stage':'conference_tournament'},
                       {'team_a_id':'wn:C'},{'timing_review':True},
                       {'reciprocal_check':'review'},{'runs_a':-1},{'runs_a':True},
                       {'tie':True},{'modes':{'regular_only':{'eligible':False}}}):
            history,bundle,_=self.inputs();bundle['games'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                c.merge_verified(history,bundle,approval(history,bundle))
        for fields in ({'corrections':[{'evidence':'official'}]},
                       {'timing_resolution':{'evidence':'official'}},
                       {'reciprocal_check':'review'}):
            history,bundle,_=self.inputs();history[2024][0].update(fields)
            with self.subTest(fields=fields),self.assertRaises(ValueError):
                c.merge_verified(history,bundle,approval(history,bundle))
        history,bundle,_=self.inputs();bundle['games'][0]['runs_a']=3
        with self.assertRaises(ValueError):c.merge_verified(history,bundle,approval(history,bundle))

    def test_tie_is_accepted_with_consistent_scores(self):
        history,bundle,_=self.inputs();bundle['games'][0].update(runs_a=1,tie=True)
        result,_=c.merge_verified(history,bundle,approval(history,bundle))
        self.assertTrue(result[2024][0]['tie'])

    def test_raw_backed_acceptance_and_export_with_real_elo(self):
        # Build two matching source pages through the actual parser/stager.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=fixtures.CandidateRefresh().fixture(root)
            request=n.read(folder/'request.json');request['teams']=['A','B']
            (folder/'request.json').write_text(json.dumps(request))
            body=(folder/'raw/A.html').read_text().replace('W 3 - 1','L 0 - 1')
            roster=n.read(root/'historical/2024/teams.json')
            contract=n.read(root/'historical/cutoffs.json')
            obs=[]
            for team,text in zip(roster,[body,body.replace('2024 A Tigers','2024 B Tigers').replace('/schedule/B','/schedule/A').replace('L 0 - 1','W 1 - 0')]):
                slug=team['slug'];raw=text.encode()
                meta=dict(url=n.url_for(2024,slug),http_status=200,raw_path=f'raw/{slug}.html',sha256=n.digest(raw),retrieved_at='2026-09-27T00:00:00Z')
                (folder/meta['raw_path']).write_bytes(raw)
                (folder/(meta['raw_path']+'.meta.json')).write_text(json.dumps(meta))
                obs.extend(c.parse(team,text,meta,2024,'2024-05-31'))
            rows,excluded=n.stage(obs,roster,2024,contract)
            for name,value in [('observations',obs),('games',rows),('exclusions',excluded)]:
                (folder/(name+'.json')).write_text(json.dumps(value))
            history={y:[] for y in range(2021,2026)}
            history[2024]=[game()];history[2025]=[dict(game('wn:2025:1'),season=2025,game_date='2025-05-20')]
            with patch.object(c,'ROOT',root):
                bundle=c.verified_refresh(folder)
                review=approval(history,bundle);path=root/'review.json';path.write_text(json.dumps(review))
                candidate,report=c.apply(folder,history,path)
                self.assertEqual(report['counts'],{'accepted_score_correction':1})
                # Full build: mock unrelated baseline evidence gates and bracket layout,
                # but run the real correction adapter, reconstruct and probabilities.
                contract['availability_rule']='synthetic two-day rule'
                for year in history:
                    contract['seasons'][str(year)]={'forecast_cutoff':f'{year}-05-29T12:00:00+00:00','ncaa_opening_date':f'{year}-05-31'}
                # Keep refresh contract file unchanged; build reads a separate root.
                buildroot=root/'build';(buildroot/'historical').mkdir(parents=True)
                (buildroot/'historical/cutoffs.json').write_text(json.dumps(contract))
                (buildroot/'historical/coverage_validation.json').write_text(json.dumps([{'season':y,'pass':True} for y in history]))
                (buildroot/'historical/correction_evidence_checks.json').write_text('{"pass":true}')
                for name in ('ingestion/candidate.py','ingestion/nolan_parser.py','ingestion/nolan_refresh.py','historical/baseline.py','historical/team_fallback.py','historical/eligibility.py'):
                    dest=buildroot/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('synthetic')
                selections=[dict(season=2025,team_id=t,source_name=t,regional_seed=i+1,provenance={}) for i,t in enumerate(('a','b'))]
                reference=[]
                for mode in b.MODES:
                    state,_=b.reconstruct(history,contract,2025,mode)
                    reference.append(dict(season=2025,mode=mode,team_a_id='a',team_b_id='b',elo=state.p('a','b')))
                from contextlib import ExitStack
                with ExitStack() as stack:
                    for obj,key,value in [(b,'ROOT',buildroot),(b.validation,'hashes',lambda:{}),
                        (b,'verify_timing',lambda:[]),(b.independent,'run',lambda:[]),
                        (b.seeds,'load',lambda _:selections),(b.validation,'opening_checks',lambda *_:[]),
                        (b,'build_regions',lambda *_:[]),(b,'load_games',lambda y:deepcopy(history[y])),
                        (b,'overlay',lambda gs,_:gs),(b.validation,'evaluate',lambda *_:(reference,None,None)),
                        (b,'forecast',lambda regions,ratings:{'synthetic_probability':b.probability(ratings['a'],ratings['b'])})]:
                        stack.enter_context(patch.object(obj,key,value))
                    output=b.build(folder,path)
                    self.assertEqual(output,b.build(folder,path))
                    for mode in b.MODES:
                        verify=output['modes'][mode]['verification']
                        self.assertEqual(verify['baseline_max_probability_difference'],0)
                        self.assertGreater(verify['max_probability_difference'],0)
                        self.assertTrue(verify['candidate_inputs_changed'])
                    # Acceptance must never disable the independent baseline equality gate.
                    reference[0]['elo']=0
                    with self.assertRaisesRegex(ValueError,'Baseline ratings diverged'):b.build(folder,path)
                # Raw tampering still fails with an approval present.
                (folder/'raw/A.html').write_text('tampered')
                with self.assertRaises(ValueError):c.apply(folder,history,path)

    def test_modes_and_cutoffs_still_govern_corrected_rows(self):
        contract={'seasons':{str(y):{'forecast_cutoff':f'{y}-05-29T12:00:00+00:00'} for y in range(2021,2026)},
                  'modes':{'regular_only':['regular_season'],'conference_inclusive':['regular_season','conference_tournament']}}
        history={y:[] for y in range(2021,2026)}
        original=dict(game(),stage='conference_tournament');history[2024]=[original]
        row=dict(fresh(),stage='conference_tournament',runs_a=0,modes={'regular_only':{'eligible':False},'conference_inclusive':{'eligible':True}})
        candidate,_=c.merge_verified(history,staged([row]),approval(history,staged([row])))
        for mode in b.MODES:
            old,_=b.reconstruct(history,contract,2025,mode);new,_=b.reconstruct(candidate,contract,2025,mode)
            self.assertEqual(old.p('a','b')==new.p('a','b'),mode=='regular_only')
        # Even if a caller supplied a candidate later than cutoff, reconstruction excludes it.
        candidate[2024][0]['game_date']='2024-05-28'
        state,_=b.reconstruct(candidate,contract,2025,'conference_inclusive')
        self.assertEqual(state.p('a','b'),.5)


if __name__=='__main__':unittest.main()
