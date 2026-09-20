"""Restore only data from the exact separately retained audit bundle."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import zipfile

EXPECTED_SHA256 = '8be5c804aeadc593faa11441f12e82b75e32adaa778b2aacdb00a70fe9f40e63'
ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def restore(archive):
    if digest(archive) != EXPECTED_SHA256:
        raise ValueError('Bundle checksum mismatch; no files restored. Use the recorded historical baseline bundle.')
    with zipfile.ZipFile(archive) as z:
        pending = []
        reused = 0
        for info in z.infolist():
            p = PurePosixPath(info.filename)
            if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] != 'historical' or '\\' in info.filename:
                raise ValueError('Unsafe archive path')
            if info.is_dir() or p.suffix in {'.py', '.md'}:
                continue
            if p.suffix not in {'.json', '.csv', '.sqlite', '.html', '.pdf', '.txt', '.log'}:
                continue
            if str(p) == 'historical/cutoffs.json':
                continue  # Git owns the configuration.
            target = ROOT.joinpath(*p.parts)
            if not target.resolve().is_relative_to((ROOT / 'historical').resolve()):
                raise ValueError('Data path escapes historical directory')
            if target.exists():
                if not target.is_file() or hashlib.sha256(z.read(info)).hexdigest() != digest(target):
                    raise ValueError(f'Local data differs; refusing to overwrite: {p}')
                reused += 1
            else:
                pending.append((info, target))
        # All existing-file conflicts checked before writing anything.
        for info, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, target.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    print(f'Restored {len(pending)} data files; reused {reused} identical files. Code and documents unchanged.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    args = ap.parse_args()
    try:
        restore(args.archive)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        ap.exit(1, f'{exc}\n')
