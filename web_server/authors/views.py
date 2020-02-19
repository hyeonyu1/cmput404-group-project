
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from users.models import Author
from friendship.models import Friend
from posts.models import Post
from comments.models import Comment
import json


# Author: Ida Hou
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
    if request.method == 'POST':
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
        #: "A post title about a post about web dev",
        new_post.title = post['title']
        #: "http://lastplaceigotthisfrom.com/posts/yyyyy",
        new_post.source = post['source']
        #: "http://whereitcamefrom.com/posts/zzzzz",
        new_post.origin = post['origin']
        # : "This post discusses stuff -- brief",
        new_post.description = post['description']
        new_post.contentType = post['contentType']  # : "text/plain",
        new_post.content = post['content']         #: "stuffs",

        # Create author object
        # @todo This adds the post to the first author in the db, must get the author information from
        # the authenticated user
        author = Author.objects.all().first()
        new_post.author = author                #: DICT,

        # @todo allow adding categories to new post
        # new_post.categories = post['categories']   #: LIST,

        new_post.count = post['count']             #: 1023,
        new_post.size = post['size']               #: 50,
        #: "http://service/posts/{post_id}/comments",
        new_post.next = post['next']

        # @todo allow adding comments to new post
        # new_post.comments = post['comments']       #: LIST OF COMMENT,

        #: "2015-03-09T13:07:04+00:00",
        new_post.published = post['published']
        new_post.visibility = post['visibility']   #: "PUBLIC",

        # @todo allow setting visibility of new post
        # new_post.visibleTo = post['visibleTo']     #: LIST,

        new_post.unlisted = post['unlisted']       #: true

        new_post.save()

        # for key in body.keys():
        #     print(f'{key}: {body[key]}')

        return HttpResponse("<h1>http://service/author/posts POST</h1>")
    elif request.method == 'GET':
        # retrive posts that are visible to the currently authenticated user
        # GET from http://service/author/posts
        return HttpResponse("<h1>http://service/author/posts GET</h1>")

    return None

# http://service/author/{AUTHOR_ID}/posts
# (all posts made by {AUTHOR_ID} visible to the currently authenticated user)


def retrieve_posts_of_author_id_visible_to_current_auth_user(request, author_id):
    return HttpResponse("<h1>http://service/author/{}/posts GET</h1>".format(author_id))

# Author: Ida Hou


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
        potential_friends = body["authors"]

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

# Author: Ida Hou
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
