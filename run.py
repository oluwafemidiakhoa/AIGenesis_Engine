# run.py
import os
from app import create_app

# Load environment variables for configuration.
# In a production environment (like on a cloud provider), these will be set directly.
# For local development, they are loaded from a .env file by the logic in config.py.
config_name = os.getenv('FLASK_CONFIG', 'dev')
app = create_app(config_name)

if __name__ == '__main__':
    # This block is intended for local development only.
    # Do NOT run the app using this method in a production environment.
    # In production, a WSGI server like Gunicorn or uWSGI should be used.
    # Example for Gunicorn: gunicorn --bind 0.0.0.0:8000 "run:app"

    # Get host and port from environment variables with sensible defaults.
    host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))

    # The 'debug' flag is controlled by the app.config['DEBUG'] value,
    # which is set based on the FLASK_CONFIG environment variable in create_app.
    app.run(host=host, port=port)
