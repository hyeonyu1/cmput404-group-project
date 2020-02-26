from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from .models import Post
from comments.models import Comment

from json import loads
from django.core import serializers

from social_distribution.utils.endpoint_utils import Endpoint, PagingHandler


def retrieve_all_public_posts_on_local_server(request):
    """
    For endpoint http://service/posts
    Retrieves all public posts located on the server
    Methods: GET
    :param request: should specify Accepted content-type
    :returns: application/json | text/html
    """
    def json_handler(request, posts, pager, pagination_uris):
        # Use Django's serializers to encode the posts as a python object
        json_posts = loads(serializers.serialize('json', posts))

        # Explicitly add authors to the serialization
        author_exclude_fields = ('password',"is_superuser", "is_staff", "groups", "user_permissions")
        json_authors = loads(serializers.serialize('json_e', [post.author for post in posts], exclude_fields=author_exclude_fields))
        for i in range(0, len(json_posts)):
            json_posts[i]['fields']['author'] = json_authors[i]['fields']  # avoid inserting the meta data

            # As per the specification, get the 5 most recent comments
            comments = Comment.objects.filter(parentPost=posts[i])[:5]
            comments_json = loads(serializers.serialize('json', comments))
            comments_author_json = loads(serializers.serialize('json_e', [comment.author for comment in comments], exclude_fields=author_exclude_fields))
            # Explicitly add authors to the comments
            for j in range(0, len(comments_json)):
                comments_json[j]['fields']['author'] = comments_author_json[i]['fields']  # avoid inserting meta data
            # Strip meta data from each comment
            comments_json = [comment['fields'] for comment in comments_json]
            json_posts[i]['fields']['comments'] = comments_json


        # And filter out the meta data from the top level object
        for post in json_posts:
            post['fields']['id'] = post['pk']
        json_posts = [post['fields'] for post in json_posts]

        output = {
            "query": "posts",
            "count": pager.count,
            "size": len(posts),
            "posts": json_posts
        }
        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri

        return JsonResponse(output)

    def html_handler(request, posts, pager, pagination_uris):
        html = ""
        for post in posts:
            html += f"<p>{post.__str__()}</p>"
        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            html += f"<a href='{prev_uri}'>PREV PAGE</a>"
        if next_uri:
            html += f"<a href='{next_uri}'>NEXT PAGE</a>"

        return HttpResponse(html)


    endpoint = Endpoint(request,
                        Post.objects.filter(visibility="PUBLIC"),
                        [
                            PagingHandler("GET", "text/html", html_handler),
                            PagingHandler("GET", "application/json", json_handler)
                        ])

    return endpoint.resolve()

# access to a single post with id = {POST_ID}
# http://service/posts/{POST_ID} 
def retrieve_single_post_with_id(request, post_id):
    #???????
    # POST to http://service/posts/{POST_ID} , sending the body
    if request.method == 'POST':
        return HttpResponse("<h1>http://service/posts/{} POST</h1>".format(post_id))
    # Get a single post
    elif request.method == 'GET':
        #return HttpResponse("<h1>http://service/posts/{} GET</h1>".format(post_id))
        return render(request, 'viewPost.html')
    return None

def comments_retrieval_and_creation_to_post_id(request, post_id):
    if request.method == 'POST':
        # JSON post body of what you post to a posts' comemnts
        # POST to http://service/posts/{POST_ID}/comments
        return HttpResponse("http://service/posts/{POST_ID}/comments POST")
    elif request.method == 'GET':
        # access to the comments in a post
        # GET from http://service/posts/{post_id}/comments 
        return HttpResponse("http://service/posts/{post_id}/comments GET")
    return None
    