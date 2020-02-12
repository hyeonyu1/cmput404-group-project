from django.db import models
from users.models import Author

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

    author = models.ForeignKey(Author, on_delete=models.PROTECT)
