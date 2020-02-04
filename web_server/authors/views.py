from django.shortcuts import render
from django.http import HttpResponse
# retrieve an author's profile
#http://service/author/author_id
def retrieve_author_profile(request, author_id):
    return HttpResponse("http://service/author/author_id")

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



