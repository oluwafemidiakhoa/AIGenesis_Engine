# run.py
#!/usr/bin/env python
"""
Application entry point for local development.

Use a WSGI server (e.g., Gunicorn) for production:
  gunicorn --bind 0.0.0.0:8000 run:app
"""
import os
from app import create_app

# Determine configuration: 'dev', 'prod', or 'test'
config_name = os.getenv('FLASK_CONFIG', 'dev')
# Create Flask app with the selected config
app = create_app(config_name)

if __name__ == '__main__':
    # Local development server
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = app.config.get('DEBUG', False)

    app.run(host=host, port=port, debug=debug)  # pragma: no cover

