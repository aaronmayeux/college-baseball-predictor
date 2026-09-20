"""Legacy Sidearm schedule reader. Full dated links guard against wrong-year pages."""
import re,html,datetime

def clean(s):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def extract(text):
 rows=[]
 for block in re.split(r'<li\b[^>]*class="sidearm-schedule-game\s',text)[1:]:
  result=re.search(r'<div class="sidearm-schedule-game-result[^>]*>(.*?)</div>',block,re.S)
  opponent=re.search(r'<div class="sidearm-schedule-game-opponent-name[^>]*>(.*?)</div>',block,re.S)
  date=re.search(r'on ([A-Z][a-z]+ \d{1,2}, 20\d{2})',block)
  gid=re.search(r'data-game-id="(\d+)"',block)
  if not all([result,opponent,date,gid]):continue
  score=re.search(r'\b([WLT]),?\s*(\d+)\s*-\s*(\d+)',clean(result[1]))
  if not score:continue
  rows.append({'date':datetime.datetime.strptime(date[1],'%B %d, %Y').date().isoformat(),'team_score':int(score[2]),'opponent_score':int(score[3]),'opponent':clean(opponent[1]),'outcome':score[1],'official_game_id':gid[1],'tournament':None})
 return rows
