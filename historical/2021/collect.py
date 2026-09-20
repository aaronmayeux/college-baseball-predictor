"""2021 results coverage pilot. Cached raw pages; no model fitting."""
import re,html,json,time,concurrent.futures
from fetch import fetch,ROOT

def clean(s):return ' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).split())
def roster():
 b,m=fetch('rpi.html','https://www.warrennolan.com/baseball/2021/rpi-live');s=re.sub(r'<!--.*?-->','',b.decode('utf-8',errors='replace'),flags=re.S);out=[]
 for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',s,re.S):
  a=re.search(r'<a[^>]+href="/baseball/2021/schedule/([^"/]+)"[^>]*>([^<]+)</a>',row)
  if not a:continue
  tds=re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.S)
  if len(tds)<3:continue
  team_cell=next(i for i,c in enumerate(tds) if re.search(r'>[^<]+</a>',c) and '/schedule/' in c)
  rec=clean(tds[team_cell+1]);conf=re.search(r'<span[^>]*>(.*?)</span>',tds[team_cell],re.S)
  assert re.fullmatch(r'\d+-\d+(?:-\d+)?',rec),rec
  out.append({'team_id':'wn:'+a[1],'slug':a[1],'name':clean(a[2]),'season':2021,'conference':re.sub(r'\s*\([\d-]+\)$','',clean(conf[1])) if conf else None,'reference_record':rec})
 assert len({x['slug'] for x in out})==len(out) and len(out)>290
 (ROOT/'teams.json').write_text(json.dumps(out,indent=2));return out

def download(t):
 time.sleep(.3)
 _,m=fetch(t['slug']+'.html','https://www.warrennolan.com/baseball/2021/schedule/'+t['slug']);return t['slug'],m
if __name__=='__main__':
 ts=roster();print('Teams discovered:',len(ts),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for i,(slug,m) in enumerate(pool.map(download,ts),1):
   if i%20==0 or 'error' in m:print(i,slug,m.get('error','downloaded'),flush=True)
 print('Collection finished',flush=True)
