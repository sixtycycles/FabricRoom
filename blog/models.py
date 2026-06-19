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
        related_name="blog_posts",
    )
    published = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField("Tag", blank=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_date"]

    def get_tags(self):
        tags = self.tags.all()
        return tags

    def get_author(self):
        author = self.author
        return author


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", args=[str(self.id)])


class Tag(models.Model):
    tag_slug = models.SlugField(max_length=200, unique=True)
    tag_name = models.CharField(max_length=200, unique=True)
    tag_description = models.TextField(blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["tag_name"]

    def __str__(self):
        return self.tag_slug

    def get_absolute_url(self):
        return reverse("tag_detail", args=[str(self.tag_slug)])


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

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("note_detail", args=[str(self.id)])


class InlineImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="inline_images",
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="inline-images/%Y/%m/%d/")
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Inline Image"
        verbose_name_plural = "Inline Images"
        ordering = ["created_at"]

    def __str__(self):
        if self.post:
            return f"Image for {self.post.title}"
        return f"Pending image ({self.session_key})"
