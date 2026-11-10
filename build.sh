#!/usr/bin/env bash
# Render build step: install, collect static files, migrate the database.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py loaddata ucl_data
