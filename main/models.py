from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField()
    birthdate = models.DateField
    
    def __str__(self):
        return f"{self.user.username}" 