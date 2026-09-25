"""Stage only the browser app and generated forecast for static hosting."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    forecast = ROOT / 'app/data/forecast.json'
    data = json.loads(forecast.read_text())
    if data['schema_version'] != 1 or len(data['teams']) != 64:
        raise ValueError('Build the complete forecast with python3 -m tournament.build first')
    target = ROOT / 'dist'
    (target / 'data').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'app/index.html', target / 'index.html')
    shutil.copyfile(forecast, target / 'data/forecast.json')
    print('Static app staged in dist/; no raw evidence included.')


if __name__ == '__main__':
    main()
