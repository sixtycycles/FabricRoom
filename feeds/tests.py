from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from feeds.models import Feed, FeedFolder, FeedItemEvent, FeedItemRead


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

        response = self.client.post(
            reverse("feeds_mark_read"),
            {
                "feed_id": feed.pk,
                "entry_key": "entry-1",
                "event_type": "manual",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeedItemRead.objects.filter(
                user=self.user,
                feed=feed,
                entry_key="entry-1",
            ).exists()
        )

    def test_clicking_article_title_logs_event_and_marks_read(self):
        self.client.login(username="reader", password="secret123")
        folder = FeedFolder.objects.create(user=self.user, name="News")
        feed = Feed.objects.create(
            user=self.user,
            folder=folder,
            title="Example Feed",
            feed_url="https://example.com/rss.xml",
            site_url="https://example.com",
        )

        response = self.client.post(
            reverse("feeds_mark_read"),
            {
                "feed_id": feed.pk,
                "entry_key": "entry-2",
                "event_type": "title_click",
                "title": "Test Article",
                "link": "https://example.com/articles/test-article",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeedItemRead.objects.filter(
                user=self.user,
                feed=feed,
                entry_key="entry-2",
            ).exists()
        )
        self.assertTrue(
            FeedItemEvent.objects.filter(
                user=self.user,
                feed=feed,
                entry_key="entry-2",
                event_type="title_click",
            ).exists()
        )
