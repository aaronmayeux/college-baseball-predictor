"""Bounded NCAA archive access check: two national CSVs per 2021–2023 season.

Explicit invocation only. Cache all responses/failures; never retry or overwrite.
No school collection, model input or D1Baseball request.
"""
import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from audit_ncaa_archive import selected_date

URL = 'https://web1.ncaa.org/stats/StatsSrv/rankings'


def fetch(raw, stem, suffix, form, **scope):
    meta_path, path = raw / (stem + '.json'), raw / (stem + suffix)
    if meta_path.exists() or path.exists():
        if not meta_path.exists():
            raise ValueError('Unpaired cached response')
        meta = json.loads(meta_path.read_text())
        if meta.get('url') != URL or meta.get('method') != 'POST' or meta.get('form') != json.loads(json.dumps(form)):
            raise ValueError('Cached request differs; use a separate evidence directory')
        if any(meta.get(k) != v for k, v in scope.items()):
            raise ValueError('Cached request scope differs')
        if meta.get('status') != 200 or not path.exists():
            raise ValueError('Cached failure; no automatic retry')
        if hashlib.sha256(path.read_bytes()).hexdigest() != meta['sha256']:
            raise ValueError('Cached hash mismatch')
        return
    meta = dict(url=URL, method='POST', form=form, **scope)
    try:
        request = urllib.request.Request(URL, data=urllib.parse.urlencode(form).encode())
        try:
            response = urllib.request.urlopen(request, timeout=40)
        except urllib.error.HTTPError as error:
            response = error
        with response as r:
            payload = r.read()
            meta.update(status=r.status, final_url=r.url, content_type=r.headers.get('Content-Type'))
        path.write_bytes(payload)
        meta.update(path=path.name, sha256=hashlib.sha256(payload).hexdigest())
    except (OSError, urllib.error.URLError) as error:
        meta.update(status=None, error=str(error))
    meta['retrieved_at_utc'] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=2) + '\n')
    if meta['status'] != 200:
        raise ValueError('Request failed; evidence retained; no retry')


def collect(raw, sample="latest"):
    dates = {"latest": {2021: None, 2022: None, 2023: None},
             "previous": {2021: "2021-05-28", 2022: "2022-05-25"},
             "weekly": {2021: "2021-05-23"}}[sample]
    raw.mkdir(parents=True, exist_ok=True)
    contract = json.loads((Path(__file__).resolve().parents[1] / 'historical/cutoffs.json').read_text())
    for season, requested_date in dates.items():
        fetch(raw, f'{season}_menu', '.html', dict(sportCode='MBA', academicYear=str(season),
              doWhat='display', year=str(season)))
        cutoff = datetime.fromisoformat(contract['seasons'][str(season)]['forecast_cutoff'])
        through, report_id = selected_date(raw, season, cutoff,
            date.fromisoformat(requested_date) if requested_date else None)
        for kind, stat in [('obp', '589'), ('era', '211')]:
            form = [('sportCode', 'MBA'), ('academicYear', str(season)), ('rptType', 'CSV'),
                    ('doWhat', 'showrankings'), ('div', '1'), ('rptWeeks', report_id)]
            form += [('statSeq', v) for v in ('-1', '-1', stat, '-1')]
            fetch(raw, f'{season}_{kind}', '.response', form,
                  requested_season=season, requested_through_date=through.isoformat(), statistic=kind)
            print(season, kind, through.isoformat(), report_id, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', required=True, type=Path)
    parser.add_argument('--sample', choices=('latest', 'previous', 'weekly'), default='latest',
                        help='Bounded reviewed checks; use a separate raw directory per sample')
    args = parser.parse_args()
    collect(args.raw_dir, args.sample)
