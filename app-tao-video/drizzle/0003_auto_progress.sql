CREATE TABLE auto_progress (
  project_id TEXT PRIMARY KEY,
  statuses TEXT NOT NULL DEFAULT '{}',
  messages TEXT NOT NULL DEFAULT '[]',
  needs_manual TEXT NOT NULL DEFAULT '[]',
  updated_at INTEGER NOT NULL DEFAULT 0
);
