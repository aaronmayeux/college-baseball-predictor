"""Coverage-only ledger: preserve every requested team, including unknown teams.

No predictions, imputation, rest estimates or interface are implemented here.
"""

def coverage_ledger(team_ids, audits, season, mode):
    if not team_ids or len(set(team_ids))!=len(team_ids):raise ValueError('Missing or duplicate tournament team IDs')
    if mode not in ('regular_only','conference_inclusive'):raise ValueError('Unknown forecast mode')
    by_team={}
    for audit in audits:
        config=audit['config']
        if config['season']!=season:continue
        team=config['team_id']
        if team in by_team:raise ValueError('Ambiguous team-season audit')
        by_team[team]=audit
    ledger=[]
    for team in team_ids:
        audit=by_team.get(team);entry=dict(team_id=team,season=season,mode=mode,
            hitting_counts='unverified',pitching_counts='unverified',recent_workload='unknown',
            needs_validated_fallback=True,feature_qualified=False)
        if audit:
            complete=audit['forecast_modes'][mode]['complete']
            for kind,label in [('batting','hitting_counts'),('pitching','pitching_counts')]:
                if complete and audit['comparisons'][kind]['totals_match']:entry[label]='reconciled_core_counts'
        ledger.append(entry)
    return ledger
