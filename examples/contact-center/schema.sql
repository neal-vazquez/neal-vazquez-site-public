-- Standalone synthetic exercise, unrelated to the website schema or client data.
-- One row per logical contact, after source deduplication and transfer-leg consolidation.
CREATE TABLE contacts (
    contact_id TEXT PRIMARY KEY NOT NULL,
    case_id TEXT NOT NULL,
    queue TEXT NOT NULL,
    started_at TEXT NOT NULL, -- canonical UTC YYYY-MM-DD HH:MM:SS
    handled INTEGER NOT NULL CHECK (handled IN (0, 1)),
    handle_seconds INTEGER CHECK (handle_seconds >= 0),
    resolved INTEGER NOT NULL CHECK (resolved IN (0, 1)),
    CHECK (handled = 1 OR (handle_seconds IS NULL AND resolved = 0))
);
CREATE INDEX contacts_case_time ON contacts(case_id, started_at, contact_id);
CREATE INDEX contacts_time ON contacts(started_at);
