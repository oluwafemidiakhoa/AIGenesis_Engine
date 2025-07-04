#!/usr/bin/env bash
set -e

echo "===> Running DB migrations …"
flask db upgrade
echo "===> DB migrations done"

echo "===> Starting Gunicorn on $PORT"
exec gunicorn --log-level debug --bind 0.0.0.0:$PORT wsgi:app
