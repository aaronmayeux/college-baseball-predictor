"""Explicit evidence-backed 2023 corrections. Never change cached provider bytes."""
import copy,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
RESEARCH=ROOT.parent/'research'
CORRECTIONS={
 '1590':{'action':'exclude','reason':'Extra NC State–Missouri State entry absent from both official season schedules; both schools played other opponents on February 19.','evidence':['ncstate_2023.html','missouri_2023.html']},
 '2245':{'action':'exclude','reason':'Extra East Carolina–Saint Josephs entry absent from both official season schedules; both schools played other opponents on February 19.','evidence':['ecu_2023.html','stjoseph_2023.html']},
 '1670':{'action':'exclude','reason':'Extra Kent State–Evansville entry absent from both official season schedules; both schools played other opponents on February 19.','evidence':['kent_2023.html','evansville_2023.html']},
 '45046':{'action':'derive_outcome_from_score','reason':'Charlotte official schedule confirms 9–2 win over Lipscomb on June 3; provider score is correct but W/L labels are reversed.','evidence':['charlotte_2023.html']},
 '30070':{'action':'timing_review','reason':'Official schedules disagree: Kent State dates the 10–5 Ohio State game April 25; Ohio State and provider say April 26. Retain provider date but quarantine from modeling.','evidence':['kent_2023.html','ohio_2023.html']},
 '28465':{'action':'timing_review','reason':'Columbia official schedule dates the 14–13 Dartmouth game April 22; provider says April 23. Possible resumed game; retain provider date and quarantine from modeling pending completion evidence.','evidence':['columbia_2023.html']}
}
def refs(names):
 out=[]
 for name in names:
  p=RESEARCH/'raw'/name;m=json.loads(p.with_name(p.name+'.meta.json').read_text())
  assert p.exists() and m.get('sha256')
  out.append({'source_url':m['url'],'retrieved_at':m['retrieved_at'],'raw_sha256':m['sha256'],'raw_path':'../research/'+m['raw_path']})
 return out

def apply(team,rows):
 for r in rows:
  c=CORRECTIONS.get(r['source_game_id'])
  if not c:continue
  r['original_fields']={k:r[k] for k in ['status','game_date','outcome','runs_for','runs_against','timing_review']}
  r['correction']={**c,'evidence_refs':refs(c['evidence'])}
  if c['action']=='exclude':r['status']='excluded_source_error'
  elif c['action']=='derive_outcome_from_score':r['outcome']='W' if r['runs_for']>r['runs_against'] else 'L' if r['runs_for']<r['runs_against'] else 'T'
  elif c['action']=='timing_review':r['timing_review']=True
 # Supplements are two explicitly derived perspectives of a SINGLE official record.
 supplements=[
  ('fordham','10630','Fordham','Dallas-Baptist','Dallas Baptist',1,13),
  ('bgsu','18523','Bowling-Green','Tennessee-Tech','Tennessee Tech',10,4),
  ('southernindiana','10682','Southern-Indiana','Western-Illinois','Western Illinois University',5,4)
 ]
 for school,gid,home,opp,official_opp,rf,ra in supplements:
  if team['slug'] not in [home,opp]:continue
  source=refs([school+'_2023.html'])[0]
  official=json.loads((RESEARCH/(school+'_2023_games.json')).read_text())
  matches=[r for r in official if str(r['official_game_id'])==gid]
  assert len(matches)==1 and matches[0]['date']=='2023-02-19' and matches[0]['team_score']==rf and matches[0]['opponent_score']==ra and matches[0]['opponent']==official_opp
  is_source=team['slug']==home;my,other=(rf,ra) if is_source else (ra,rf)
  rows.append({'provider':'official_'+school,'source_game_id':school+'-'+gid,'team_id':team['team_id'],'team_name':team['name'],'conference':team['conference'],'opponent_id':'wn:'+ (opp if is_source else home),'opponent_name':official_opp if is_source else home.replace('-',' '),'non_d1_explicit':False,'game_date':'2023-02-19','time_precision':'date_only','status':'completed','source_result':f'official {school} {rf}-{ra}','score_basis':'official_schedule_supplement','timing_review':False,'outcome':'W' if my>other else 'L','runs_for':my,'runs_against':other,'source_location':None,'venue_text':None,'source_event_label':'','stage':'regular_season','stage_basis':'official_'+school+'_schedule','observation_basis':'derived_perspective_of_one_official_record_not_two_independent_observations','correction':{'action':'supplement_missing_game','reason':f'Provider schedules omit February 19 {home} {rf}–{ra} {opp}; official {school} schedule game {gid} supplies result.','evidence_refs':[source]},**source})
 return rows
if __name__=='__main__':
 (ROOT/'correction_registry.json').write_text(json.dumps(CORRECTIONS,indent=2))
