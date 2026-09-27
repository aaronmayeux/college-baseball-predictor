"""One locked schedule-aware OBP/ERA challenger; no baseline/app mutations."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
from itertools import groupby
import json
import math
from pathlib import Path

import team_components as components
from team_components import common, regional, seeds, State, load_games, overlay, reject, metric, group_probabilities

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'schedule_component_output'
KEYS = ['obp', 'era', 'schedule']
PROTOCOL = dict(version=1, train=[2021,2022], select=2023, validate=2024,
    candidate='components_schedule', keys=KEYS, ridge=.01, min_schedule_games=20,
    mode='conference_inclusive', scaling='covered training matchup RMS, no centering',
    schedule='game-weighted opponent Elo at NCAA snapshot date; prior-year baseline carry',
    diagnostics=['raw_locked','schedule_only','strict','without_2021'])


def fingerprints(evidence):
    result = components.fingerprints(evidence)
    for path in [Path(__file__), *sorted(components.OUT.glob('*.json'))]:
        result[str(path.relative_to(ROOT.parent))] = common.digest(path)
    text = (ROOT.parent / 'docs/Schedule_Adjusted_Components.md').read_text().split('\n## Results',1)[0]
    result['schedule_protocol'] = common.fingerprint(text)
    return result


def load_raw(evidence):
    refs = common.gates()
    data = common.read(components.OUT/'prepared.json')
    lock = common.read(components.OUT/'selection_lock.json')
    if data['inputs'] != components.fingerprints(evidence) or common.fingerprint(data['protocol']) != common.fingerprint(components.PROTOCOL):
        raise ValueError('Raw experiment inputs changed')
    if lock['prepared_sha256'] != common.digest(components.OUT/'prepared.json') or common.read(components.OUT/'report.json')['selection'] != lock:
        raise ValueError('Raw experiment lock mismatch')
    return refs, data, lock


def update_through(start, games, cutoff, stages, through):
    """Copy a season-start state; apply only eligible same-date batches through day."""
    state = deepcopy(start)
    eligible = [g for g in games if reject(g,cutoff,stages) is None and g['game_date']<=through]
    if len({g['game_id'] for g in eligible}) != len(eligible):
        raise ValueError('Duplicate eligible schedule game')
    for _,batch in groupby(sorted(eligible,key=lambda g:g['game_date']),lambda g:g['game_date']):
        state.update(list(batch))
    return state, eligible


def schedule_feature(team, games, state):
    appearances = [g for g in games if team in (g['a'],g['b'])]
    opponents = [g['b'] if g['a']==team else g['a'] for g in appearances]
    reasons=[]
    if len(appearances)<PROTOCOL['min_schedule_games']:
        reasons.append('insufficient_d1_schedule')
    if any(not state.n.get(t) or t not in state.r or not math.isfinite(state.r[t]) for t in opponents):
        reasons.append('missing_opponent_rating')
    return dict(value=None if reasons else sum(state.r[t] for t in opponents)/len(opponents),
        reasons=reasons, games=len(opponents), unique_opponents=len(set(opponents)),
        game_ids=sorted(g['game_id'] for g in appearances))


def pair(a,b,p,features,**extra):
    covered=all(features[t]['values'] is not None for t in (a,b))
    return dict(extra,elo=p,covered=covered,flagged=any(features[t]['flags'] for t in (a,b)),
        differences={k:features[a]['values'][k]-features[b]['values'][k] for k in KEYS} if covered else {})


def prepare(evidence):
    refs,raw,_=load_raw(evidence)
    before=fingerprints(evidence)
    contract=common.read(ROOT/'cutoffs.json')
    state=State()
    result=dict(protocol=PROTOCOL,inputs=before,features=[],samples=[],coverage=[],ratings={})
    for year in range(2021,2025):
        if year>2021: state.regress()
        games=overlay(load_games(year),refs)
        cutoff=datetime.fromisoformat(contract['seasons'][str(year)]['forecast_cutoff'])
        stages=contract['modes'][PROTOCOL['mode']]
        through=components.SNAPSHOTS[year][1]
        snapshot,eligible=update_through(state,games,cutoff,stages,through)
        # Independently advance full pre-NCAA state for the baseline and next year's carry.
        state,_=update_through(state,games,cutoff,stages,cutoff.date().isoformat())
        features={}
        for source in [r for r in raw['features'] if r['season']==year]:
            team=source['team_id']
            schedule=schedule_feature(team,eligible,snapshot)
            values=dict(source['values'],schedule=schedule['value']) if source['values'] is not None and not schedule['reasons'] else None
            features[team]=dict(source,values=values,reasons=source['reasons']+schedule['reasons'],schedule=schedule)
        if len(features)!=64: raise ValueError('Incomplete field')
        result['features'].extend(features.values())
        result['ratings'][str(year)]={t:state.r[t] for t in sorted(features)}
        for row in [r for r in raw['samples'] if r['season']==year]:
            a,b=row['team_a_id'],row['team_b_id']
            if not state.n.get(a) or not state.n.get(b) or abs(state.p(a,b)-row['elo'])>1e-14:
                raise ValueError('Baseline carry or probability mismatch')
            extra={k:v for k,v in row.items() if k not in ('elo','covered','flagged','differences')}
            result['samples'].append(pair(a,b,row['elo'],features,**extra))
        sample=[r for r in result['samples'] if r['season']==year]
        usable=[r for r in features.values() if r['values'] is not None]
        result['coverage'].append(dict(season=year,through=through,teams=64,usable_teams=len(usable),
            games=len(sample),covered_games=sum(r['covered'] for r in sample),
            strict_adjusted_games=sum(r['covered'] and not r['flagged'] for r in sample),
            schedule_range=[min(r['schedule']['value'] for r in usable),max(r['schedule']['value'] for r in usable)],
            schedule_game_range=[min(r['schedule']['games'] for r in usable),max(r['schedule']['games'] for r in usable)],
            fallback_teams=[dict(name=r['name'],reasons=r['reasons']) for r in features.values() if r['values'] is None],
            flags=dict(Counter(f for r in features.values() for f in r['flags']))))
    if before!=fingerprints(evidence): raise ValueError('Inputs changed')
    components.lock(OUT/'prepared.json',result)
    print(json.dumps(result['coverage'],indent=2))


def fit(rows,keys=KEYS,candidate='components_schedule'):
    """Fixed ridge logistic offset regression; no mutable legacy-model settings."""
    if any(r.get('tie') or r['season'] not in (2021,2022,2023) for r in rows):
        raise ValueError('Forbidden training season or tied outcome')
    rows=[r for r in rows if r['covered']]
    if not rows: raise ValueError('No covered training games')
    scale=[math.sqrt(sum(r['differences'][k]**2 for r in rows)/len(rows)) for k in keys]
    if any(s<=0 or not math.isfinite(s) for s in scale): raise ValueError('Invalid training variation')
    xs=[[r['differences'][k]/s for k,s in zip(keys,scale)] for r in rows]
    offsets=[math.log(r['elo']/(1-r['elo'])) for r in rows]
    beta=[0.]*len(keys)
    for iteration in range(1000):
        old=beta[:]
        for j in range(len(keys)):
            def gradient(value):
                return sum((common.sigmoid(o+sum((value if k==j else beta[k])*x[k] for k in range(len(keys))))-r['outcome'])*x[j] for o,x,r in zip(offsets,xs,rows))/len(rows)+PROTOCOL['ridge']*value
            lo,hi=-1.,1.
            while gradient(lo)>0: lo*=2
            while gradient(hi)<0: hi*=2
            for _ in range(55):
                mid=(lo+hi)/2
                if gradient(mid)>0: hi=mid
                else: lo=mid
            beta[j]=(lo+hi)/2
        if max(abs(a-b) for a,b in zip(old,beta))<1e-12: break
    else: raise ValueError('Fit did not converge')
    return dict(candidate=candidate,keys=keys,beta=beta,scale=scale,n=len(rows),training_seasons=sorted({r['season'] for r in rows}))


def choose(sample,model):
    baseline=metric(sample,'elo')
    candidate=metric(components.scored(sample,model),'challenger')
    selected=all(candidate[k]<baseline[k] for k in ('log_loss','brier'))
    return selected,dict(elo=baseline,candidate=candidate)


def evaluate(evidence):
    refs,raw,raw_lock=load_raw(evidence)
    before=fingerprints(evidence)
    data=common.read(OUT/'prepared.json')
    if data['inputs']!=before or common.fingerprint(data['protocol'])!=common.fingerprint(PROTOCOL):
        raise ValueError('Stale preparation')
    rows=data['samples']
    train=[r for r in rows if r['season'] in PROTOCOL['train']]
    training=fit(train)
    selected,selection=choose([r for r in rows if r['season']==2023],training)
    models={}
    for year in (2023,2024):
        train=[r for r in rows if r['season']<year]
        models[str(year)]=dict(challenger=training if year==2023 else fit(train),
            schedule_only=fit(train,['schedule'],'schedule_only'),
            without_2021=fit([r for r in train if r['season']!=2021]),
            raw_locked=raw_lock['training_models'][raw_lock['winner']] if year==2023 else raw_lock['refitted_model'])
    selection_lock=dict(protocol=PROTOCOL,prepared_sha256=common.digest(OUT/'prepared.json'),
        selected=selected,selection=selection,models=models,
        policy='selected candidate' if selected else 'retain Elo; candidate results diagnostic only')
    components.lock(OUT/'selection_lock.json',selection_lock)
    source_raw={(r['season'],r['team_id']):r for r in raw['features']}
    raw_predictions={(r['season'],r['game_id']):r for r in common.read(components.OUT/'predictions.json')}
    variants=('elo','challenger','seed','strict','without_2021','schedule_only','raw_locked')
    selected_field=seeds.load(common.read(ROOT/'cutoffs.json'))
    forecasts=[]; equivalence=0
    for year in (2023,2024):
        model=models[str(year)]
        features={r['team_id']:r for r in data['features'] if r['season']==year}
        raw_features={t:source_raw[year,t] for t in features}
        ratings=data['ratings'][str(year)]
        def probability(a,b,key,seed_values=None):
            p=1/(1+10**((ratings[b]-ratings[a])/400))
            if key=='elo': return p
            if key=='seed': return seeds.probability(seed_values[a],seed_values[b])
            row=components.build_row(a,b,p,raw_features) if key=='raw_locked' else pair(a,b,p,features)
            return components.probability(row,model['challenger' if key=='strict' else key],key=='strict')
        for row in [r for r in rows if r['season']==year]:
            a,b=row['team_a_id'],row['team_b_id']
            if (abs(probability(a,b,'elo')-row['elo'])>1e-14 or
                abs(probability(a,b,'challenger')-components.probability(row,model['challenger']))>1e-14 or
                abs(probability(a,b,'raw_locked')-raw_predictions[year,row['game_id']]['challenger'])>1e-14):
                raise ValueError('Observed/hypothetical or raw-lock mismatch')
            equivalence+=1
        for region in regional.regions(selected_field,year):
            probabilities={key:group_probabilities(region['teams'],lambda a,b:probability(a,b,key,region['seeds'])) for key in variants}
            forecasts.append(dict(season=year,**region,probabilities=probabilities))
    components.lock(OUT/'forecast_lock.json',dict(selection_sha256=common.digest(OUT/'selection_lock.json'),forecasts=forecasts))
    report=dict(selection=selection_lock,coverage=data['coverage'],games=[],game_groups=[],regionals=[],advancement=[],
        equivalence_checks=equivalence,promoted=False,uncertainty='Repeated exposed-season development comparisons; no untouched holdout or future-season significance claim.')
    predictions=[]
    for year in (2023,2024):
        model=models[str(year)]
        for variant in ('challenger','strict','without_2021','schedule_only','raw_locked'):
            sample=[r for r in (raw['samples'] if variant=='raw_locked' else rows) if r['season']==year]
            scored=components.scored(sample,model['challenger' if variant=='strict' else variant],variant=='strict')
            if variant=='challenger': predictions.extend(scored)
            adjusted=[r for r in scored if r['covered'] and not (variant=='strict' and r['flagged'])]
            fallback=[r for r in scored if r not in adjusted]
            subsets={'all':scored,'adjusted':adjusted,'fallback':fallback}
            if variant=='challenger': subsets.update({stage:[r for r in scored if r['stage']==stage] for stage in sorted({r['stage'] for r in scored})})
            for subset,rs in subsets.items():
                if rs: report['games'].append(dict(season=year,variant=variant,subset=subset,n=len(rs),**common.summarize(rs)))
        games=overlay(load_games(year),refs)
        covered=set(); winners=set(); groups=[]
        for f in [f for f in forecasts if f['season']==year]:
            match=[g for g in games if g['stage']=='regional' and g['a'] in f['teams'] and g['b'] in f['teams']]
            outcome=regional.champion(f['teams'],match)
            covered.update(g['game_id'] for g in match); winners.add(outcome['winner'])
            groups.append(dict(**f,**outcome,scores={k:regional.score(p,outcome['winner']) for k,p in f['probabilities'].items()}))
        if covered!={g['game_id'] for g in games if g['stage']=='regional'} or winners!={g[t] for g in games if g['stage']=='super_regional' for t in ('a','b')}:
            raise ValueError('Regional outcomes mismatch')
        report['regionals'].extend(groups)
        for group in groups:
            rs=[r for r in predictions if r['season']==year and r['stage']=='regional' and r['team_a_id'] in group['teams'] and r['team_b_id'] in group['teams']]
            report['game_groups'].append(dict(season=year,regional=group['name'],n=len(rs),**common.summarize(rs)))
        for variant in ('challenger','strict','without_2021','schedule_only','raw_locked'):
            adjusted=[dict(r,scores=dict(r['scores'],challenger=r['scores'][variant]),probabilities=dict(r['probabilities'],challenger=r['probabilities'][variant])) for r in groups]
            report['advancement'].append(dict(season=year,variant=variant,**regional.summary(adjusted)))
    if before!=fingerprints(evidence): raise ValueError('Protected inputs changed')
    report['preserved_inputs_unchanged']=True
    common.write(OUT/'predictions.json',predictions)
    common.write(OUT/'report.json',report)
    print(json.dumps(dict(selected=selected,selection=selection,models=models,
        games=[r for r in report['games'] if r['subset']=='all'],advancement=report['advancement']),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','evaluate'))
    parser.add_argument('--evidence-dir',required=True,type=Path)
    args=parser.parse_args()
    (prepare if args.action=='prepare' else evaluate)(args.evidence_dir.resolve())
