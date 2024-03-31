#!/bin/sh

# echo "Flushing database..."
# python manage.py flush --no-input

echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Updating embeddings..."
python manage.py generate_vectors

# Start the Django server
echo "Starting Django server..."
exec "$@"