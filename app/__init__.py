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
    app_config = config.get(config_name, config['dev'])

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

<<<<<<< HEAD
    # Initialize Sentry if a DSN is provided and looks valid.
    # This prevents the app from crashing if the env var is set to an empty or invalid string.
    sentry_dsn = app.config.get('SENTRY_DSN')
    if sentry_dsn and sentry_dsn.startswith('http'):
        sentry_sdk.init(
            dsn=sentry_dsn,
            # Enable performance monitoring
=======
    # Init Sentry only in production or when DSN is provided
    sentry_dsn = app.config.get('SENTRY_DSN')
    if sentry_sdk and sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
>>>>>>> f35751b (Initial commit)
            enable_tracing=True,
            traces_sample_rate=1.0
        )

    # Setup extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Celery context binding
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

<<<<<<< HEAD
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    from .admin import admin
    admin.init_app(app)

    # Within the app context, ensure the database and its tables are created.
    with app.app_context():
        # Importing models here prevents circular import errors
        from . import models

        @login_manager.user_loader
        def load_user(user_id):
            # Since the user_id is just the primary key of our user table,
            # use it in the query for the user
            return models.User.query.get(int(user_id))

    # Import and register the blueprints for our routes
=======
    # Register blueprints
>>>>>>> f35751b (Initial commit)
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

    # Setup user loader and import models
    with app.app_context():
        from . import models

        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

        # Optional: create tables if needed (not usually used in production)
        # db.create_all()

    from .admin import admin
    admin.init_app(app)

    return app
