from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.staticfiles import finders

from .models import Post
from comments.models import Comment
from users.models import Author
from nodes.models import Node
from friendship.models import Friend
from friendship.views import FOAF_verification

from json import loads
from django.core import serializers
from django.contrib.auth.models import AnonymousUser

from social_distribution.utils.endpoint_utils import Endpoint, PagingHandler, Handler
from social_distribution.utils.basic_auth import validate_remote_server_authentication

import requests
import base64


# No Authentication Required
def retrieve_all_public_posts_on_local_server(request):
    """
    For endpoint http://service/posts
    Retrieves all public posts located on the server
    Methods: GET
    :param request: should specify Accepted content-type
    :returns: application/json | text/html
    """
    def json_handler(request, posts, pager, pagination_uris):
        output = {
            "query": "posts",
            "count": pager.count,
            "size": len(posts),
            "posts": [post.to_api_object() for post in posts]
        }
        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri

        return JsonResponse(output)

    return Endpoint(request, Post.objects.filter(visibility="PUBLIC").order_by('-published'), [
        PagingHandler("GET", "application/json", json_handler)
    ]).resolve()

def check_perm(request, api_object_post):
    """
    Checks the permissions on a post api object to see if it can be seen by the currently authenticated user
    """
    visibility = api_object_post["visibility"]
    # Foreign servers can access all posts, unless they are 'SERVERONLY'
    if request.remote_server_authenticated:
        if visibility != Post.SERVERONLY:
            return True
        else:
            return False

    user_id = request.user.uid
    author_id = api_object_post["author"]['id']

    if user_id == author_id or visibility == Post.PUBLIC:
        return True

    elif visibility == Post.FOAF:
        # getting the friends of the author
        return FOAF_verification(request, author_id)
    elif visibility == Post.SERVERONLY:
        if request.user.host == Author.objects.get(id=author_id).host:
            return True
    elif visibility == Post.PRIVATE:
        if user_id in api_object_post["visibleTo"]:
            return True
    elif visibility == Post.FRIENDS:
        author_friends = Friend.objects.filter(author_id=author_id)
        for friend in author_friends:
            if user_id == friend.friend_id:
                return True
    else:
        return False
@validate_remote_server_authentication()
def retrieve_single_post_with_id(request, post_id):
    """
    For endpoint http://service/posts/{POST_ID}
    Access the single specified post.
    For consistency, it maintains the same pageable format as http://service/posts if JSON is requested
    If HTML is requested it will return a page that will view the post details, or if the post is an image it
    will respond directly with image data for use in hosting images.
    Methods: GET
    :param request: should specify Accepted content-type
    :returns: application/json | text/html
    """


    def json_handler(request, posts, pager, pagination_uris):
        output = {
            "query": "post",
            "count": 1,
            "size": 1,
            "posts": [post.to_api_object() for post in posts if check_perm(request, post.to_api_object())],
        }
        return JsonResponse(output)

    def html_handler(request, posts, pager, pagination_uris):
        post = Post.objects.get(id=post_id)
        if post.contentType == post.TYPE_PNG or post.contentType == post.TYPE_JPEG:
            if not check_perm(request, post.to_api_object()):
                # The user does not have permission to access this post, they must be served the 401 image
                with open(finders.find('401-image.png'), 'rb') as f:
                    return HttpResponse(f.read(), content_type='image/png', status=401)
            # Note, this REQUIRES that the content be in base64 format.
            response = HttpResponse(base64.b64decode(post.content), status=200)
            response['Content-Type'] = post.contentType
            return response

        if not check_perm(request, post.to_api_object()):
            return HttpResponse("You do not have permission to see this post", status=401)
        return render(request, 'posts/post.html', {'post': post})

    # Get a single post
    return Endpoint(request, Post.objects.filter(id=post_id), [
        PagingHandler("GET", "text/html", html_handler),
        PagingHandler("GET", "application/json", json_handler)
    ]).resolve()



