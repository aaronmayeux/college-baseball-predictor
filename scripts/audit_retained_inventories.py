"""Apply the shared schedule parser to retained 2025 embedded-SIDEARM pages.

No downloads and no appearance qualification. Failed/unsupported teams remain
explicit. Expected D1 counts are comparison targets, not proof of completeness.
"""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path

from audit_official_player_sample import read
from audit_official_season_inventory import REPO, reconcile, ALIASES
from sidearm_structured import schedule, payload, opponent_name
from eligibility import reject

# Scoped to Louisville's retained 2025 opponent metadata, not global guesses.
# In particular, plain "Miami" is never mapped without the Coral Gables record.
LOUISVILLE_ALIASES = {
    "St. John's": ('wn:Saint-Johns', 'http://www.redstormsports.com/', 'Queens, NY'),
    'Cal': ('wn:California', 'http://www.calbears.com/', 'Berkeley, CA'),
    'NC State': ('wn:North-Carolina-State', 'http://gopack.com/', 'Raleigh, NC'),
    'Pitt': ('wn:Pittsburgh', 'http://www.pittsburghpanthers.com', 'Pittsburgh, PA'),
    'Miami': ('wn:Miami-FL', 'http://www.hurricanesports.com/', 'Coral Gables, FL'),
}


def louisville_aliases(text, config):
    data = payload(text, config['schedule_url'])['schedule']['schedules']['schedules-baseball,2025']
    seen = set()
    for game in data['games']:
        opponent = game['opponent']; name = opponent['title']
        if name not in LOUISVILLE_ALIASES: continue
        _, website, location = LOUISVILLE_ALIASES[name]
        if (opponent.get('website'), opponent.get('location')) != (website, location):
            raise ValueError('Reviewed opponent metadata changed: ' + name)
        seen.add(name)
    if seen != set(LOUISVILLE_ALIASES): raise ValueError('Missing reviewed opponent metadata')
    return {name: v[0] for name, v in LOUISVILLE_ALIASES.items()}


def reviewed_aliases(text, config, review, identities):
    """Scope aliases to an exact season/page and verify every affected record.

    A normalized label alone cannot authorize an identity. Even a new ranked
    variant must have a reviewed original title and matching school metadata.
    """
    if any(config[key] != review[key] for key in ('season', 'schedule_url')):
        raise ValueError('Alias review scope mismatch')
    rules = review['aliases']
    aliases = {}
    for title, rule in rules.items():
        name = opponent_name(title)
        target = rule['team_id']
        if target not in identities.values(): raise ValueError('Unknown alias target')
        if name in identities and identities[name] != target:
            raise ValueError('Alias conflicts with existing identity')
        if name in aliases and aliases[name] != target:
            raise ValueError('Conflicting reviewed aliases')
        aliases[name] = target
    data = payload(text, config['schedule_url'])['schedule']['schedules'][f"schedules-baseball,{config['season']}"]
    seen = set()
    for game in data['games']:
        opponent = game['opponent']; title = opponent['title']
        if opponent_name(title) not in aliases: continue
        if title not in rules: raise ValueError('Unreviewed alias title: ' + title)
        rule = rules[title]
        if any(opponent.get(key) != rule[key] for key in ('website', 'location')):
            raise ValueError('Reviewed opponent metadata changed: ' + title)
        seen.add(title)
    if seen != set(rules): raise ValueError('Missing reviewed opponent metadata')
    return aliases


def audit(raw, field):
    if field['season'] != 2025 or len(field['teams']) != 64 or len({t['team_id'] for t in field['teams']}) != 64:
        raise ValueError('Require the full 2025 field')
    game_path = REPO/'historical/2025/games.json'
    team_path = REPO/'historical/2025/teams.json'
    games, teams = [json.loads(p.read_text()) for p in (game_path, team_path)]
    if any(r['season'] != 2025 for r in games + teams): raise ValueError('Mixed baseline seasons')
    contract_path = REPO/'historical/cutoffs.json'
    contract = json.loads(contract_path.read_text())
    cutoff = dt.datetime.fromisoformat(contract['seasons']['2025']['forecast_cutoff'])
    identities = {t['name']: t['team_id'] for t in teams}
    identities.update(ALIASES)
    alias_path = REPO/'historical/schedule_aliases_2025.json'
    reviews = json.loads(alias_path.read_text())
    output = []
    for team in field['teams']:
        row = dict(team_id=team['team_id'], name=team['name'], status='no_supported_retained_schedule',
            appearance_histories_reconciled=False, recent_workload='unknown')
        probes = [p for p in team['probes'] if p['kind'] == 'schedule' and
            p['status'] == 'historical_index_present' and p.get('parser_family') == 'sidearm_embedded']
        if len(probes) > 1: raise ValueError('Ambiguous schedule snapshot')
        if probes:
            p = probes[0]
            config = dict(team_name=team['name'], season=2025, schedule_url=p['url'],
                expected_completed_games=sum(team['team_id'] in (g['team_a_id'], g['team_b_id']) for g in games))
            text, evidence = read(raw, p['key'])
            if evidence['url'] != p['url']: raise ValueError('Schedule URL mismatch')
            row['evidence'] = evidence
            row['expected_d1_games'] = config['expected_completed_games']
            try:
                local_identities = dict(identities)
                if team['team_id'] in reviews:
                    review = reviews[team['team_id']]
                    local_identities.update(reviewed_aliases(text, config, review, identities))
                    row['reviewed_aliases'] = review
                if team['team_id'] == 'wn:Louisville':
                    aliases = louisville_aliases(text, config)
                    if not set(aliases.values()) <= set(identities.values()): raise ValueError('Unknown alias target')
                    local_identities.update(aliases)
                    row['reviewed_aliases'] = LOUISVILLE_ALIASES
                source, excluded = schedule(text, config)
                inventory = reconcile(source, games, local_identities, team['team_id'])
                row.update(status='result_inventory_reconciled' if inventory['inventory_pass'] else 'unresolved_result_joins',
                    inventory=inventory, excluded_schedule_rows=excluded,
                    retained_rescheduling_labels=[r for r in source if r.get('source_noplay_text')])
                good = {r['game_id'] for r in inventory['games'] if not r['issues']}
                row['forecast_modes'] = {}
                for mode, stages in contract['modes'].items():
                    expected = {g['game_id'] for g in games if team['team_id'] in (g['team_a_id'], g['team_b_id']) and reject(g, cutoff, stages) is None}
                    row['forecast_modes'][mode] = dict(expected_games=len(expected), matched_games=len(expected & good),
                        result_inventory_complete=bool(expected) and expected <= good,
                        player_appearances_verified=False, actual_work_dates_qualified=False)
            except (ValueError, KeyError, TypeError) as error:
                row.update(status='parser_or_inventory_gap', issue=str(error))
        output.append(row)
    return dict(schema_version=1, season=2025, development_only=True, requests_performed=0,
        summary=dict(Counter(r['status'] for r in output)), teams=output,
        point_in_time_certified=False, feature_qualified=False,
        input_sha256={str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (game_path, team_path, contract_path, alias_path)})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir', type=Path, required=True)
    p.add_argument('--field-audit', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = audit(args.raw_dir, json.loads(args.field_audit.read_text()))
    result['field_audit_sha256'] = hashlib.sha256(args.field_audit.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary'], indent=2))
