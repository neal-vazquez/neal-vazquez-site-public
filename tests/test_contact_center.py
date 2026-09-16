import sqlite3
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from contact_center import connect, report, PARAMS


class ContactCenterTests(unittest.TestCase):
    def setUp(self):
        self.db = connect()

    def tearDown(self):
        self.db.close()

    def rows(self, params=None):
        return {row['queue']: row for row in report(self.db, params)}

    def test_hand_calculated_fixture_totals(self):
        rows = self.rows()
        self.assertEqual(sum(r['offered_contacts'] for r in rows.values()), 10)
        billing = rows['billing']
        self.assertEqual((billing['handled_contacts'], billing['abandoned_contacts']), (5, 1))
        self.assertEqual(billing['aht_seconds'], 324)
        self.assertEqual((billing['eligible_cases'], billing['fcr_cases'], billing['pending_cases']), (3, 2, 1))
        self.assertEqual(billing['fcr_pct'], 66.67)
        technical = rows['technical']
        self.assertEqual(technical['aht_seconds'], 660)
        self.assertEqual((technical['eligible_cases'], technical['fcr_cases']), (3, 1))
        self.assertEqual(technical['fcr_pct'], 33.33)
        # Recombine sufficient statistics, never average queue averages.
        self.assertEqual(sum(r['total_handle_seconds'] for r in rows.values()) /
                         sum(r['timed_contacts'] for r in rows.values()), 450)

    def test_missing_handle_time_is_not_zero(self):
        row = self.rows()['technical']
        self.assertEqual((row['handled_contacts'], row['timed_contacts'], row['missing_handle_times']), (4, 3, 1))
        self.db.execute('UPDATE contacts SET handle_seconds = NULL WHERE handled = 1')
        self.assertTrue(all(r['aht_seconds'] is None for r in report(self.db)))

    def test_followup_outside_reporting_window_changes_fcr_only(self):
        before = self.rows()['technical']
        self.db.execute("DELETE FROM contacts WHERE contact_id = 'c10'")
        after = self.rows()['technical']
        self.assertEqual(after['offered_contacts'], before['offered_contacts'])
        self.assertEqual(after['fcr_cases'], before['fcr_cases'] + 1)

    def test_maturity_boundary_and_future_records(self):
        params = {**PARAMS, 'as_of': '2026-09-16 11:00:00'}
        self.assertEqual(self.rows(params)['billing']['pending_cases'], 1)
        params['as_of'] = '2026-09-16 11:00:01'
        self.assertEqual(self.rows(params)['billing']['pending_cases'], 0)
        before = report(self.db)
        self.db.execute("INSERT INTO contacts VALUES ('future', 'issue-1', 'billing', '2026-09-16 00:00:00', 1, 10, 1)")
        self.assertEqual(report(self.db), before)

    def test_repeat_exactly_seven_days_later_disqualifies_case(self):
        self.db.execute("INSERT INTO contacts VALUES ('boundary', 'issue-1', 'billing', '2026-09-08 09:00:00', 1, 10, 1)")
        self.assertEqual(self.rows()['billing']['fcr_cases'], 1)
        self.db.execute("UPDATE contacts SET started_at = '2026-09-08 09:00:01' WHERE contact_id = 'boundary'")
        self.assertEqual(self.rows()['billing']['fcr_cases'], 2)

    def test_prior_history_prevents_false_first_contact_and_queue_fanout(self):
        self.db.execute("INSERT INTO contacts VALUES ('prior', 'issue-1', 'technical', '2026-08-31 09:00:00', 1, 100, 0)")
        row = self.rows()['billing']
        self.assertEqual((row['eligible_cases'], row['fcr_cases']), (2, 1))
        self.assertEqual(sum(r['offered_contacts'] for r in report(self.db)), 10)

    def test_empty_and_unmatured_cohorts_have_no_fabricated_rates(self):
        params = {**PARAMS, 'as_of': PARAMS['end_at']}
        self.assertEqual(self.rows(params)['billing']['pending_cases'], 2)
        self.db.execute('DELETE FROM contacts')
        self.assertEqual(report(self.db), [])
        self.db.execute("INSERT INTO contacts VALUES ('only', 'only', 'billing', '2026-09-09 00:00:00', 1, 10, 1)")
        self.assertIsNone(self.rows(params)['billing']['fcr_pct'])
        self.db.execute("UPDATE contacts SET handled = 0, handle_seconds = NULL, resolved = 0")
        row = self.rows()['billing']
        self.assertEqual(row['first_contact_cases'], 0)
        self.assertIsNone(row['fcr_pct'])
        self.assertIsNone(row['aht_seconds'])

    def test_unique_contacts_and_valid_reporting_window(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO contacts SELECT * FROM contacts WHERE contact_id = 'c01'")
        with self.assertRaises(ValueError):
            report(self.db, {**PARAMS, 'end_at': '2026-09-17 00:00:00'})


if __name__ == '__main__':
    unittest.main()
