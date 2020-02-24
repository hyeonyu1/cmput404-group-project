from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core.paginator import Paginator
from .models import Post

from urllib.parse import urlparse, urlunparse
from json import dumps

class Endpoint:
    """
    This function defines an endpoint for a request. Given the query that defines this endpoint,
    it will automatically paginate the results, and provide the list of objects to the handler.
    It determines which handler should handle the request based on the request headers.

    It also manages some basic errors that can arise when dealing with requests:
    Error 405 - there is no handler that accepts the method verb requested (e.g. GET or POST)
    Error 406 - there is no handler that produces the requested content (e.g. Accepts: text/html)
    """

    def __init__(self, request, query, handlers, default_page_size=10, max_page_size=50):
        """
        Create this endpoint with the specified handlers
        :param request: the HttpRequest object from Django
        :param query: An unresolved Django query (pagination will be applied automatically)
        :param handlers: A list of Handler objects
        :param default_page_size: the default number of results in a page,
            may be overridden by the query string in the request
        :param max_page_size: a hard maximum on the number of results in a page
        """
        self.request = request
        self.query = query
        self.handlers = handlers

        self.page_size = min(
            int(request.GET.get('size', default_page_size)),
            max_page_size
        )
        self.page = int(request.GET.get('page', 1))
        self.total_available_pages = None
        self.total_results = None

    def resolve(self):
        """
        Finds the most appropriate handler and uses that handler to respond to the request.
        Implicitly resolves the query to provide the data to the chosen handler.
        :return: HttpResponse from the handler
        """

    def _get_data_page(self):
        """
        Resolves the query and returns the data from the query
        :return: list of query results
        """
        pager = Paginator(self.query, self.page_size)
        self.total_available_pages = pager.num_pages
        self.total_results = pager.count
        return pager.get_page(self.page)

    def _get_pagination_uris(self):
        """
        Returns a tuple containing absolute uris to the next and previous page of results.
        Will return None instead of a uri if there is no valid next or previous page (e.g. first or last page)
        :return: (prev_page_uri, next_page_uri,)
        """
        # Page and size might not have been passed in to this request, so we need to build a pagination url
        # that includes these variables. However we cannot simply modify the request object, so we must
        # deconstruct, modify, and reconstruct the uri.

        # START STACKOVERFLOW DERIVATIVE CONTENT
        # This solution has been provided via StackOverflow, and the following code snippet is CC-BY-SA
        # Original Question: https://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
        # Question By: EvdB https://stackoverflow.com/users/5349/evdb
        # Answer By: Tom Christie https://stackoverflow.com/users/596689/tom-christie
        pagination_uri = self.request.build_absolute_uri()
        (scheme, netloc, path, params, query, fragment) = urlparse(pagination_uri)

        next_uri = None
        next_query_dict = QueryDict(query).copy()
        # We only set the next page if we are not on the last page
        if self.page < self.total_available_pages:
            next_query_dict['page'] = int(next_query_dict['page']) + 1 if "page" in next_query_dict else 2
            next_query = next_query_dict.urlencode()
            next_uri = urlunparse((scheme, netloc, path, params, next_query, fragment))

        prev_uri = None
        prev_query_dict = QueryDict(query).copy()
        # We only set the previous page if we are not on the first page
        if self.page > 1:
            prev_query_dict['page'] = int(prev_query_dict['page']) - 1
            prev_query = prev_query_dict.urlencode()
            prev_uri = urlunparse((scheme, netloc, path, params, prev_query, fragment))
        # END STACKOVERFLOW DERIVATIVE CONTENT

        return (prev_uri, next_uri)





