-- Invented contacts only. No customer identifiers, transcripts, or client records.
INSERT INTO contacts VALUES
('c01', 'issue-1', 'billing', '2026-09-01 09:00:00', 1, 300, 1),
('c02', 'issue-2', 'billing', '2026-09-01 10:00:00', 1, 600, 1),
('c03', 'issue-2', 'billing', '2026-09-03 10:00:00', 1, 300, 1),
('c04', 'issue-3', 'technical', '2026-09-02 09:00:00', 1, 900, 0),
('c05', 'issue-3', 'technical', '2026-09-04 09:00:00', 1, 600, 1),
('c06', 'issue-4', 'billing', '2026-09-04 10:00:00', 0, NULL, 0),
('c07', 'issue-5', 'technical', '2026-09-07 10:00:00', 1, NULL, 1),
('c08', 'issue-6', 'billing', '2026-09-08 10:00:00', 1, 240, 1),
('c09', 'issue-7', 'technical', '2026-09-08 11:00:00', 1, 480, 1),
-- Follow-up outside the reporting period still disqualifies first-contact resolution.
('c10', 'issue-7', 'technical', '2026-09-10 11:00:00', 1, 420, 1),
-- Recent first contact lacks a complete seven-day follow-up window at the cutoff.
('c11', 'issue-8', 'billing', '2026-09-09 11:00:00', 1, 180, 1);
