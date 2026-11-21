#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative commands with the ClubEvents settings module."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubevents.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install the requirements in an active virtual environment."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
