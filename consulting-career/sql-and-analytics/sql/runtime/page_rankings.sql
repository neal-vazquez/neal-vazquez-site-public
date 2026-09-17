-- Rank page views across legacy and current browser events.
-- Extracted from db/portfolio-events.ts; parameter order: start_sql_timestamp, start_sql_timestamp.
SELECT path, SUM(count) AS count FROM (
    SELECT path,COUNT(*) AS count FROM portfolio_events WHERE created_at>=? AND event_name='page_view' GROUP BY path
    UNION ALL SELECT path,COUNT(*) AS count FROM analytics_events WHERE received_at>=? AND source='browser' AND event_name='page_view' GROUP BY path
  ) GROUP BY path ORDER BY count DESC,path ASC LIMIT 10;
