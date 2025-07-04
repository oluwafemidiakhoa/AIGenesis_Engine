# celery_worker.py

import os
from app import create_app, celery

config_name = os.getenv('FLASK_CONFIG') or 'prod'
app = create_app(config_name)
<<<<<<< HEAD
app.app_context().push()
=======
app.app_context().push()
>>>>>>> f35751b (Initial commit)
