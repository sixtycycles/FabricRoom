from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from feeds.models import Feed, FeedFolder, FeedItem
from feeds.views import ReadArticlesView


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

    def test_read_articles_view_includes_current_user_in_context(self):
        self.client.login(username="reader", password="secret123")
        response = self.client.get(reverse("feeds_read"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], self.user)

    def test_dashboard_sorting_by_date(self):
        self.client.login(username="reader", password="secret123")
        feed_a = Feed.objects.create(
            user=self.user,
            title="A Feed",
            feed_url="https://example.com/a.xml",
        )
        feed_b = Feed.objects.create(
            user=self.user,
            title="B Feed",
            feed_url="https://example.com/b.xml",
        )
        item1 = FeedItem.objects.create(
            feed=feed_a,
            entry_id="1",
            title="First Item",
            published="2026-07-01T00:00:00Z",
        )
        item2 = FeedItem.objects.create(
            feed=feed_b,
            entry_id="2",
            title="Second Item",
            published="2026-07-02T00:00:00Z",
        )

        # Default or date sorting: newest first (item2 then item1)
        response = self.client.get(reverse("feeds_dashboard") + "?sort=date")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["entries"]), [item2, item1])

    def test_dashboard_sorting_by_source(self):
        self.client.login(username="reader", password="secret123")
        feed_b = Feed.objects.create(
            user=self.user,
            title="B Feed",
            feed_url="https://example.com/b.xml",
        )
        feed_a = Feed.objects.create(
            user=self.user,
            title="A Feed",
            feed_url="https://example.com/a.xml",
        )
        item1 = FeedItem.objects.create(
            feed=feed_b,
            entry_id="1",
            title="First Item",
            published="2026-07-01T00:00:00Z",
        )
        item2 = FeedItem.objects.create(
            feed=feed_a,
            entry_id="2",
            title="Second Item",
            published="2026-07-02T00:00:00Z",
        )

        # Sorted by source name alphabetically (A Feed item2, B Feed item1)
        response = self.client.get(reverse("feeds_dashboard") + "?sort=source")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["entries"]), [item2, item1])

    def test_dashboard_reports_most_recent_last_fetched_at(self):
        from django.utils.dateparse import parse_datetime

        self.client.login(username="reader", password="secret123")
        Feed.objects.create(
            user=self.user,
            title="Older",
            feed_url="https://example.com/older.xml",
            last_fetched_at=parse_datetime("2026-07-01T08:00:00Z"),
        )
        newest = Feed.objects.create(
            user=self.user,
            title="Newest",
            feed_url="https://example.com/newest.xml",
            last_fetched_at=parse_datetime("2026-07-24T15:00:00Z"),
        )
        FeedItem.objects.create(
            feed=newest,
            entry_id="new-1",
            title="Newest article",
            published="2026-07-24T12:00:00Z",
        )

        response = self.client.get(reverse("feeds_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["last_updated_at"],
            newest.last_fetched_at,
        )

    def test_dashboard_reports_none_when_no_feeds_fetched(self):
        self.client.login(username="reader", password="secret123")
        Feed.objects.create(
            user=self.user,
            title="Stale",
            feed_url="https://example.com/stale.xml",
        )

        response = self.client.get(reverse("feeds_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["last_updated_at"])

    def test_dashboard_pagination_and_unread_count(self):
        self.client.login(username="reader", password="secret123")
        feed = Feed.objects.create(
            user=self.user,
            title="Test Feed",
            feed_url="https://example.com/feed.xml",
        )
        for i in range(15):
            FeedItem.objects.create(
                feed=feed,
                entry_id=f"entry-{i}",
                title=f"Article {i}",
                published=f"2026-07-01T{i:02d}:00:00Z",
            )

        # Page 1 should contain 10 items and report unread_count of 15
        response = self.client.get(reverse("feeds_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["unread_count"], 15)
        self.assertEqual(len(response.context["entries"]), 10)
        self.assertTrue(response.context["page_obj"].has_next())

        # Page 2 should contain the remaining 5 items
        response_page2 = self.client.get(reverse("feeds_dashboard") + "?page=2")
        self.assertEqual(response_page2.status_code, 200)
        self.assertEqual(len(response_page2.context["entries"]), 5)
        self.assertFalse(response_page2.context["page_obj"].has_next())

