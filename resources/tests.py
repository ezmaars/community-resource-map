"""
Basic tests. Run with:  python manage.py test
These cover the rules that matter most for trust: pending resources stay
hidden, submissions land in the queue, and the API only exposes approved data.
"""

from datetime import time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, OperatingHours, Resource


class ResourceVisibilityTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Food")
        self.approved = Resource.objects.create(
            name="Open Pantry",
            category=self.cat,
            description="Free food.",
            city="Denver",
            latitude=39.74,
            longitude=-104.99,
            status=Resource.Status.APPROVED,
        )
        self.pending = Resource.objects.create(
            name="Secret Pantry",
            category=self.cat,
            description="Awaiting review.",
            city="Denver",
            latitude=39.75,
            longitude=-104.98,
            status=Resource.Status.PENDING,
        )

    def test_browse_shows_only_approved(self):
        resp = self.client.get(reverse("browse"))
        self.assertContains(resp, "Open Pantry")
        self.assertNotContains(resp, "Secret Pantry")

    def test_detail_hides_pending_from_public(self):
        resp = self.client.get(
            reverse("resource_detail", args=[self.pending.slug])
        )
        self.assertEqual(resp.status_code, 404)

    def test_api_returns_only_approved(self):
        resp = self.client.get(reverse("api_resources"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        names = [f["properties"]["name"] for f in data["features"]]
        self.assertIn("Open Pantry", names)
        self.assertNotIn("Secret Pantry", names)

    def test_search_filter(self):
        resp = self.client.get(reverse("browse"), {"q": "Open"})
        self.assertContains(resp, "Open Pantry")


class SubmissionTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Health")

    def test_submission_creates_pending_resource(self):
        resp = self.client.post(
            reverse("submit"),
            {
                "name": "New Clinic",
                "category": self.cat.id,
                "description": "A helpful clinic.",
                "city": "Denver",
                "is_free": "on",
                "country": "USA",
            },
        )
        self.assertEqual(resp.status_code, 302)
        r = Resource.objects.get(name="New Clinic")
        self.assertEqual(r.status, Resource.Status.PENDING)

    def test_honeypot_blocks_spam(self):
        resp = self.client.post(
            reverse("submit"),
            {
                "name": "Spam Clinic",
                "category": self.cat.id,
                "description": "spam",
                "city": "Denver",
                "company": "i-am-a-bot",
            },
        )
        # Form is invalid -> page re-renders (200) and nothing is saved.
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Resource.objects.filter(name="Spam Clinic").exists())


class OpenNowTests(TestCase):
    def test_is_open_now_unknown_without_hours(self):
        cat = Category.objects.create(name="Jobs")
        r = Resource.objects.create(
            name="No Hours", category=cat, description="x",
            status=Resource.Status.APPROVED,
        )
        self.assertIsNone(r.is_open_now())

    def test_is_open_now_true_when_within_hours(self):
        cat = Category.objects.create(name="Jobs2")
        r = Resource.objects.create(
            name="Always Open", category=cat, description="x",
            status=Resource.Status.APPROVED,
        )
        now = timezone.localtime()
        OperatingHours.objects.create(
            resource=r,
            day_of_week=now.weekday(),
            opens=time(0, 0),
            closes=time(23, 59),
        )
        self.assertTrue(r.is_open_now())
