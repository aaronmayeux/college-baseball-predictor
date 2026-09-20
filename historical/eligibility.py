"""Produce explicit game-by-mode cutoff decisions, preserving exclusions."""
import datetime as dt,json,pathlib,csv
ROOT=pathlib.Path(__file__).resolve().parent
UTC=dt.timezone.utc
NCAA={'regional','super_regional','omaha','championship_series'}
def available_at(g):return dt.datetime.combine(dt.date.fromisoformat(g['game_date'])+dt.timedelta(days=2),dt.time(),UTC)
def reject(g,cutoff,stages):
 if g.get('reciprocal_check')!='pass':return 'reciprocal_conflict'
 if g.get('timing_review'):return 'suspension_or_result_timing_needs_review'
 if not g.get('game_date'):return 'missing_game_date'
 if g['stage'] not in stages:return 'excluded_phase:'+g['stage']
 if available_at(g)>cutoff:return 'after_cutoff_with_two_day_lag'
 return None
def run():
 contract=json.loads((ROOT/'cutoffs.json').read_text());out=[]
 for y in range(2021,2026):
  gs=json.loads((ROOT/str(y)/'games.json').read_text());cut=dt.datetime.fromisoformat(contract['seasons'][str(y)]['forecast_cutoff'])
  for g in gs:
   for mode,stages in contract['modes'].items():
    reason=reject(g,cut,stages)
    out.append({'season':y,'game_id':g['game_id'],'game_date':g['game_date'],'phase':g['stage'],'mode':mode,'forecast_cutoff':cut.isoformat(),'assumed_available_at':available_at(g).isoformat() if g['game_date'] else None,'eligible_reconstruction':reason is None,'point_in_time_certified':False,'exclusion_reason':reason or '', 'provenance_ref':str(y)+'/games.json#'+g['game_id']})
 with (ROOT/'forecast_eligibility.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 summary=[]
 from collections import Counter
 for y in range(2021,2026):
  for mode in contract['modes']:
   rows=[r for r in out if r['season']==y and r['mode']==mode]
   summary.append({'season':y,'mode':mode,'eligible':sum(r['eligible_reconstruction'] for r in rows),'exclusions':dict(Counter(r['exclusion_reason'] for r in rows if not r['eligible_reconstruction']))})
 (ROOT/'cutoff_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
