"""Nolan schedule parser adapted from the preserved 2024 parser.

Raw source observations only. Missing dates, ambiguous phases and source conflicts
are retained for staging; no official corrections are silently applied.
"""
import re
import html
import datetime
import calendar


def clean(s):
 return ' '.join(html.unescape(re.sub('<[^>]+>', ' ', s)).split())


def first(s,pat):
 m=re.search(pat,s,re.S)
 return clean(m.group(1)) if m else None


def parse(t, source, m, season, opening_date):
 s=re.sub(r'<!--.*?-->', '', source, flags=re.S)
 headers=[clean(x) for x in re.findall(r'<h2[^>]*>(.*?)</h2>',s,re.S)]
 prefix=f"{season} {t['name']} "
 if not any(h.startswith(prefix) and h.endswith(' Schedule') for h in headers):
  raise ValueError('Missing requested season/team schedule heading')
 out=[];label='' 
 for attrs,body in re.findall(r'<li\b([^>]*)>(.*?)</li>',s,re.S):
  cls=first(attrs,r'class="([^"]+)"') or ''
  if cls=='team-schedule__special--start':label=clean(body);continue
  if cls=='team-schedule__special--end':label='';continue
  if cls!='team-schedule':continue
  day=first(body,r'game-date--day">(.*?)</span>');month=first(body,r'game-date--month">(.*?)</span>')
  try:date=datetime.date(season,list(calendar.month_abbr).index(month.title()),int(day)).isoformat()
  except Exception:date=None
  opp=first(body,r'opp-line-link"[^>]*>(.*?)</a>') or first(body,r'team-schedule__opp-line">(.*?)</span>')
  oppid=re.search(rf'opp-line-link"[^>]+href="/baseball/{season}/schedule/([^"/]+)"',body)
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
  elif 'Tournament' in label and date and date>=f'{season}-05-01':stage='conference_tournament'
  elif date and date>=opening_date:stage='late_season_unclassified'
  basis='source_event_label' if label and stage!='regular_season' else 'absence_of_postseason_label'
  out.append({'provider':'warren_nolan','source_game_id':gid,'team_id':t['team_id'],'team_name':t['name'],'conference':t['conference'],'opponent_id':'wn:'+oppid[1] if oppid else None,'opponent_name':opp,'non_d1_explicit':'Non Div I' in body,'game_date':date,'time_precision':'date_only','status':'completed' if score else 'not_scored','source_result':result,'score_basis':score_basis,'timing_review':bool(re.search(r'suspend|resum|forfeit|no.contest',clean(body),re.I)),'outcome':score[1] if score else None,'runs_for':int(score[2]) if score else None,'runs_against':int(score[3]) if score else None,'source_location':first(body,r'<div class="team-schedule__location[^>]*>(.*?)</div>'),'venue_text':first(body,r'<div class="team-schedule__info[^>]*>(.*?)</div>'),'source_event_label':label,'stage':stage,'stage_basis':basis,'source_url':m['url'],'retrieved_at':m['retrieved_at'],'raw_sha256':m['sha256'],'raw_path':m['raw_path']})
 if not out:raise ValueError('No schedule rows; refuse empty/changed source format')
 ids=[r['source_game_id'] for r in out if r['source_game_id']]
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate source game IDs')
 return out
