# ClubEvents

<div align="center">

<img src="static/images/favicon.svg" alt="ClubEvents logo" width="96" height="96">

**Discover, join, and organize campus events.**

[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Deployed with Vercel](https://img.shields.io/badge/Deployed%20with-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/)

</div>

## Features

- Browse and filter public campus events
- View event details and register for events
- Manage personal registrations and tickets
- Organizer dashboard for creating, editing, and deleting events
- Attendance controls and CSV export for organizers
- Responsive design with browser-ready favicon and social share card

## Run locally

Requires Python 3.12.

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

Demo accounts can be recreated from the seed command. The seed command is also safe to rerun, but check `python manage.py seed_demo --help` for its options.

## Deploy to Vercel

Vercel will run Django through `clubevents/wsgi.py`. Static files are compressed and served by WhiteNoise.

### 1. Push the project to GitHub

```powershell
git add .
git commit -m "Prepare ClubEvents for Vercel"
git push origin main
```

### 2. Import the repository

1. Sign in at [vercel.com](https://vercel.com/) with GitHub.
2. Select **Add New... > Project**.
3. Import `yashsejuro/EventManaging`.
4. Keep the project as a **Python**/other framework project; do not select a frontend framework preset.
5. Add the environment variables below.
6. Select **Deploy**.

### 3. Environment variables

Set these in **Project Settings > Environment Variables**:

| Variable | Example/value |
| --- | --- |
| `DJANGO_SECRET_KEY` | A long, random secret. Generate it with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,.vercel.app,your-project.vercel.app,your-custom-domain.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app,https://your-custom-domain.com` |
| `DATABASE_URL` | PostgreSQL connection URL |

The `DATABASE_URL` value is strongly recommended. Vercel serverless functions have a read-only/ephemeral filesystem, so SQLite changes may disappear and concurrent instances may not share them. Use a managed PostgreSQL database (such as Neon or Vercel Postgres), then run migrations from a local machine or deployment command:

```powershell
$env:DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DATABASE"
$env:DJANGO_SECRET_KEY="a-long-random-secret"
python manage.py migrate
python manage.py seed_demo
```

### 4. Custom domain

In Vercel, open **Domains**, add the domain, and follow the DNS instructions. Add the final HTTPS domain to both `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS`.

For example:

```text
DJANGO_ALLOWED_HOSTS=your-project.vercel.app,events.example.com,.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app,https://events.example.com
```

Redeploy after changing environment variables.

The Vercel build runs migrations and seeds repeatable demo data automatically.
It is safe to redeploy because `seed_demo` uses `get_or_create` for demo users
and events.

## Production checks

Run these before sharing the deployment:

```powershell
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py test
```