"""Reproduce official schedule comparisons; raw HTML is cached by research collectors."""
import pathlib,re,json,collections
ROOT=pathlib.Path(__file__).resolve().parent
ALIASES={'CSUN':'Cal State Northridge',"Hawai'i":'Hawaii',"Saint Mary's":"Saint Mary's College",'University of Portland':'Portland','Miami':'Miami (FL)','UConn':'Connecticut','UAlbany':'Albany','LIU':'Long Island','Brigham Young':'BYU','UNCW':'UNC Wilmington','Army West Point':'Army','CSU Bakersfield':'Cal State Bakersfield','FDU':'Fairleigh Dickinson','Loyola Marymount':'Loyola-Marymount','McNeese State':'McNeese','Seattle':'Seattle University',"St. John's":"Saint John's"}
def opponent_key(s):
 s=re.sub(r'^(?:#\d+|\(\d+\))\s*','',s).strip()
 return ALIASES.get(s,s)
def extract(p):
 s=p.read_text();m=re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>',s,re.S)
 if not m:raise ValueError('Missing schedule structure: '+str(p))
 a=json.loads(m[1]);val=lambda v:a[v] if isinstance(v,int) and v>=0 else None
 rows=[]
 for x in a:
  if not isinstance(x,dict) or 'game_links' not in x or 'result' not in x:continue
  r=val(x['result']);opp=val(x['opponent'])
  if not isinstance(r,dict):continue
  score=val(r.get('team_score'));other=val(r.get('opponent_score'))
  if score is None or other is None or not str(score).isdigit() or not str(other).isdigit():continue
  tournament=val(x['tournament'])
  rows.append({'date':val(x['date'])[:10],'team_score':int(score),'opponent_score':int(other),'opponent':val(opp['title']),'outcome':val(r['status']),'official_game_id':val(x['id']),'tournament':val(tournament['title']) if isinstance(tournament,dict) else None})
 return rows
if __name__=='__main__':
 out=[]
 for y in range(2021,2025):
  if not (ROOT/str(y)/'observations.json').exists():continue
  obs=json.loads((ROOT/str(y)/'observations.json').read_text())
  for name,slug in [('oregon','Oregon-State'),('columbia','Columbia')]:
   p=ROOT/'research/raw'/f'{name}_{y}.html'
   try:rows=extract(p)
   except Exception as e:out.append({'season':y,'team':slug,'error':str(e)});continue
   if any(not r['date'].startswith(str(y)+'-') for r in rows):
    out.append({'season':y,'team':slug,'error':'requested_season_not_returned','observed_seasons':sorted(set(r['date'][:4] for r in rows))});continue
   wn=[r for r in obs if r['team_id']=='wn:'+slug and r['status']=='completed'];matches=[]
   for r in rows:
    ms=[x for x in wn if x['game_date']==r['date'] and x['runs_for']==r['team_score'] and x['runs_against']==r['opponent_score'] and opponent_key(r['opponent'])==opponent_key(x['opponent_name'])]
    candidates=[x for x in wn if x['runs_for']==r['team_score'] and x['runs_against']==r['opponent_score'] and opponent_key(r['opponent'])==opponent_key(x['opponent_name']) and x.get('timing_review')]
    matches.append(dict(r,quarantined_date_disagreement=(not ms and len(candidates)==1),quarantined_game_ids=[x['source_game_id'] for x in candidates] if not ms else [],matches=[{'game_id':x['source_game_id'],'stage':x['stage']} for x in ms]))
   out.append({'season':y,'team':slug,'official_scored_rows':len(rows),'provider_scored_rows':len(wn),'matched_rows':sum(len(r['matches'])==1 for r in matches),'quarantined_date_rows':sum(r['quarantined_date_disagreement'] for r in matches),'rows':matches,'source_url':json.loads(p.with_name(p.name+'.meta.json').read_text())['url']})
 (ROOT/'official_comparison_2021_2024.json').write_text(json.dumps(out,indent=2));print([{k:v for k,v in r.items() if k!='rows'} for r in out])
