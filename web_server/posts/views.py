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

import re

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
            if request.user.host == Author.objects.get(uid=author_id).host:
                return True
        elif visibility == Post.PRIVATE:
            # The visibleTo list contains protocols, which we dont want
            no_protocol_visible_to = [re.sub(r'http(s)*://', '', vt) for vt in api_object_post["visibleTo"]]
            if user_id in no_protocol_visible_to:
                return True
        elif visibility == Post.FRIENDS:
            author_friends = Friend.objects.filter(author_id=author_id)
            for friend in author_friends:
                if user_id == friend.friend_id:
                    return True
        else:
            return False

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




def comments_retrieval_and_creation_to_post_id(request, post_id):
    def get_handler(request, posts, pager, pagination_uris):
        # Explicitly add authors to the serialization
        author_exclude_fields = (
            'password', "is_superuser", "is_staff", "groups", "user_permissions")

        # Get the comments
        comments = Comment.objects.filter(parentPost=posts[0])
        comments_json = loads(serializers.serialize('json', comments))
        comments_author_json = loads(serializers.serialize('json_e', [
                                     comment.author for comment in comments], exclude_fields=author_exclude_fields))
        # Explicitly add authors to the comments
        for j in range(0, len(comments_json)):
            # avoid inserting meta data
            comments_json[j]['fields']['author'] = comments_author_json[j]['fields']
        # Strip meta data from each comment
        for comment in comments_json:
            comment['fields']['id'] = comment['pk']
        comments_json = [comment['fields'] for comment in comments_json]

        output = {
            "query": "comments",
            "count": pager.count,
            "size": len(posts),
            "comments": comments_json
        }

        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri

        return JsonResponse(output)

    def post_handler(request):
        # JSON post body of what you post to a posts' comemnts
        # POST to http://service/posts/{POST_ID}/comments
        output = {
            "query": "addComment",
        }
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
            new_comment.author = Author.objects.filter(
                id=comment_info['author']['id']).first()
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

    return Endpoint(request, Post.objects.filter(id=post_id), [
        Handler("POST", "application/json", post_handler),
        PagingHandler("GET", "application/json", get_handler)
    ]).resolve()


