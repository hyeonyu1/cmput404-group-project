from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from users.models import Author
from friendship.models import Friend
from posts.models import Post, Category
from comments.models import Comment
from django.db.models import Q


import json

from social_distribution.utils.endpoint_utils import Endpoint, Handler

# Ida Hou
# return a list of author id that are currently stored in database and
# are not friend with current author
def view_list_of_available_authors_to_befriend(request, author_id):
    if request.method != 'GET':
        return HttpResponse("Method not Allowed", status=405)
    if not Author.objects.filter(id=author_id).exists():
        return HttpResponse("No Author Record", status=404)
    authors_on_record = Author.objects.filter(~Q(id=author_id)).filter(
        is_active=1).filter(is_superuser=0)
    # compose full url of author id
    host = request.get_host()
    if request.is_secure():
        host = "https://" + host
    else:
        host = "http://" + host

    author_id = host + "/author/" + str(author_id)
    response_data = {}
    response_data["available_authors_to_befriend"] = []
    for each in authors_on_record:
        response_data["available_authors_to_befriend"].append(each.uid)
    if not Friend.objects.filter(author_id=author_id).exists():

        return JsonResponse(response_data)

    # need to make sure that existing_friends be a subset of authors_on_record
    # which brings up a question that where should we store foreign author? In the Author table?
    # or should we make another "Foreign_Author" table ?
    # TODO
    existing_friends = Friend.objects.filter(author_id=author_id)

    return JsonResponse(response_data)


# Ida Hou
# service/author/unfriend endpoint handler
# post request body
# {
#  author_id :http://127.0.0.1:8000/author/019fcd68-9224-4d1d-8dd3-e6e865451a31
#  friend_id : http://127.0.0.1:8000/author/019fcd68-9224-4d1d-8dd3-e6e865451a31
#
# }
def unfriend(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        body = json.loads(body)
        author_id = body.get("author_id", None)
        friend_id = body.get("friend_id", None)
        if not author_id or not friend_id:
            # Unprocessable Entity
            return HttpResponse("post request body missing fields", status=422)
        if Friend.objects.filter(author_id=author_id).filter(friend_id=friend_id).exists():
            Friend.objects.filter(author_id=author_id).filter(
                friend_id=friend_id).delete()
        return HttpResponse("Unfriended !", status=200)

    return HttpResponse("Method Not Allowed", status=405)
# handler for endpoint: http://service/author/<str:author_id>/update
# post body data requirement
# require a json objects with following fields:
# first_name, last_name, email, bio, github, display_name, delete
# allow authors delete themselves (delete  = True if to be deleted)
# if no changes to above field, original values should be passed
# username, uid, id, url, host of author can't be changed


def update_author_profile(request, author_id):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)
    if not Author.objects.filter(id=author_id).exists():
        return HttpResponse("Author Does not Exist", status=404)
    # unpack post body data
    body = request.body.decode('utf-8')
    body = json.loads(body)
    delete = body.get('delete', None)
    if delete is None:
        return HttpResponse("Post body missing fields: delete", status=404)

    first_name = body.get('first_name', None)
    if first_name is None:
        return HttpResponse("Post body missing fields: first_name", status=404)

    last_name = body.get('last_name', None)
    if last_name is None:
        return HttpResponse("Post body missing fields: last_name", status=404)

    email = body.get('email', None)
    if email is None:
        return HttpResponse("Post body missing fields: email", status=404)

    bio = body.get('bio', None)
    if bio is None:
        return HttpResponse("Post body missing fields: bio", status=404)

    github = body.get('github', None)
    if github is None:
        return HttpResponse("Post body missing fields: github", status=404)

    display_name = body.get('display_name', None)
    if display_name is None:
        return HttpResponse("Post body missing fields: display_name", status=404)

    if delete:
        author_to_be_deleted = Author.objects.get(
            pk=author_id)
        author_to_be_deleted.delete()
    else:
        obj, created = Author.objects.update_or_create(
            id=author_id,
            defaults={'first_name': first_name, 'last_name': last_name,
                      'email': email, 'bio': bio, 'github': github,
                      'display_name': display_name},
        )

    return HttpResponse("Author successfully updated", status=200)


# Ida Hou
# service/author/{author_id} endpoint handler
def retrieve_author_profile(request, author_id):
    if request.method == 'GET':

        author = get_object_or_404(Author, id=author_id)
        response_data = {}
        response_data['id'] = author.uid
        response_data['host'] = author.host
        response_data['displayName'] = author.display_name
        response_data['friends'] = []
        # if current user has friends
        if Friend.objects.filter(author_id=author.uid).exists():
            # get friend id from Friend table
            friends = Friend.objects.filter(
                author_id=author.uid)
            # retrieve full information from Author table (local Author only, foreign friends need send http request to retrieve full information)
            friends_full_info = Author.objects.filter(
                uid__in=[friend.friend_id for friend in friends])
            # compose response data
            for each in friends_full_info:
                entry = {}
                entry['id'] = each.uid
                entry['host'] = each.host
                entry['displayName'] = each.display_name
                entry['url'] = each.url
                response_data['friends'].append(entry)
        # add optional information of current user
        response_data['github'] = author.github
        response_data['firstName'] = author.first_name
        response_data['lastName'] = author.last_name
        response_data['email'] = author.email
        response_data['bio'] = author.bio
        return JsonResponse(response_data)

    return HttpResponse("You can only GET the URL", status=405)


