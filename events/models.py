"""Core data models for published events and student registrations."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Event(models.Model):
    """An event an organizer can publish for students to discover."""

    class Category(models.TextChoices):
        TECH = "TECH", "Tech"
        WORKSHOP = "WORKSHOP", "Workshop"
        TALK = "TALK", "Talk"
        CULTURAL = "CULTURAL", "Cultural"
        SPORTS = "SPORTS", "Sports"

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, max_length=190, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=16, choices=Category.choices)
    venue = models.CharField(max_length=160)
    start_datetime = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    poster = models.ImageField(upload_to="posters/%Y/%m/", blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("start_datetime",)

    def __str__(self):
        return self.title

    def _make_unique_slug(self):
        """Make a readable, collision-safe slug without requiring an extra form field."""
        root = slugify(self.title)[:180] or "event"
        candidate = root
        counter = 2
        queryset = type(self).objects.exclude(pk=self.pk)
        while queryset.filter(slug=candidate).exists():
            suffix = f"-{counter}"
            candidate = f"{root[:190 - len(suffix)]}{suffix}"
            counter += 1
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._make_unique_slug()
        super().save(*args, **kwargs)

    def clean(self):
        """New events must be in the future; existing records remain editable."""
        super().clean()
        if self._state.adding and self.start_datetime and self.start_datetime < timezone.now():
            raise ValidationError({"start_datetime": "A new event must start in the future."})
        if self.capacity < 1:
            raise ValidationError({"capacity": "Capacity must be at least 1."})

    @property
    def seats_left(self):
        """Use an annotated count when a list view has supplied one, else query safely."""
        count = getattr(self, "registration_total", None)
        if count is None:
            # Support the conventional name used by querysets in views.
            count = getattr(self, "registration_count", None)
        if count is None:
            count = self.registrations.count()
        return max(self.capacity - count, 0)

    @property
    def is_full(self):
        return self.seats_left <= 0

    @property
    def is_past(self):
        return self.start_datetime <= timezone.now()


class Registration(models.Model):
    """One student's booking; the database constraint prevents duplicates."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)

    class Meta:
        ordering = ("-registered_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "event"), name="unique_user_event_registration"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.event}"
