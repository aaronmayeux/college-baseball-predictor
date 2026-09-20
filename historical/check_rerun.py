"""Check cached deterministic rebuild, including predictions and correction ledgers."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
paths=[ROOT/str(y)/name for y in range(2021,2025) for name in ['games.json','observations.json','team_coverage.json','excluded_observations.json']]
paths += [ROOT/n for n in ['team_crosswalk.json','forecast_eligibility.csv','predictions.csv','baseline_metrics.json','calibration.json','official_comparison_2021_2024.json']]
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes()
with (ROOT/'cached_rerun_log.txt').open('w') as f:subprocess.run([sys.executable,str(ROOT/'run.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
after=hashes();checks={p:before[p]==after[p] for p in before}
(ROOT/'rerun_validation.json').write_text(json.dumps({'pass':all(checks.values()),'checks':checks,'before':before,'after':after},indent=2));assert all(checks.values()),checks
print('Cached rebuild reproduced',len(checks),'normalized and prediction artifacts byte-for-byte')
