"""Bounded NCAA Guillen counts; two HAVOC schema samples, no school collection."""
import argparse
import csv
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re

from audit_ncaa_archive import selected_date
from collect_ncaa_archive import fetch, URL

SNAPSHOTS = {2021: ('weekly', '2021-05-23'), 2022: ('previous', '2022-05-25'),
             2023: ('raw', '2023-05-28'), 2024: ('raw', '2024-05-26')}
SPECS = {'hr': ('513', 'Home Runs', ['Rank','Name','G','W-L','HR']),
         'runs': ('486', 'Runs', ['Rank','Name','G','W-L','R'])}
PILOTS = {'sb': '493', 'batting': '210'}


def form_for(evidence, year, kind):
    folder, day = SNAPSHOTS[year]
    cutoff = datetime.fromisoformat(json.loads((Path(__file__).resolve().parents[1] /
        'historical/cutoffs.json').read_text())['seasons'][str(year)]['forecast_cutoff'])
    _, report_id = selected_date(evidence/folder, year, cutoff, date.fromisoformat(day))
    code = SPECS[kind][0] if kind in SPECS else PILOTS[kind]
    menu = (evidence/folder/f'{year}_menu.html').read_text()
    team_menu = menu.split('id="LIST2"',1)[1].split('</select>',1)[0]
    if not re.search(r'<option value="'+code+r'">[^<]+\(Team\)</option>', team_menu):
        raise ValueError('Requested statistic absent from retained team menu')
    form = [('sportCode','MBA'),('academicYear',str(year)),('rptType','CSV'),
            ('doWhat','showrankings'),('div','1'),('rptWeeks',report_id)]
    return form + [('statSeq',v) for v in ('-1','-1',code,'-1')]


def collect(evidence, raw):
    raw.mkdir(parents=True,exist_ok=True)
    for year, (_, day) in SNAPSHOTS.items():
        for kind in SPECS:
            fetch(raw,f'{year}_{kind}','.response',form_for(evidence,year,kind),
                requested_season=year,requested_through_date=day,statistic=kind)
            print(year,kind,day,flush=True)
    # Only these two schemas are inspected for HAVOC; no dates/schools sweep.
    for kind in PILOTS:
        fetch(raw,f'2023_{kind}','.response',form_for(evidence,2023,kind),
            requested_season=2023,requested_through_date=SNAPSHOTS[2023][1],statistic=kind)


def parse(text, kind, year, day):
    _, title, fields = SPECS[kind]
    if 'NCAA Baseball' not in text or 'Division I'+title+'\n' not in text:
        raise ValueError('Wrong sport/division/statistic')
    dates = re.findall(r'Through Games (\d{2}/\d{2}/\d{4})',text)
    if len(dates)!=1 or datetime.strptime(dates[0],'%m/%d/%Y').date().isoformat()!=day or date.fromisoformat(day).year!=year:
        raise ValueError('Wrong or ambiguous date/season')
    lines=text.splitlines()
    start=next((i for i,l in enumerate(lines) if l.startswith('"Rank","Name"')),None)
    if start is None or next(csv.reader([lines[start]]))!=fields:
        raise ValueError('Unexpected CSV schema')
    rows={}; reclassifying=False
    for line in lines[start+1:]:
        line=line.strip()
        if not line: continue
        if line.startswith('<script'): break
        if line=='Reclassifying':
            reclassifying=True
            continue
        cells=next(csv.reader([line]))
        if len(cells)!=len(fields): raise ValueError('Malformed/empty report')
        row=dict(zip(fields,cells))
        if not row['Name'] or row['Name'] in rows: raise ValueError('Duplicate/empty team')
        for k in ('G',fields[-1]):
            if not row[k].isdigit(): raise ValueError('Invalid count')
            row[k]=int(row[k])
        record=row['W-L'].split('-')
        if len(record) not in (2,3) or any(not v.isdigit() for v in record) or sum(map(int,record))!=row['G']:
            raise ValueError('Invalid record')
        row['reclassifying']=reclassifying
        rows[row['Name']]=row
    if not rows: raise ValueError('Empty report')
    return rows


def load_report(evidence,raw,year,kind):
    path=raw/f'{year}_{kind}.response'
    meta=json.loads((raw/f'{year}_{kind}.json').read_text())
    payload=path.read_bytes()
    expected=json.loads(json.dumps(form_for(evidence,year,kind)))
    if (meta.get('status')!=200 or meta.get('url')!=URL or meta.get('method')!='POST'
        or meta.get('form')!=expected or meta.get('requested_season')!=year
        or meta.get('requested_through_date')!=SNAPSHOTS[year][1]
        or meta.get('statistic')!=kind or meta.get('sha256')!=hashlib.sha256(payload).hexdigest()):
        raise ValueError('Invalid style-report provenance')
    return parse(payload.decode(),kind,year,SNAPSHOTS[year][1])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir',type=Path,required=True)
    parser.add_argument('--raw-dir',type=Path,required=True)
    args=parser.parse_args()
    collect(args.evidence_dir,args.raw_dir)
