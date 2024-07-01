from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    profile_picture = models.ImageField(upload_to='static/uploaded_profile_pictures/', blank=True, null=True)


    def __str__(self):
        return self.user.username