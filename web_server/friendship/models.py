from django.db import models
from uuid import uuid4


# Create your models here.
"""Friend Model: This model is used to store friendship information. There are
    in total three columns within the model

    Columns
    ----------
    id: django auto-inserted column
    author_id: the full url id of an author. eg: http://127.0.0.1:8000/author/d7a387df-2b46-43ed-90f1-51c7e02c51d6
    friend_id: the full url id of a friend of the current author. eg: http://127.0.0.1:8000/author/019fcd68-9224-4d1d-8dd3-e6e865451a31

    Schema
    -------
    CREATE TABLE IF NOT EXISTS "friendship_friend" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "author_id" varchar(500) NOT NULL, "friend_id" varchar(500) NOT NULL);
    CREATE UNIQUE INDEX "friendship_friend_author_id_friend_id_e5de178b_uniq" ON "friendship_friend" ("author_id", "friend_id");
    
    Note
    -------
    my intention was to make author_id and friend_id together acts as primary key, the order does matter. 
    i.e author_id = 1, friend_id = 2 identifies a different row from author_id = 2, friend_id = 1 

    """
# Author: Ida Hou


class Friend(models.Model):

    author_id = models.URLField(max_length=500)
    friend_id = models.URLField(max_length=500)

    class Meta:
        unique_together = (("author_id", "friend_id"),)


"""FriendRequest Model: This model is used to store incoming (outgoing may as well) friend requests information. There are
    in total three columns within the model

    Columns
    ----------
    id: django auto-inserted column
    from_id: the full url id of an author who sends the friend request. eg: http://127.0.0.1:8000/author/d7a387df-2b46-43ed-90f1-51c7e02c51d6
    to_id: the full url id of an author who receives the friend request. eg: http://127.0.0.1:8000/author/019fcd68-9224-4d1d-8dd3-e6e865451a31

    Schema
    -------
    CREATE TABLE IF NOT EXISTS "friendship_friendrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "from_id" varchar(500) NOT NULL, "to_id" varchar(500) NOT NULL);
    CREATE UNIQUE INDEX "friendship_friendrequest_from_id_to_id_c10e9741_uniq" ON "friendship_friendrequest" ("from_id", "to_id");
    
    Note
    -------
    my intention was to make from_id and to_id together acts as primary key, the order does matter. 
    i.e from_id = 1, to_id = 2 identifies a different row from from_id = 2, to_id = 1 
    """

# Author: Ida Hou


class FriendRequest(models.Model):
    from_id = models.URLField(max_length=500)
    to_id = models.URLField(max_length=500)

    class Meta:
        unique_together = (("from_id", "to_id"),)
