"""Locked team-run candidate: historical regional advancement, no fitting."""
import argparse
import collections
import datetime as dt
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'validation_v2'))
from tournament.engine import group_probabilities, next_game
from baseline import State, frozen, load_games
from validation_v2 import seeds
from validation_v2.evidence import overlay
import team_runs as runs

OUT = runs.ROOT / 'regional_output'
PROTOCOL = dict(version=1, seasons=[2023, 2024], primary=2024,
    models=['elo', 'challenger', 'seed'], bootstrap_samples=5000, bootstrap_seed=20240926,
    brier='sum of four squared errors per regional', picks='highest advancement probability; fractional exact ties',
    uncertainty='paired regional clusters, exploratory within-season only')


def fingerprints():
    paths = [runs.ROOT / 'team_run_output' / n for n in
             ('prepared.json', 'selection_lock.json', 'report.json', 'predictions.json')]
    paths += [Path(__file__), runs.ROOT.parent / 'tournament/engine.py',
              runs.ROOT / 'validation_v2/seeds.py']
    for year in PROTOCOL['seasons']:
        paths += [runs.ROOT / f'{year}/teams.json']
        for name in (f'ncaa_{year}.pdf', f'ncaa_selections_{year}.html'):
            paths += [runs.ROOT / 'research/raw' / name, runs.ROOT / 'research/raw' / (name+'.meta.json')]
    return {str(p.relative_to(runs.ROOT.parent)): runs.digest(p) for p in paths}


def regions(selected, year):
    rows = [r for r in selected if r['season'] == year]
    groups = collections.defaultdict(dict)
    if len(rows) != 64 or len({r['team_id'] for r in rows}) != 64:
        raise ValueError('Incomplete or duplicate selection field')
    for row in rows:
        group = groups[row['regional']]
        if row['regional_seed'] in group:
            raise ValueError('Duplicate seed')
        group[row['regional_seed']] = row['team_id']
    if len(groups) != 16 or any(set(g) != {1,2,3,4} for g in groups.values()):
        raise ValueError('Invalid regional groups')
    return [dict(name=name, teams=[g[i] for i in (1,4,2,3)], seeds={g[i]:i for i in g})
            for name,g in sorted(groups.items())]


def qualified_inputs():
    refs = runs.gates()
    prepared = runs.read(runs.OUT / 'prepared.json')
    lock = runs.read(runs.OUT / 'selection_lock.json')
    if prepared['inputs'] != runs.inputs() or lock['preparation_sha256'] != runs.digest(runs.OUT / 'prepared.json'):
        raise ValueError('Original experiment inputs/lock changed')
    if runs.fingerprint(prepared['protocol']) != runs.fingerprint(runs.PROTOCOL):
        raise ValueError('Original protocol changed')
    if runs.read(runs.OUT / 'report.json')['lock'] != lock:
        raise ValueError('Original evaluation lock mismatch')
    # Manuals were read against the engine; hashes bind the reviewed rule evidence.
    for year in PROTOCOL['seasons']:
        path = runs.ROOT / 'research/raw' / f'ncaa_{year}.pdf'
        meta = runs.read(path.with_name(path.name+'.meta.json'))
        if meta['sha256'] != runs.digest(path) or meta.get('http_status') != 200:
            raise ValueError('Invalid retained NCAA manual')
    return refs, prepared, lock


