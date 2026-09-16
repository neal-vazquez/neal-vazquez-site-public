"""Run a standalone, synthetic contact-center SQL case study without dependencies."""
import json
from pathlib import Path
import sqlite3

EXAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'contact-center'
PARAMS = {
    'start_at': '2026-09-01 00:00:00',
    'end_at': '2026-09-10 00:00:00',
    'as_of': '2026-09-16 00:00:00',
}


def connect(seed=True):
    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    db.executescript((EXAMPLE / 'schema.sql').read_text(encoding='utf-8'))
    if seed:
        db.executescript((EXAMPLE / 'fixture.sql').read_text(encoding='utf-8'))
    return db


def report(db, params=None):
    params = PARAMS if params is None else params
    if not params['start_at'] < params['end_at'] <= params['as_of']:
        raise ValueError('Require start_at < end_at <= as_of in canonical UTC format.')
    statement = (EXAMPLE / 'queue_metrics.sql').read_text(encoding='utf-8')
    return [dict(row) for row in db.execute(statement, params)]


def main():
    db = connect()
    try:
        print(json.dumps({
            'dataset': 'Synthetic contact-center exercise; no client data',
            'window': PARAMS,
            'queues': report(db),
        }, indent=2))
    finally:
        db.close()


if __name__ == '__main__':
    main()
