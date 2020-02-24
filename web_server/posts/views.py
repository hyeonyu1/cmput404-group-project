from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core.paginator import Paginator
from .models import Post

from urllib.parse import urlparse, urlunparse
from json import loads
from django.core import serializers


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
        self.pager = Paginator(self.query, self.page_size)

    def resolve(self):
        """
        Finds the most appropriate handler and uses that handler to respond to the request.
        Implicitly resolves the query to provide the data to the chosen handler.
        :return: HttpResponse from the handler
        """
        # Filter the list of handlers based on http verb method
        method_handlers = [handler for handler in self.handlers if handler.method == self.request.method]
        if len(method_handlers) == 0:
            supported_methods = set([handler.method for handler in self.handlers])
            response = HttpResponse(f"Attempt to request endpoint using '{self.request.method}' method, "
                                    f"but only one of methods in '{supported_methods}' allowed.",
                                    status=405)
            response["Allow"] = ", ".join(supported_methods)
            return response

        # Find out which response content types we can support on this method
        supported_content_types = [handler.produces for handler in method_handlers]

        # Find out which content type should be served to the user agent
        accepted_content_types = self.request.headers['Accept'].split(',')
        accepted_type = None
        for content_type in accepted_content_types:
            # Find and serve the first acceptable type to the user
            if len(supported_content_types) == 0:
                # We dont support any types
                break
            # @todo do we need to do actual pattern matching for things like 'application/*'
            if content_type == '*/*':
                # The user will accept anything, serve the first available type on this method
                accepted_type = supported_content_types[0]
                break
            if content_type in supported_content_types:
                accepted_type = content_type
                break

        if accepted_type is None:
            return HttpResponse(f"Server unable to produce content of type {accepted_type}. "
                                f"Available content types one of {supported_content_types}.",
                                status=406)

        # Filter method handlers based on the chosen content type, and choose the first one
        handler = [handler for handler in method_handlers if handler.produces == accepted_type][0]

        # Attempt to fulfill the request using the handler
        try:
            response = handler.handle(self.pager.get_page(self.page), self.pager, self._get_pagination_uris())
            if issubclass(type(response), HttpResponse):
                return response
            else:
                raise Exception("Response handler unable to produce HttpResponse like object")
        except Exception as e:
            return HttpResponse(f"The server failed to handle your request. Cause Hint: {e}", status=500)


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
        if self.page < self.pager.num_pages:
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

        return prev_uri, next_uri


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
                pager: A Paginator that has been loaded with the query to get information about pagination
                pagination_uris: A tuple of absolute_uris of form (previous_page, next_page).
                    If there is no previous or next page the uri should be None
            And return:
                A valid HttpResponse object consistent with it's produces string
        """
        self.method = method
        self.produces = produces
        self.handler = handling_func

    def handle(self, results, pager, pagination_uris):
        # Attempt to fulfill the request using the handler
        try:
            response = self.handler(results, pager, pagination_uris)
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
    def json_handler(posts, pager, pagination_uris):
        # Use Django's serializers to encode the posts as a python object
        json_posts = loads(serializers.serialize('json', posts))
        # But then filter because the format from the serializer contains meta data
        json_posts = [post['fields'] for post in json_posts]

        # @todo this serialization needs to expand the author field (rn it is only the UUID)
        # @todo this serialization needs to include a query to grab comments

        output = {
            "query": "posts",
            "count": pager.count,
            "size": len(posts),
            "posts": json_posts
        }
        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            output['prev'] = prev_uri
        if next_uri:
            output['next'] = next_uri

        return JsonResponse(output)

    def html_handler(posts, pager, pagination_uris):
        html = ""
        for post in posts:
            html += f"<p>{post.__str__()}</p>"
        (prev_uri, next_uri) = pagination_uris
        if prev_uri:
            html += f"<a href='{prev_uri}'>PREV PAGE</a>"
        if next_uri:
            html += f"<a href='{next_uri}'>NEXT PAGE</a>"

        return HttpResponse(html)


    endpoint = Endpoint(request,
                        Post.objects.filter(visibility="PUBLIC"),
                        [
                            Handler("GET", "text/html", html_handler),
                            Handler("GET", "application/json", json_handler)
                        ])

    return endpoint.resolve()

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
    