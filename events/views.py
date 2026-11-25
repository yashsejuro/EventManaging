"""Public and organizer views for ClubEvents.

The site intentionally uses Django's server-rendered generic views.  The two
state-changing registration actions remain small function views so their
database transactions are easy to see and explain in a viva.
"""

import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import Count, F, IntegerField, OuterRef, Subquery, Sum
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from .forms import EventForm
from .models import Event, Registration


def is_organizer(user):
    """Return whether a user may access the custom organizer area."""
    return user.is_authenticated and (
        user.is_superuser or user.has_perm("events.add_event")
    )


def event_queryset():
    """Return events with data needed by cards without N+1 registration queries."""
    registrations = Count("registrations", distinct=True)
    return (
        Event.objects.select_related("created_by")
        .annotate(registration_count=registrations)
        .annotate(
            seats_open=ExpressionWrapper(
                F("capacity") - registrations,
                output_field=IntegerField(),
            )
        )
    )


class AnonymousEdgeCacheMixin:
    """Set CDN edge cache headers only for anonymous, message-free GET requests."""

    cache_control = "public, s-maxage=60, stale-while-revalidate=300"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        is_anon = not request.user.is_authenticated and not request.COOKIES.get("sessionid")
        has_messages = bool(messages.get_messages(request))
        if request.method == "GET" and response.status_code == 200 and is_anon and not has_messages:
            response["Cache-Control"] = self.cache_control
        elif request.user.is_authenticated:
            response["Cache-Control"] = "private, no-store"
        return response


class HomeView(AnonymousEdgeCacheMixin, TemplateView):
    """Landing page with a small set of database-derived figures."""

    template_name = "events/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        upcoming = event_queryset().filter(start_datetime__gte=now)
        featured = list(upcoming.order_by("start_datetime")[:3])

        def _compute_stats():
            rows = list(
                Event.objects.filter(start_datetime__gte=now)
                .values("id", "capacity")
                .annotate(regs=Count("registrations"))
            )
            events_count = len(rows)
            total_capacity = sum(r["capacity"] for r in rows)
            registration_total = sum(r["regs"] for r in rows)
            return {
                "events": events_count,
                "registrations": registration_total,
                "seats_open": max(total_capacity - registration_total, 0),
            }

        stats = cache.get_or_set("home_stats_v1", _compute_stats, 60)
        context.update(
            featured_events=featured,
            event_count=stats["events"],
            registration_count=stats["registrations"],
            seats_open=stats["seats_open"],
            stats=stats,
            categories=Event._meta.get_field("category").choices,
        )
        return context


class EventListView(AnonymousEdgeCacheMixin, ListView):
    """Searchable, paginated public listing (nine cards on each page)."""

    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        queryset = event_queryset().order_by("start_datetime")
        query = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()

        if query:
            # Q lets one search term cover several useful fields.
            from django.db.models import Q

            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(venue__icontains=query)
            )
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            categories=Event._meta.get_field("category").choices,
            selected_category=self.request.GET.get("category", ""),
            search_query=self.request.GET.get("q", ""),
        )
        return context


class EventDetailView(AnonymousEdgeCacheMixin, DetailView):
    """Display one event and, for signed-in users, their registration state."""

    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return event_queryset().prefetch_related("registrations")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration = None
        if self.request.user.is_authenticated:
            # registrations is prefetched above, so this does not make a query.
            registration = next(
                (
                    item
                    for item in context["event"].registrations.all()
                    if item.user_id == self.request.user.id
                ),
                None,
            )
        context.update(
            user_registration=registration,
            is_registered=registration is not None,
            is_organizer=is_organizer(self.request.user),
        )
        return context


@login_required
@require_POST
def register_event(request, slug):
    """Create one registration after rechecking every rule inside a transaction."""
    try:
        with transaction.atomic():
            # Lock the event row before counting registrations to reduce race windows.
            event = Event.objects.select_for_update().get(slug=slug)
            if event.is_past:
                messages.error(request, "Registration is closed because this event has ended.")
                return redirect("events:event_detail", slug=event.slug)
            if Registration.objects.filter(user=request.user, event=event).exists():
                messages.info(request, "You are already registered for this event.")
                return redirect("events:event_detail", slug=event.slug)
            if Registration.objects.filter(event=event).count() >= event.capacity:
                messages.error(request, "This event is now full.")
                return redirect("events:event_detail", slug=event.slug)

            Registration.objects.create(user=request.user, event=event)
            transaction.on_commit(
                lambda: send_mail(
                    subject=f"You are registered: {event.title}",
                    message=(
                        f"Hi {request.user.get_username()},\n\n"
                        f"Your registration for {event.title} at {event.venue} is confirmed.\n"
                        f"Starts: {timezone.localtime(event.start_datetime):%d %b %Y, %I:%M %p}."
                    ),
                    from_email=None,
                    recipient_list=[request.user.email] if request.user.email else [],
                    fail_silently=True,
                )
            )
    except Event.DoesNotExist as exc:
        raise Http404("Event not found.") from exc
    except IntegrityError:
        # The database UniqueConstraint is the final guard if two requests race.
        messages.info(request, "You are already registered for this event.")
        return redirect("events:event_detail", slug=slug)

    messages.success(request, "Registration confirmed. Check your email for the details.")
    return redirect("events:event_detail", slug=event.slug)


