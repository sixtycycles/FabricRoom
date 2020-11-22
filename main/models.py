from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField()
    birthdate = models.DateField(default=datetime.now)
    profile_image = models.ImageField(upload_to ='uploads/', default='/srv/code/static/default_profile.jpg')

class Tag(models.Model):
    tag_slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.tag_slug

class Note(models.Model):
    author = models.ForeignKey(User, verbose_name="Author", on_delete=models.CASCADE)    
    link = models.URLField(blank=True)
    subject = models.CharField(max_length=100, blank=True)
    note_body = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f"{self.subject}"