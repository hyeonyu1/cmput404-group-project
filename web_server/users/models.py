from django.db import models
from django.conf import settings
from uuid import uuid4
from django.contrib.auth.models import AbstractUser
# Create your models here.

"""Author Model: This model is used to store all Author related information. This model is an extension of 
    built-in auth-users model. 
    
    Important Columns to Note
    ----------
    id: UUIDField. eg: d7a387df-2b46-43ed-90f1-51c7e02c51d6
    uid: primary key which is the full url id of an author. eg: 127.0.0.1:8000/author/d7a387df-2b46-43ed-90f1-51c7e02c51d6
    url: same value as uid, this is an url to author's profile page. eg: http://127.0.0.1:8000/author/019fcd68-9224-4d1d-8dd3-e6e865451a31
    is_active: default to False when author signs up, as per requirements. 

    Schema
    -------
    CREATE TABLE IF NOT EXISTS "users_author" 
    ("password" varchar(128) NOT NULL, 
    "last_login" datetime NULL, 
    "is_superuser" bool NOT NULL, 
    "username" varchar(150) NOT NULL UNIQUE, 
    "first_name" varchar(30) NOT NULL, 
    "last_name" varchar(150) NOT NULL, 
    "email" varchar(254) NOT NULL, 
    "is_staff" bool NOT NULL, 
    "is_active" bool NOT NULL, 
    "date_joined" datetime NOT NULL, 
    "id" char(32) NOT NULL, 
    "uid" varchar(500) NOT NULL PRIMARY KEY, 
    "bio" text NOT NULL, 
    "host" varchar(200) NOT NULL, 
    "display_name" varchar(256) NOT NULL, 
    "url" varchar(500) NOT NULL, 
    "github" varchar(200) NOT NULL);
    """

# Author: Ida Hou


class Author(AbstractUser):
    # Author ID's must be unique, we use privacy respecting uuid4 to get random 128bit ids.
    id = models.UUIDField(primary_key=False, default=uuid4,
                          editable=False, unique=True)
    uid = models.CharField(
        primary_key=True, max_length=500)  # without protocol
    bio = models.TextField(blank=True)
    host = models.URLField(max_length=500)
    display_name = models.CharField(max_length=256, blank=True)
    url = models.URLField(max_length=500)
    github = models.URLField(blank=True)

    def save(self, *args, **kwargs):

        if self.is_superuser:
            self.uid = settings.HOSTNAME + "/author/" + str(self.id.hex)
        super(Author, self).save(*args, **kwargs)
