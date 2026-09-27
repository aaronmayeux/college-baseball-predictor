"""Bounded two-formula HAVOC screen; refuse fitting without chronological coverage."""
import argparse
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent/'scripts'))
import havoc_inputs as source
import team_runs as common
from reconcile import internal
from baseline import metric

OUT = ROOT/'havoc_output'
CANDIDATES = ('havoc', 'havoc_net_steals')
PROTOCOL = dict(version=1, train=[2021,2022], select=2023,
    mode='conference_inclusive', ridge=.01, candidates=list(CANDIDATES),
    sample={str(y):list(ts) for y,ts in source.SAMPLES.items()},
    minimum_training=16, minimum_each_training_year=4, minimum_selection=8,
    formulas=['(2*SB+BB+HBP)/K','(2*(SB-CS)+BB+HBP)/K'],
    scaling='training-only RMS of matchup differences',
    offset='unchanged frozen Elo log odds; no intercept',
    selection='both log_loss and Brier improve; order loss,Brier,name',
    max_final_run_delta=10, sensitivity='flagged_pairs_use_elo',
    later_scoring=False, promotion=False)


def lock(path, value):
    if path.exists() and common.fingerprint(common.read(path)) != common.fingerprint(value):
        raise ValueError('Existing lock differs; use a new explicitly versioned output directory')
    common.write(path, value)


def fingerprints(raw):
    result = common.inputs()
    for p in (Path(__file__), Path(source.__file__), ROOT.parent/'scripts/reconstruct_havoc_pilot.py'):
        result[str(p.relative_to(ROOT.parent))] = common.digest(p)
    result['protocol_text'] = common.fingerprint((ROOT.parent/'docs/Havoc_Chronological_Experiment.md').read_text().split('\n## Results',1)[0])
    result.update({'raw/'+str(p.relative_to(raw)):common.digest(p) for p in sorted(raw.rglob('*')) if p.is_file()})
    return result


def sample_row(prediction, features):
    a, b = (features.get(prediction[k]) for k in ('team_a_id','team_b_id'))
    covered = bool(a and b and a['values'] is not None and b['values'] is not None)
    return dict(prediction, covered=covered, flagged=bool((a or {}).get('flags') or (b or {}).get('flags')),
                differences={k:a['values'][k]-b['values'][k] for k in CANDIDATES} if covered else {})


def coverage_gate(rows):
    counts = {y:sum(r['covered'] and not r['tie'] and r['season']==y for r in rows) for y in (2021,2022,2023)}
    reasons = []
    if counts[2021]+counts[2022] < PROTOCOL['minimum_training']:
        reasons.append('fewer_than_16_covered_training_games')
    if any(counts[y] < PROTOCOL['minimum_each_training_year'] for y in (2021,2022)):
        reasons.append('fewer_than_4_covered_games_in_each_training_year')
    if counts[2023] < PROTOCOL['minimum_selection']:
        reasons.append('fewer_than_8_covered_selection_games')
    return dict(pass_gate=not reasons, covered_games=counts, reasons=reasons)


def prepare(raw):
    common.gates()
    before = fingerprints(raw)
    reconstructed = source.reconstruct(raw)
    predictions = common.read(ROOT/'validation_v2/output/frozen_predictions.json')
    samples, coverage = [], []
    for year in (2021,2022,2023):
        features = {internal(r['team_id'].removeprefix('wn:')):r for r in reconstructed['features'] if r['season']==year}
        rows = [sample_row(p,features) for p in predictions if p['season']==year and p['mode']==PROTOCOL['mode'] and not p['tie']]
        if len({r[k] for r in rows for k in ('team_a_id','team_b_id')}) != 64 or len({r['game_id'] for r in rows}) != len(rows):
            raise ValueError('Incomplete or duplicate baseline sample')
        samples.extend(rows)
        coverage.append(dict(season=year, targeted_teams=8, complete_batting=sum('final_counts' in r for r in features.values()),
            usable_teams=sum(r['values'] is not None for r in features.values()),
            covered_games=sum(r['covered'] for r in rows), fallback_games=sum(not r['covered'] for r in rows), games=len(rows)))
    data = dict(protocol=PROTOCOL, inputs=before, source=reconstructed, samples=samples,
                coverage=coverage, gate=coverage_gate(samples))
    if before != fingerprints(raw):
        raise ValueError('Inputs changed during preparation')
    lock(OUT/'prepared.json', data)
    print(__import__('json').dumps(dict(coverage=coverage,gate=data['gate']),indent=2))


