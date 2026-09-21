"""Recover the exact truncated source-expansion checkpoint without changing it.

The published hash identifies a ZIP truncated within its final derived audit.
All 117 raw responses and 117 metadata files precede that truncation. Only
CRC-verified complete entries are recovered; every raw SHA is then checked.
Regenerate audit.json with audit_player_source_expansion.py, never salvage its
partial bytes as a valid report.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

EXPECTED = '33fb20a46b46c81cc372865aa28baec8e51701b89d72b9803c2bcf3ae7973a6f'


def restore(archive, destination):
    data = archive.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError('Not the recorded truncated checkpoint')
    entries = {}
    offset = 0
    while data[offset:offset + 4] == b'PK\x03\x04':
        _, _, flags, method, _, _, crc, size, original_size, namesize, extrasize = struct.unpack_from('<4s5H3I2H', data, offset)
        name = data[offset + 30:offset + 30 + namesize].decode()
        start = offset + 30 + namesize + extrasize
        if start + size > len(data):
            if name != 'audit.json':
                raise ValueError('Unexpected incomplete entry')
            break
        if flags & 9 or method not in (0, 8):
            raise ValueError('Unsupported ZIP member')
        raw = data[start:start + size]
        content = zlib.decompress(raw, -15) if method == 8 else raw
        if len(content) != original_size or zlib.crc32(content) != crc:
            raise ValueError('ZIP member integrity failure')
        if not name.startswith('raw/') or '..' in Path(name).parts or name in entries:
            raise ValueError('Unexpected member path')
        entries[name] = content
        offset = start + size
    if len(entries) != 234:
        raise ValueError('Missing raw evidence')
    for name, content in entries.items():
        if name.endswith('.meta.json'):
            meta = json.loads(content)
            if hashlib.sha256(entries[name.removesuffix('.meta.json')]).hexdigest() != meta['sha256']:
                raise ValueError('Raw SHA mismatch')
    for name, content in entries.items():
        target = destination / name
        if target.exists() and target.read_bytes() != content:
            raise ValueError('Refusing differing local evidence')
    for name, content in entries.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return len(entries)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('destination', type=Path)
    a = p.parse_args()
    print('Verified/recovered', restore(a.archive, a.destination), 'entries; regenerate audit.json')
