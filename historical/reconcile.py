"""Cross-season identity and source-level audit. Run after per-season normalization."""
import collections,csv,hashlib,json,pathlib,uuid
ROOT=pathlib.Path(__file__).resolve().parent
ALIASES={'Houston-Baptist':'Houston-Christian','Dixie-State':'Utah-Tech'}
EVIDENCE={'Houston-Christian':'https://hc.edu/about-hcu/history/','Utah-Tech':'https://about.utahtech.edu/history/'}
def canonical(slug):return ALIASES.get(slug,slug)
def internal(slug):return 'cb:'+str(uuid.uuid5(uuid.NAMESPACE_URL,'college-baseball/team/'+canonical(slug)))
def read(p):return json.loads(p.read_text())
def run():
 cross=[];audits=[];changes=[];prior=set()
 for y in range(2021,2026):
  d=ROOT/str(y);ts=read(d/'teams.json');gs=read(d/'games.json');cov=read(d/'team_coverage.json');obs=read(d/'observations.json')
  ids=set()
  for t in ts:
   cid=internal(t['slug']);assert cid not in ids,(y,cid);ids.add(cid)
   cross.append({'season':y,'provider':'warren_nolan','provider_id':t['team_id'],'provider_name':t['name'],'internal_team_id':cid,'canonical_slug':canonical(t['slug']),'source_conference':t['conference'],'identity_basis':'explicit_rename_with_official_history' if canonical(t['slug']) in EVIDENCE else 'exact_provider_slug_continuity','identity_source':EVIDENCE.get(canonical(t['slug']),f'https://www.warrennolan.com/baseball/{y}/rpi-live'),'ncaa_team_id':None,'ncaa_tournament_eligibility':'not_assessed'})
  if prior:changes.append({'season':y,'newly_listed_internal_ids':sorted(ids-prior),'no_longer_listed_internal_ids':sorted(prior-ids)})
  prior=ids
  hashes=[];errors=[]
  for p in sorted((d/'raw').glob('*.meta.json')):
   m=read(p)
   if 'sha256' in m:hashes.append(hashlib.sha256((d/m['raw_path']).read_bytes()).hexdigest()==m['sha256'])
   if 'error' in m:errors.append(m)
  totals=[0,0,0]
  for t in ts:
   for i,n in enumerate(map(int,t['reference_record'].split('-'))):totals[i]+=n
  expected=sum(totals)/2
  checks={'records_reconcile':all(t['record_matches'] for t in cov),'games_reconcile':len(gs)==expected,'reciprocal_pass':all(g['reciprocal_check']=='pass' for g in gs),'unique_game_ids':len({g['game_id'] for g in gs})==len(gs),'source_hashes_match':bool(hashes) and all(hashes),'no_unknown_completed_opponents':not any(t['missing_opponent_ids'] for t in cov),'dates_in_season':all(g['game_date'].startswith(str(y)+'-') for g in gs),'phases_classified':all(g['stage']!='late_season_unclassified' for g in gs),'all_team_pages_cached':all((d/'raw'/(t['slug']+'.html')).exists() for t in ts)}
  audits.append({'season':y,'provider_teams':len(ts),'active_d1_teams':sum(t['completed_d1']>0 for t in cov),'zero_record_teams':[t['slug'] for t in ts if t['reference_record']=='0-0'],'games':len(gs),'ties':sum(g['tie'] for g in gs),'record_matches':sum(t['record_matches'] for t in cov),'expected_games_from_records':expected,'published_team_wins_losses_ties':totals,'stages':dict(collections.Counter(g['stage'] for g in gs)),'checks':checks,'pass':all(checks.values()),'raw_hashes_checked':len(hashes),'retrieval_errors':errors,'unscored_results':dict(collections.Counter(r['source_result'] for r in obs if r['status']=='not_scored')),'source_error_exclusions':sum(r['status']=='excluded_source_error' for r in obs),'official_supplement_games':sum(g['game_id'].startswith('official:') for g in gs),'line_score_recoveries':[{'team_id':r['team_id'],'source_game_id':r['source_game_id']} for r in obs if r.get('score_basis')=='completed_Final_labeled_line_score'],'timing_review_rows':[r for r in obs if r.get('timing_review')]})
 research_hashes=[]
 for p in sorted((ROOT/'research/raw').glob('*.meta.json')):
  m=read(p)
  if 'sha256' in m:research_hashes.append(hashlib.sha256((ROOT/'research'/m['raw_path']).read_bytes()).hexdigest()==m['sha256'])
 assert research_hashes and all(research_hashes),'Research evidence hash mismatch'
 (ROOT/'research_hash_validation.json').write_text(json.dumps({'raw_files':len(research_hashes),'pass':all(research_hashes)},indent=2))
 (ROOT/'team_crosswalk.json').write_text(json.dumps(cross,indent=2))
 with (ROOT/'team_crosswalk.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(cross[0]));w.writeheader();w.writerows(cross)
 (ROOT/'membership_changes.json').write_text(json.dumps(changes,indent=2))
 (ROOT/'coverage_validation.json').write_text(json.dumps(audits,indent=2))
 print(json.dumps([{k:a[k] for k in ['season','provider_teams','active_d1_teams','games','record_matches','pass','checks']} for a in audits],indent=2))
if __name__=='__main__':run()
