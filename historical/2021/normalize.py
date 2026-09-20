"""Parse cached 2021 Warren Nolan schedules and reconcile reciprocal observations.
No source ratings or end-season statistics are model features.
"""
import re,json,html,datetime,calendar,collections,hashlib
from fetch import ROOT
from collect import clean

def first(s,pat):
 m=re.search(pat,s,re.S);return clean(m.group(1)) if m else None

def parse(t):
 p=ROOT/'raw'/(t['slug']+'.html')
 if not p.exists():return []
 s=re.sub(r'<!--.*?-->','',p.read_text(errors='replace'),flags=re.S)
 # Adapt the older CSS names in memory; raw response stays unchanged.
 for old,new in [('schedule-special-game-end','team-schedule__special--end'),('schedule-special-game','team-schedule__special--start'),('class="schedule"','class="team-schedule"'),('game-date-day','game-date--day'),('game-date-month','game-date--month'),('schedule-result','team-schedule__result'),('schedule-location','team-schedule__location'),('schedule-info','team-schedule__info'),('class="opp-line"','class="team-schedule__opp-line"')]:
  s=s.replace(old,new)
 m=json.loads(p.with_name(p.name+'.meta.json').read_text());out=[];label=''
 for attrs,body in re.findall(r'<li\b([^>]*)>(.*?)</li>',s,re.S):
  cls=first(attrs,r'class="([^"]+)"') or ''
  if cls=='team-schedule__special--start':label=clean(body);continue
  if cls=='team-schedule__special--end':label='';continue
  if cls!='team-schedule':continue
  day=first(body,r'game-date--day">(.*?)</span>');month=first(body,r'game-date--month">(.*?)</span>')
  try:date=datetime.date(2021,list(calendar.month_abbr).index(month.title()),int(day)).isoformat()
  except Exception:date=None
  opp=first(body,r'opp-line-link"[^>]*>(.*?)</a>') or first(body,r'team-schedule__opp-line">(.*?)</span>')
  oppid=re.search(r'opp-line-link"[^>]+href="/baseball/2021/schedule/([^"/]+)"',body)
  gid=first(body,r'id="(\d+)-schedule-toggle"')
  result=first(body,r'<div class="team-schedule__result[^>]*>(.*?)</div>') or ''
  score=re.search(r'\b([WLT])\s+(\d+)\s*-\s*(\d+)',result)
  score_basis='result_text'
  if not score and result=='Final':
   lines={}
   for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',body,re.S):
    cells=re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)
    if len(cells)>=4 and all(clean(c).isdigit() for c in cells[-3:]):
     lines[clean(cells[0])]=int(clean(cells[-3]))
   if t['name'] in lines and opp in lines and len(lines)==2:
    rf,ra=lines[t['name']],lines[opp]
    score=(None,'W' if rf>ra else 'L' if rf<ra else 'T',str(rf),str(ra))
    score_basis='completed_Final_labeled_line_score'
  stage='regular_season'
  if 'Super Regional' in label:stage='super_regional'
  elif 'Regional' in label:stage='regional'
  elif 'CWS Championship' in label:stage='championship_series'
  elif 'College World Series' in label:stage='omaha'
  elif 'Tournament' in label and date and date>='2021-05-01':stage='conference_tournament'
  elif date and date>='2021-06-04':stage='late_season_unclassified'
  basis='source_event_label' if label and stage!='regular_season' else 'absence_of_postseason_label'
  out.append({'provider':'warren_nolan','source_game_id':gid,'team_id':t['team_id'],'team_name':t['name'],'conference':t['conference'],'opponent_id':'wn:'+oppid[1] if oppid else None,'opponent_name':opp,'non_d1_explicit':'Non Div I' in body,'game_date':date,'time_precision':'date_only','status':'completed' if score else 'not_scored','source_result':result,'score_basis':score_basis,'timing_review':bool(re.search(r'suspend|resum|forfeit|no.contest',clean(body),re.I)),'outcome':score[1] if score else None,'runs_for':int(score[2]) if score else None,'runs_against':int(score[3]) if score else None,'source_location':first(body,r'<div class="team-schedule__location[^>]*>(.*?)</div>'),'venue_text':first(body,r'<div class="team-schedule__info[^>]*>(.*?)</div>'),'source_event_label':label,'stage':stage,'stage_basis':basis,'source_url':m['url'],'retrieved_at':m['retrieved_at'],'raw_sha256':m['sha256'],'raw_path':m['raw_path']})
 return out