def prepare():
    refs, prepared, lock = qualified_inputs()
    before = fingerprints()
    contract = runs.read(runs.ROOT / 'cutoffs.json')
    selected = seeds.load(contract)  # Reparse retained articles; verify hashes and cutoffs.
    features = {(r['season'],r['mode'],r['team_id']):r for r in prepared['features']}
    old = {(r['season'],r['mode'],r['game_id']):r for r in prepared['samples']}
    expected = {(r['season'],r['mode'],r['game_id']):r for r in runs.read(runs.OUT / 'predictions.json')}
    result = dict(protocol=PROTOCOL, inputs=before, forecasts=[], equivalence_checks=0)
    for mode in contract['modes']:
        state = State()
        for year in range(2021,2025):
            if year > 2021:
                state.regress()
            cutoff = dt.datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
            games = overlay(load_games(year), refs)
            observed = frozen(games, state, mode, cutoff, contract['modes'][mode])
            if year not in PROTOCOL['seasons']:
                continue
            candidate = lock['winner']
            model = lock['training_models'][candidate] if year == 2023 and candidate != 'elo' else lock['refitted_model']
            def pair(a,b):
                if not state.n.get(a) or not state.n.get(b):
                    raise ValueError('Missing eligible current-season history')
                row = dict(elo=state.p(a,b), differences={k:features[year,mode,a][k]-features[year,mode,b][k] for k in runs.CANDIDATES})
                return row['elo'], runs.probability(row, model)
            for row in observed:
                key = year,mode,row['game_id']
                p,q = pair(row['team_a_id'],row['team_b_id'])
                if abs(p-old[key]['elo']) > 1e-14 or abs(q-expected[key]['challenger']) > 1e-14:
                    raise ValueError('Frozen pair differs from locked experiment')
                result['equivalence_checks'] += 1
            for region in regions(selected, year):
                pairs = {(a,b):pair(a,b) for a in region['teams'] for b in region['teams'] if a!=b}
                probabilities = {}
                for key in PROTOCOL['models']:
                    def p(a,b):
                        return seeds.probability(region['seeds'][a],region['seeds'][b]) if key=='seed' else pairs[a,b][0 if key=='elo' else 1]
                    probabilities[key] = group_probabilities(region['teams'], p)
                    if not math.isclose(sum(probabilities[key].values()),1,abs_tol=1e-12):
                        raise ValueError('Regional probability mass failed')
                result['forecasts'].append(dict(season=year, mode=mode, **region, probabilities=probabilities))
    if before != fingerprints():
        raise ValueError('Input changed during forecasting')
    path = OUT / 'forecast_lock.json'
    if path.exists() and runs.fingerprint(runs.read(path)) != runs.fingerprint(result):
        raise ValueError('Existing forecast lock differs; no silent overwrite')
    runs.write(path,result)
    print(f"Locked {len(result['forecasts'])} regional/mode forecasts; {result['equivalence_checks']} matching game probabilities")


def champion(entrants, games):
    """Find all legal paths; never break same-day ties by ID or row order."""
    if len(games) not in (6,7) or len({g['game_id'] for g in games}) != len(games):
        raise ValueError('Incomplete or duplicate regional results')
    if len(set(entrants)) != 4:
        raise ValueError('Invalid entrants')
    for g in games:
        if (g['a'] not in entrants or g['b'] not in entrants or g['a']==g['b'] or
            g['runs_a']==g['runs_b'] or g.get('tie') or g['reciprocal_check']!='pass' or
            g.get('timing_review') or g['stage']!='regional' or not g.get('game_date')):
            raise ValueError('Unqualified regional outcome')
    paths = []
    def visit(results, remaining, dates, used):
        pair = next_game(entrants,results)
        if pair is None:
            if not remaining:
                paths.append(dict(winner=results[-1][0], game_ids=used))
            return
        a,b = pair
        for i,g in enumerate(remaining):
            if {a,b} != {g['a'],g['b']}:
                continue
            if any(g['game_date'] < dates.get(t,'') for t in (a,b)):
                continue
            w,l = (g['a'],g['b']) if g['runs_a']>g['runs_b'] else (g['b'],g['a'])
            visit(results+[(w,l)],remaining[:i]+remaining[i+1:],dict(dates,**{a:g['game_date'],b:g['game_date']}),used+[g['game_id']])
    visit([],games,{},[])
    winners = {p['winner'] for p in paths}
    if len(winners)!=1:
        raise ValueError('Illegal or ambiguous regional path')
    return dict(winner=next(iter(winners)), legal_paths=len(paths), paths=sorted(paths,key=lambda p:p['game_ids']))


def score(probs, winner):
    if winner not in probs or len(probs)!=4 or not all(0<p<1 for p in probs.values()) or not math.isclose(sum(probs.values()),1,abs_tol=1e-12):
        raise ValueError('Invalid advancement distribution')
    best = max(probs.values())
    picks = [t for t,p in probs.items() if p==best]
    return dict(log_loss=-math.log(probs[winner]), brier=sum((p-int(t==winner))**2 for t,p in probs.items()),
                accuracy=1/len(picks) if winner in picks else 0)


