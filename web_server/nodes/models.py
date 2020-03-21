from django.db import models
from django.contrib.auth.hashers import make_password


# Create your models here.

# As a server admin, I want to be able to add node to share with #44
class Node(models.Model):
    # the credentials this foreign server use to log into our server
    foreign_server_hostname = models.URLField(
        primary_key=True, max_length=500, unique=True)
    foreign_server_password = models.CharField(max_length=30, null=False)

    # the credentials our server use to log into this foreign server
    hostname_registered_on_foreign_server = models.URLField(
        max_length=500)
    password_registered_on_foreign_server = models.CharField(
        max_length=30)

    # As a server admin, I want to share or not share images with users on other servers. #5
    image_share = models.BooleanField(default=True)

    # As a server admin, I want to share or not share posts with users on other servers. #6
    post_share = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # make_password hashes the password
        self.foreign_server_password = make_password(
            self.foreign_server_password)
        # self.password_registered_on_foreign_server = make_password(
        #     self.password_registered_on_foreign_server)
        super(Node, self).save(*args, **kwargs)
