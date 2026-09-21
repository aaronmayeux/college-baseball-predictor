"""Offline path-specific access triage, not a collection permission grant.

Distinguishes known robots denials from missing/error/unsupported rules and
unresolved terms. No numeric quota is invented from crawl pacing. The existing
project bulk gate remains closed; retained bytes can be analyzed offline.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
from urllib.robotparser import RobotFileParser

from audit_official_player_sample import read
from audit_source_access import inspect_robots, USER_AGENT


def path_rules(text, robots_url, target, final_url=None):
    result = inspect_robots(text, robots_url, [target], final_url)
    if result['status'] != 'robots_rules_parsed':
        return dict(status='unknown_document', allowed=None, delay_seconds=None)
    # urllib.robotparser does not implement REP wildcard/end-marker matching
    # or longest-rule precedence. Do not report an allowance when those could
    # affect this path. This is conservative triage, not a complete REP engine.
    parsed = urlparse(target)
    path = parsed.path + ('?' + parsed.query if parsed.query else '')
    parser = RobotFileParser(); parser.parse(text.splitlines())
    entries = [e for e in parser.entries if e.applies_to(USER_AGENT)]
    if len(entries) > 1:
        return dict(status='unknown_multiple_agent_groups', allowed=None, delay_seconds=result['crawl_delay_seconds'])
    entry = entries[0] if entries else parser.default_entry
    matches = []
    for line in entry.rulelines if entry else []:
        rule = unquote(line.path)
        if not rule: continue
        if '%' in rule or '%' in path:
            return dict(status='unknown_encoded_rules', allowed=None, delay_seconds=result['crawl_delay_seconds'])
        if '*' in rule or '$' in rule:
            pattern = '^' + re.escape(rule.removesuffix('$')).replace(r'\*', '.*') + ('$' if rule.endswith('$') else '')
            if re.search(pattern, path):
                return dict(status='unknown_pattern_rules', allowed=None, delay_seconds=result['crawl_delay_seconds'])
        elif path.startswith(rule):
            matches.append(line.allowance)
    if len(set(matches)) > 1:
        return dict(status='unknown_rule_precedence', allowed=None, delay_seconds=result['crawl_delay_seconds'])
    allowed = result['paths'][0]['robots_allowed']
    return dict(status='allowed_by_robots' if allowed else 'disallowed_by_robots',
        allowed=allowed, delay_seconds=result['crawl_delay_seconds'])


def audit(raw, field):
    if field['season'] != 2025 or len(field['teams']) != 64 or len({t['team_id'] for t in field['teams']}) != 64:
        raise ValueError('Require full 2025 field')
    robots = {}
    for mp in sorted(raw.glob('*.meta.json')):
        meta = json.loads(mp.read_text())
        url = urlparse(meta['url'])
        if url.path != '/robots.txt': continue
        origin = (url.scheme, url.netloc)
        robots.setdefault(origin, []).append((mp.name.removesuffix('.meta.json'), meta))
    teams = []
    for team in field['teams']:
        paths = []
        for probe in team['probes']:
            # Preserve school-host exclusions even when an alternate conference
            # archive is available. Root checks are not stats-path permissions.
            target = probe['url'] if probe['kind'] != 'robots' else probe['url'].removesuffix('robots.txt')
            url = urlparse(target)
            snapshots = robots.get((url.scheme, url.netloc), [])
            evidence = None
            rules = dict(status='unknown_missing_snapshot', allowed=None, delay_seconds=None)
            if snapshots:
                signatures = {(m.get('http_status'), m.get('sha256'), m.get('final_url')) for _, m in snapshots}
                key, evidence = max(snapshots, key=lambda item: item[1]['retrieved_at'])
                if len(signatures) > 1:
                    rules['status'] = 'unknown_conflicting_robots_snapshots'
                elif evidence.get('http_status') == 200:
                    text, evidence = read(raw, key)
                    rules = path_rules(text, evidence['url'], target, evidence.get('final_url'))
                else:
                    rules['status'] = 'unknown_failed_or_missing_robots_response'
            paths.append(dict(url=target, kind=probe['kind'], robots=rules, robots_evidence=evidence,
                retained_robots_snapshots=[m for _, m in snapshots],
                final_url=probe.get('evidence', {}).get('final_url'),
                cross_origin_redirect=bool(probe.get('evidence', {}).get('final_url') and
                    urlparse(probe['evidence']['final_url']).netloc != url.netloc),
                redirect_access_status='requires_separate_origin_review' if probe.get('evidence', {}).get('final_url') and
                    urlparse(probe['evidence']['final_url']).netloc != url.netloc else 'no_cross_origin_redirect_recorded',
                source_status=probe['status'],
                terms_status='linked_personal_use_terms_no_numeric_automation_allowance'
                    if any(urlparse(u).netloc == 'sidearmsports.com' for u in probe.get('terms_links', []))
                    else 'terms_unverified_for_this_source',
                automated_collection_enabled=False))
        teams.append(dict(team_id=team['team_id'], paths=paths,
            local_retained_evidence_analysis_enabled=True, new_bulk_collection_enabled=False))
    counts = Counter(p['robots']['status'] for t in teams for p in t['paths'])
    return dict(schema_version=1, season=2025, requests_performed=0, teams=teams,
        summary=dict(teams=len(teams), reviewed_paths=sum(counts.values()), path_statuses=dict(counts)),
        permitted_new_bulk_requests=0, provider_numeric_automation_allowance=None,
        volume_basis='Existing project gate, not an asserted provider zero-request quota.',
        standing_restrictions=['D1Baseball automated collection prohibited under recorded terms; no requests.',
            'Do not contact providers without user authorization.'],
        unresolved=['Personal-use copying clauses are not a verified nationwide automation scope.',
            'Crawl delays are pacing rules, not request-count permissions.',
            'A conference or alternate-host rule does not authorize a school-host path.'])


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
