CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'root')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_key TEXT NOT NULL,
    setting_value TEXT NOT NULL,
    PRIMARY KEY (user_id, setting_key)
);

CREATE TABLE IF NOT EXISTS calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    event_date TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('exam', 'colloquium', 'deadline', 'other')),
    goal_id INTEGER REFERENCES goals(id) ON DELETE SET NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS planned_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES calendar_events(id) ON DELETE CASCADE,
    study_date TEXT NOT NULL,
    minutes INTEGER NOT NULL DEFAULT 30 CHECK (minutes BETWEEN 15 AND 120),
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS work_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL DEFAULT 'todo'
        CHECK (status IN ('todo', 'in_progress', 'done')),
    estimate_minutes INTEGER NOT NULL DEFAULT 30
        CHECK (estimate_minutes BETWEEN 5 AND 1440),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);
CREATE INDEX IF NOT EXISTS idx_sessions_goal_date ON study_sessions(goal_id, studied_on DESC);
CREATE INDEX IF NOT EXISTS idx_calendar_event_date ON calendar_events(event_date);
CREATE INDEX IF NOT EXISTS idx_planned_sessions_event_date ON planned_sessions(event_id, study_date);
CREATE INDEX IF NOT EXISTS idx_work_tasks_due_status ON work_tasks(due_date, status);
