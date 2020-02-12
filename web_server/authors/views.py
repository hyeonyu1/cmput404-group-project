from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from users.models import Author
from friendship.models import Friend
from django.core import serializers

# retrieve an author's profile
# http://service/author/author_id

# {
#     "id": "http://service/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
#     "host": "http://127.0.0.1:5454/",
#     "displayName": "Lara",
#     "url": "http://127.0.0.1:5454/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
#     "friends": [
#         {
#           "id": "http://127.0.0.1:5454/author/8d919f29c12e8f97bcbbd34cc908f19ab9496989",
#           "host": "http://127.0.0.1:5454/",
#           "displayName": "Greg",
#           "url": "http://127.0.0.1:5454/author/8d919f29c12e8f97bcbbd34cc908f19ab9496989"
#         }
#     ],

#     # Optional attributes
#     "github": "http://github.com/lara",
#     "firstName": "Lara",
#     "lastName": "Smith",
#     "email": "lara@lara.com",
#     "bio": "Hi, I'm Lara"
# }


def retrieve_author_profile(request, author_id):
    if request.method == 'GET':

        author = get_object_or_404(Author, id=author_id)
        response_data = {}
        response_data['id'] = author.uid
        response_data['host'] = author.host
        response_data['displayName'] = author.display_name
        response_data['friends'] = []
        # if current user has friends
        if Friend.objects.filter(user_id=author.uid).exists():
            # get friend id from Friend table
            friends = Friend.objects.filter(
                user_id=author.uid)
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
        # Create a post to the currently authenticated user
        # POST to http://service/author/posts
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


def friend_checking_and_retrieval_of_author_id(request, author_id):
    if request.method == 'POST':
        # ask a service if anyone in the list is a friend
        # POST to http://service/author/<authorid>/friends
        return HttpResponse("POST to http://service/author/<authorid>/friends")
    elif request.method == 'GET':
        # a reponse if friends or not
        # ask a service GET http://service/author/<authorid>/friends/
        return HttpResponse("GET http://service/author/<authorid>/friends/")


# Ask if 2 authors are friends
# GET http://service/author/<authorid>/friends/<authorid2>
def check_if_two_authors_are_friends(request, author1_id, author2_id):

    return HttpResponse("GET http://service/author/id1/friends/id2")
