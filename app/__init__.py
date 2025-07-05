"""Application factory and extension initialisation for AI‑Genesis Engine."""
from __future__ import annotations

import os
from typing import Type

from celery import Celery
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

# Optional Sentry import (keeps local dev lean)
try:
    import sentry_sdk
except ImportError:  # pragma: no cover
    sentry_sdk = None  # type: ignore

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------

db: SQLAlchemy = SQLAlchemy()
mail: Mail = Mail()
migrate: Migrate = Migrate(render_as_batch=True)
login_manager: LoginManager = LoginManager()
login_manager.login_view = "auth.login"

# Celery instance is module‑level so tasks can import it directly.
# Broker / backend are injected via env‑vars in render.yaml.
celery: Celery = Celery(__name__)

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    # ---------------------------------------------------------------------
    # Config selection
    # ---------------------------------------------------------------------

    config_name = config_name or os.getenv("FLASK_CONFIG", "dev")
    app_config: Type[object] = config.get(config_name, config["dev"])

    app: Flask = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    # ---------------------------------------------------------------------
    # Initialise extensions
    # ---------------------------------------------------------------------

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Celery needs broker / backend + app context
    celery.conf.update(
        broker_url=app.config.get("CELERY_BROKER_URL"),
        result_backend=app.config.get("CELERY_RESULT_BACKEND"),
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
    )

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):  # type: ignore[override]
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask  # type: ignore[assignment]

    # ---------------------------------------------------------------------
    # Conditional Sentry setup
    # ---------------------------------------------------------------------

    if sentry_sdk and (dsn := app.config.get("SENTRY_DSN")):
        sentry_sdk.init(
            dsn=dsn,
            enable_tracing=True,
            traces_sample_rate=1.0,
        )

    # ---------------------------------------------------------------------
    # Blueprints
    # ---------------------------------------------------------------------

    from .main import main as main_bp
    from .auth import auth as auth_bp
    from .payments import payments as payments_bp
    from .features import features as features_bp
    from .api import api as api_bp
    from .admin import admin as admin_ext

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(features_bp, url_prefix="/features")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    admin_ext.init_app(app)

    # ---------------------------------------------------------------------
    # User loader
    # ---------------------------------------------------------------------

    from .models import User  # local import to avoid circular dependency

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:  # type: ignore[name-defined]
        return User.query.get(int(user_id))  # type: ignore[attr-defined]

    return app
