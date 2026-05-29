#!/bin/sh
set -e

sh /scripts/wait-for-db.sh
python manage.py migrate --noinput

exec "$@"