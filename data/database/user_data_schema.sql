PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS study_sessions;

CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  study_space_id INTEGER NOT NULL,
  building_id TEXT NOT NULL,

  started_at TEXT NOT NULL,
  ended_at TEXT,
  duration_ms INTEGER,
  ended_reason TEXT,

  start_date TEXT NOT NULL,
  start_weather_time_local TEXT,

  session_traffic REAL,

  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_date
ON study_sessions(user_id, start_date);

CREATE INDEX IF NOT EXISTS idx_sessions_weather_time
ON study_sessions(start_weather_time_local);

CREATE TABLE IF NOT EXISTS bookmarks (
  user_id TEXT NOT NULL,
  study_space_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  deleted_at TEXT,
  PRIMARY KEY (user_id, study_space_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS spot_feedback (
  user_id TEXT NOT NULL,
  study_space_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  thumb TEXT NOT NULL CHECK (thumb IN ('UP','DOWN')),
  updated_at TEXT NOT NULL,
  PRIMARY KEY (user_id, study_space_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS spot_detail_views (
  view_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  study_space_id INTEGER NOT NULL,
  building_id INTEGER NOT NULL,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  dwell_ms INTEGER,
  source TEXT,
  list_rank INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_bookmarks_user
ON bookmarks(user_id);

CREATE INDEX IF NOT EXISTS idx_feedback_user
ON spot_feedback(user_id);

CREATE INDEX IF NOT EXISTS idx_views_user_time
ON spot_detail_views(user_id, opened_at);
