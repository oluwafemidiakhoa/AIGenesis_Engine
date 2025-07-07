import os
from app import create_app, celery

# Set the Flask configuration (e.g., 'dev', 'prod', 'test')
config_name = os.getenv('FLASK_CONFIG', 'prod')

# Create the Flask app and push the app context for Celery to use
app = create_app(config_name)
app.app_context().push()

# Retrieve Redis connection URL from environment (Render internal Key Value URL)
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Update Celery configuration
celery.conf.update(
    broker_url=redis_url,
    result_backend=redis_url
)

# Optionally import tasks here to ensure they are registered
# from app.tasks import *  # noqa

if __name__ == '__main__':
    # Run Celery worker: Used mainly for local testing
    celery.start()
