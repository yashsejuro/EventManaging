"""Core business-rule tests for registration and organizer access."""

from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, Registration


class RegistrationFlowTests(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user("organizer", password="pass12345")
        self.student = User.objects.create_user("student", password="pass12345")
        self.event = Event.objects.create(
            title="Future meetup",
            description="An event used by the test suite.",
            category="TECH",
            venue="Room 101",
            start_datetime=timezone.now() + timedelta(days=2),
            capacity=2,
            created_by=self.organizer,
        )

    def test_cannot_register_twice(self):
        self.client.force_login(self.student)
        url = reverse("events:register_event", kwargs={"slug": self.event.slug})
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Registration.objects.filter(event=self.event, user=self.student).count(), 1)

    def test_cannot_register_for_full_event(self):
        self.event.capacity = 1
        self.event.save(update_fields=["capacity"])
        other = User.objects.create_user("other", password="pass12345")
        Registration.objects.create(event=self.event, user=other)
        self.client.force_login(self.student)
        self.client.post(reverse("events:register_event", kwargs={"slug": self.event.slug}))
        self.assertFalse(Registration.objects.filter(event=self.event, user=self.student).exists())

    def test_cannot_register_for_past_event(self):
        past_event = Event.objects.create(
            title="Past meetup",
            description="Already finished.",
            category="TALK",
            venue="Room 102",
            start_datetime=timezone.now() - timedelta(days=1),
            capacity=10,
            created_by=self.organizer,
        )
        self.client.force_login(self.student)
        self.client.post(reverse("events:register_event", kwargs={"slug": past_event.slug}))
        self.assertFalse(Registration.objects.filter(event=past_event, user=self.student).exists())

    def test_anonymous_users_are_redirected_to_login(self):
        response = self.client.get(reverse("events:my_registrations"))
        self.assertRedirects(
            response,
            f"/accounts/login/?next={reverse('events:my_registrations')}",
        )


class OrganizerPermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("student", password="pass12345")

    def test_non_organizers_cannot_access_organizer_pages(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("events:organizer_dashboard"))
        self.assertEqual(response.status_code, 403)
