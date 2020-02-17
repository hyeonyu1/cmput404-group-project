from django.shortcuts import render
from django.http import HttpResponse
from posts.models import Post
from authors.models import Author
from comments.models import Comment

import json
# retrieve an author's profile
#http://service/author/author_id
def retrieve_author_profile(request, author_id):
    return HttpResponse("http://service/author/author_id")

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
        new_post.title = post['title']             #: "A post title about a post about web dev",
        new_post.source = post['source']           #: "http://lastplaceigotthisfrom.com/posts/yyyyy",
        new_post.origin = post['origin']           #: "http://whereitcamefrom.com/posts/zzzzz",
        new_post.description = post['description'] #: "This post discusses stuff -- brief",
        new_post.contentType = post['contentType'] #: "text/plain",
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
        new_post.next = post['next']               #: "http://service/posts/{post_id}/comments",

        # @todo allow adding comments to new post
        # new_post.comments = post['comments']       #: LIST OF COMMENT,

        new_post.published = post['published']     #: "2015-03-09T13:07:04+00:00",
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



