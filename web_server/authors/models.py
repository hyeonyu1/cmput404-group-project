from django.db import models
from uuid import uuid4

# Create your models here.
class Author(models.Model):
    # Author ID's must be unique, we use privacy respecting uuid4 to get random 128bit ids.
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField()
    bio = models.TextField()
    host = models.URLField()
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256)
    url = models.URLField()
    github = models.URLField()

    def __str__(self):
        return self.display_name