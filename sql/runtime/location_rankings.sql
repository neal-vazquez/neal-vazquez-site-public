-- Rank meaningful page areas and exclude chat/operational events.
-- Extracted from db/portfolio-events.ts; parameter order: start_sql_timestamp, start_date.
SELECT location,SUM(count) AS count FROM (
    SELECT COALESCE(NULLIF(location,''),'other') AS location,COUNT(*) AS count FROM portfolio_events WHERE created_at>=? AND event_name NOT GLOB 'chat_*' AND event_name NOT IN ('web_vital','client_error','server_error') GROUP BY location
    UNION ALL SELECT location,count FROM analytics_daily WHERE date>=? AND event_name NOT GLOB 'chat_*' AND event_name NOT IN ('web_vital','client_error','server_error')
  ) WHERE location NOT IN ('homepage','portfolio_dashboard','service_landing','testimonial_archive','legal','other','chat_widget','chat_launcher') GROUP BY location ORDER BY count DESC,location ASC LIMIT 100;
