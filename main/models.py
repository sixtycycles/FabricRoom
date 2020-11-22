from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField()
    birthdate = models.DateField(default=datetime.now)
    profile_image = models.ImageField(upload_to ='uploads/', default='/srv/code/static/default_profile.jpg')
    

class Note(models.Model):
    author = models.ForeignKey(User, verbose_name="Author", on_delete=models.CASCADE)    
    link = models.URLField()
    note_body = models.TextField()