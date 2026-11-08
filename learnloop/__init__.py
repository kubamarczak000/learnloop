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
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-key"),
        DATABASE_PATH=os.environ.get(
            "DATABASE_PATH", str(Path(app.instance_path) / "naukaplan.sqlite3")
        ),
        MAX_CONTENT_LENGTH=1 * 1024 * 1024,
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

    @app.context_processor
    def inject_today() -> dict:
        return {"today_iso": date.today().isoformat()}

    return app
