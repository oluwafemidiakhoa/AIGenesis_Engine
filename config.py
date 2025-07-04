import os
from dotenv import load_dotenv

# Load variables from a .env file for local development.
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask secret key (REQUIRED for sessions, CSRF, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("FATAL ERROR: No SECRET_KEY set. Please set this in your .env file or Render environment.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # DATABASE_URI is optional here; each subclass will define fallback behavior.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # API Keys and integrations
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    HF_API_KEY = os.getenv('HF_API_KEY')
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 25))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    SENTRY_DSN = os.getenv('SENTRY_DSN')


class DevelopmentConfig(Config):
    """Local development config using SQLite if DATABASE_URL is missing."""
    DEBUG = True
    if not Config.SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    """Production configuration — requires DATABASE_URL."""
    DEBUG = False
    if not Config.SQLALCHEMY_DATABASE_URI:
        raise ValueError("FATAL ERROR: No DATABASE_URL set for production.")


class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'


# Used in create_app() to switch configs
config = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}
