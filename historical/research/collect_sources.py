from fetch import fetch
from concurrent.futures import ThreadPoolExecutor
sources=[(f'ncaa_{y}.pdf',f'https://ncaaorg.s3.amazonaws.com/championships/sports/baseball/d1/{y-1}-{str(y)[2:]}D1MBA_PreChampsManual.pdf') for y in range(2021,2025)]
sources += [(f'oregon_{y}.html',f'https://osubeavers.com/sports/baseball/schedule/{y}') for y in range(2021,2025)]
sources += [(f'columbia_{y}.html',f'https://gocolumbialions.com/sports/baseball/schedule/{y}') for y in range(2021,2025)]
sources += [('hcu_history.html','https://hc.edu/about-hcu/history/'),('utah_history.html','https://about.utahtech.edu/history/'),('oregon_arizona_20220525.html','https://goducks.com/news/2022/5/25/baseball-ducks-drop-pac-12-tournament-opener.aspx')]
sources += [(name+'_2023.html',url) for name,url in [('ncstate','https://gopack.com/sports/baseball/schedule/2023'),('ecu','https://ecupirates.com/sports/baseball/schedule/2023'),('kent','https://kentstatesports.com/sports/baseball/schedule/2023'),('evansville','https://gopurpleaces.com/sports/baseball/schedule/2023'),('missouri','https://missouristatebears.com/sports/baseball/schedule/2023'),('charlotte','https://charlotte49ers.com/sports/baseball/schedule/2023'),('stjoseph','https://sjuhawks.com/sports/baseball/schedule/2023'),('fordham','https://fordhamsports.com/sports/baseball/schedule/2023'),('ohio','https://ohiostatebuckeyes.com/sports/baseball/schedule/2023'),('bgsu','https://bgsufalcons.com/sports/baseball/schedule/2023'),('southernindiana','https://usiscreamingeagles.com/sports/baseball/schedule/2023')]]
def run(x):
 b,m=fetch(*x);print(x[0],m.get('http_status'),len(b),m.get('error'),flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,sources))
