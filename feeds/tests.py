from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from feeds.models import FeedFolder


class FeedReaderTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reader",
            email="reader@example.com",
            password="secret123",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("feeds_dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_user_can_create_folder(self):
        self.client.login(username="reader", password="secret123")
        response = self.client.post(
            reverse("feeds_folder_create"),
            {"name": "Tech", "description": "Technology updates"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeedFolder.objects.filter(user=self.user, name="Tech").exists()
        )
