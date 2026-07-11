from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from feeds.models import Feed, FeedFolder, FeedItem


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
        self.assertTrue(FeedFolder.objects.filter(user=self.user, name="Tech").exists())

    def test_user_can_mark_feed_item_as_read(self):
        self.client.login(username="reader", password="secret123")
        folder = FeedFolder.objects.create(user=self.user, name="News")
        feed = Feed.objects.create(
            user=self.user,
            folder=folder,
            title="Example Feed",
            feed_url="https://example.com/rss.xml",
            site_url="https://example.com",
        )
        item = FeedItem.objects.create(
            feed=feed,
            entry_id="entry-1",
            title="Example Article",
            link="https://example.com/articles/entry-1",
        )

        response = self.client.post(
            reverse("feeds_toggle_read", args=[item.pk]),
            {"next": reverse("feeds_dashboard")},
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertTrue(item.is_read)
        self.assertIsNotNone(item.read_at)

    def test_user_can_mark_feed_item_as_unread(self):
        self.client.login(username="reader", password="secret123")
        folder = FeedFolder.objects.create(user=self.user, name="News")
        feed = Feed.objects.create(
            user=self.user,
            folder=folder,
            title="Example Feed",
            feed_url="https://example.com/rss.xml",
            site_url="https://example.com",
        )
        item = FeedItem.objects.create(
            feed=feed,
            entry_id="entry-2",
            title="Example Article",
            link="https://example.com/articles/entry-2",
            is_read=True,
            read_at="2024-01-01T00:00:00Z",
        )

        response = self.client.post(
            reverse("feeds_toggle_read", args=[item.pk]),
            {"next": reverse("feeds_read")},
        )

        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertFalse(item.is_read)
        self.assertIsNone(item.read_at)
