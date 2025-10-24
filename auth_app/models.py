from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    fullname = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.email or self.username
