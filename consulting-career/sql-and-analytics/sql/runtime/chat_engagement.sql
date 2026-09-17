-- Aggregate chat actions with allowlisted JSON device, page and topic dimensions.
-- Extracted from db/chat-engagement.ts; parameter order: start_sql_timestamp, start_iso_timestamp, end_iso_timestamp.
SELECT substr(occurred_at,1,10) AS date, event_name AS eventName,
      CASE json_extract(parameters,'$.device_category') WHEN 'mobile' THEN 'mobile' WHEN 'tablet' THEN 'tablet' WHEN 'desktop' THEN 'desktop' ELSE 'unknown' END AS device,
      CASE path WHEN '/' THEN '/' WHEN '/dashboard' THEN '/dashboard' WHEN '/services/data-ai' THEN '/services/data-ai' WHEN '/services/research-ux' THEN '/services/research-ux' WHEN '/services/career-brand' THEN '/services/career-brand' WHEN '/testimonials' THEN '/testimonials' WHEN '/privacy' THEN '/privacy' ELSE '/other' END AS page,
      CASE WHEN event_name='chat_guide_select' THEN CASE json_extract(parameters,'$.guide_topic') WHEN 'project' THEN 'project' WHEN 'experience' THEN 'experience' WHEN 'writing' THEN 'writing' WHEN 'availability' THEN 'availability' ELSE 'overview' END ELSE 'none' END AS topic,
      COUNT(*) AS count FROM analytics_events
      WHERE received_at >= ? AND occurred_at >= ? AND occurred_at <= ?
      AND event_name IN ('chat_button_click','chat_open','chat_guide_select','chat_ai_open','chat_message_attempt','chat_message_sent','chat_sms_open','chat_contact_open','chat_topic_select','chat_fallback')
      GROUP BY date,event_name,device,page,topic ORDER BY date LIMIT 10001;
