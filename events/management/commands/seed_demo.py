"""Create safe, repeatable local demo data for ClubEvents."""

import os
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from events.models import Event, Registration


DEMO_PASSWORD = "Demo@12345"
LOCAL_HOSTS = {"", "localhost", "127.0.0.1", "::1"}


def _is_non_local_db():
    """Return (is_remote, host) if DATABASE_URL or default DB targets a remote host."""
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        parsed = urlparse(database_url)
        if not parsed.scheme.startswith("sqlite"):
            host = (parsed.hostname or "").lower()
            if host not in LOCAL_HOSTS:
                return True, host

    default_db = settings.DATABASES.get("default", {})
    engine = default_db.get("ENGINE", "")
    host = (default_db.get("HOST") or "").lower()
    if "sqlite" not in engine and host not in LOCAL_HOSTS:
        return True, host
    return False, host


class Command(BaseCommand):
    help = "Create local demo accounts (student, organizer, admin) and eight realistic events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Allow seeding even when DATABASE_URL points to a non-local database.",
        )

    def handle(self, *args, **options):
        is_remote, remote_host = _is_non_local_db()
        if is_remote and not options["force"]:
            raise CommandError(
                f"Refusing to run seed_demo against non-local database host '{remote_host}'. "
                "Pass --force to override."
            )

        user_model = get_user_model()
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        organizer_permissions = Permission.objects.filter(
            content_type__app_label="events",
            codename__in=[
                "add_event",
                "change_event",
                "delete_event",
                "view_event",
                "add_registration",
                "view_registration",
                "change_registration",
                "delete_registration",
            ],
        )
        organizer_group.permissions.set(organizer_permissions)

        demo_admin, _ = user_model.objects.get_or_create(
            username="demo_admin",
            defaults={
                "email": "riya.admin@clubevents.edu",
                "first_name": "Riya",
                "last_name": "Verma",
            },
        )
        demo_admin.is_staff = True
        demo_admin.is_superuser = True
        demo_admin.set_password(DEMO_PASSWORD)
        demo_admin.save()

        demo_organizer, _ = user_model.objects.get_or_create(
            username="demo_organizer",
            defaults={
                "email": "aarav.organizer@clubevents.edu",
                "first_name": "Aarav",
                "last_name": "Sharma",
            },
        )
        demo_organizer.is_staff = True
        demo_organizer.set_password(DEMO_PASSWORD)
        demo_organizer.save()
        demo_organizer.groups.add(organizer_group)

        demo_student, _ = user_model.objects.get_or_create(
            username="demo_student",
            defaults={
                "email": "maya.student@clubevents.edu",
                "first_name": "Maya",
                "last_name": "Patel",
            },
        )
        demo_student.set_password(DEMO_PASSWORD)
        demo_student.save()

        filler_profiles = [
            ("aisha", "Aisha", "Kapoor", "aisha@clubevents.edu"),
            ("rohan", "Rohan", "Mehta", "rohan@clubevents.edu"),
            ("sneha", "Sneha", "Iyer", "sneha@clubevents.edu"),
            ("kabir", "Kabir", "Shah", "kabir@clubevents.edu"),
            ("meera", "Meera", "Rao", "meera@clubevents.edu"),
            ("arjun", "Arjun", "Nair", "arjun@clubevents.edu"),
            ("diya", "Diya", "Kulkarni", "diya@clubevents.edu"),
            ("vihaan", "Vihaan", "Singh", "vihaan@clubevents.edu"),
            ("nisha", "Nisha", "Menon", "nisha@clubevents.edu"),
        ]
        fillers = []
        for username, first_name, last_name, email in filler_profiles:
            filler, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                filler.set_password(DEMO_PASSWORD)
                filler.save()
            fillers.append(filler)

        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        # 8 realistic events covering: open upcoming, nearly full (9/10), sold-out (5/5),
        # starting very soon, and past with attended check-ins.
        demo_events = [
            {
                "title": "Build Night: Django",
                "category": Event.Category.TECH,
                "venue": "Innovation Lab 204",
                "description": (
                    "Hands-on evening building and shipping a real campus web app with Django, "
                    "ORM queries, and clean forms. Laptops welcome; mentors on hand."
                ),
                "start_datetime": now + timedelta(days=3, hours=18),
                "capacity": 40,
                "poster": "posters/demo/build-night.svg",
                "include_demo_student": True,
                "filler_count": 4,
                "attended": False,
            },
            {
                "title": "Figma to Frontend",
                "category": Event.Category.WORKSHOP,
                "venue": "Design Studio B",
                "description": (
                    "Translate design tokens, responsive grids, and accessible UI components "
                    "straight from Figma into production HTML and CSS. Nearly full."
                ),
                "start_datetime": now + timedelta(days=2, hours=17),
                "capacity": 10,
                "poster": "posters/demo/figma-front.svg",
                "include_demo_student": False,
                "filler_count": 9,  # 9/10 filled (nearly full: 1 seat left)
                "attended": False,
            },
            {
                "title": "Founders' Fireside",
                "category": Event.Category.TALK,
                "venue": "Main Auditorium",
                "description": (
                    "Candid conversation with alumni founders on building first products out of "
                    "a dorm room, finding early users, and surviving launches."
                ),
                "start_datetime": now + timedelta(days=5, hours=18),
                "capacity": 5,
                "poster": "posters/demo/founders.svg",
                "include_demo_student": False,
                "filler_count": 5,  # 5/5 filled (sold out)
                "attended": False,
            },
            {
                "title": "Open Mic After Dark",
                "category": Event.Category.CULTURAL,
                "venue": "Student Amphitheatre",
                "description": (
                    "Acoustic sets, spoken word, and stand-up under string lights. Door list closes "
                    "shortly before showtime."
                ),
                "start_datetime": now + timedelta(hours=18),
                "capacity": 60,
                "poster": "posters/demo/open-mic.svg",
                "include_demo_student": False,
                "filler_count": 4,
                "attended": False,
            },
            {
                "title": "Campus 5K",
                "category": Event.Category.SPORTS,
                "venue": "North Pavilion Gate",
                "description": (
                    "Community sunrise 5K loop around the botanical quad and track. Hydration "
                    "stations and timed bibs included at check-in."
                ),
                "start_datetime": now + timedelta(days=9, hours=7),
                "capacity": 150,
                "poster": "posters/demo/campus-5k.svg",
                "include_demo_student": True,
                "filler_count": 6,
                "attended": False,
            },
            {
                "title": "Python Puzzle Sprint",
                "category": Event.Category.TECH,
                "venue": "Computing Hall 101",
                "description": (
                    "Team-based algorithmic sprint focused on clean Python, graphs, and fast "
                    "debugging rounds."
                ),
                "start_datetime": now + timedelta(days=12, hours=16),
                "capacity": 48,
                "poster": "posters/demo/python-sprint.svg",
                "include_demo_student": False,
                "filler_count": 5,
                "attended": False,
            },
            {
                "title": "Film & Frame",
                "category": Event.Category.CULTURAL,
                "venue": "Media Screening Room",
                "description": (
                    "Student short-film screening followed by cinematography breakdown and Q&A "
                    "with the student directors."
                ),
                "start_datetime": now - timedelta(days=4, hours=18),
                "capacity": 60,
                "poster": "posters/demo/film-frame.svg",
                "include_demo_student": True,
                "filler_count": 5,
                "attended": True,  # Past event with attended check-ins
            },
            {
                "title": "First-aid on Court",
                "category": Event.Category.WORKSHOP,
                "venue": "Sports Complex",
                "description": (
                    "Practical sideline injury response and CPR fundamentals led by campus "
                    "athletic trainers for club captains."
                ),
                "start_datetime": now + timedelta(days=16, hours=15),
                "capacity": 36,
                "poster": "posters/demo/first-aid.svg",
                "include_demo_student": False,
                "filler_count": 3,
                "attended": False,
            },
        ]

        created_count = 0
        for spec in demo_events:
            event, created = Event.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "description": spec["description"],
                    "category": spec["category"],
                    "venue": spec["venue"],
                    "start_datetime": spec["start_datetime"],
                    "capacity": spec["capacity"],
                    "poster": spec["poster"],
                    "created_by": demo_organizer,
                },
            )
            created_count += int(created)

            desired_users = []
            if spec["include_demo_student"]:
                desired_users.append(demo_student)
            desired_users.extend(fillers[: spec["filler_count"]])

            for attendee in desired_users[: spec["capacity"]]:
                reg, reg_created = Registration.objects.get_or_create(
                    event=event,
                    user=attendee,
                    defaults={"attended": spec["attended"]},
                )
                if not reg_created and reg.attended != spec["attended"]:
                    reg.attended = spec["attended"]
                    reg.save(update_fields=["attended"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo seed complete ({created_count} new events, {Event.objects.count()} total events).\n"
                f"Accounts (password: {DEMO_PASSWORD}):\n"
                f"  - Student:   demo_student\n"
                f"  - Organizer: demo_organizer\n"
                f"  - Admin:     demo_admin"
            )
        )
