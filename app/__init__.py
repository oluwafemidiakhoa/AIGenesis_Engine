# app/__init__.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from celery import Celery

from config import config

# Conditional import for sentry
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

# Extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Celery setup
celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

def create_app(config_name='dev'):
    """
    Application factory function.
    Configures and returns the Flask application instance.
    """
    app_config = config.get(config_name, config['dev'])

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    # --- Initialize Extensions ---
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, render_as_batch=True) # render_as_batch is good practice for SQLite
    login_manager.init_app(app)
    
    from .admin import admin
    admin.init_app(app)

    # --- Sentry Initialization ---
    sentry_dsn = app.config.get('SENTRY_DSN')
    if sentry_sdk and sentry_dsn and sentry_dsn.startswith('http'):
        sentry_sdk.init(
            dsn=sentry_dsn,
            enable_tracing=True,
            traces_sample_rate=1.0
        )

    # --- Celery Configuration ---
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # --- Register Blueprints ---
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .payments import payments as payments_blueprint
    app.register_blueprint(payments_blueprint, url_prefix='/payments')
    from .features import features as features_blueprint
    app.register_blueprint(features_blueprint, url_prefix='/features')
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    # --- App Context Configuration ---
    with app.app_context():
        from . import models

        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

    return app
