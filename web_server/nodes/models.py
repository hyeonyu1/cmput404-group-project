from django.db import models
from uuid import uuid4

# Create your models here.

# As a server admin, I want to be able to add node to share with #44
class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4,
                          editable=False, unique=True)
    friend_node = models.URLField(max_length=500, unique=True)

    # As a server admin, I want to share or not share images with users on other servers. #5
    image_share = models.BooleanField(default=True)

    # As a server admin, I want to share or not share posts with users on other servers. #6
    post_share = models.BooleanField(default=True)

