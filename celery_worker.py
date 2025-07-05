import os
from app import create_app, celery

# Determine the configuration (development, production, testing)
config_name = os.getenv('FLASK_CONFIG', 'prod')

# Create Flask application and push its context for Celery tasks
app = create_app(config_name)
app.app_context().push()

# Configure Celery with Redis broker and result backend from environment
celery.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND')
)

# Optional: Import tasks so they are registered with Celery
# from app.tasks import *  # noqa

if __name__ == '__main__':
    # Start the worker for local debugging: celery -A celery_worker worker --loglevel=info
    celery.start()