def post_creation_and_retrival_to_curr_auth_user(request):
    """
    Endpoint handler for service/author/posts
    POST is for creating a new post using the currently authenticated user
    GET is for retrieving posts visible to currently authenticated user
    :param request:
    :return:
    """
    def create_new_post(request):
        # POST to http://service/author/posts
        # Create a post to the currently authenticated user
        # First get the information out of the request body
        body = request.body.decode('utf-8')
        body = json.loads(body)
        post = body['post']
        author = post['author']
        comments = post['comments']
        categories = post['categories']
        visible_to = post['visibleTo']

        new_post = Post()

        # new_post.id = post['id']                  #: "de305d54-75b4-431b-adb2-eb6b9e546013",
        new_post.title       = post['title']        #: "A post title about a post about web dev",
        new_post.source      = post['source']       #: "http://lastplaceigotthisfrom.com/posts/yyyyy"
        new_post.origin      = post['origin']       #: "http://whereitcamefrom.com/posts/zzzzz"
        new_post.description = post['description']  # : "This post discusses stuff -- brief",
        new_post.contentType = post['contentType']  # : "text/plain",
        new_post.content     = post['content']      #: "stuffs",
        new_post.author      = request.user         # the authenticated user
        # Categories added after new post is saved
        new_post.count       = post['count']        #: 1023,
        new_post.size        = post['size']         #: 50,
        new_post.next        = post['next']         #: "http://service/posts/{post_id}/comments",

        # @todo allow adding comments to new post
        # new_post.comments = post['comments']  #: LIST OF COMMENT,


        new_post.published = post['published']  #: "2015-03-09T13:07:04+00:00"
        new_post.visibility = post['visibility']  #: "PUBLIC",

        # @todo allow setting visibility of new post
        # new_post.visibleTo = post['visibleTo']  #: LIST,

        new_post.unlisted = post['unlisted']  #: true
        new_post.save()

        for category in categories:
            cat_object = None
            try:
                cat_object = Category.objects.get(name=category)  # Try connecting to existing categories
            except Category.DoesNotExist as e:
                cat_object = Category.objects.create(name=category)  # Create one if not
            new_post.categories.add(cat_object)    #: LIST,

        # for key in body.keys():
        #     print(f'{key}: {body[key]}')

        return JsonResponse({
            "query": "addPost",
            "success": True,
            "message": "Post Added"
        })

    return Endpoint(request,None,[
        Handler("POST", "application/json", create_new_post)
    ]).resolve()

    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        # retrive posts that are visible to the currently authenticated user
        # GET from http://service/author/posts
        return HttpResponse("<h1>http://service/author/posts GET</h1>")

    return None

def post_edit_and_delete(request, post_id):
    pass

# http://service/author/{AUTHOR_ID}/posts
# (all posts made by {AUTHOR_ID} visible to the currently authenticated user)


def retrieve_posts_of_author_id_visible_to_current_auth_user(request, author_id):
    return HttpResponse("<h1>http://service/author/{}/posts GET</h1>".format(author_id))

# Ida Hou


def friend_checking_and_retrieval_of_author_id(request, author_id):
    # compose author id
    host = request.get_host()
    if request.is_secure():
        host = "https://" + host
    else:
        host = "http://" + host

    author_id = host + "/author/" + str(author_id)

    if request.method == 'POST':
        # ask a service if anyone in the list is a friend
        # POST to http://service/author/<authorid>/friends
        body_unicode = str(request.body, 'utf-8')
        body = json.loads(body_unicode)
        potential_friends = body.get("authors", None)
        if not potential_friends:
            return HttpResponse("Post body missing fields", status=404)

        response_data = {}
        response_data["query"] = "friends"
        response_data["author"] = author_id
        response_data["authors"] = []
        if Friend.objects.filter(author_id=author_id).exists():
            for potential_friend in potential_friends:
                if Friend.objects.filter(author_id=author_id).filter(friend_id=potential_friend).exists():
                    response_data["authors"].append(potential_friend)

        return JsonResponse(response_data)
    elif request.method == 'GET':
        # a reponse if friends or not
        # ask a service GET http://service/author/<authorid>/friends/
        # compose response data
        response_data = {}
        response_data['query'] = "friends"
        response_data['authors'] = []

        if Friend.objects.filter(author_id=author_id).exists():
            # get friend id from Friend table
            friends = Friend.objects.filter(
                author_id=author_id)

            for friend in friends:
                response_data['authors'].append(friend.friend_id)
        return JsonResponse(response_data)
    else:
        HttpResponse("You can only GET or POST to the URL", status=405)

# Ida Hou
# Ask if 2 authors are friends
# GET http://service/author/<authorid>/friends/<authorid2>


def check_if_two_authors_are_friends(request, author1_id, author2_id):
    if request.method == 'GET':
        # compose author id from author uid
        host = request.get_host()
        if request.is_secure():
            host = "https://" + host
        else:
            host = "http://" + host

        author1_id = host + "/author/" + str(author1_id)
        author2_id = host + "/author/" + str(author2_id)
        # compose response data
        response_data = {}
        response_data["query"] = "friends"
        response_data["authors"] = [author1_id, author2_id]
        # query friend table for friendship information
        if Friend.objects.filter(author_id=author1_id).filter(friend_id=author2_id).exists():
            response_data["friends"] = True
        else:
            response_data["friends"] = False
        # add optional information of current user

        return JsonResponse(response_data)

    return HttpResponse("You can only GET the URL", status=405)


def post_creation_page(request):
    return HttpResponse("Not Implemented", status=404)
