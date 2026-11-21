"""Forms used by the public and organizer event pages."""

from django import forms
from django.utils import timezone

from .models import Event


class EventForm(forms.ModelForm):
    """A small, readable ModelForm for organizers creating an event."""

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "category",
            "venue",
            "start_datetime",
            "capacity",
            "poster",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "start_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "capacity": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTML datetime-local controls expect a local, timezone-free string.
        value = self.initial.get("start_datetime")
        if value:
            self.initial["start_datetime"] = timezone.localtime(value).strftime(
                "%Y-%m-%dT%H:%M"
            )

    def clean_poster(self):
        """Keep uploaded posters reasonably small in addition to ImageField checks."""
        poster = self.cleaned_data.get("poster")
        if not poster:
            return poster

        if poster.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Poster images must be 5 MB or smaller.")

        content_type = getattr(poster, "content_type", "")
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if content_type and content_type not in allowed_types:
            raise forms.ValidationError("Use a JPEG, PNG, or WebP poster image.")
        return poster

    def clean_start_datetime(self):
        start_datetime = self.cleaned_data["start_datetime"]
        # Existing historical events may be edited; only new events need a future date.
        if not self.instance.pk and start_datetime < timezone.now():
            raise forms.ValidationError("New events must start in the future.")
        return start_datetime
