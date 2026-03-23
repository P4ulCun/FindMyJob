#!/bin/sh
# wait-for-db.sh — Wait until PostgreSQL is ready to accept connections

set -e

echo "Waiting for PostgreSQL at ${DATABASE_HOST}:${DATABASE_PORT}..."

until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$POSTGRES_USER" -q; do
  echo "PostgreSQL is unavailable — sleeping 1s"
  sleep 1
done

echo "PostgreSQL is up — continuing"
