-- Portfolio extension: event counts by received UTC date.
-- These are repeatable actions, not unique visitors or a sequential funnel.
-- Bind :start_date and :end_date as inclusive dates.
SELECT substr(received_at, 1, 10) AS date,
       SUM(CASE WHEN source = 'browser' AND event_name = 'page_view' THEN 1 ELSE 0 END) AS page_views,
       SUM(CASE WHEN source = 'browser' AND event_name = 'project_click' THEN 1 ELSE 0 END) AS project_clicks,
       SUM(CASE WHEN source = 'browser' AND event_name = 'chat_open' THEN 1 ELSE 0 END) AS chat_opens,
       SUM(CASE WHEN source = 'server' AND event_name = 'lead_saved' THEN 1 ELSE 0 END) AS inquiries_saved
FROM analytics_events
WHERE received_at >= :start_date || ' 00:00:00'
  AND received_at < date(:end_date, '+1 day') || ' 00:00:00'
GROUP BY substr(received_at, 1, 10)
ORDER BY date;
