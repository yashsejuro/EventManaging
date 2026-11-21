"""ASGI configuration for ClubEvents."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubevents.settings")
application = get_asgi_application()
app = application
