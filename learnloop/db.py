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
    """Tworzy brakujące tabele; bezpieczne do uruchomienia przy każdym starcie."""
    connection = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    connection.commit()

