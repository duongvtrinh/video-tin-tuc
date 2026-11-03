DROP TABLE entries;
--> statement-breakpoint
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  step TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'running',
  started_at INTEGER NOT NULL,
  finished_at INTEGER,
  exit_code INTEGER,
  log_tail TEXT NOT NULL DEFAULT '',
  note TEXT NOT NULL DEFAULT ''
);
--> statement-breakpoint
CREATE TABLE trash (
  project_id TEXT PRIMARY KEY,
  name TEXT NOT NULL DEFAULT '',
  deleted_at INTEGER NOT NULL
);
--> statement-breakpoint
CREATE TABLE snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  note TEXT NOT NULL DEFAULT ''
);
