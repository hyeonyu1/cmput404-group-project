from django.db import models

from uuid import uuid4
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Author(AbstractUser):
    # Author ID's must be unique, we use privacy respecting uuid4 to get random 128bit ids.
    id = models.UUIDField(primary_key=True, default=uuid4,
                          editable=False)
    uid = models.URLField(primary_key=False, max_length=500)

    bio = models.TextField()
    host = models.URLField()
    display_name = models.CharField(max_length=256)
    url = models.URLField(max_length=500)
    github = models.URLField()
