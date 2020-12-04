from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.conf import settings


class CustomUser(AbstractUser):
    birthdate = models.DateField(default=datetime.now)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField()
    
    profile_image = models.ImageField(
        upload_to='uploads/', default='/srv/code/static/default_profile.jpg')
