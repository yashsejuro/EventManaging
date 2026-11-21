"""URL patterns for both the public and custom organizer areas."""

from django.urls import path

from . import views


app_name = "events"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/<slug:slug>/", views.EventDetailView.as_view(), name="event_detail"),
    path("events/<slug:slug>/register/", views.register_event, name="register_event"),
    path("events/<slug:slug>/cancel/", views.cancel_registration, name="cancel_registration"),
    path("my-registrations/", views.MyRegistrationsView.as_view(), name="my_registrations"),
    path("organizer/", views.OrganizerDashboardView.as_view(), name="organizer_dashboard"),
    path("organizer/events/new/", views.OrganizerEventCreateView.as_view(), name="event_create"),
    path(
        "organizer/events/<slug:slug>/edit/",
        views.OrganizerEventUpdateView.as_view(),
        name="event_edit",
    ),
    path(
        "organizer/events/<slug:slug>/delete/",
        views.OrganizerEventDeleteView.as_view(),
        name="event_delete",
    ),
    path(
        "organizer/events/<slug:slug>/registrants/",
        views.EventRegistrantsView.as_view(),
        name="event_registrants",
    ),
    path(
        "organizer/events/<slug:slug>/registrants.csv",
        views.event_csv,
        name="event_csv",
    ),
    path(
        "organizer/events/<slug:slug>/registrants/<int:registration_id>/attendance/",
        views.toggle_attendance,
        name="toggle_attendance",
    ),
]
