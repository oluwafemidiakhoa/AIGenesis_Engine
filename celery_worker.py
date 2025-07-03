# celery_worker.py

import os
from app import create_app, celery

config_name = os.getenv('FLASK_CONFIG') or 'prod'
app = create_app(config_name)
app.app_context().push()
