from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title

class Tag(models.Model):
    tag_slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.tag_slug

class Note(models.Model):
    author = models.ForeignKey(User, verbose_name="Author", related_name="authors_notes", on_delete=models.CASCADE)    
    link = models.URLField(blank=True)
    title = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f"{self.title}"