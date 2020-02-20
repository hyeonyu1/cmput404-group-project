from django.db import models
from uuid import uuid4
from users.models import Author


# Create your models here.


class Friend(models.Model):

    author_id = models.URLField(max_length=500)
    friend_id = models.URLField(max_length=500)

    class Meta:
        unique_together = (("author_id", "friend_id"),)


class FriendRequest(models.Model):
    from_id = models.URLField(max_length=500)
    to_id = models.URLField(max_length=500)

    class Meta:
        unique_together = (("from_id", "to_id"),)
