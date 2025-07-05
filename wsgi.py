#!/usr/bin/env python
"""
WSGI entry point for Gunicorn.
Run with:
  gunicorn --bind 0.0.0.0:$PORT wsgi:app
"""

import os
from app import create_app

# Load the appropriate config: 'dev', 'prod', or 'test'
config_name = os.getenv('FLASK_CONFIG', 'prod')

# Instantiate the Flask application
app = create_app(config_name)

