"""Obsługa połączenia i inicjalizacji lokalnej bazy SQLite."""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Zwraca jedno połączenie z bazą na cały bieżący request."""
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    """Tworzy tabele i dodaje kolumny kont do starszych lokalnych baz."""
    connection = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    for table in ("goals", "calendar_events", "work_tasks"):
        columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
        if "user_id" not in columns:
            connection.execute(
                f"ALTER TABLE {table} ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"
            )
    user_columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)")}
    if "role" not in user_columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'root'))"
        )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_single_root_user ON users(role) WHERE role = 'root'"
    )
    connection.execute(
        """INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value)
           SELECT u.id, 'weekly_goal_minutes',
                  COALESCE((SELECT setting_value FROM app_settings
                            WHERE setting_key = 'weekly_goal_minutes'), '180')
           FROM users u"""
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, status)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_events_user_date ON calendar_events(user_id, event_date)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_due ON work_tasks(user_id, due_date)")
    connection.commit()

