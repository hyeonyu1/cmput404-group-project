from django.db import models
from django.contrib.auth.hashers import make_password


# Create your models here.
#

# http://dsnfof.herokuapp.com/
# from hostname ->  Authentication: basic server_username:server_password
# hostname = "dsnfof.herokuapp.com"
# server_username = "their username"
# server_password = "password"
# we send -> to api_location Authentication: api_username:api_password
# api_location = "dsnfof.herokuapp.com/api"
# api_username = "our username"
# api_password = "some password"

# As a server admin, I want to be able to add node to share with #44
class Node(models.Model):

    foreign_server_hostname = models.CharField(
        primary_key=True, max_length=500, unique=True)

    # the credentials this foreign server use to log into our server
    foreign_server_username = models.CharField(max_length=500, null=False)
    foreign_server_password = models.CharField(max_length=500, null=False)

    foreign_server_api_location = models.CharField(max_length=500, null=False)
    # the credentials our server use to log into this foreign server
    username_registered_on_foreign_server = models.CharField(
        max_length=500)
    password_registered_on_foreign_server = models.CharField(
        max_length=500)

    # As a server admin, I want to share or not share images with users on other servers. #5
    image_share = models.BooleanField(default=True)

    # As a server admin, I want to share or not share posts with users on other servers. #6
    post_share = models.BooleanField(default=True)

    append_slash = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # make_password hashes the password
        self.foreign_server_password = make_password(
            self.foreign_server_password)
        # self.password_registered_on_foreign_server = make_password(
        #     self.password_registered_on_foreign_server)
        super(Node, self).save(*args, **kwargs)
