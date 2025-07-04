#!/bin/sh
set -e

echo "--- [Entrypoint] Running database migrations ---"
flask db upgrade
echo "--- [Entrypoint] Migrations complete ---"

# Now, execute the command passed into the script (from the Dockerfile's CMD)
exec "$@"
