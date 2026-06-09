#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Render build script for the Community Resource Map.
#
# Render runs this automatically on every deploy. It is written so that a
# first-time deploy sets everything up with no terminal access required:
#   1. install Python dependencies
#   2. collect static files (CSS/JS) so WhiteNoise can serve them
#   3. apply database migrations (creates the tables)
#   4. optionally load the sample resources (when SEED=true)
#   5. optionally create the admin login (from environment variables)
#
# Re-running this on later deploys is safe: migrations and seeding are
# idempotent, and the admin user is only created if it does not already exist.
# ---------------------------------------------------------------------------
set -o errexit  # stop immediately if any command fails

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load the fictional sample resources the first time, if SEED is turned on.
if [ "${SEED}" = "true" ] || [ "${SEED}" = "True" ] || [ "${SEED}" = "1" ]; then
  echo "SEED is on -> loading sample resources"
  python manage.py seed_resources
fi

# Create the Django admin account from environment variables, but only if it
# does not exist yet. This means you never have to open the Render Shell.
if [ -n "${DJANGO_SUPERUSER_USERNAME}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD}" ]; then
  echo "Ensuring admin user '${DJANGO_SUPERUSER_USERNAME}' exists"
  python manage.py shell <<PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created admin user {username}")
else:
    print(f"Admin user {username} already exists, leaving it unchanged")
PYTHON
fi
