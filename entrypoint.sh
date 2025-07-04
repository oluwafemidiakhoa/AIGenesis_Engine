#!/bin/sh
set -e

# The 'web' service is designated to run migrations.
if [ "$SERVICE_TYPE" = "web" ]; then
  echo "--- [Entrypoint] Running database migrations for web service ---"
  flask db upgrade
  echo "--- [Entrypoint] Migrations complete ---"
fi

# Now, execute the command passed into the script (from the Dockerfile's CMD)
exec "$@"