class Handler:
    """
    Handles a request
    """
    def __init__(self, method, produces, handling_func):
        """
        Create the handler
        :param method: Which http verb this handler deals with (e.g. "GET" or "POST")
        :param produces: Which content type this handler produces (e.g. "text/html")
        :param handling_func: function used to handle the request.
            Should take the following arguments:
                results: the list of results from the query, may have been filtered by the Endpoint
                page: which page these results come from
                page_size: the number of results that was requested,
                    len(results) may not be the same if not enough results were available to be served.
                total_available: total number of results available across all pages
                total_pages_available: total number of pages of results
                next_page: absolute URI to the next page of results, maintains other query string parameters.
                    If this is the last page then this field will be None
                prev_page: absolute URI to the previous page of results, maintains other query string parameters.
                    If this is the first page then this field will be None
            And return:
                A valid HttpResponse object consistent with it's produces string
        """
        self.method = method
        self.produces = produces
        self.handler = handling_func

    def handle(self, results, page=None, page_size=None, total_available=None, total_pages_available=None, next_page=None, prev_page=None):
        # Attempt to fulfill the request using the handler
        try:
            response = self.handler(results, page, page_size, total_available, total_pages_available, next_page, prev_page)
            if issubclass(type(response), HttpResponse):
                return response
            else:
                raise Exception("Response handler unable to produce HttpResponse like object")
        except Exception as e:
            return HttpResponse(f"The endpoint was reached, but the handler threw an unrecoverable error. "
                                f"Cause Hint: {e}", status=500)

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
    accepted_content_types = request.headers['Accept'].split(',')
    accepted_type = None
    for content_type in accepted_content_types:
        # Find and serve the first acceptable type to the user
        # @todo do we need to do actual pattern matching for things like 'application/*'
        if content_type == '*/*' and len(methods) > 0:
            # The user will accept anything, serve the first available type on this method
            accepted_type = list(methods[request.method].keys())[0]
            break
        if content_type in methods[request.method]:
            accepted_type = content_type
            break

    if accepted_type is None:
        return HttpResponse(f"Server unable to produce content of type {accepted_type}. "
                            f"Available content types one of {list(methods[request.method].keys())}.",
                            status=406)

    # Attempt to fulfill the request using the handler
    try:
        response = methods[request.method][accepted_type](request)
        if issubclass(type(response), HttpResponse):
            return response
        else:
            raise Exception("Response handler unable to produce HttpResponse like object")
    except Exception as e:
        return HttpResponse(f"The server failed to handle your request. Cause Hint: {e}", status=500)

# retrieve all posts marked as public on the server
def retrieve_all_public_posts_on_local_server(request):
    """
    For endpoint http://service/posts
    Retrieves all public posts located on the server
    Methods: GET
    :param request: should specify Accepted content-type, default is HTML
    :returns: application/json | text/html
    """


    default_page_size = "10"
    max_page_size = 50
    def json_handler(req):
        # @todo: how to extract this pagination behavior so that other endpoints can use it automatically?
        page = int(req.GET.get('page', "1"))
        size = min(int(req.GET.get('size', default_page_size)), max_page_size)
        posts = Post.objects.filter(visibility="PUBLIC")
        pager = Paginator(posts, size)

        output = {
            "count": pager.count,
            "size": size,
            # @todo how to implement better serialization of posts in a general way?
            "posts": [
                {
                    "author": post.author.display_name,
                    "content": post.content
                } for post in pager.get_page(page)
            ]
        }

        pagination_uri = req.build_absolute_uri()
        # Page and size might not have been passed in to this request, so we need to build a pagination url
        # that includes these variables. However we cannot simply modify the request object, so we must
        # deconstruct, modify, and reconstruct the uri.

        # START STACKOVERFLOW DERIVATIVE CONTENT
        # This solution has been provided via StackOverflow, and the following code snippet is CC-BY-SA
        # Original Question: https://stackoverflow.com/questions/5755150/altering-one-query-parameter-in-a-url-django
        # Question By: EvdB https://stackoverflow.com/users/5349/evdb
        # Answer By: Tom Christie https://stackoverflow.com/users/596689/tom-christie
        (scheme, netloc, path, params, query, fragment) = urlparse(pagination_uri)

        next_query_dict = QueryDict(query).copy()
        # We only set the next page if we are not on the last page
        if page < pager.num_pages:
            next_query_dict['page'] = int(next_query_dict['page']) + 1 if page in next_query_dict else 2
            next_query = next_query_dict.urlencode()
            output['next'] = urlunparse((scheme, netloc, path, params, next_query, fragment))

        prev_query_dict = QueryDict(query).copy()
        # We only set the previous page if we are not on the first page
        if page > 1:
            prev_query_dict['page'] = int(prev_query_dict['page']) - 1  # if page in prev_query_dict else 1
            prev_query = prev_query_dict.urlencode()
            output['prev'] = urlunparse((scheme, netloc, path, params, prev_query, fragment))
        # END STACKOVERFLOW DERIVATIVE CONTENT

        return JsonResponse(output)

    def html_handler(req):
        # @todo add pagination behaviour once it can be extracted from other handler
        posts = Post.objects.filter(visibility="PUBLIC")
        html = ""
        for post in posts:
            html += f"<p>{post.__str__()}</p>"

        return HttpResponse(html)

    def json_handler(posts)


    endpoint = Endpoint(request,
                        Post.objects.filter(visibility="PUBLIC"),
                        [
                            Handler("GET", "application/json", json_handler),
                            Handler("GET", "text/html", html_handler)
                        ])

    return __handle_api_request(request, {
        "GET": {
            "application/json": json_handler,
            "text/html": html_handler
        }
    })

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
    