def run():
 teams=json.loads((ROOT/'teams.json').read_text());ids={t['team_id'] for t in teams};rows=[];coverage=[]
 for t in teams:
  rs=parse(t);rows+=rs;fs=[r for r in rs if r['status']=='completed' and r['opponent_id'] in ids and not r['non_d1_explicit']]
  counts=collections.Counter(r['outcome'] for r in fs);record=f"{counts['W']}-{counts['L']}"+(f"-{counts['T']}" if counts['T'] else '')
  coverage.append(dict(t,schedule_rows=len(rs),completed_d1=len(fs),parsed_record=record,record_matches=record==t['reference_record'],completed_non_d1=sum(r['status']=='completed' and r['non_d1_explicit'] for r in rs),missing_opponent_ids=sum(r['status']=='completed' and not r['non_d1_explicit'] and r['opponent_id'] not in ids for r in rs)))
 groups=collections.defaultdict(list);excluded=[]
 for r in rows:
  if r['status']!='completed' or r['non_d1_explicit'] or r['opponent_id'] not in ids or not r['source_game_id']:excluded.append(r);continue
  groups[r['source_game_id']].append(r)
 games=[];issues=[]
 for gid,rs in groups.items():
  rs.sort(key=lambda r:r['team_id']);a=rs[0];errs=[]
  if len(rs)!=2:errs.append('observation_count_'+str(len(rs)))
  else:
   b=rs[1]
   if a['team_id']!=b['opponent_id'] or a['opponent_id']!=b['team_id']:errs.append('team_mismatch')
   if a['runs_for']!=b['runs_against'] or a['runs_against']!=b['runs_for']:errs.append('score_mismatch')
   if a['game_date']!=b['game_date']:errs.append('date_mismatch')
   if a['stage']!=b['stage']:errs.append('stage_mismatch')
  if not a['game_date']:errs.append('missing_date')
  for r in rs:
   expected='W' if r['runs_for']>r['runs_against'] else 'L' if r['runs_for']<r['runs_against'] else 'T'
   if r['outcome']!=expected:errs.append('outcome_mismatch')
  game={'game_id':'wn:2021:'+gid,'season':2021,'game_date':a['game_date'],'team_a_id':a['team_id'],'team_b_id':a['opponent_id'],'runs_a':a['runs_for'],'runs_b':a['runs_against'],'tie':a['outcome']=='T','stage':a['stage'],'stage_basis':a['stage_basis'],'source_event_label':a['source_event_label'],'venue_text':a['venue_text'],'actual_home_team_id':None,'venue_verification':'unverified','timing_review':any(r.get('timing_review',False) for r in rs),'score_bases':sorted(set(r.get('score_basis','result_text') for r in rs)),'observation_count':len(rs),'reciprocal_check':'pass' if not errs else 'review','issues':errs,'observation_refs':[{'team_id':r['team_id'],'source_url':r['source_url'],'raw_path':r['raw_path'],'raw_sha256':r['raw_sha256'],'retrieved_at':r['retrieved_at']} for r in rs]}
  games.append(game)
  if errs:issues.append(game)
 games.sort(key=lambda g:(g['game_date'] or '',g['game_id']))
 # Collision audit: same date and teams can legitimately represent a doubleheader.
 same=collections.defaultdict(list)
 for g in games:same[(g['game_date'],*sorted([g['team_a_id'],g['team_b_id']]))].append(g['game_id'])
 doubles=[{'date':k[0],'teams':k[1:],'game_ids':v} for k,v in same.items() if len(v)>1]
 for name,obj in [('observations',rows),('team_coverage',coverage),('games',games),('issues',issues),('excluded_observations',excluded),('same_day_matchups',doubles)]:
  (ROOT/(name+'.json')).write_text(json.dumps(obj,indent=2))
 stats={'teams_expected':len(teams),'teams_parsed':sum(x['schedule_rows']>0 for x in coverage),'teams_record_matches':sum(x['record_matches'] for x in coverage),'observations':len(rows),'unique_completed_d1_games':len(games),'reciprocal_pass':sum(g['reciprocal_check']=='pass' for g in games),'issues':len(issues),'ties':sum(g['tie'] for g in games),'stages':dict(collections.Counter(g['stage'] for g in games)),'not_scored_statuses':dict(collections.Counter(r['source_result'] for r in rows if r['status']!='completed')),'completed_non_d1_observations':sum(r['status']=='completed' and r['non_d1_explicit'] for r in rows),'same_day_matchup_groups':len(doubles)}
 (ROOT/'summary.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
if __name__=='__main__':run()
