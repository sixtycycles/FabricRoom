from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class FeedFolder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feed_folders",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("feeds_dashboard")


class Feed(models.Model):
    folder = models.ForeignKey(
        FeedFolder,
        on_delete=models.CASCADE,
        related_name="feeds",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feeds",
    )
    title = models.CharField(max_length=255)
    feed_url = models.URLField(max_length=500)
    site_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    last_fetched_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        unique_together = ("user", "feed_url")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("feeds_dashboard")


class FeedItem(models.Model):
    """A single entry parsed from a Feed, persisted so we can track read state.

    `entry_id` is a stable identifier provided by the feed itself (guid/id),
    falling back to the entry link when neither is present. It is unique
    per feed so refreshing the feed doesn't create duplicates.
    """

    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE,
        related_name="items",
    )
    entry_id = models.CharField(max_length=1000)
    title = models.CharField(max_length=500, blank=True)
    link = models.URLField(max_length=1000, blank=True)
    summary = models.TextField(blank=True)
    author = models.CharField(max_length=255, blank=True)
    published = models.DateTimeField(blank=True, null=True)
    fetched_at = models.DateTimeField(default=timezone.now)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-published", "-fetched_at"]
        unique_together = ("feed", "entry_id")
        indexes = [
            models.Index(fields=["feed", "is_read"]),
            models.Index(fields=["feed", "-published"]),
        ]

    def __str__(self):
        return self.title or self.link or self.entry_id

    def get_absolute_url(self):
        return reverse("feeds_dashboard")

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_unread(self):
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=["is_read", "read_at"])
