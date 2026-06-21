from django.conf import settings
from django.db import models
from django.urls import reverse


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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        unique_together = ("user", "feed_url")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("feeds_dashboard")
