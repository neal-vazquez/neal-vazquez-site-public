-- Reporting period: [:start_at, :end_at); data observed strictly before :as_of.
-- Seven-day FCR proxy: first handled contact marked resolved, no further handled
-- contact on the same case within seven days, and complete follow-up observed.
-- Equality at the maturity boundary stays pending because :as_of is exclusive.
WITH observed AS (
    SELECT * FROM contacts WHERE started_at < :as_of
), volumes AS (
    SELECT queue,
           COUNT(*) AS offered_contacts,
           SUM(handled) AS handled_contacts,
           COUNT(*) - SUM(handled) AS abandoned_contacts,
           SUM(CASE WHEN handled = 1 AND handle_seconds IS NOT NULL THEN 1 ELSE 0 END) AS timed_contacts,
           SUM(CASE WHEN handled = 1 AND handle_seconds IS NULL THEN 1 ELSE 0 END) AS missing_handle_times,
           SUM(CASE WHEN handled = 1 THEN COALESCE(handle_seconds, 0) ELSE 0 END) AS total_handle_seconds
    FROM observed
    WHERE started_at >= :start_at AND started_at < :end_at
    GROUP BY queue
), ranked AS (
    -- Rank full observed history, before restricting the first-contact cohort.
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY case_id ORDER BY started_at, contact_id
    ) AS contact_number
    FROM observed WHERE handled = 1
), first_contacts AS (
    SELECT *, CASE WHEN datetime(started_at, '+7 days') < :as_of THEN 1 ELSE 0 END AS mature
    FROM ranked
    WHERE contact_number = 1 AND started_at >= :start_at AND started_at < :end_at
), cohort AS (
    SELECT f.queue, COUNT(*) AS first_contact_cases,
           SUM(f.mature) AS eligible_cases,
           SUM(CASE WHEN f.mature = 0 THEN 1 ELSE 0 END) AS pending_cases,
           SUM(CASE WHEN f.mature = 1 AND f.resolved = 1 AND NOT EXISTS (
               SELECT 1 FROM observed AS followup
               WHERE followup.case_id = f.case_id AND followup.handled = 1
                 AND followup.contact_id <> f.contact_id
                 AND followup.started_at >= f.started_at
                 AND followup.started_at <= datetime(f.started_at, '+7 days')
           ) THEN 1 ELSE 0 END) AS fcr_cases
    FROM first_contacts AS f
    GROUP BY f.queue
)
-- Aggregate the two grains independently before joining to avoid fan-out.
SELECT v.queue, v.offered_contacts, v.handled_contacts, v.abandoned_contacts,
       v.timed_contacts, v.missing_handle_times, v.total_handle_seconds,
       ROUND(1.0 * v.total_handle_seconds / NULLIF(v.timed_contacts, 0), 2) AS aht_seconds,
       COALESCE(c.first_contact_cases, 0) AS first_contact_cases,
       COALESCE(c.eligible_cases, 0) AS eligible_cases,
       COALESCE(c.pending_cases, 0) AS pending_cases,
       COALESCE(c.fcr_cases, 0) AS fcr_cases,
       ROUND(100.0 * c.fcr_cases / NULLIF(c.eligible_cases, 0), 2) AS fcr_pct
FROM volumes AS v
LEFT JOIN cohort AS c USING (queue)
ORDER BY v.queue;
