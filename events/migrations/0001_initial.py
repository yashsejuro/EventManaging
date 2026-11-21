# Generated manually for the small, stable initial ClubEvents schema.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=190, unique=True)),
                ("description", models.TextField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("TECH", "Tech"),
                            ("WORKSHOP", "Workshop"),
                            ("TALK", "Talk"),
                            ("CULTURAL", "Cultural"),
                            ("SPORTS", "Sports"),
                        ],
                        max_length=16,
                    ),
                ),
                ("venue", models.CharField(max_length=160)),
                ("start_datetime", models.DateTimeField()),
                ("capacity", models.PositiveIntegerField()),
                (
                    "poster",
                    models.ImageField(
                        blank=True, null=True, upload_to="posters/%Y/%m/"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ("start_datetime",)},
        ),
        migrations.CreateModel(
            name="Registration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("registered_at", models.DateTimeField(auto_now_add=True)),
                ("attended", models.BooleanField(default=False)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registrations",
                        to="events.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registrations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ("-registered_at",)},
        ),
        migrations.AddConstraint(
            model_name="registration",
            constraint=models.UniqueConstraint(
                fields=("user", "event"), name="unique_user_event_registration"
            ),
        ),
    ]
