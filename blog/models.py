from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings


class Post(models.Model):

    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    published = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args=[str(self.id)])


class Tag(models.Model):
    tag_slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.tag_slug


class Note(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        verbose_name="Author",
        related_name="authors_notes",
        on_delete=models.CASCADE,
    )
    link = models.URLField(blank=True)
    title = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("note_detail", args=[str(self.id)])
