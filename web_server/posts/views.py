from django.shortcuts import render
from django.http import HttpResponse
# retrieve all posts marked as public on the server
# http://service/posts
def retrieve_all_public_posts_on_local_server(request):
    
    return HttpResponse("<h1>http://service/posts</h1>")

# access to a single post with id = {POST_ID}
# http://service/posts/{POST_ID} 
def retrieve_single_post_with_id(request, post_id):
    #???????
    # POST to http://service/posts/{POST_ID} , sending the body
    if request.method == 'POST':
        return HttpResponse("<h1>http://service/posts/{} POST</h1>".format(post_id))
    # Get a single post
    elif request.method == 'GET':
        return HttpResponse("<h1>http://service/posts/{} GET</h1>".format(post_id))
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
    