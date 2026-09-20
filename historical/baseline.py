"""Fixed neutral Elo. Chronological, conservative two-day availability; no tuning."""
import collections,csv,datetime as dt,itertools,json,math,pathlib
from eligibility import available_at,reject,NCAA
from reconcile import internal
ROOT=pathlib.Path(__file__).resolve().parent
class State:
 def __init__(self,k=20):self.r=collections.defaultdict(lambda:1500.);self.w=collections.defaultdict(float);self.n=collections.defaultdict(int);self.k=k
 def regress(self):
  self.r={t:1500.+.5*(v-1500.) for t,v in self.r.items()};self.r=collections.defaultdict(lambda:1500.,self.r)
  self.w=collections.defaultdict(float);self.n=collections.defaultdict(int)
 def p(self,a,b):return 1/(1+10**((self.r[b]-self.r[a])/400))
 def wp(self,a,b):
  # Beta(1,1) smoothing, then odds comparison; only earlier eligible season results.
  x=(self.w[a]+1)/(self.n[a]+2);y=(self.w[b]+1)/(self.n[b]+2)
  return x*(1-y)/(x*(1-y)+y*(1-x))
 def update(self,gs):
  change=collections.defaultdict(float)
  for g in gs:
   a,b=g['a'],g['b'];out=.5 if g['tie'] else float(g['runs_a']>g['runs_b']);v=self.k*(out-self.p(a,b));change[a]+=v;change[b]-=v
   self.w[a]+=out;self.w[b]+=1-out;self.n[a]+=1;self.n[b]+=1
  for t,v in change.items():self.r[t]+=v

def load_games(y):
 gs=json.loads((ROOT/str(y)/'games.json').read_text())
 for g in gs:g['a']=internal(g['team_a_id'].removeprefix('wn:'));g['b']=internal(g['team_b_id'].removeprefix('wn:'))
 return gs

def predict(g,state,mode,cutoff):
 return {'season':g['season'],'mode':mode,'game_id':g['game_id'],'game_date':g['game_date'],'stage':g['stage'],'forecast_cutoff':cutoff,'team_a_id':g['a'],'team_b_id':g['b'],'outcome':.5 if g['tie'] else int(g['runs_a']>g['runs_b']),'tie':g['tie'],'elo':state.p(g['a'],g['b']),'win_rate':state.wp(g['a'],g['b']),'coin':.5}

def metric(rows,key):
 rows=[r for r in rows if not r['tie']];n=len(rows)
 if not n:return {'n':0}
 ps=[min(1-1e-12,max(1e-12,r[key])) for r in rows];ys=[r['outcome'] for r in rows]
 return {'n':n,'log_loss':-sum(y*math.log(p)+(1-y)*math.log(1-p) for y,p in zip(ys,ps))/n,'brier':sum((p-y)**2 for y,p in zip(ys,ps))/n,'accuracy':sum(.5 if p==.5 else float((p>.5)==bool(y)) for y,p in zip(ys,ps))/n}

def daily(gs,state):
 valid=[g for g in gs if g['reciprocal_check']=='pass' and not g.get('timing_review') and g['stage']!='late_season_unclassified']
 groups=[(day,list(a)) for day,a in itertools.groupby(sorted(valid,key=lambda g:g['game_date']),lambda g:g['game_date'])];done=0;preds=[]
 for day,today in groups:
  cutoff=dt.datetime.fromisoformat(day+'T00:00:00+00:00')
  while done<len(groups) and available_at(groups[done][1][0])<=cutoff:
   state.update(groups[done][1]);done+=1
  preds += [predict(g,state,'daily_updated',cutoff.isoformat()) for g in today]
 # Include final season results only after all predictions, for the following year's state.
 for _,batch in groups[done:]:state.update(batch)
 return preds

def frozen(gs,state,mode,cutoff,stages):
 valid=[g for g in gs if reject(g,cutoff,stages) is None]
 for _,a in itertools.groupby(sorted(valid,key=lambda g:g['game_date']),lambda g:g['game_date']):state.update(list(a))
 rows=[predict(g,state,mode,cutoff.isoformat()) for g in gs if g['stage'] in NCAA and g['reciprocal_check']=='pass' and not g.get('timing_review') and dt.datetime.fromisoformat(g['game_date']+'T00:00:00+00:00')>cutoff]
 return rows

def run():
 audit=json.loads((ROOT/'coverage_validation.json').read_text())
 if len(audit)!=5 or not all(a['pass'] for a in audit):raise RuntimeError('Coverage gate failed; do not evaluate')
 if not json.loads((ROOT/'correction_evidence_checks.json').read_text())['pass']:raise RuntimeError('Correction evidence gate failed')
 official=json.loads((ROOT/'official_comparison_2021_2024.json').read_text())
 if any('error' not in r and (r['matched_rows']+r.get('quarantined_date_rows',0)!=r['official_scored_rows'] or r['matched_rows']+r.get('quarantined_date_rows',0)!=r['provider_scored_rows']) for r in official):raise RuntimeError('Independent comparison mismatch')
 if not all(any(r['season']==y and r.get('matched_rows',0)>0 for r in official) for y in range(2021,2025)):raise RuntimeError('Missing independent sample')
 contract=json.loads((ROOT/'cutoffs.json').read_text());rolling=State();frozen_states={m:State() for m in contract['modes']};preds=[]
 for y in range(2021,2026):
  gs=load_games(y)
  if y>2021:
   rolling.regress()
   for st in frozen_states.values():st.regress()
  preds+=daily(gs,rolling)
  for mode,st in frozen_states.items():
   cut=dt.datetime.fromisoformat(contract['seasons'][str(y)]['forecast_cutoff'])
   preds+=frozen(gs,st,mode,cut,contract['modes'][mode])
 with (ROOT/'predictions.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(preds[0]));w.writeheader();w.writerows(preds)
 metrics=[];cal=[]
 for y in range(2021,2026):
  for mode in ['daily_updated',*contract['modes']]:
   rows=[r for r in preds if r['season']==y and r['mode']==mode]
   for subset in ['all','ncaa'] if mode=='daily_updated' else ['ncaa']:
    sample=[r for r in rows if subset=='all' or r['stage'] in NCAA]
    metrics.append({'season':y,'role':'initialization' if y==2021 else 'development' if y==2025 else 'chronological_validation_fixed_parameters','mode':mode,'subset':subset,**{k:metric(sample,k) for k in ['elo','win_rate','coin']}})
   for lo in range(0,10):
    a=[r for r in rows if not r['tie'] and lo/10<=r['elo']<(lo+1)/10]
    if a:cal.append({'season':y,'mode':mode,'bin_lower':lo/10,'n':len(a),'mean_predicted':sum(r['elo'] for r in a)/len(a),'observed_win_fraction':sum(r['outcome'] for r in a)/len(a)})
 (ROOT/'baseline_metrics.json').write_text(json.dumps(metrics,indent=2));(ROOT/'calibration.json').write_text(json.dumps(cal,indent=2))
 print(json.dumps(metrics,indent=2))
if __name__=='__main__':run()
