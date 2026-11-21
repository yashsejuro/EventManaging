"""WSGI configuration for ClubEvents."""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubevents.settings")
application = get_wsgi_application()
app = application

if os.environ.get("VERCEL"):
    call_command("migrate", interactive=False, verbosity=0)
    call_command("seed_demo", verbosity=0)
