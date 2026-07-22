from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


class PrivacyPolicy(models.Model):
    content = models.TextField(help_text="Enter the privacy policy content in HTML format.")

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and PrivacyPolicy.objects.exists():
            raise ValueError('Only one PrivacyPolicy instance is allowed.')
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Privacy Policy"

    class Meta:
        verbose_name = "Privacy Policy"
        verbose_name_plural = "Privacy Policies"


class CustomUser(AbstractUser):
    birthdate = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Custom User"
        verbose_name_plural = "Custom Users"
        ordering = ["username"]


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField()

    profile_image = models.ImageField(
        upload_to="uploads/", default="default_profile.jpg"
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["user"]

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_absolute_url(self):
        return reverse("profile_detail", args=[str(self.user.id)])


class ManagementCommandRun(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    command_name = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, db_index=True)
    summary = models.TextField(blank=True)
    details = models.TextField(blank=True)
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    finished_at = models.DateTimeField(default=timezone.now)
    duration_seconds = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "Management Command Run"
        verbose_name_plural = "Management Command Runs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.command_name} ({self.status})"
