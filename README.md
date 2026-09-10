# KAndyn Restaurant — Reservation System

A Flask web app for booking restaurant tables online. Guests search for a table
by date, time, and party size, see which ones are actually free — with a
photo of each — and reserve one directly. Every booking starts as
**Pending** until a staff member approves or rejects it; approval sends the
guest an email confirmation automatically.

## Features

**Guests**
- Register / log in (single split-screen page with a sliding Login ↔ Register toggle)
- Search tables by date, time, and party size, and see live availability
- Reserve a specific table from the search results
- Track booking status (Pending / Approved / Rejected) on a dashboard and history page
- Browse a public photo gallery and an About page — no login required

**Admins**
- Add, photograph, and remove tables
- Approve or reject every incoming reservation
- Upload photos to the public gallery
- Everything a guest can do, plus the above

**Automated emails** (via Brevo)
- Welcome email on registration
- Booking-confirmed email when an admin approves a reservation, showing date/time/guests/table

**Images** (via Cloudinary)
- Table photos and gallery photos are uploaded straight to Cloudinary; only the resulting URL is stored in the database

## Tech stack

| Layer      | Choice                                   |
|------------|-------------------------------------------|
| Backend    | Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| Database   | SQLite by default; PostgreSQL supported via `DATABASE_URL` |
| Images     | Cloudinary |
| Email      | Brevo (transactional email API) |
| Frontend   | Server-rendered Jinja templates, hand-written CSS (glassmorphism / gradient design) |
| Deployment | Gunicorn-ready (`gunicorn` + `psycopg2-binary` included) |

## Project structure

```
app/
  __init__.py          # App factory: config, extensions, one-time DB column migration
  config.py             # Reads all settings from environment variables
  models.py              # User, RestaurantTable, Reservation, RestaurantImage
  forms.py                # WTForms form classes
  routes.py                # All view functions (single blueprint: "main")
  decorators.py             # @admin_required
  cloudinary_service.py      # Cloudinary upload helper
  services/
    email_service.py          # Brevo email helper + welcome/booking-confirmation senders
  templates/                   # Jinja templates (+ templates/emails/ for HTML emails)
  static/css/                   # app.css (site-wide), home.css (login/register page)
create_admin.py                  # One-off script to create the first admin user
run.py                            # Local dev entrypoint
requirements.txt
.env.example                       # Copy to .env and fill in your own values
```

## Getting started (Windows)

**1. Clone and enter the project**

```powershell
git clone <repo-url> "Restaurant Reservation System"
cd "Restaurant Reservation System"
```

**2. Create and activate a virtual environment**

```powershell
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```powershell
pip install -r requirements.txt
```

**4. Configure environment variables**

Copy `.env.example` to `.env` and fill in your own values:

```powershell
copy .env.example .env
```

| Variable | Required | Purpose |
|---|---|---|
| `SECRET_KEY` | Yes | Flask session/CSRF signing key |
| `DATABASE_URL` | No | PostgreSQL URL; omit to use a local SQLite file |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | Yes | Table & gallery photo uploads |
| `BREVO_API_KEY` | Yes | Sending transactional emails |
| `BREVO_SENDER_EMAIL` | Yes | Must be a sender address verified in your Brevo account |
| `BREVO_SENDER_NAME` | No | Defaults to `"Restaurant"` |

**5. Create an admin account**

```powershell
python create_admin.py
```

This creates `admin@gmail.com` / `Admin123` — change the password (or edit
`create_admin.py` before running it) before using this anywhere but your own
machine.

**6. Run the app**

```powershell
python run.py
```

Visit **http://127.0.0.1:5000**. The database and its tables are created
automatically on first run — no manual migration step needed for a fresh
install (an existing database is upgraded in place for the one schema change
this app currently needs).

## Notes on external services

- **Cloudinary** and **Brevo** both require their own free-tier accounts.
  Without valid credentials, image uploads and emails will fail — the app
  logs the error and keeps working rather than crashing the request.
- Brevo blocks API calls from IP addresses it doesn't recognize by default.
  If emails aren't sending, check **Brevo → Security → Authorised IPs**.

## Deployment

The app is ready for a platform like Render or Railway: it reads
`DATABASE_URL` for PostgreSQL and ships with `gunicorn`. Typical start
command:

```
gunicorn run:app
```

Set the same environment variables listed above in your hosting platform's
dashboard — never commit `.env` (it's already git-ignored).
