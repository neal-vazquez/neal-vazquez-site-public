-- Portfolio extension: gap-free daily page views and a seven-calendar-day mean.
-- Bind :start_date and :end_date as inclusive UTC YYYY-MM-DD dates.
-- Restrict the window to days with retained raw events and known collection.
WITH RECURSIVE calendar(date) AS (
    SELECT date(:start_date) WHERE date(:start_date) <= date(:end_date)
    UNION ALL
    SELECT date(date, '+1 day') FROM calendar WHERE date < date(:end_date)
), daily AS (
    SELECT substr(received_at, 1, 10) AS date, COUNT(*) AS page_views
    FROM analytics_events
    WHERE source = 'browser' AND event_name = 'page_view'
      AND received_at >= :start_date || ' 00:00:00'
      AND received_at < date(:end_date, '+1 day') || ' 00:00:00'
    GROUP BY substr(received_at, 1, 10)
), filled AS (
    SELECT calendar.date, COALESCE(daily.page_views, 0) AS page_views
    FROM calendar LEFT JOIN daily USING (date)
), windows AS (
    SELECT date, page_views,
           LAG(page_views) OVER (ORDER BY date) AS previous_day,
           COUNT(*) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS days_in_window,
           ROUND(AVG(page_views) OVER (
               ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
           ), 2) AS trailing_mean
    FROM filled
)
SELECT date, page_views, days_in_window, trailing_mean,
       ROUND(100.0 * (page_views - previous_day) / NULLIF(previous_day, 0), 2) AS change_pct
FROM windows ORDER BY date;
