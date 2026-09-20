"""Rebuild portable multi-season SQLite with identities, provenance and eligibility."""
import csv,json,os,pathlib,sqlite3
from reconcile import internal
ROOT=pathlib.Path(__file__).resolve().parent
if __name__=='__main__':
 tmp=ROOT/'historical.tmp.sqlite';tmp.unlink(missing_ok=True);con=sqlite3.connect(tmp)
 con.execute('PRAGMA foreign_keys=ON')
 con.executescript('''
 CREATE TABLE teams(team_id TEXT PRIMARY KEY, canonical_slug TEXT);
 CREATE TABLE team_seasons(season INTEGER, team_id TEXT REFERENCES teams, provider_id TEXT, provider_name TEXT, source_conference TEXT, identity_basis TEXT, identity_source TEXT, PRIMARY KEY(season,team_id));
 CREATE TABLE games(game_id TEXT PRIMARY KEY, season INTEGER, game_date TEXT, team_a_id TEXT, team_b_id TEXT, runs_a INTEGER, runs_b INTEGER, tie INTEGER, phase TEXT, source_json TEXT, FOREIGN KEY(season,team_a_id) REFERENCES team_seasons, FOREIGN KEY(season,team_b_id) REFERENCES team_seasons);
 CREATE TABLE observations(observation_id INTEGER PRIMARY KEY, season INTEGER, game_id TEXT, provider_team_id TEXT, source_url TEXT, retrieved_at TEXT, raw_path TEXT, raw_sha256 TEXT, source_json TEXT);
 CREATE TABLE forecast_eligibility(game_id TEXT REFERENCES games, mode TEXT, forecast_cutoff TEXT, assumed_available_at TEXT, eligible_reconstruction INTEGER, point_in_time_certified INTEGER, exclusion_reason TEXT, PRIMARY KEY(game_id,mode));
 CREATE TABLE metadata(key TEXT PRIMARY KEY, value_json TEXT);
 CREATE INDEX games_by_date ON games(season,game_date);
 CREATE INDEX observations_by_game ON observations(game_id);
 ''')
 cross=json.loads((ROOT/'team_crosswalk.json').read_text())
 for t in cross:
  con.execute('INSERT OR IGNORE INTO teams VALUES(?,?)',(t['internal_team_id'],t['canonical_slug']))
  con.execute('INSERT INTO team_seasons VALUES(?,?,?,?,?,?,?)',tuple(t[k] for k in ['season','internal_team_id','provider_id','provider_name','source_conference','identity_basis','identity_source']))
 for y in range(2021,2026):
  for g in json.loads((ROOT/str(y)/'games.json').read_text()):
   con.execute('INSERT INTO games VALUES(?,?,?,?,?,?,?,?,?,?)',(g['game_id'],y,g['game_date'],internal(g['team_a_id'].removeprefix('wn:')),internal(g['team_b_id'].removeprefix('wn:')),g['runs_a'],g['runs_b'],g['tie'],g['stage'],json.dumps(g)))
  for r in json.loads((ROOT/str(y)/'observations.json').read_text()):
   con.execute('INSERT INTO observations(season,game_id,provider_team_id,source_url,retrieved_at,raw_path,raw_sha256,source_json) VALUES(?,?,?,?,?,?,?,?)',(y,f"{'wn' if r['provider']=='warren_nolan' else 'official'}:{y}:{r['source_game_id']}",r['team_id'],r['source_url'],r['retrieved_at'],str(y)+'/'+r['raw_path'],r['raw_sha256'],json.dumps(r)))
 with (ROOT/'forecast_eligibility.csv').open() as f:
  for r in csv.DictReader(f):con.execute('INSERT INTO forecast_eligibility VALUES(?,?,?,?,?,?,?)',(r['game_id'],r['mode'],r['forecast_cutoff'],r['assumed_available_at'],r['eligible_reconstruction']=='True',False,r['exclusion_reason']))
 for name in ['cutoffs','coverage_validation','membership_changes','baseline_metrics']:
  p=ROOT/(name+'.json')
  if p.exists():con.execute('INSERT INTO metadata VALUES(?,?)',(name,p.read_text()))
 assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 assert not con.execute('PRAGMA foreign_key_check').fetchall()
 con.commit();print('Database games:',con.execute('SELECT count(*) FROM games').fetchone()[0]);con.close();os.replace(tmp,ROOT/'College_Baseball_Historical.sqlite')
