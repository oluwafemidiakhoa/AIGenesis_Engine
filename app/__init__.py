# app/__init__.py

from celery import Celery
from flask import Flask, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from config import config # Import the final, chosen config object
import sentry_sdk
import os # <--- THE MISSING IMPORT IS NOW HERE

db = SQLAlchemy()
celery = Celery(
    __name__,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)
mail = Mail()
login_manager = LoginManager()
migrate = Migrate()
# Set the login view so that @login_required redirects to the right page
login_manager.login_view = 'auth.login'

def create_app(config_name='dev'):
    # Select the configuration object
    app_config = config.get(config_name, config['dev'])
    
    # Create the app, telling it where the instance folder is
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    # Initialize Sentry if a DSN is provided
    if app.config['SENTRY_DSN']:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            # Enable performance monitoring
            enable_tracing=True,
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        )

    # Update celery config with the Flask app's config
    celery.conf.update(app.config)

    # This ensures that tasks run with the Flask application context.
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask

    # Use the instance path from the config object
    # This ensures it points to a writable directory like /data/instance
    instance_path = app.instance_path
    if not os.path.exists(instance_path):
        try:
            os.makedirs(instance_path)
        except OSError as e:
            # Handle potential race conditions in a multi-worker environment
            if not os.path.isdir(instance_path):
                raise e
    
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

    return app
