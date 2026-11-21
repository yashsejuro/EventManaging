"""Create safe, repeatable local demo data for ClubEvents."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event


class Command(BaseCommand):
    help = "Create an Organizer group, two demo users, and eight upcoming events."

    def handle(self, *args, **options):
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

        organizer, created = user_model.objects.get_or_create(
            username="organizer",
            defaults={"email": "organizer@clubevents.local", "first_name": "Aarav"},
        )
        if created:
            organizer.set_password("demo12345")
            organizer.save()
        organizer.groups.add(organizer_group)

        student, created = user_model.objects.get_or_create(
            username="student",
            defaults={"email": "student@clubevents.local", "first_name": "Maya"},
        )
        if created:
            student.set_password("demo12345")
            student.save()

        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        demo_events = [
            ("Build Night: Django", "TECH", "Lab 204", 2, 40),
            ("Figma to Frontend", "WORKSHOP", "Design Studio", 4, 28),
            ("Founders' Fireside", "TALK", "Auditorium", 6, 180),
            ("Open Mic After Dark", "CULTURAL", "Amphitheatre", 8, 120),
            ("Campus 5K", "SPORTS", "Main Gate", 10, 250),
            ("Python Puzzle Sprint", "TECH", "Lab 101", 12, 48),
            ("Film & Frame", "CULTURAL", "Media Room", 15, 65),
            ("First-aid on Court", "WORKSHOP", "Sports Complex", 18, 36),
        ]
        created_count = 0
        for title, category, venue, days, capacity in demo_events:
            _, event_created = Event.objects.get_or_create(
                title=title,
                created_by=organizer,
                defaults={
                    "description": (
                        f"A practical ClubEvents demo for {title}. "
                        "Bring curiosity, meet fellow students, and leave with a new idea."
                    ),
                    "category": category,
                    "venue": venue,
                    "start_datetime": now + timedelta(days=days, hours=18),
                    "capacity": capacity,
                },
            )
            created_count += int(event_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo ready: organizer / demo12345, student / demo12345; "
                f"{created_count} events created."
            )
        )