def summary(rows):
    metrics = {m:{k:sum(r['scores'][m][k] for r in rows)/len(rows) for k in ('log_loss','brier','accuracy')} for m in PROTOCOL['models']}
    rng = random.Random(PROTOCOL['bootstrap_seed'])
    deltas = {k:[r['scores']['challenger'][k]-r['scores']['elo'][k] for r in rows] for k in ('log_loss','brier')}
    draws = {k:[] for k in deltas}
    for _ in range(PROTOCOL['bootstrap_samples']):
        ix = [rng.randrange(len(rows)) for _ in rows]
        for k,ds in deltas.items():
            draws[k].append(sum(ds[i] for i in ix)/len(ix))
    intervals = {k:[sorted(ds)[int((len(ds)-1)*q)] for q in (.025,.975)] for k,ds in draws.items()}
    calibration = {}
    for m in PROTOCOL['models']:
        values = [(p,int(t==r['winner'])) for r in rows for t,p in r['probabilities'][m].items()]
        bins = []
        for i in range(10):
            subset=[(p,y) for p,y in values if i/10<=p<(i+1)/10]
            if subset:
                bins.append(dict(lower=i/10,teams=len(subset),mean_probability=sum(p for p,y in subset)/len(subset),observed=sum(y for p,y in subset)/len(subset)))
        calibration[m]=bins
    return dict(regionals=len(rows),metrics=metrics,paired_delta={k:sum(ds)/len(ds) for k,ds in deltas.items()},
                exploratory_95pct_paired_regional_bootstrap=intervals,calibration=calibration)


def evaluate():
    refs,_,_ = qualified_inputs()
    locked = runs.read(OUT/'forecast_lock.json')
    before = fingerprints()
    if locked['inputs'] != before or runs.fingerprint(locked['protocol'])!=runs.fingerprint(PROTOCOL):
        raise ValueError('Forecast lock no longer matches')
    rows=[]
    for year in PROTOCOL['seasons']:
        games=overlay(load_games(year),refs)
        regional=[g for g in games if g['stage']=='regional']
        groups=[r for r in locked['forecasts'] if r['season']==year and r['mode']=='regular_only']
        covered=set(); winners=set(); outcomes={}
        for group in groups:
            match=[g for g in regional if g['a'] in group['teams'] and g['b'] in group['teams']]
            outcome=champion(group['teams'],match)
            outcomes[group['name']]=outcome
            covered.update(g['game_id'] for g in match)
            winners.add(outcome['winner'])
        if covered!={g['game_id'] for g in regional}:
            raise ValueError('Unassigned/cross-group regional game')
        supers={g[t] for g in games if g['stage']=='super_regional' for t in ('a','b')}
        if len(winners)!=16 or winners!=supers:
            raise ValueError('Regional champions disagree with super field')
        for forecast in locked['forecasts']:
            if forecast['season']!=year:
                continue
            outcome=outcomes[forecast['name']]
            scores={m:score(probs,outcome['winner']) for m,probs in forecast['probabilities'].items()}
            rows.append(dict(**forecast,**outcome,scores=scores))
    summaries=[dict(season=year,mode=mode,**summary([r for r in rows if r['season']==year and r['mode']==mode]))
               for year in PROTOCOL['seasons'] for mode in ('regular_only','conference_inclusive')]
    if before!=fingerprints():
        raise ValueError('Protected inputs changed')
    runs.write(OUT/'report.json',dict(protocol=PROTOCOL,forecast_sha256=runs.digest(OUT/'forecast_lock.json'),
        preserved_inputs_unchanged=True,promoted=False,regionals=rows,summaries=summaries))
    for r in summaries:
        print(r['season'],r['mode'],r['metrics'],r['paired_delta'],r['exploratory_95pct_paired_regional_bootstrap'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','evaluate'))
    args=parser.parse_args()
    (prepare if args.action=='prepare' else evaluate)()
