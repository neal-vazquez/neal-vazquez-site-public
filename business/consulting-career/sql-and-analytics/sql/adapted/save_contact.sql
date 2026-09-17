-- Translation of the site's Drizzle contact INSERT, not an extracted literal.
-- Bind: name, email, inquiry_type, service, timeline, message, source.
-- Schema defaults supply ID, status and created_at. Never use real inquiries here.
INSERT INTO contact_inquiries
    (name, email, inquiry_type, service, timeline, message, source)
VALUES (?, ?, ?, ?, ?, ?, ?);
