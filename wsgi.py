import os
from app import create_app

# Create an application instance for the Gunicorn server
app = create_app(os.getenv("FLASK_CONFIG") or "default")
