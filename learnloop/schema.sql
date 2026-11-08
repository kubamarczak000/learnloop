CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT 'Inne',
    target_date TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'paused')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    minutes INTEGER NOT NULL CHECK (minutes BETWEEN 1 AND 1440),
    note TEXT NOT NULL DEFAULT '',
    studied_on TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL
);

INSERT OR IGNORE INTO app_settings (setting_key, setting_value)
VALUES ('weekly_goal_minutes', '180');

CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_sessions_goal_date ON study_sessions(goal_id, studied_on DESC);
