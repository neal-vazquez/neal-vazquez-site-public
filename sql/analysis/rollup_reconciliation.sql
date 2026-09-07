-- Portfolio extension: compare raw browser events with trigger totals.
-- Only interpret as an integrity check for fully retained receipt-date windows.
-- Bind :start_date and :end_date as inclusive dates.
WITH raw AS (
    SELECT substr(received_at, 1, 10) AS date, event_name, location, COUNT(*) AS raw_count
    FROM analytics_events
    WHERE source = 'browser'
      AND received_at >= :start_date || ' 00:00:00'
      AND received_at < date(:end_date, '+1 day') || ' 00:00:00'
    GROUP BY substr(received_at, 1, 10), event_name, location
), rolled AS (
    SELECT date, event_name, location, SUM(count) AS rollup_count
    FROM analytics_daily WHERE date BETWEEN :start_date AND :end_date
    GROUP BY date, event_name, location
), dimensions AS (
    SELECT date, event_name, location FROM raw
    UNION
    SELECT date, event_name, location FROM rolled
)
SELECT d.date, d.event_name, d.location,
       COALESCE(r.raw_count, 0) AS raw_count,
       COALESCE(a.rollup_count, 0) AS rollup_count,
       COALESCE(a.rollup_count, 0) - COALESCE(r.raw_count, 0) AS difference
FROM dimensions AS d
LEFT JOIN raw AS r USING (date, event_name, location)
LEFT JOIN rolled AS a USING (date, event_name, location)
ORDER BY d.date, d.event_name, d.location;
