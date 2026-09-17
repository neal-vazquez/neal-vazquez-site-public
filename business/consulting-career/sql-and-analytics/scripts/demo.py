"""Run the portfolio against an in-memory SQLite database. No network or credentials."""
import argparse
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
WINDOW = {'start_date': '2026-09-01', 'end_date': '2026-09-07'}

def sql(path):
    return (ROOT / path).read_text()

def connect(seed=True):
    if sqlite3.sqlite_version_info < (3, 35, 0):
        raise RuntimeError('SQLite 3.35+ with JSON functions is required.')
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.execute("SELECT json_extract('{\"ready\":1}', '$.ready')")
    for migration in sorted((ROOT/'sql/migrations').glob('*.sql')):
        db.executescript(migration.read_text())
    if seed:
        db.executescript(sql('fixtures/synthetic.sql'))
    return db

def query(db, name, params=()):
    return db.execute(sql('sql/runtime/' + name + '.sql'), params)

def sample_bindings():
    return {
        'event_id':'demo-probe', 'event_name':'project_click', 'path':'/',
        'location':'work', 'parameters_json':'{}', 'session_id':'demo-session',
        'occurred_at':'2026-09-07T12:00:00.000Z', 'source':'browser',
        'now_epoch_seconds':1788782400, 'expires_at_seconds':2000000000,
        'maximum':3, 'bucket_id':'demo-bucket', 'breaker_id':'demo-breaker',
        'lifetime_id':'demo-lifetime', 'lifetime_max':100,
        'month_id':'demo-month', 'month_max':20, 'day_id':'demo-day', 'day_max':5,
        'start_sql_timestamp':'2026-09-01 00:00:00', 'start_date':'2026-09-01',
        'start_iso_timestamp':'2026-09-01T00:00:00.000Z',
        'end_iso_timestamp':'2026-09-07T23:59:59.999Z',
        'lock_until_seconds':1788782460, 'maximum_turns':3, 'messages_json':'[]',
        'cache_owner':'demo-owner', 'cache_key':'demo-cache',
        'record_json':'{"repositories":[]}', 'updated_at_milliseconds':2000,
    }

def smoke_runtime():
    """Execute every extracted statement independently, including mutation paths."""
    manifest = json.loads(sql('docs/source-manifest.json'))
    values = sample_bindings()
    for item in manifest['queries']:
        db = connect()
        params = [values[p] for p in item['parameters']]
        if item['name'] == 'create_session':
            params[0] = 'demo-new-session'
        db.execute(sql(item['path']), params).fetchall()
        db.close()
    return len(manifest['queries'])

def reports(db):
    return {
        name:[dict(row) for row in db.execute(sql('sql/analysis/'+name+'.sql'), WINDOW)]
        for name in ['calendar_activity','action_mix','rollup_reconciliation']
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Execute every runtime SQL statement and validate fixture totals.')
    args=parser.parse_args()
    db=connect()
    output=reports(db)
    if args.check:
        count=smoke_runtime()
        assert [r['page_views'] for r in output['calendar_activity']]==[2,0,4,0,1,0,2]
        assert all(r['difference']==0 for r in output['rollup_reconciliation'])
        assert db.execute('SELECT COUNT(*) FROM analytics_events').fetchone()[0]==17
        assert db.execute('SELECT SUM(count) FROM analytics_daily').fetchone()[0]==16
        print(f'PASS: 5 migrations, {count} runtime statements, 3 analysis reports; fixture totals verified.')
    else:
        print(json.dumps({'dataset':'Synthetic demonstration only','sqlite':sqlite3.sqlite_version,**output},indent=2))
    db.close()

if __name__=='__main__':
    main()
