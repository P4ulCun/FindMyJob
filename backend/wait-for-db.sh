#!/bin/sh
# wait-for-db.sh — Wait until PostgreSQL is ready to accept connections

set -e

echo "Waiting for PostgreSQL at ${DATABASE_HOST}:${DATABASE_PORT}..."

until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        host=os.environ['DATABASE_HOST'],
        port=os.environ['DATABASE_PORT'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        dbname=os.environ['POSTGRES_DB'],
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "PostgreSQL is unavailable — sleeping 1s"
  sleep 1
done

echo "PostgreSQL is up — continuing"
