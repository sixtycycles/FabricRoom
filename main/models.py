from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


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
