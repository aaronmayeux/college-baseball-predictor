"""Restore the exact v2 add-on without changing the original baseline checkpoint."""
import argparse
import hashlib
import pathlib
import zipfile

SHA256 = '9a9b2d059bc8858bfd127732ad848f87670a90769ecc3ed5d5c0ba961fd11376'
ROOT = pathlib.Path(__file__).resolve().parents[1]

def restore(archive):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError('Not the preserved v2 evidence checkpoint')
    with zipfile.ZipFile(archive) as z:
        targets = []
        for member in z.infolist():
            relative = pathlib.PurePosixPath(member.filename)
            if relative.is_absolute() or '..' in relative.parts or member.is_dir():
                raise ValueError('Unsafe archive member')
            parent = str(relative.parent)
            if parent not in {'historical/research/raw', 'historical/validation_v2/output'}:
                raise ValueError('Unexpected archive path')
            target = ROOT.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('Destination escapes repository')
            data = z.read(member)
            if target.exists() and target.read_bytes() != data:
                raise ValueError('Refusing to overwrite differing local file: ' + str(relative))
            targets.append((target, data))
        for target, data in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
    print('Verified/restored', len(targets), 'v2 evidence/output files; baseline unchanged')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=pathlib.Path)
    restore(parser.parse_args().archive)
