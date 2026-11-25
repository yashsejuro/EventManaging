"""WSGI configuration for ClubEvents."""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubevents.settings")
application = get_wsgi_application()
app = application

# Only auto-bootstrap the ephemeral /tmp SQLite fallback when DATABASE_URL is not configured.
if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
    call_command("migrate", interactive=False, verbosity=0)
    call_command("seed_demo", verbosity=0)
