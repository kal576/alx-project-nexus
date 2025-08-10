#!/bin/bash
set -e

echo "=== Starting Deployment ==="
echo "PORT: $PORT"

echo "Running database migrations..."
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py create_superuser_if_not_exists

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn ecommerce_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-level info