@login_required  # Local server usage only
def fetch_public_posts_from_nodes(request):
    """
    Fetches public posts from all the nodes available to the server

    Due to the nature of this API, getting deep pages may take a really long time as random access is not possible

    :param request:
    :return:
    """
    output = {
        'query': "getPosts",
        'page': 0,
        'size': 10,
        'count': 0,
        'posts': [],
        'errors': dict()
    }

    # First we need to find out what page of results they are looking for, and how many
    try:
        output['page'] = int(request.GET.get('page', '0'))
        output['size'] = int(request.GET.get('size', '10'))
    except Exception as e:
        output['errors'] = str(e)
        # Bad request with invalid parameters
        return JsonResponse(output, status=400)

    # Then we need to track the pages of each Node, pull their results and merge them together
    class NodePager:
        def __init__(self, api_location, username, password, page, size):
            self.api_location = api_location
            self.username = username
            self.password = password
            self.page = page
            self.size = size
            self.results = None

        def fetch_page(self):
            """
            Gets the current page of public posts from the node. Returns empty list if no results or error.
            Caches the results so it will only fetch the page if the page has not already been fetched
            """
            if self.results is not None:
                return self.results

            response = requests.get(self.api_location,
                                    auth=(self.username, self.password),
                                    headers={
                                        'Accept': 'application/json'
                                    },
                                    params={
                                        'size': self.size,
                                        'page': self.page
                                    })
            if response.status_code != 200:
                self.results = []
            else:
                try:
                    res_json = response.json()
                    self.results = res_json['posts']
                except:
                    self.results = []
            return self.results

        def next_page(self):
            self.page += 1
            self.results = None

    class NodeCollectionPager:
        """
        Manages a collection of node pagers, returning pages of their combined results
        """
        def __init__(self, size):
            self.size = size
            self.node_pagers = dict()
            for node in Node.objects.all():
                # Create a pager so we can handle paging through all the results
                self.node_pagers[node.foreign_server_hostname] = NodePager(node.get_safe_api_url('posts'),
                                                                           node.username_registered_on_foreign_server,
                                                                           node.password_registered_on_foreign_server,
                                                                           0,  # Always start on the first page, we have no other way to ensure all results are seen
                                                                           size)

        def get_page(self, page):
            """
            Gets the specified page by individually and sequentially querying each node and combining results until the
            desired page is reached. Thus getting deep pages should be avoided if possible.
            """
            current_page = 0
            current_results_queue = []
            while len(self.node_pagers) > 0 and len(current_results_queue) < ((page+1) * self.size):
                # make an array from the keys so that we can delete keys during the loop
                for node in [*self.node_pagers.keys()]:
                    pager = self.node_pagers[node]
                    pager_page = pager.fetch_page()
                    if len(pager_page) == 0:
                        # This node has exhausted it's pages
                        del self.node_pagers[node]
                    current_results_queue += pager_page
                    pager.next_page()


            return current_results_queue[page*self.size:(page+1)*self.size]


    manager = NodeCollectionPager(10)
    output['posts'] = manager.get_page(output['page'])

    return JsonResponse(output)







    # for node in Node.objects.all():
    #     # Get the url of the api
    #     api_url = node.get_safe_api_url('posts')
    #
    #     response = requests.get(api_url,
    #                             auth=(node.username_registered_on_foreign_server,
    #                                   node.password_registered_on_foreign_server),
    #                             headers={'Accept': 'application/json'})
    #     if response.status_code != 200:
    #         output['errors'][node.foreign_server_hostname] = f"Received response code {response.status_code} " \
    #                                                          f"at api endpoint: {api_url}"
    #         continue
    #
    #     try:
    #         json = response.json()
    #     except Exception as e:
    #         output['errors'][node.foreign_server_hostname] = f"During JSON decode got {e} for response like " \
    #                                                          f"'{response.content[:20]}...'"
    #         continue
    #
    #     for post in json['posts']:
    #         output['count'] += 1
    #         output['posts'].append(post)
    #         if output['count'] >= output['size']:
    #             break
    #
    #     if output['count'] >= output['size']:
    #         break

    return JsonResponse(output, status=200)

@login_required
def proxy_foreign_server_image(request, image_url):
    """
    For markdown posts that contain images in them, we need to proxy the request through our server.
    This is because foreign servers require authorization. Requires an image url, which should NOT include the protocol

    If the url passed is not for a specific node we have connections for, it will be returned with the https protocol
    appended so that other img urls are not affected and resolve as normal.
    """
    image_url_parts = image_url.split('/')
    credentials = None
    try:
        node = Node.objects.get(foreign_server_hostname=image_url_parts[0])
        credentials = (node.username_registered_on_foreign_server, node.password_registered_on_foreign_server)
    except Node.DoesNotExist as e:
        # This url is not for a node that we have credentials for, we have to return the url as is
        return HttpResponse('https://' + image_url)

    request_args = dict()
    if credentials is not None:
        request_args['auth'] = credentials
    # Make a request to the url, and pass in the credentials if they exist
    response = requests.get('http://' + image_url, *request_args)
    if response.status_code != 200:
        # Return the original server response as an HTTP response
        return HttpResponse(f'The server failed to deliver a valid response. The response was {response.content}', status=response.status_code)

    try:
        # Decode the json response to get the post
        post = response.json()['posts'][0]
    except Exception as e:
        return HttpResponse(f'The foreign server responded, but the post returned was invalid: {e}', status=500)

    # Otherwise read the image data and return the image
    uri = ("data:" + post['contentType'] + ", " + post['content'])

    return HttpResponse(uri, content_type=response.headers['Content-Type'])