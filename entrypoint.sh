#!/usr/bin/env bash
set -e

# Wait for PostgreSQL if a Postgres DATABASE_URL is configured.
if [[ "${DATABASE_URL}" == postgres* ]]; then
  echo "Waiting for the database..."
  python - <<'PY'
import os, time, sys
import environ
env = environ.Env()
cfg = env.db_url_config(os.environ["DATABASE_URL"])
import socket
host, port = cfg.get("HOST", "db"), int(cfg.get("PORT") or 5432)
for _ in range(30):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Database is up.")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print("Database did not become available in time.", file=sys.stderr)
sys.exit(1)
PY
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optionally load sample data on first boot (set SEED=1 in .env).
if [[ "${SEED}" == "1" || "${SEED}" == "True" || "${SEED}" == "true" ]]; then
  echo "Seeding sample data..."
  python manage.py seed_resources || true
fi

echo "Starting: $*"
exec "$@"
