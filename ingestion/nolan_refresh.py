"""Bounded Nolan schedule refresh into a new immutable staging version.

No historical/app writes, crawling, automatic retries, or forecast promotion.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'historical'))
from eligibility import reject
from ingestion.nolan_parser import parse

OUT = ROOT/'ingestion/output'
MAX_TEAMS = 8
MAX_BYTES = 5_000_000
AGENT = 'CollegeBaseballResearch/0.2 (personal on-demand schedule refresh)'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write_new(path, value):
    content = (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()
    if path.exists():
        if path.read_bytes()!=content:
            raise ValueError('Existing version differs; choose a new version: '+str(path))
        return
    with path.open('xb') as stream:
        stream.write(content)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # A changed destination requires inspection, not silent year switching.


def url_for(season, slug):
    if not re.fullmatch(r'[A-Za-z0-9-]+', slug):
        raise ValueError('Unsafe team slug')
    return f'https://www.warrennolan.com/baseball/{season}/schedule/{slug}'


def source(raw, season, slug, cached=None):
    """Store success or failure once. Failed versions never retry automatically."""
    url = url_for(season, slug)
    path = raw/(slug+'.html'); meta_path = raw/(slug+'.html.meta.json')
    if meta_path.exists():
        meta = read(meta_path)
        if meta['url']!=url:
            raise ValueError('Cached source URL mismatch')
        if meta.get('sha256'):
            body = path.read_bytes()
            if digest(body)!=meta['sha256']:
                raise ValueError('Cached source hash mismatch')
            return body, meta
        return None, meta
    if path.exists():
        raise ValueError('Orphan source bytes; use a new version')
    if cached is not None:
        old = cached/(slug+'.html')
        original = read(old.with_name(old.name+'.meta.json'))
        body = old.read_bytes()
        if (original.get('url')!=url or original.get('final_url',url)!=url or
            original.get('http_status')!=200 or original.get('sha256')!=digest(body)):
            raise ValueError('Unverified retained source')
        meta = dict(original, raw_path='raw/'+path.name, acquisition='retained_replay',
                    original_metadata=original)
    else:
        meta = dict(url=url, retrieved_at=datetime.now(timezone.utc).isoformat(),
                    raw_path='raw/'+path.name, acquisition='live_request')
        body = None
        try:
            request = Request(url, headers={'User-Agent':AGENT})
            with build_opener(NoRedirect).open(request, timeout=30) as response:
                meta.update(http_status=response.status, final_url=response.url,
                            content_type=response.headers.get('Content-Type'))
                body = response.read(MAX_BYTES+1)
                if len(body)>MAX_BYTES:
                    body=None
                    raise ValueError('Response exceeds size limit')
                if response.status!=200 or response.url!=url or 'text/html' not in (meta['content_type'] or ''):
                    raise ValueError('Unexpected response status, URL or content type')
        except Exception as exc:
            meta['error'] = str(exc)
            if isinstance(exc,HTTPError):
                meta['http_status'] = exc.code
                meta['redirect_location'] = exc.headers.get('Location')
                body = exc.read(MAX_BYTES)
    if body is not None:
        with path.open('xb') as stream:
            stream.write(body)
        meta.update(bytes=len(body),sha256=digest(body))
    write_new(meta_path, meta)
    return body, meta


def stage(observations, roster, season, contract):
    """Require matching reciprocal fresh observations before any eligible game."""
    known={t['team_id'] for t in roster}
    groups=defaultdict(list); exclusions=[]
    for row in observations:
        reason = ('unscored' if row['status']!='completed' else
                  'non_d1' if row['non_d1_explicit'] else
                  'unknown_opponent' if row['opponent_id'] not in known else
                  'missing_game_id' if not row['source_game_id'] else None)
        if reason:
            exclusions.append(dict(team_id=row['team_id'],source_game_id=row['source_game_id'],reason=reason))
        else:
            groups[row['source_game_id']].append(row)
    games=[]
    cutoff=datetime.fromisoformat(contract['seasons'][str(season)]['forecast_cutoff'])
    for gid, rows in sorted(groups.items()):
        rows=sorted(rows,key=lambda r:r['team_id']); a=rows[0]; issues=[]
        if len(rows)!=2:
            issues.append('missing_or_duplicate_reciprocal_observation')
        else:
            b=rows[1]
            if a['team_id']!=b['opponent_id'] or a['opponent_id']!=b['team_id'] or a['team_id']==b['team_id']:
                issues.append('team_mismatch')
            if a['runs_for']!=b['runs_against'] or a['runs_against']!=b['runs_for']:
                issues.append('score_mismatch')
            for key in ('game_date','stage'):
                if a[key]!=b[key]:issues.append(key+'_mismatch')
        for row in rows:
            rf,ra=row['runs_for'],row['runs_against']
            if row['outcome']!=('W' if rf>ra else 'L' if rf<ra else 'T'):
                issues.append('outcome_mismatch')
        game=dict(game_id=f'wn:{season}:{gid}',season=season,game_date=a['game_date'],
            team_a_id=a['team_id'],team_b_id=a['opponent_id'],runs_a=a['runs_for'],runs_b=a['runs_against'],
            tie=a['runs_for']==a['runs_against'],stage=a['stage'],
            timing_review=any(r['timing_review'] for r in rows),
            reciprocal_check='review' if issues else 'pass',issues=sorted(set(issues)),
            observation_refs=[dict(team_id=r['team_id'],raw_path=r['raw_path'],raw_sha256=r['raw_sha256'],
                                   source_url=r['source_url'],retrieved_at=r['retrieved_at']) for r in rows])
        game['modes']={mode:dict(eligible=reject(game,cutoff,stages) is None,
            exclusion_reason=reject(game,cutoff,stages)) for mode,stages in contract['modes'].items()}
        games.append(game)
    return games,exclusions


def run(season, slugs, version, cached=None):
    contract=read(ROOT/'historical/cutoffs.json')
    # New years require a reviewed cutoff/roster, not assumptions or model use.
    if str(season) not in contract['seasons']:
        raise ValueError('Season has no reviewed cutoff; 2026/future imports are not enabled')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',version):
        raise ValueError('Unsafe version name')
    if not 1<=len(slugs)<=MAX_TEAMS or len(set(slugs))!=len(slugs):
        raise ValueError('Specify 1–8 distinct team slugs; no automatic expansion')
    roster_path=ROOT/f'historical/{season}/teams.json'
    roster=read(roster_path); by_slug={t['slug']:t for t in roster}
    if len(by_slug)!=len(roster) or any(t['season']!=season or t['team_id']!='wn:'+t['slug'] for t in roster):
        raise ValueError('Invalid season roster')
    for slug in slugs:
        url_for(season,slug)
        if slug not in by_slug:raise ValueError('Unknown team; exact roster identity required: '+slug)
    folder=OUT/version
    folder.mkdir(parents=True,exist_ok=True)
    raw=folder/'raw';raw.mkdir(exist_ok=True)
    paths=[roster_path,ROOT/'historical/cutoffs.json',Path(__file__),ROOT/'ingestion/nolan_parser.py',ROOT/'historical/eligibility.py']
    inputs={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in paths}
    request=dict(schema=1,season=season,teams=sorted(slugs),source='retained_replay' if cached else 'live',inputs=inputs)
    write_new(folder/'request.json',request)
    observations=[]; failures=[]; sources=[]; last_request=None
    for slug in sorted(slugs):
        if cached is None and not (raw/(slug+'.html.meta.json')).exists():
            if last_request is not None:
                time.sleep(max(0,2-(time.monotonic()-last_request)))
            last_request=time.monotonic()
        body,meta=source(raw,season,slug,cached)
        sources.append(dict(team=slug,**meta))
        if body is None or meta.get('error'):
            failures.append(dict(team=slug,reason=meta.get('error','source_unavailable')))
            if meta.get('http_status') in (401,403,429):
                # Stop this batch on explicit access/rate-limit responses.
                failures.extend(dict(team=t,reason='batch_stopped_after_access_response') for t in sorted(slugs) if t>slug)
                break
            continue
        try:
            observations.extend(parse(by_slug[slug],body.decode('utf-8',errors='replace'),meta,
                                      season,contract['seasons'][str(season)]['ncaa_opening_date']))
        except ValueError as exc:
            failures.append(dict(team=slug,reason=str(exc)))
    games,exclusions=stage(observations,roster,season,contract)
    summary=dict(season=season,version=version,requested_teams=len(slugs),
        parsed_teams=len({r['team_id'] for r in observations}),observations=len(observations),
        games=len(games),reciprocal_games=sum(g['reciprocal_check']=='pass' for g in games),
        eligible_games={mode:sum(g['modes'][mode]['eligible'] for g in games) for mode in contract['modes']},
        excluded_observations=dict(Counter(r['reason'] for r in exclusions)),failures=failures,
        status='staged_partial_snapshot_not_forecast_ready',production_ready=False,
        model='unchanged_fixed_neutral_elo',app_updated=False,point_in_time_certified=False,
        note='Bounded schedule import only; missing reciprocal pages are explicit gaps, not zero results. No model fitting or scoring.')
    if any(digest((ROOT/p).read_bytes())!=sha for p,sha in inputs.items()):
        raise ValueError('Protected inputs changed during refresh')
    for name,value in [('observations',observations),('games',games),('exclusions',exclusions),('sources',sources),('summary',summary)]:
        write_new(folder/(name+'.json'),value)
    print(json.dumps(summary,indent=2))
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--season',required=True,type=int)
    parser.add_argument('--teams',required=True,nargs='+')
    parser.add_argument('--version',required=True)
    parser.add_argument('--cached-raw',type=Path,help='Offline replay of verified retained pages')
    args=parser.parse_args()
    summary=run(args.season,args.teams,args.version,args.cached_raw)
    if summary['failures']:raise SystemExit(2)


if __name__=='__main__':main()
