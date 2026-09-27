"""Verify a saved refresh and connect corroborated inputs to the fixed Elo export.

Changed/new/unpaired rows retain the verified baseline as an explicit fallback.
A refresh cannot silently revoke official corrections or rewrite evaluated history.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path

from ingestion import nolan_refresh as refresh
from ingestion.nolan_parser import parse

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('game_date','team_a_id','team_b_id','runs_a','runs_b','tie','stage','timing_review')


def hashes(folder):
    return {str(p.relative_to(folder)):refresh.digest(p.read_bytes())
            for p in sorted(folder.rglob('*')) if p.is_file()}


def verified_refresh(folder):
    """Reparse retained bytes; never trust editable generated eligible flags."""
    folder=Path(folder).resolve()
    before=hashes(folder)
    request=refresh.read(folder/'request.json')
    season=request['season']
    contract=refresh.read(ROOT/'historical/cutoffs.json')
    if request.get('schema')!=1 or str(season) not in contract['seasons']:
        raise ValueError('Unsupported refresh season/schema')
    teams=request['teams']
    if not 1<=len(teams)<=refresh.MAX_TEAMS or len(set(teams))!=len(teams):
        raise ValueError('Invalid requested teams')
    required=[f'historical/{season}/teams.json','historical/cutoffs.json',
              'ingestion/nolan_refresh.py','ingestion/nolan_parser.py','historical/eligibility.py']
    expected={key:refresh.digest((ROOT/key).read_bytes()) for key in required}
    if request['inputs']!=expected:
        raise ValueError('Refresh source contract/code changed; replay saved bytes into a new version')
    roster=refresh.read(ROOT/f'historical/{season}/teams.json')
    lookup={t['slug']:t for t in roster}
    observations=[]; failures=[]
    for slug in sorted(teams):
        url=refresh.url_for(season,slug)
        if slug not in lookup:
            raise ValueError('Unknown refresh team')
        path=folder/'raw'/(slug+'.html')
        meta_path=path.with_name(path.name+'.meta.json')
        if not meta_path.exists():
            failures.append(dict(team=slug,reason='no_source_response'))
            continue
        meta=refresh.read(meta_path)
        if meta.get('url')!=url or meta.get('raw_path')!='raw/'+path.name:
            raise ValueError('Unexpected source identity/path')
        if meta.get('sha256') and (not path.exists() or refresh.digest(path.read_bytes())!=meta['sha256']):
            raise ValueError('Source bytes changed')
        if meta.get('error') or meta.get('http_status')!=200:
            failures.append(dict(team=slug,reason=meta.get('error','source_unavailable')))
            continue
        if not meta.get('sha256') or meta.get('final_url',url)!=url:
            raise ValueError('Unverified successful source')
        try:
            observations.extend(parse(lookup[slug],path.read_text(errors='replace'),meta,
                season,contract['seasons'][str(season)]['ncaa_opening_date']))
        except ValueError as exc:
            failures.append(dict(team=slug,reason=str(exc)))
    games,exclusions=refresh.stage(observations,roster,season,contract)
    for name,value in [('observations',observations),('games',games),('exclusions',exclusions)]:
        if refresh.read(folder/(name+'.json'))!=value:
            raise ValueError('Staged rows do not reproduce from raw evidence: '+name)
    if hashes(folder)!=before:
        raise ValueError('Refresh changed during verification')
    return dict(season=season,teams=teams,games=games,failures=failures,
                source_sha256=before,version=folder.name)


def merge_verified(history, staged):
    """Attach new corroboration; retain baseline values/provenance for all fallbacks."""
    year=staged['season']
    if year not in history:
        raise ValueError('Refresh outside available initialization history')
    result=deepcopy(history)
    base={g['game_id']:g for g in result[year]}
    incoming={g['game_id']:g for g in staged['games']}
    if len(base)!=len(result[year]) or len(incoming)!=len(staged['games']):
        raise ValueError('Duplicate game IDs')
    decisions=[]
    for gid,g in sorted(incoming.items()):
        if g['season']!=year:
            raise ValueError('Mixed refresh seasons')
        original=base.get(gid)
        differences=[]
        if original is None:
            status='fallback_new_unreviewed'
        elif g['reciprocal_check']!='pass':
            status='fallback_unpaired_or_conflicting'
        else:
            differences=[key for key in FIELDS if original.get(key)!=g.get(key)]
            if original.get('reciprocal_check')!='pass':
                status='fallback_baseline_unqualified'
            elif differences:
                status='fallback_changed_requires_review'
            else:
                status='confirmed_unchanged'
                original['refresh_confirmation']=dict(version=staged['version'],
                    observation_refs=deepcopy(g['observation_refs']))
        decisions.append(dict(game_id=gid,status=status,changed_fields=differences,
            baseline_preserved=original is not None,
            fresh_mode_eligibility=deepcopy(g['modes'])))
    requested={'wn:'+slug for slug in staged['teams']}
    missing=[g['game_id'] for g in result[year] if g['game_id'] not in incoming and
             requested.intersection((g['team_a_id'],g['team_b_id']))]
    report=dict(schema=1,season=year,refresh_version=staged['version'],
        policy='corroborate unchanged; retain verified baseline for changed/new/missing/conflicting rows',
        counts=dict(Counter(r['status'] for r in decisions)),missing_baseline_game_ids=sorted(missing),
        missing_baseline_games=len(missing),source_failures=staged['failures'],decisions=decisions,
        numerical_inputs_changed=False,baseline_game_count=len(result[year]),
        candidate_game_count=len(result[year]),refresh_sha256=staged['source_sha256'])
    return result,report


def apply(folder,history):
    staged=verified_refresh(folder)
    return merge_verified(history,staged)
