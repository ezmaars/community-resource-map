# 🧭 Community Resource Map

A free, open-source web app that helps people find local help — **food banks,
shelters, clinics, legal aid, community centers, free classes, job support, and
emergency assistance** — on a searchable map.

Built to be **simple to run, easy to maintain, and friendly to low-tech users.**

- **Stack:** Django 5 · PostgreSQL (SQLite for dev) · Leaflet + OpenStreetMap · Bootstrap 5
- **Everything is free and open source.** No paid APIs. No proprietary services.
- **Runs anywhere:** locally on Linux with SQLite, or via Docker with PostgreSQL.

---

## Why this stack

| Need | How Django delivers it |
|------|------------------------|
| Solo-maintainable | One language, one codebase, one process — no separate frontend build |
| Admin & moderation out of the box | Django admin gives full CRUD + the custom `/manage/queue/` adds one-click approve/reject |
| Security basics included | CSRF, auth, password hashing, security middleware, env-based secrets |
| Multilingual readiness | Built-in `gettext`/`LocaleMiddleware` i18n framework |
| Low system requirements | Plain lat/lng (no PostGIS/GDAL); WhiteNoise serves static files (no separate Nginx) |
| Fast for users | Server-rendered HTML, minimal JS, OSM tiles |

FastAPI + React would mean two codebases and a build step; Express would mean
hand-rolling the admin, ORM, auth, and migrations. Django is the best fit for a
solo developer who wants a real moderation workflow without extra moving parts.

---

## Quick start (local, SQLite — no Docker)

Requires Python 3.10+.

```bash
git clone <your-repo-url> community-resource-map
cd community-resource-map

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then edit SECRET_KEY etc.
python manage.py migrate
python manage.py seed_resources   # loads sample data
python manage.py createsuperuser  # for the admin & moderation queue
python manage.py runserver
```

Open <http://127.0.0.1:8000>. The admin is at `/admin/`, the moderation queue at
`/manage/queue/`.

> SQLite is created automatically as `db.sqlite3` when `DATABASE_URL` is unset.

---

## Quick start (Docker + PostgreSQL)

Requires Docker and the Docker Compose plugin.

```bash
cp .env.example .env          # set SECRET_KEY; set SEED=1 to auto-load sample data
docker compose up --build
```

The app comes up on <http://localhost:8000>. Migrations and `collectstatic` run
automatically. Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

To load sample data manually (if `SEED` was 0):

```bash
docker compose exec web python manage.py seed_resources
```

---

## How the moderation workflow works

1. Anyone submits a resource at **`/submit/`** (no login required).
2. It is saved with `status = pending` and **does not appear on the map**.
3. A staff member signs in and opens **`/manage/queue/`**:
   - **Approve** → status becomes `approved`, verification `verified`, and it goes live.
   - **Reject** → status becomes `rejected` (kept for the record, stays hidden).
   - **Edit before approving** links straight into the Django admin.
4. The Django admin (`/admin/`) offers full editing plus bulk
   *Approve / Reject / Mark verified* actions and structured opening-hours editing.

A "staff member" is any user with **`is_staff = True`** (set it on the user in
the admin, or use a superuser).

---

## Features (v1)

- Home page with search bar + category grid
- Interactive Leaflet map with colored, category-based pins
- List view that mirrors the map (and works without JavaScript / for screen readers)
- Resource detail pages with contact, hours, tags, and a location map
- Submit-a-resource form with validation + honeypot spam protection
- Staff moderation queue + full Django admin
- Filters: **search**, **category**, **free only**, **open now**, and feature **tags**
  (wheelchair accessible, family friendly, multilingual, walk-in, appointment required, no ID required)
- Categories: Food, Housing, Health, Legal, Education, Jobs, Emergency
- JSON API at `/api/resources/` (GeoJSON `FeatureCollection`, honors the same filters)

### Sample API

```
GET /api/resources/?category=food&free=1
```

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [-104.987, 39.746] },
      "properties": {
        "name": "Eastside Community Food Bank",
        "category": "Food", "is_free": true,
        "address": "1420 Welton St, Denver, CO",
        "url": "/resources/eastside-community-food-bank/"
      }
    }
  ]
}
```

---

## Configuration

All settings come from environment variables — see **`.env.example`** for the
full annotated list. Key ones:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret — set a long random value in production |
| `DEBUG` | `True` for dev, **`False`** in production (turns on HTTPS/HSTS/secure cookies) |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `DATABASE_URL` | Unset = SQLite; `postgres://…` = PostgreSQL |
| `MAP_DEFAULT_LAT/LNG/ZOOM` | Where the map centers before data loads |
| `TIME_ZONE` | Used by the "Open now" filter |

---

## Accessibility notes

- Skip-to-content link, semantic landmarks (`header`/`main`/`footer`), and labelled form fields
- The map always has a synchronized **list view** as a non-visual equivalent
- Visible keyboard focus styles; map scroll-zoom only activates on focus (no scroll hijacking)
- Color is never the only signal (icons + text labels accompany pins and badges)
- High-contrast, large, readable type; mobile-first responsive layout

## Security notes

- Secrets via environment variables only (`.env` is git-ignored)
- CSRF protection on every form; Django's auth + password validators
- In production (`DEBUG=False`): SSL redirect, HSTS, secure + httpOnly cookies,
  `X-Frame-Options: DENY`, no-sniff, referrer policy
- Pending/rejected resources are never exposed publicly or via the API
- Honeypot field on the public form blocks basic spam bots
- Runs as a non-root user in Docker
- **For production also:** put it behind HTTPS (e.g. Caddy/Nginx + Let's Encrypt),
  set strong DB credentials, and consider adding rate limiting (see roadmap).

> The Bootstrap and Leaflet assets load from a CDN for convenience. For maximum
> reliability/privacy, download and serve them from `static/` instead.

---

## Running the tests

```bash
python manage.py test
```

Covers: pending resources stay hidden, the API exposes only approved data,
submissions land in the queue, the honeypot blocks spam, and the open-now logic.

---

## Project layout

```
config/      Django project (settings, urls, wsgi/asgi)
resources/   The app: models, views, api, admin, forms, seed command, tests
templates/   Server-rendered HTML (Bootstrap)
static/      app.css + map.js
locale/      Translation catalogs (i18n-ready; English only in v1)
```

---

## Roadmap

See the project prompt / `ROADMAP` section below in the chat answer, or open an
issue. Highlights: full Spanish translation, user accounts & "claim this listing",
PostGIS distance search, "near me" geolocation, photos, saved/favourite lists,
data export/import (CSV), email notifications to moderators, and rate limiting.

## License

MIT — see `LICENSE`. Map data © OpenStreetMap contributors.
