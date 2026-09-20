import urllib.request,urllib.error,pathlib,json,datetime,hashlib,time
ROOT=pathlib.Path(__file__).resolve().parent
(ROOT/'raw').mkdir(exist_ok=True)
def fetch(key,url):
 path=ROOT/'raw'/key
 meta_path=path.with_name(path.name+'.meta.json')
 if path.exists() and meta_path.exists():return path.read_bytes(),json.loads(meta_path.read_text())
 m={'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'raw_path':'raw/'+key}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'CollegeBaseballResearch/0.1 (historical coverage audit)'})
  with urllib.request.urlopen(req,timeout=30) as r:
   b=r.read();m.update(http_status=r.status,content_type=r.headers.get('Content-Type'),final_url=r.url)
  path.write_bytes(b);m.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:
  b=b'';m['error']=str(e)
 meta_path.write_text(json.dumps(m,indent=2));return b,m
if __name__=='__main__':
 b,m=fetch('rpi.html','https://www.warrennolan.com/baseball/2022/rpi-live');print(m)
 b,m=fetch('LSU.html','https://www.warrennolan.com/baseball/2022/schedule/LSU');print(m)