def fit(rows, candidate):
    if candidate not in CANDIDATES or any(r['season'] not in (2021,2022) or r['tie'] for r in rows):
        raise ValueError('Invalid candidate or training chronology')
    rows = [r for r in rows if r['covered']]
    if not rows:
        raise ValueError('No training games')
    x = [r['differences'][candidate] for r in rows]
    scale = math.sqrt(sum(v*v for v in x)/len(x))
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError('No valid training variation')
    x = [v/scale for v in x]
    offsets = [math.log(r['elo']/(1-r['elo'])) for r in rows]
    def gradient(beta):
        return sum((common.sigmoid(o+beta*v)-r['outcome'])*v for o,v,r in zip(offsets,x,rows))/len(rows) + .01*beta
    lo, hi = -1., 1.
    while gradient(lo)>0: lo*=2
    while gradient(hi)<0: hi*=2
    for _ in range(60):
        mid = (lo+hi)/2
        if gradient(mid)>0: hi=mid
        else: lo=mid
    return dict(candidate=candidate, scale=scale, beta=(lo+hi)/2, n=len(rows), training_seasons=sorted({r['season'] for r in rows}))


def probability(row, model, strict=False):
    if not row['covered'] or (strict and row.get('flagged')):
        return row['elo']
    return common.sigmoid(math.log(row['elo']/(1-row['elo'])) + model['beta']*row['differences'][model['candidate']]/model['scale'])


def evaluate(raw):
    common.gates()
    data = common.read(OUT/'prepared.json')
    before = fingerprints(raw)
    if before != data['inputs'] or data['protocol'] != PROTOCOL:
        raise ValueError('Stale preparation')
    gate = coverage_gate(data['samples'])
    if not gate['pass_gate']:
        report = dict(status='blocked_insufficient_chronological_inputs', gate=gate,
                      coverage=data['coverage'], fitted=False, scored=False, promoted=False,
                      candidates={k:'untested' for k in CANDIDATES},
                      preparation_sha256=common.digest(OUT/'prepared.json'))
    else:
        train = [r for r in data['samples'] if r['season'] in (2021,2022)]
        selection = [r for r in data['samples'] if r['season']==2023]
        models = {k:fit(train,k) for k in CANDIDATES}
        results = {}
        for k,m in models.items():
            rows = [dict(r,challenger=probability(r,m)) for r in selection]
            strict_rows = [dict(r,challenger=probability(r,m,strict=True)) for r in selection]
            results[k] = dict(all=common.summarize(rows), covered=common.summarize([r for r in rows if r['covered']]),
                              flagged_pairs_use_elo=common.summarize(strict_rows))
        qualifying = [k for k,v in results.items() if all(v['all']['paired_delta'][s]<0 for s in ('log_loss','brier'))]
        winner = min(qualifying,key=lambda k:(results[k]['all']['metrics']['challenger']['log_loss'],results[k]['all']['metrics']['challenger']['brier'],k)) if qualifying else 'elo'
        report = dict(status='preliminary_screen_passed' if qualifying else 'closed_at_selection',
                      fitted=True, scored=True, promoted=False, winner=winner, models=models,
                      results=results, coverage=data['coverage'], gate=gate,
                      preparation_sha256=common.digest(OUT/'prepared.json'))
        lock(OUT/'selection_lock.json',report)
    if before != fingerprints(raw):
        raise ValueError('Inputs changed during evaluation')
    common.write(OUT/'report.json',report)
    print(__import__('json').dumps(report,indent=2))


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['prepare','evaluate'])
    ap.add_argument('--raw-dir',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=OUT)
    args=ap.parse_args()
    OUT=args.output.resolve()
    (prepare if args.command=='prepare' else evaluate)(args.raw_dir.resolve())
