#!/bin/sh
set -e
python manage.py collectstatic --noinput
exec gunicorn "$WSGI_APP" \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile -
