"""Qualify retained 2022 team game logs offline; never collect or fit a model.

Dated rows supply features. Final totals only audit their full-season sums.
This separate adapter qualifies team hitting, not player appearance histories.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

from audit_expansion_preflight import ROOT, SOURCES, source
from audit_official_season_inventory import reconcile
from audit_season_appearances import count
from evidence import overlay, verify_timing
from extract_hitting_inputs import aggregate
from hitting_inputs import FIELDS, rates
import sidearm_structured as sidearm

MAPPING = {f: sidearm.BAT[f] for f in FIELDS}
OPPONENT = {'AB':'opponentAtBats', 'H':'hitsAllowed', 'BB':'walksAllowed',
    'SO':'strikeouts', '2B':'doublesAllowed', '3B':'triplesAllowed',
    'HR':'homerunsAllowed', 'HBP':'hitBatters', 'SF':'sacrificeFliesAllowed',
    'SH':'sacrificeHitsAllowed', 'CI':'catchersInterferenceAllowed'}
# Retained mirrored rows use this exact abbreviation on eight matching games.
SELF_ALIASES = {'okstate': {'Oklahoma St.': 'Oklahoma State'}, 'gcu': {}}
OVERALL = {'AB':'ourAtBats', 'H':'ourHits', 'BB':'ourWalks',
           '2B':'ourDoubles', '3B':'ourTriples', 'HR':'ourHomeRuns'}


def batting(raw):
    result = sidearm.counts(raw, MAPPING, 0)
    result.update(CI=None, PA=None)
    rates(result)
    return result


def identity(row, config):
    date = dt.datetime.strptime(row['date'], '%m/%d/%Y').date()
    if date.year != 2022:
        raise ValueError('Wrong game-log season')
    url = urljoin(config['url'], row['boxscoreUrl'] or '')
    if urlparse(url).netloc != urlparse(config['url']).netloc or '/stats/2022/' not in urlparse(url).path:
        raise ValueError('Game-log box outside historical scope')
    return dict(date=date.isoformat(), teams=[config['team_name'], row['opponent']],
                runs=[count(row['ourScore']), count(row['opponentScore'])], box_url=url)


def denominator(row, opponent, counts, config):
    """A separate failure here leaves validated ISO/OBP available."""
    if (opponent['date'], config.get('self_aliases', {}).get(opponent['opponent'], opponent['opponent']), opponent['ourScore'], opponent['opponentScore']) != (
            row['date'], config['team_name'], row['opponentScore'], row['ourScore']):
        raise ValueError('Opponent log identity mismatch')
    ci = count(row['hitting']['reachedOnCatchersInteference'])
    check = dict(counts, CI=ci)
    for field, key in OPPONENT.items():
        if count(opponent['pitching'][key]) != check[field]:
            raise ValueError('Opponent log component mismatch: '+field)
    pa = sum(check[f] for f in ('AB','BB','HBP','SF','SH','CI'))
    if pa != count(opponent['pitching']['battersFaced']):
        raise ValueError('Opponent BF mismatch')
    return dict(counts, CI=ci, PA=pa)


def extract_logs(data, config, players):
    group = data['gameByGameStats']
    own = group['ourGameByGameStats']
    opponents = group['opponentGameByGameStats']
    if any(type(r.get('isAFooterStat')) is not bool for r in own+opponents):
        raise ValueError('Missing footer classification')
    footer = sidearm.only(r for r in own if r['isAFooterStat'])
    opponent_footer = sidearm.only(r for r in opponents if r['isAFooterStat'])
    entries = [r for r in own if not r['isAFooterStat']]
    if len(entries) != config['expected']:
        raise ValueError('Incomplete season game log')
    opp_index = {}
    for row in opponents:
        if row['isAFooterStat']:
            continue
        url = identity(row, config)['box_url']
        if url in opp_index:
            raise ValueError('Duplicate opponent game log')
        opp_index[url] = row
    records = []; seen = set()
    for raw in entries:
        record = identity(raw, config)
        if record['box_url'] in seen:
            raise ValueError('Duplicate team game log')
        seen.add(record['box_url'])
        record.update(counts=None, issues=[], denominator_issues=[], source_hitting=raw['hitting'])
        try:
            c = batting(raw['hitting'])
            if count(raw['hitting']['runsScored']) != record['runs'][0]:
                raise ValueError('Hitting runs disagree with result')
            record['counts'] = c
        except (ValueError, KeyError, TypeError) as error:
            record['issues'].append(str(error))
        if record['counts'] is not None:
            try:
                record['counts'] = denominator(raw, opp_index[record['box_url']], c, config)
            except (ValueError, KeyError, TypeError) as error:
                record['denominator_issues'].append(str(error))
        records.append(record)
    if set(opp_index) != seen:
        raise ValueError('Opponent game-log coverage differs')
    observed = {f:sum(r['counts'][f] for r in records if r['counts']) for f in FIELDS}
    target = batting(footer['hitting'])
    player_target = {f:sum(p['counts'][f] for p in players.values()) for f in FIELDS}
    overall = {f:count(data['overallTeamStats']['teamStats'][key]) for f,key in OVERALL.items()}
    full_pass = (all(r['counts'] is not None and not r['issues'] for r in records)
        and observed == {f:target[f] for f in FIELDS} == player_target
        and all(observed[f] == v for f,v in overall.items()))
    pa_pass = all(r['counts'] is not None and r['counts']['PA'] is not None for r in records)
    pa_issues = []
    try:
        # Footer identity is not a game identity; only check denominator totals.
        ci = count(footer['hitting']['reachedOnCatchersInteference'])
        pa = sum(target[f] for f in ('AB','BB','HBP','SF','SH')) + ci
        if not pa_pass or ci != sum(r['counts']['CI'] for r in records) or pa != sum(r['counts']['PA'] for r in records):
            raise ValueError('Season PA/CI totals disagree or incomplete')
        for f,key in OPPONENT.items():
            if count(opponent_footer['pitching'][key]) != (ci if f=='CI' else target[f]):
                raise ValueError('Season opponent component mismatch: '+f)
        if count(opponent_footer['pitching']['battersFaced']) != pa:
            raise ValueError('Season opponent BF mismatch')
    except (ValueError, KeyError, TypeError) as error:
        pa_pass = False; pa_issues.append(str(error))
    return records, dict(pass_counts=full_pass, observed=observed,
        footer_target={f:target[f] for f in FIELDS}, player_target=player_target,
        overall_target=overall, PA_pass=pa_pass, PA_issues=pa_issues)


def qualify_modes(records, games, config, contract, check, inventory_pass, sample_pass):
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2022']['forecast_cutoff'])
    modes = {mode:aggregate(records,games,config['team_id'],cutoff,phases)
             for mode,phases in contract['modes'].items()}
    for m in modes.values():
        if not (check['pass_counts'] and inventory_pass and sample_pass):
            m.update(complete=False, PA_complete=False, counts=None, rates=None,
                     block_reason='season_inventory_counts_or_sample_failed')
        elif m['complete'] and not check['PA_pass']:
            m['counts'].update(PA=None, CI=None)
            m.update(PA_complete=False, rates=rates(m['counts']),
                     PA_block_reason='full_season_denominator_check_failed')
    return modes


def run(raw):
    paths = [ROOT/'historical/2022/games.json', ROOT/'historical/2022/teams.json', ROOT/'historical/cutoffs.json']
    paths += sorted((ROOT/'scripts').glob('*.py')) + sorted((ROOT/'historical/validation_v2').glob('*.py'))
    paths += [ROOT/'historical/eligibility.py']
    paths = [p for p in paths if p.is_file()]
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    timing = verify_timing()
    games = overlay(json.loads((ROOT/'historical/2022/games.json').read_text()), timing)
    identities = {t['name']:t['team_id'] for t in json.loads((ROOT/'historical/2022/teams.json').read_text())}
    contract = json.loads((ROOT/'historical/cutoffs.json').read_text())
    results = []
    for key in ('okstate','gcu'):
        config = dict(SOURCES[key], self_aliases=SELF_ALIASES[key])
        text, meta = source(raw,key+'_cumulative.html',config['url'])
        cfg = dict(config,season=2022,cumulative_url=config['url'],expected_completed_games=config['expected'])
        players, _ = sidearm.cumulative(text,cfg)
        data = sidearm.only(sidearm.payload(text,config['url'])['statsSeason']['cumulativeStats'].values())
        records, check = extract_logs(data,config,players['batting'])
        original = {r['box_url']:r for r in records}
        inventory = reconcile(records,games,dict(identities,**config['aliases']),config['team_id'])
        records = inventory['games']
        # reconcile supplies identity issues; preserve count failures as well.
        for r in records:
            r['issues'] += original[r['box_url']]['issues']
        sample = sidearm.only(r for r in records if r['box_url']==config['first'])
        box, box_meta = source(raw,key+'_first_box.html',config['first'])
        parsed, _ = sidearm.box(box,config['first'],sample,cfg)
        sample_counts = {f:sum(p['counts'][f] for p in parsed['batting']) for f in FIELDS}
        sample_pass = sample['counts'] is not None and all(sample_counts[f]==sample['counts'][f] for f in FIELDS)
        modes = qualify_modes(records,games,config,contract,check,inventory['inventory_pass'],sample_pass)
        results.append(dict(team_id=config['team_id'], season=2022, source=meta,
            explicit_aliases=config['aliases'], self_aliases=config['self_aliases'], full_season_check=check,
            inventory_pass=inventory['inventory_pass'], sample_check=dict(pass_counts=sample_pass,source=box_meta,counts=sample_counts),
            forecast_modes=modes, records=records, appearance_histories_qualified=False))
    if any(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=sha for p,sha in hashes.items()):
        raise ValueError('Inputs changed during extraction')
    return dict(schema_version=1, dataset_version='retained_hitting_logs_v1', teams=results,
        input_code_sha256=hashes, timing_evidence=timing, requests_performed=0, model_adjustments_enabled=False,
        point_in_time_certified=False, bulk_collection_enabled=False,
        limitation='Within-source team hitting checks only; no player histories, national validation, fitting or rest inference.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir',type=Path,required=True)
    args = p.parse_args()
    print(json.dumps(run(args.raw_dir),indent=2,sort_keys=True))
