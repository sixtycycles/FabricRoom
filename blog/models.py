from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image, ImageOps


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


class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ["author", "text"]

    def __str__(self):
        if self.author:
            return f"{self.text} — {self.author}"
        return self.text


class InlineImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="inline_images",
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="inline-images/%Y/%m/%d/")
    alt_text = models.CharField(max_length=255, default="Blog image")
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    MAX_DIMENSION = 1600
    JPEG_QUALITY = 85

    class Meta:
        verbose_name = "Inline Image"
        verbose_name_plural = "Inline Images"
        ordering = ["created_at"]

    def __str__(self):
        if self.post:
            return f"Image for {self.post.title}"
        return f"Pending image ({self.session_key})"

    def save(self, *args, **kwargs):
        if self.image and not self._is_resized_image():
            self.image = self._optimize_image(self.image)
        super().save(*args, **kwargs)

    def _is_resized_image(self):
        return getattr(self.image, "name", "").startswith("inline-images/") and self.pk is not None

    def _optimize_image(self, uploaded_image):
        image = Image.open(uploaded_image)
        image = ImageOps.exif_transpose(image)

        if image.mode in {"RGBA", "LA", "P"}:
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")

        image.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)

        output = BytesIO()
        image.save(output, format="JPEG", quality=self.JPEG_QUALITY, optimize=True)
        output.seek(0)

        return ContentFile(output.getvalue(), name=self._image_filename(uploaded_image.name))

    def _image_filename(self, original_name):
        base_name, _ = original_name.rsplit(".", 1)
        return f"{base_name}.jpg"
