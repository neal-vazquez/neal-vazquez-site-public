import sys
import hashlib
import json
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from demo import connect, query, reports, smoke_runtime, sql, WINDOW

class SQLBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
    def tearDown(self):
        self.db.close()

    def test_all_runtime_statements_execute(self):
        self.assertEqual(smoke_runtime(),22)

    def test_historical_source_hashes_are_preserved(self):
        manifest = json.loads(sql('docs/source-manifest.json'))
        for item in manifest['migrations']:
            with self.subTest(path=item['path']):
                path = Path(__file__).resolve().parents[1] / item['path']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])
        for item in manifest['queries']:
            with self.subTest(path=item['path']):
                literal = '\n'.join(line for line in sql(item['path']).splitlines()
                                    if not line.startswith('--')).strip().removesuffix(';')
                self.assertEqual(hashlib.sha256(literal.encode()).hexdigest(), item['literal_sha256'])

    def test_replay_is_idempotent_and_server_events_do_not_roll_up(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM analytics_events').fetchone()[0],17)
        self.assertEqual(self.db.execute('SELECT SUM(count) FROM analytics_daily').fetchone()[0],16)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM analytics_daily WHERE event_name='lead_saved'").fetchone()[0],0)
        before=self.db.execute('SELECT SUM(count) FROM analytics_daily').fetchone()[0]
        query(self.db,'record_event',('demo-03','project_click','/','work','{}',None,'2026-09-01T10:02:00.000Z','browser'))
        self.assertEqual(self.db.execute('SELECT SUM(count) FROM analytics_daily').fetchone()[0],before)

    def test_legacy_and_current_counts_combine_once(self):
        rows=query(self.db,'daily_activity',('2026-09-01 00:00:00','2026-09-01')).fetchall()
        self.assertEqual(sum(r['count'] for r in rows if r['eventName']=='page_view'),10)
        self.assertEqual(sum(r['count'] for r in rows if r['eventName']=='project_click'),4)
        pages=query(self.db,'page_rankings',('2026-09-01 00:00:00',)*2).fetchall()
        self.assertEqual({r['path']:r['count'] for r in pages},{'/':7,'/dashboard':3})
        locations=query(self.db,'location_rankings',('2026-09-01 00:00:00','2026-09-01')).fetchall()
        self.assertEqual([dict(r) for r in locations],[{'location':'work','count':4}])

    def test_quota_stops_at_cap(self):
        for name in ['reserve_chat_quota','reserve_analytics_quota']:
            self.assertEqual(query(self.db,name,(name,2000000000,2)).fetchone()[0],1)
            self.assertEqual(query(self.db,name,(name,2000000000,2)).fetchone()[0],2)
            self.assertIsNone(query(self.db,name,(name,2000000000,2)).fetchone())

    def test_session_lease_prevents_second_reservation_and_turn_cap(self):
        args=(1060,'demo-session',1000,1)
        self.assertIsNotNone(query(self.db,'acquire_session_lock',args).fetchone())
        self.assertIsNone(query(self.db,'acquire_session_lock',args).fetchone())
        query(self.db,'save_session_turn',('[]','demo-session')).fetchone()
        self.assertIsNone(query(self.db,'acquire_session_lock',(1120,'demo-session',1061,1)).fetchone())
        self.assertIsNone(query(self.db,'read_active_session',('demo-session',2000000000)).fetchone())

    def test_older_cache_write_cannot_overwrite_newer_record(self):
        query(self.db,'upsert_cache',('demo-owner','new','{"version":2}',2000))
        query(self.db,'upsert_cache',('demo-owner','old','{"version":1}',1500))
        self.assertEqual(query(self.db,'read_cache',('demo-owner',)).fetchone()['cache_key'],'new')

    def test_breaker_expiry_never_shortens(self):
        query(self.db,'extend_breaker',('demo-breaker',2000))
        query(self.db,'extend_breaker',('demo-breaker',1500))
        self.assertEqual(self.db.execute("SELECT expires_at FROM chat_usage WHERE id='demo-breaker'").fetchone()[0],2000)
        self.assertEqual(query(self.db,'budget_status',('demo-breaker',1000,'l',100,'m',20,'d',5)).fetchone()[0],1)
        self.assertEqual(query(self.db,'budget_status',('demo-breaker',2000,'l',100,'m',20,'d',5)).fetchone()[0],0)

    def test_cleanup_is_bounded_and_preserves_daily_history(self):
        self.db.executemany("INSERT INTO analytics_events (id,event_name,path,location,occurred_at,received_at) VALUES (?,'page_view','/','homepage','2000-01-01T00:00:00.000Z','2000-01-01 00:00:00')",[(f'old-{i}',) for i in range(105)])
        query(self.db,'prune_analytics_events')
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM analytics_events WHERE id LIKE 'old-%'").fetchone()[0],5)
        self.assertEqual(self.db.execute("SELECT count FROM analytics_daily WHERE date='2000-01-01'").fetchone()[0],105)
        for table,name in [('chat_sessions','prune_chat_sessions'),('chat_usage','prune_chat_usage'),('analytics_limits','prune_analytics_limits')]:
            self.db.executemany(f'INSERT INTO {table} (id,expires_at) VALUES (?,1)',[(f'expired-{i}',) for i in range(105)])
            query(self.db,name,(1000,))
            self.assertEqual(self.db.execute(f"SELECT COUNT(*) FROM {table} WHERE id LIKE 'expired-%'").fetchone()[0],5)

    def test_chat_dimensions_and_time_bounds(self):
        rows=query(self.db,'chat_engagement',('2026-09-01 00:00:00','2026-09-01T00:00:00.000Z','2026-09-07T23:59:59.999Z')).fetchall()
        self.assertEqual(sum(r['count'] for r in rows),3)
        self.assertTrue(any(r['device']=='unknown' and r['page']=='/other' for r in rows))
        self.assertTrue(any(r['topic']=='project' for r in rows))
        self.assertEqual(set(rows[0].keys()),{'date','eventName','device','page','topic','count'})

    def test_calendar_includes_empty_days_and_safe_denominator(self):
        rows=reports(self.db)['calendar_activity']
        self.assertEqual([r['page_views'] for r in rows],[2,0,4,0,1,0,2])
        self.assertIsNone(rows[0]['change_pct'])
        self.assertIsNone(rows[2]['change_pct'])
        self.assertEqual(rows[-1]['days_in_window'],7)
        self.assertEqual(rows[-1]['trailing_mean'],1.29)
        self.assertEqual(self.db.execute(sql('sql/analysis/calendar_activity.sql'),{'start_date':'2026-09-07','end_date':'2026-09-01'}).fetchall(),[])

    def test_reconciliation_detects_missing_or_extra_rollups(self):
        self.assertTrue(all(r['difference']==0 for r in reports(self.db)['rollup_reconciliation']))
        self.db.execute("UPDATE analytics_daily SET count=count+2 WHERE date='2026-09-01' AND event_name='project_click'")
        self.assertTrue(any(r['difference']==2 for r in reports(self.db)['rollup_reconciliation']))
        self.db.execute("DELETE FROM analytics_daily WHERE date='2026-09-05'")
        self.assertTrue(any(r['difference']<0 for r in reports(self.db)['rollup_reconciliation']))

    def test_receipt_date_semantics_and_contact_translation(self):
        self.assertEqual(self.db.execute("SELECT count FROM analytics_daily WHERE date='2026-09-07' AND event_name='project_click'").fetchone()[0],1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM analytics_daily WHERE date='2026-09-06'").fetchone()[0],0)
        self.db.execute(sql('sql/adapted/save_contact.sql'),('Demo Person','demo@example.invalid','General inquiry',None,None,'Synthetic example only.','demo'))
        self.assertEqual(self.db.execute('SELECT status FROM contact_inquiries').fetchone()[0],'new')

if __name__=='__main__':
    unittest.main()
