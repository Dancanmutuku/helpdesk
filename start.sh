#!/bin/bash

# Exit immediately if a command fails
set -e

echo "=== Running Django migrations ==="
python manage.py migrate --noinput

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Starting Gunicorn ==="
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT