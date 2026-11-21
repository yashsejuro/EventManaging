"""Useful staff administration for events and their registrations."""

import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Event, Registration


class RegistrationInline(admin.TabularInline):
    """Lets staff inspect and update registrations from the event page."""

    model = Registration
    extra = 0
    readonly_fields = ("registered_at",)
    autocomplete_fields = ("user",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "venue",
        "start_datetime",
        "capacity",
        "created_by",
    )
    list_filter = ("category", "start_datetime")
    search_fields = ("title", "description", "venue", "created_by__username")
    date_hierarchy = "start_datetime"
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ("created_by",)
    inlines = (RegistrationInline,)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "registered_at", "attended")
    list_filter = ("attended", "event__category")
    search_fields = ("user__username", "user__email", "event__title")
    date_hierarchy = "registered_at"
    list_select_related = ("user", "event")
    actions = ("export_selected_registrations_csv", "mark_attended")

    @admin.action(description="Export selected registrations as CSV")
    def export_selected_registrations_csv(self, request, queryset):
        """Return a simple spreadsheet-friendly export for staff."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="registrations.csv"'
        writer = csv.writer(response)
        writer.writerow(["Event", "Student", "Email", "Registered at", "Attended"])
        for registration in queryset.select_related("user", "event"):
            writer.writerow(
                [
                    registration.event.title,
                    registration.user.username,
                    registration.user.email,
                    registration.registered_at.isoformat(),
                    registration.attended,
                ]
            )
        return response

    @admin.action(description="Mark selected registrations attended")
    def mark_attended(self, request, queryset):
        queryset.update(attended=True)
