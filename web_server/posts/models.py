from django.db import models
from authors.models import Author

from uuid import uuid4

# Create your models here.
class Post(models.Model):
    # Post ID's must be unique, we use privacy respecting uuid4 to get random 128bit ids.
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=256)
    source = models.URLField()
    origin = models.URLField()
    description = models.CharField(max_length=512)

    TYPE_PLAIN = "text/plain"
    TYPE_MARKDOWN = "text/markdown"
    TYPE_PNG = "image/png;base64"
    TYPE_JPEG = "image/jpeg;base64"
    TYPE_BASE64 = "application/base64"
    CONTENT_TYPE_CHOICES = (
        ('Text', (
            (TYPE_PLAIN, "plain text"),
            (TYPE_MARKDOWN, "markdown")
        )),
        ("Image", (
            (TYPE_PNG, "png"),
            (TYPE_JPEG, "jpeg")
        )),
        (TYPE_BASE64, "base64 encoded")
    )
    contentType = models.CharField(max_length=32, choices=CONTENT_TYPE_CHOICES, default=TYPE_MARKDOWN)

    content = models.TextField()
    # @todo Should deleting an author delete their posts? I feel like a good user experience is to say the
    # post still exists, but the user has been deleted, as per reddit
    author = models.ForeignKey(Author, on_delete=models.PROTECT)

    # Storing a list of comma delineated categories
    # @todo Should this be replaced with a many-to-many combo table and a separate 'categories' model?
    # categories = models.CharField(max_length=256)

    # Count of comments
    count = models.PositiveIntegerField()

    # Page Size
    # @todo What is a 'page'? A page of comments?
    size = models.PositiveIntegerField()

    # Comments
    # @todo obviously this should not be implemented in this model, it should be implemented as
    # a foreign key in the comments model

    # Always defaults to right now on object creation
    # @todo Are posts editable? Should we allow this and if so would this field update to match?
    published = models.DateTimeField(auto_now_add=True)

    PUBLIC = 'PUBLIC'
    FOAF = 'FOAF'
    FRIENDS = 'FRIENDS'
    PRIVATE = 'PRIVATE'
    SERVERONLY = 'SERVERONLY'
    VISIBILITY_CHOICES = (
        (PUBLIC, "Public"),
        # @todo what does FOAF mean? Update this to something human readable
        (FOAF, "FOAF"),
        (FRIENDS, "Friends"),
        (PRIVATE, "Private"),
        (SERVERONLY, "Server Admins Only")
    )
    visibility = models.CharField(max_length=16, choices=VISIBILITY_CHOICES, default=FRIENDS)

    # List of user URI's who can read this message
    # @todo this clearly should be some sort of many-to-many relationship table
    #

    # Unlisted posts are hidden from users. By default posts should show to users.
    unlisted = models.BooleanField(default=False)

