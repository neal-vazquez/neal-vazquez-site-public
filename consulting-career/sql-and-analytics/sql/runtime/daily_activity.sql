-- Combine legacy event counts and current daily rollups.
-- Extracted from db/portfolio-events.ts; parameter order: start_sql_timestamp, start_date.
SELECT date,eventName,SUM(count) AS count FROM (
    SELECT substr(created_at,1,10) AS date,event_name AS eventName,COUNT(*) AS count FROM portfolio_events WHERE created_at>=? GROUP BY date,event_name
    UNION ALL SELECT date,event_name AS eventName,count FROM analytics_daily WHERE date>=?
  ) GROUP BY date,eventName ORDER BY date ASC,count DESC;
