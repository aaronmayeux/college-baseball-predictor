"""Inspect retained robots responses without fetching or granting bulk permission."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from audit_official_player_sample import read

USER_AGENT = 'CollegeBaseballResearch/0.1'
SOURCES = [
    ('ovc_robots.txt', ['https://ovcsports.com/custompages/stats/baseball/2025/lr.htm']),
    ('cusa_robots.txt', ['https://conferenceusa.com/schedule.aspx?schedule=4255']),
    ('wmt_robots.txt', ['https://wmt.games/ucla/stats/season/596514']),
    ('wmt_digital_robots.txt', ['https://wmt.digital/terms-of-service']),
    ('Little-Rock_robots.txt', ['https://lrtrojans.com/sports/baseball/schedule/2025']),
    ('dbu_robots.txt', ['https://dbupatriots.com/sports/baseball/schedule/2025']),
]


def inspect_robots(text, origin, targets, final_url=None):
    origin = urlparse(origin)
    if any((urlparse(u).scheme, urlparse(u).netloc) != (origin.scheme, origin.netloc) for u in targets):
        raise ValueError('Robots rules cannot authorize another origin')
    result = dict(status='unverified_robots_document', user_agent=USER_AGENT,
        crawl_delay_seconds=None, paths=[dict(url=u, robots_allowed=None) for u in targets], bulk_permission='unverified', collection_enabled=False)
    if final_url and (urlparse(final_url).scheme, urlparse(final_url).netloc) != (origin.scheme, origin.netloc):
        return result
    if re.search(r'<\s*(?:!doctype|html|script|body)\b', text, re.I) or not re.search(r'^\s*User-agent\s*:', text, re.M | re.I):
        return result
    parser = RobotFileParser();parser.parse(text.splitlines())
    result.update(status='robots_rules_parsed', crawl_delay_seconds=parser.crawl_delay(USER_AGENT))
    result['paths'] = [dict(url=u, robots_allowed=parser.can_fetch(USER_AGENT, u)) for u in targets]
    return result


def audit(raw):
    output = []
    for key, targets in SOURCES:
        mp = raw/(key+'.meta.json');meta = json.loads(mp.read_text())
        if meta.get('http_status') == 200:
            text, meta = read(raw, key)
            result = inspect_robots(text, meta['url'], targets, meta.get('final_url'))
        else:
            result = dict(status='access_failed', paths=[dict(url=u, robots_allowed=None) for u in targets], bulk_permission='unverified', collection_enabled=False)
        output.append(dict(key=key, evidence=meta, metadata_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(), **result))
    return dict(schema_version=1, requests_performed=0, sources=output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-dir', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();result = audit(a.raw_dir)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    for row in result['sources']:print(row['key'], row['status'], row.get('crawl_delay_seconds'), row['paths'])
