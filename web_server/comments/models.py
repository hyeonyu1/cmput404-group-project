from django.db import models
from users.models import Author
from posts.models import Post
from nodes.models import Node
import requests


from django.conf import settings


from uuid import uuid4

# Create your models here.


class Comment(models.Model):
    # Comment ID's must be unique, we use privacy respecting uuid4 to get random 128bit ids.
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    TYPE_PLAIN = "text/plain"
    TYPE_MARKDOWN = "text/markdown"
    CONTENT_TYPE_CHOICES = (
        (TYPE_PLAIN, "plain text"),
        (TYPE_MARKDOWN, "markdown")
    )
    contentType = models.CharField(
        max_length=32, choices=CONTENT_TYPE_CHOICES, default=TYPE_MARKDOWN)

    content = models.TextField()

    # Always defaults to right now on object creation
    # @todo Are comments editable? Should we allow this and if so would this field update to match?
    published = models.DateTimeField(auto_now_add=True)

    # author = models.ForeignKey(Author, on_delete=models.PROTECT)
    #uid of author
    author = models.CharField(max_length=500)


    parentPost = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        # Number of characters to include as snippet before cutting off with elipsis
        snippet_length = 15
        return f'{self.author} commented "{self.content[:snippet_length]}{"..." if len(self.content) >= snippet_length else ""}"'

    def to_api_object(self):
        """
        Returns a python object that mimics the API, ready to be converted to a JSON string for delivery.
        """
        try:
            author = Author.objects.get(uid=self.author)
            return {
                "author": author.to_api_object(),
                "comment": self.content,
                "contentType": self.contentType,
                "published": self.published,
                "id": str(self.id.hex)
            }
        except Author.DoesNotExist:
            print("\n\n\n\n\n\n\n\nforeign author=", self.author)
            node = self.author.split("/author/")[0]
            username = Node.objects.get(foreign_server_hostname=node).username_registered_on_foreign_server
            password = Node.objects.get(foreign_server_hostname=node).password_registered_on_foreign_server
            api = Node.objects.get(foreign_server_hostname=node).foreign_server_api_location
            if Node.objects.get(foreign_server_hostname=node).append_slash:
                api = api + "/"
            response = requests.get(
                "http://{}/author/{}".format(api, self.author.split("/author/")[-1]),
                auth=(username, password)
            )
            if response.status_code == 200:
                author_info = response.json()

            return {
                "author": {
                    "id": author_info["id"],
                    "host": author_info["host"],
                    "displayName": author_info["display_name"],
                    "first_name": author_info["first_name"],
                    "last_name": author_info["last_name"],
                    "url": author_info["uid"],
                    "github": author_info["github"]
                },
                "comment": self.content,
                "contentType": self.contentType,
                "published": self.published,
                "id": str(self.id.hex)
            }