@validate_remote_server_authentication()
def comments_retrieval_and_creation_to_post_id(request, post_id):
    print("\n\n\n\n\n\n\n")
    print("request ", requests)

    def get_handler(request, comments, pager, pagination_uris):
        print("get_handler")
        if not Post.objects.filter(id=post_id).exists():

            return JsonResponse({
                "success": False,
                "message": "Post Does Not Exists"
            }, status=404)

        comments_list = []
        for comment in comments:
            c = comment.to_api_object()
            content = {
                "author": c["author"],
                "content": c["comment"],
                "contentType": c["contentType"],
                "published": c["published"],
                "id": c["id"]
            }
            comments_list.append(content)

        output = {
            "query": "comments",
            "count": pager.count,
            "size":  min(int(request.GET.get('size', 10)), 50),
            "comments": comments_list
        }

        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri

        return JsonResponse(output)

    # 3 cases
    # - auth user comments on local post
    # - auth user comments on foreign post
    # - foreign user comments on local post
    def post_handler(request):
        # JSON post body of what you post to a posts' comemnts
        # POST to http://service/posts/{POST_ID}/comments
        output = {
            "query": "addComment",
        }

        # checks if local host
        if Post.objects.filter(id=post_id).exists():
            # checks visibility of the post
            if not check_perm(request, Post.objects.get(id=post_id).to_api_object()):
                return JsonResponse(
                    {
                        "query": "addComment",
                        "success": False,
                        "message": "Comment not allowed"
                    }
                )
    # - auth user comments on local post
    # - foreign user comments on local post
    # if request.user.is_authenticated or request.remote_server_authenticated:
        # change body = request.POST to body = request.body.decode('utf-8'),
        # because request.POST only accepts form, but here is json format.
        # change new_comment.comment to new_comment.content,
        # because that's how it defined in comment model.
        try:
            body = request.body.decode('utf-8')
            comment_info = loads(body)
            comment_info = comment_info['comment']
            new_comment = Comment()
            new_comment.contentType = comment_info['contentType']
            new_comment.content = comment_info['comment']
            new_comment.published = comment_info['published']
            # Need to change
            # new_comment.author = Author.objects.filter(
            #     id=comment_info['author']['id']).first()
            new_comment.author = comment_info['author']['id']
            new_comment.parentPost = Post.objects.filter(id=post_id).first()
            new_comment.save()
            output['type'] = True
            output['message'] = "Comment added"
        except Exception as e:
            output['type'] = False
            output['message'] = "Comment not allowed"
            output['error'] = str(e)
        finally:
            return JsonResponse(output)
        # # foreign post
        # else:
        #     # getting the node with the post
        #     for node in Node.objects.all():
        #         username = node.username_registered_on_foreign_server
        #         password = node.password_registered_on_foreign_server
        #         api = node.foreign_server_api_location
        #         if node.append_slash:
        #             api = api + "/"
        #         response = requests.get("http://{}/posts/{POST_ID}/comments".format(api, post_id),
        #                                 auth=(username, password))
        #         if response.status_code == 200:
        #             break

    #
    #
    #         # "comment":{
    #         # 	    "author":{
    #         # 	           # ID of the Author
    #         #                    "id":"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
    #         # 		   "host":"http://127.0.0.1:5454/",
    #         # 		   "displayName":"Greg Johnson",
    #         # 		   # url to the authors information
    #         #                    "url":"http://127.0.0.1:5454/author/1d698d25ff008f7538453c120f581471",
    #         # 		   # HATEOS url for Github API
    #         # 		   "github": "http://github.com/gjohnson"
    #         # 	   },
    #         # 	   "comment":"Sick Olde English",
    #         # 	   "contentType":"text/markdown",
    #         # 	   # ISO 8601 TIMESTAMP
    #         # 	   "published":"2015-03-09T13:07:04+00:00",
    #         # 	   # ID of the Comment (UUID)
    #         # 	   "id":"de305d54-75b4-431b-adb2-eb6b9e546013"
    #         # 	}
    #
    #         # our own user making a comment to foreign post
    #         else:
    #             print("AHDASFSAOFJSAOFJAS")
    #             print(request.body.decode('utf-8'))
    #
    #             # # Find the node that contains the post
    #
    #             #
    #             # output = {
    #             #     "query": "addComment",
    #             #     "post":
    #             # }
    #             # response = requests.post("http://{}/posts/{POST_ID}/comments".format(api, post_id),
    #             #                          auth=(username, password), data=output)
    #             #
    #
    #
    #     # else:
    #     #
    #     #     output = {
    #     #         "query": "addComment",
    #     #     }
    # return Endpoint(request, Post.objects.filter(id=post_id), [
    #     # Handler("POST", "application/json", post_handler),
    #     PagingHandler("GET", "application/json", get_handler)
    # ]).resolve()

    def api_response(request, comments, pager, pagination_uris):
        print("\n\n\n\n\n\n\n")
        print("request ", requests)
        size = min(int(request.GET.get('size', 10)), 50)
        output = {
            "query": "comments",
            "count": pager.count,
            "size": size,
            "comments": [comment.to_api_object() for comment in comments]
        }
        print("output", output)
        print("\n\n\n\n\n\n\n")

        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri
        return JsonResponse(output)

    if request.user.is_authenticated:
        return Endpoint(request, Comment.objects.filter(parentPost=post_id).order_by("-published"),
                        [Handler("POST", "application/json", post_handler),
                        PagingHandler("GET", "application/json", get_handler)]
                        ).resolve()
    else:
        return Endpoint(request, Comment.objects.filter(parentPost=post_id).order_by("-published"),
                        [PagingHandler("GET", "application/json", api_response)]
                        ).resolve()


@login_required  # Local server usage only
def fetch_public_posts_from_nodes(request):
    """
    Fetches public posts from all the nodes available to the server
    :param request:
    :return:
    """
    output = {
        'query': "getPosts",
        'size': 10,
        'count': 0,
        'posts': [],
        'errors': dict()
    }
    for node in Node.objects.all():
        # Get the url of the api
        api_url = node.get_safe_api_url('posts')

        response = requests.get(api_url,
                                auth=(node.username_registered_on_foreign_server,
                                      node.password_registered_on_foreign_server),
                                headers={'Accept': 'application/json'})
        if response.status_code != 200:
            output['errors'][node.foreign_server_hostname] = f"Received response code {response.status_code} " \
                                                             f"at api endpoint: {api_url}"
            continue

        try:
            json = response.json()
        except Exception as e:
            output['errors'][node.foreign_server_hostname] = f"During JSON decode got {e} for response like " \
                                                             f"'{response.content[:20]}...'"
            continue

        for post in json['posts']:
            output['count'] += 1
            output['posts'].append(post)
            if output['count'] >= output['size']:
                break

        if output['count'] >= output['size']:
            break

    return JsonResponse(output, status=200)
