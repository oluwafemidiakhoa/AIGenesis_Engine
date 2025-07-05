import os

class Config:
    """Base configuration class."""

    # SECRET_KEY is required for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("FATAL ERROR: No SECRET_KEY set. Please set SECRET_KEY in environment variables.")

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Third-party API keys
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID')

    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    HF_API_KEY = os.environ.get('HF_API_KEY')
    SERPER_API_KEY = os.environ.get('SERPER_API_KEY')

    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    SENTRY_DSN = os.environ.get('SENTRY_DSN')


class DevelopmentConfig(Config):
    """Local development config; fallback to SQLite if DATABASE_URL is not set."""
    DEBUG = True
    if not Config.SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    """Production config; enforce DATABASE_URL presence."""
    DEBUG = False
    if not Config.SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("FATAL ERROR: No DATABASE_URL set for production. Please set DATABASE_URL environment variable.")


class TestingConfig(Config):
    """Testing config; use in-memory SQLite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'


# Mapping for create_app
config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}
