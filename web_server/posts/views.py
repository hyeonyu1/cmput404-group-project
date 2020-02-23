from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Post

def __handle_api_request(request, methods):
    """
    Handle an API request, the methods dictionary should link methods to a function that will handle that method
    on this endpoint. This function automatically handles server error responses.
    :param request: the django request object to handle
    :param methods: the methods dictionary with methods as keys and handler functions as values
        the handler must return an HttpResponse (or a subclass, such as JsonResponse)

        Preconditions:
        Keys MUST be strings in all caps e.g. "GET" or "POST"
        Handlers must take a django request object as their first argument
    :return: HttpResponse
    """
    # Check if this method is supported
    if request.method not in methods:
        response = HttpResponse(f"Attempt to request endpoint using '{request.method}' method, "
                                f"but only one of methods in '{list(methods.keys())}' allowed.",
                                status=405)
        response["Allow"] = ", ".join(methods.keys())
        return response

    # Check if this method can produce the requested content type
    # @todo is it possible that Accept header might be comma delineated list? What should the behaviour be in this case?
    if request.headers['Accept'] not in methods[request.method]:
        return HttpResponse(f"Server unable to produce content of type {request.headers['Accept']}. "
                            f"Available content types one of {list(methods[request.method].keys())}.",
                            status=406)

    # Attempt to fulfill the request using the handler
    try:
        response = methods[request.method][request.headers['Accept']](request)
        if type(response) == HttpResponse:
            return response
        else:
            raise Exception("Response handler unable to produce HttpResponse object")
    except Exception as e:
        return HttpResponse(f"The server failed to handle your request. Cause Hint: {e.args[0]}", status=500)

# retrieve all posts marked as public on the server
def retrieve_all_public_posts_on_local_server(request):
    """
    For endpoint http://service/posts
    Retrieves all public posts located on the server
    Methods: GET
    :param request: should specify Accepted content-type, default is HTML
    :returns: application/json | text/html
    """
    def json_handler(req):
        posts = Post.objects.filter(visibility="PUBLIC")
        return JsonResponse(posts)

    def html_handler(req):
        posts = Post.objects.filter(visibility="PUBLIC")
        html = ""
        for post in posts:
            html += f"<p>{post.__str__()}</p>"

        return HttpResponse(html)

    return __handle_api_request(request, {
        "GET": {
            "application/json": json_handler,
            "text/html": html_handler
        }
    })
    # Determine desired output
    # requested_content_type = request.headers['accept']
    # if requested_content_type == 'application/json':
    #     pass
    # elif requested_content_type == 'text/html':
    #     pass
    # else:
    #     pass
    #
    # return HttpResponse("<h1>http://service/posts</h1>")

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
    