@login_required
@require_POST
def cancel_registration(request, slug):
    """Remove the current user's registration; cancellation is always a POST."""
    with transaction.atomic():
        event = get_object_or_404(Event.objects.select_for_update(), slug=slug)
        registration = Registration.objects.filter(user=request.user, event=event).first()
        if registration:
            registration.delete()
            messages.success(request, "Your registration has been cancelled.")
        else:
            messages.info(request, "You did not have a registration for this event.")
    return redirect("events:event_detail", slug=event.slug)


class MyRegistrationsView(LoginRequiredMixin, ListView):
    """A student's registrations, with event and organizer fetched efficiently."""

    template_name = "events/my_registrations.html"
    context_object_name = "registrations"

    def get_queryset(self):
        return (
            Registration.objects.filter(user=self.request.user)
            .select_related("event", "event__created_by")
            .order_by("event__start_datetime")
        )


class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Authorize the Organizer group (or a superuser) on custom staff pages."""

    raise_exception = True

    def test_func(self):
        return is_organizer(self.request.user)


class OwnedEventQuerysetMixin:
    """Limit organizers to their events while allowing superusers to see all."""

    def get_queryset(self):
        queryset = event_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(created_by=self.request.user)


class OrganizerDashboardView(OrganizerRequiredMixin, ListView):
    template_name = "organizer/dashboard.html"
    context_object_name = "events"

    def get_queryset(self):
        return OwnedEventQuerysetMixin.get_queryset(self).order_by("start_datetime")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = context["object_list"]
        context["total_events"] = events.count()
        context["total_registrations"] = Registration.objects.filter(
            event__in=events
        ).count()
        context["seats_open"] = sum(max(event.seats_open, 0) for event in events)
        return context


class OrganizerEventCreateView(OrganizerRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "organizer/event_form.html"

    def form_valid(self, form):
        # created_by is never exposed in HTML; it always comes from the session user.
        form.instance.created_by = self.request.user
        messages.success(self.request, "Event published.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("events:event_registrants", kwargs={"slug": self.object.slug})


class OrganizerEventUpdateView(OrganizerRequiredMixin, OwnedEventQuerysetMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "organizer/event_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        messages.success(self.request, "Event updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("events:event_registrants", kwargs={"slug": self.object.slug})


class OrganizerEventDeleteView(OrganizerRequiredMixin, OwnedEventQuerysetMixin, DeleteView):
    model = Event
    template_name = "organizer/event_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("events:organizer_dashboard")

    def form_valid(self, form):
        messages.success(self.request, "Event deleted.")
        return super().form_valid(form)


class EventRegistrantsView(OrganizerRequiredMixin, OwnedEventQuerysetMixin, ListView):
    """Organizer-only attendee list for one owned event."""

    template_name = "organizer/registrants.html"
    context_object_name = "registrations"

    def get_event(self):
        """Look up the owned event after the access mixin has authorized the user."""
        if not hasattr(self, "_event"):
            self._event = get_object_or_404(
                OwnedEventQuerysetMixin.get_queryset(self), slug=self.kwargs["slug"]
            )
        return self._event

    def get_queryset(self):
        return Registration.objects.filter(event=self.get_event()).select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context


def _owned_event_or_404(request, slug):
    queryset = event_queryset()
    if not request.user.is_superuser:
        queryset = queryset.filter(created_by=request.user)
    return get_object_or_404(queryset, slug=slug)


@login_required
def event_csv(request, slug):
    """Return a simple CSV export for an organizer's own event."""
    if not is_organizer(request.user):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    event = _owned_event_or_404(request, slug)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{event.slug}-registrants.csv"'
    writer = csv.writer(response)
    writer.writerow(["Username", "Name", "Email", "Registered at", "Attended"])
    for registration in Registration.objects.filter(event=event).select_related("user"):
        user = registration.user
        writer.writerow(
            [
                user.get_username(),
                user.get_full_name(),
                user.email,
                timezone.localtime(registration.registered_at).strftime("%Y-%m-%d %H:%M"),
                "Yes" if registration.attended else "No",
            ]
        )
    return response


@login_required
@require_POST
def toggle_attendance(request, slug, registration_id):
    """Toggle one attendee's check-in, after verifying event ownership."""
    if not is_organizer(request.user):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    event = _owned_event_or_404(request, slug)
    registration = get_object_or_404(
        Registration.objects.select_related("user"), pk=registration_id, event=event
    )
    registration.attended = not registration.attended
    registration.save(update_fields=["attended"])
    messages.success(
        request,
        f"Attendance marked {'present' if registration.attended else 'not attended'} for "
        f"{registration.user.get_username()}.",
    )
    return redirect("events:event_registrants", slug=event.slug)
