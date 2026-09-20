"""Cached deterministic rebuild; --collect downloads only missing season schedules."""
import argparse,pathlib,subprocess,sys,hashlib,json
ROOT=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--collect',action='store_true');args=ap.parse_args()
if not (ROOT/'2025/games.json').exists() or not (ROOT/'research/raw').is_dir():
 raise SystemExit('Data snapshot missing. Run: python3 scripts/restore_data.py /path/to/College_Baseball_Historical_Baseline_Bundle.zip')
def run(script):subprocess.run([sys.executable,str(ROOT/script)],check=True)
run('verify_corrections.py')
for y in range(2021,2025):
 if args.collect:run(f'{y}/collect.py')
 run(f'{y}/normalize.py')
run('reconcile.py');run('official_checks.py');run('eligibility.py');run('test_baseline.py');run('baseline.py');run('build_database.py');run('write_report.py')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and p.suffix in ['.py','.json','.csv','.md'] and p.name!='manifest.json' and '__pycache__' not in str(p)}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
