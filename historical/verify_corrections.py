"""Re-extract official correction evidence; fail if the asserted evidence changes."""
import json,pathlib,sys
from official_checks import extract,opponent_key
from research.parse_sidearm import extract as legacy
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE_NAMES=['ncstate','missouri','ecu','stjoseph','kent','evansville','charlotte','fordham','ohio','bgsu','southernindiana']
def run():
 data={};evidence=[]
 for n in SOURCE_NAMES:
  p=ROOT/'research/raw'/f'{n}_2023.html'
  try:rows=extract(p)
  except ValueError:rows=legacy(p.read_text())
  assert rows,n
  data[n]=rows;(ROOT/f'research/{n}_2023_games.json').write_text(json.dumps(rows,indent=2))
 for n,opp in {'ncstate':'Wagner','missouri':'Cal Poly','ecu':'George Washington','stjoseph':'Duke','kent':'Jacksonville','evansville':'Troy'}.items():
  a=[r for r in data[n] if r['date']=='2023-02-19'];assert len(a)==1 and opponent_key(a[0]['opponent'])==opp,(n,a)
  evidence.append({'school':n,'finding':'one official Feb 19 game, different opponent from excluded provider entry','record':a[0]})
 a=[r for r in data['charlotte'] if r['date']=='2023-06-03'];assert len(a)==1 and a[0]['team_score']==9 and a[0]['opponent_score']==2 and a[0]['outcome']=='W' and 'Lipscomb' in a[0]['opponent'];evidence.append({'finding':'Charlotte outcome correction','record':a[0]})
 a=[r for r in data['fordham'] if str(r['official_game_id'])=='10630'];assert len(a)==1 and a[0]['date']=='2023-02-19' and a[0]['team_score']==1 and a[0]['opponent_score']==13 and a[0]['opponent']=='Dallas Baptist';evidence.append({'finding':'missing game supplement','record':a[0]})
 a=[r for r in data['kent'] if r['date']=='2023-04-25'];b=[r for r in data['ohio'] if r['date']=='2023-04-26'];assert len(a)==1 and a[0]['team_score']==10 and a[0]['opponent_score']==5;assert len(b)==1 and b[0]['team_score']==5 and b[0]['opponent_score']==10
 evidence.append({'finding':'April 25/26 disagreement confirmed; quarantine from model','records':a+b})
 for n,gid,rf,ra,opp in [('bgsu','18523',10,4,'Tennessee Tech'),('southernindiana','10682',5,4,'Western Illinois University')]:
  a=[r for r in data[n] if str(r['official_game_id'])==gid];assert len(a)==1 and a[0]['date']=='2023-02-19' and (a[0]['team_score'],a[0]['opponent_score'],a[0]['opponent'])==(rf,ra,opp);evidence.append({'finding':'missing game supplement','record':a[0]})
 (ROOT/'correction_evidence_checks.json').write_text(json.dumps({'pass':True,'checks':evidence,'official_sources':SOURCE_NAMES,'limitation':'DBU official page returned 502; three supplemental games each use one official school schedule; two perspectives do not constitute independent reciprocal evidence.'},indent=2));print('Official correction evidence verified')
if __name__=='__main__':run()
