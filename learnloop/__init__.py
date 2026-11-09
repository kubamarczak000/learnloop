"""Fabryka aplikacji LearnLoop."""

import os
from pathlib import Path
from datetime import date

from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app(test_config: dict | None = None) -> Flask:
    """Buduje aplikację Flask i przygotowuje jej lokalną bazę danych."""
    app = Flask(__name__, instance_relative_config=True)
    default_data_dir = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", app.instance_path)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-key"),
        DATABASE_PATH=os.environ.get(
            "DATABASE_PATH", str(Path(default_data_dir) / "naukaplan.sqlite3")
        ),
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true",
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    csrf.init_app(app)

    from . import db

    with app.app_context():
        db.init_db()
    app.teardown_appcontext(db.close_db)

    from .routes import bp

    app.register_blueprint(bp)

    @app.cli.command("create-root")
    def create_root_command() -> None:
        """Create the single administrator account using private terminal prompts."""
        import re
        import sqlite3

        import click
        from werkzeug.security import generate_password_hash

        from .db import get_db

        email = click.prompt("E-mail administratora root").strip().lower()
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise click.ClickException("Podaj poprawny adres e-mail.")
        password = click.prompt("Unikalne hasło root", hide_input=True, confirmation_prompt=True)
        if len(password) < 10 or len(password) > 128:
            raise click.ClickException("Hasło musi mieć od 10 do 128 znaków.")

        connection = get_db()
        try:
            password_hash = generate_password_hash(password)
            existing_user = connection.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing_user:
                connection.execute(
                    "UPDATE users SET password_hash = ?, role = 'root' WHERE id = ?",
                    (password_hash, existing_user["id"]),
                )
                root_id = existing_user["id"]
            else:
                connection.execute(
                    "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'root')",
                    (email, password_hash),
                )
                root_id = connection.execute("SELECT last_insert_rowid()").fetchone()[0]
                connection.execute(
                    """INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value)
                       VALUES (?, 'weekly_goal_minutes', '180')""",
                    (root_id,),
                )
            connection.execute(
                """INSERT OR IGNORE INTO user_settings (user_id, setting_key, setting_value)
                   VALUES (?, 'weekly_goal_minutes', '180')""",
                (root_id,),
            )
            connection.commit()
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise click.ClickException(
                "Ten e-mail jest już używany albo konto root już istnieje."
            ) from error
        click.echo("Konto root zostało skonfigurowane. Zaloguj się przez stronę LearnLoop.")

    @app.context_processor
    def inject_today() -> dict:
        return {"today_iso": date.today().isoformat()}

    return app
