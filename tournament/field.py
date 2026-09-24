"""2025 bracket routing, verified against the NCAA selection-day bracket.

Source URLs and verification are in docs/Tournament_Engine.md. This is placement
configuration, never a rating feature or a record of actual tournament winners.
"""
# Each adjacent pair feeds a super; each consecutive eight feeds one Omaha group.
HOST_ORDER = ('Vanderbilt', 'Southern-Miss', 'Florida-State', 'Oregon-State',
              'North-Carolina', 'Oregon', 'Coastal-Carolina', 'Auburn',
              'Texas', 'UCLA', 'Ole-Miss', 'Georgia',
              'LSU', 'Clemson', 'Tennessee', 'Arkansas')


def build_regions(selected, internal):
    if len(selected) != 64 or any(r['season'] != 2025 for r in selected):
        raise ValueError('Require the 2025 selection field')
    by_region = {}
    for row in selected:
        group = by_region.setdefault(row['regional'], {})
        if row['regional_seed'] in group:
            raise ValueError('Duplicate regional seed')
        group[row['regional_seed']] = row['team_id']
    if len(by_region) != 16 or any(set(g) != {1, 2, 3, 4} for g in by_region.values()):
        raise ValueError('Invalid regional seed groups')
    by_host = {g[1]: (name, g) for name, g in by_region.items()}
    if set(by_host) != {internal(h) for h in HOST_ORDER}:
        raise ValueError('Selection hosts differ from verified bracket')
    regions = []
    for i, host in enumerate(HOST_ORDER):
        name, seeds = by_host[internal(host)]
        regions.append(dict(id=f'regional-{i+1}', name=name.split(' hosted by ')[0],
                            teams=[seeds[s] for s in range(1, 5)]))
    if len({t for r in regions for t in r['teams']}) != 64:
        raise ValueError('Duplicate field team')
    return regions
