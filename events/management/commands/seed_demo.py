"""Create safe, repeatable local demo data for ClubEvents."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, Registration


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

        admin_user, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@clubevents.local", "first_name": "Admin"},
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("admin12345")
        admin_user.save()

        organizer, created = user_model.objects.get_or_create(
            username="organizer",
            defaults={"email": "organizer@clubevents.local", "first_name": "Aarav"},
        )
        organizer.is_staff = True
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

        demo_students = [
            ("aisha", "Aisha", "Kapoor", "aisha@clubevents.local"),
            ("rohan", "Rohan", "Mehta", "rohan@clubevents.local"),
            ("sneha", "Sneha", "Iyer", "sneha@clubevents.local"),
            ("kabir", "Kabir", "Shah", "kabir@clubevents.local"),
            ("meera", "Meera", "Rao", "meera@clubevents.local"),
            ("arjun", "Arjun", "Nair", "arjun@clubevents.local"),
            ("diya", "Diya", "Patel", "diya@clubevents.local"),
            ("vihaan", "Vihaan", "Singh", "vihaan@clubevents.local"),
        ]
        for username, first_name, last_name, email in demo_students:
            demo_user, created = user_model.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            if created:
                demo_user.set_password("demo12345")
                demo_user.save()

        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        demo_events = [
            ("Build Night: Django", "TECH", "Lab 204", 2, 40, "build-night.svg"),
            ("Figma to Frontend", "WORKSHOP", "Design Studio", 4, 28, "figma-front.svg"),
            ("Founders' Fireside", "TALK", "Auditorium", 6, 180, "founders.svg"),
            ("Open Mic After Dark", "CULTURAL", "Amphitheatre", 8, 120, "open-mic.svg"),
            ("Campus 5K", "SPORTS", "Main Gate", 10, 250, "campus-5k.svg"),
            ("Python Puzzle Sprint", "TECH", "Lab 101", 12, 48, "python-sprint.svg"),
            ("Film & Frame", "CULTURAL", "Media Room", 15, 65, "film-frame.svg"),
            ("First-aid on Court", "WORKSHOP", "Sports Complex", 18, 36, "first-aid.svg"),
        ]
        created_count = 0
        for title, category, venue, days, capacity, poster_name in demo_events:
            event, event_created = Event.objects.get_or_create(
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
                    "poster": f"posters/demo/{poster_name}",
                },
            )
            poster_path = f"posters/demo/{poster_name}"
            if event.poster.name != poster_path:
                event.poster = poster_path
                event.save(update_fields=["poster"])
            created_count += int(event_created)

            participants = list(
                user_model.objects.filter(username__in=[
                    "student", "aisha", "rohan", "sneha", "kabir",
                    "meera", "arjun", "diya", "vihaan",
                ])
            )
            participant_limit = min(max(3, event.capacity // 5), len(participants))
            for participant in participants[:participant_limit]:
                Registration.objects.get_or_create(
                    event=event,
                    user=participant,
                    defaults={"attended": days < 0},
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo ready: organizer / demo12345, student / demo12345; "
                f"{created_count} events created."
            )
        )
