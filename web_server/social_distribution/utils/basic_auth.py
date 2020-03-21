#############################################################################
# The following code is a derivative work from the django-basic-authentication-decorator package
# Original Code: https://pypi.org/project/django-basic-authentication-decorator/
# Original License: BSD
# Package Maintainer: LeaChim
#############################################################################


import base64
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from nodes.models import Node
from django.contrib.auth.hashers import check_password

#############################################################################
#


def view_or_basicauth(view, request, test_func, realm="", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(
                    auth[1]).decode('utf-8').split(':', 1)
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        if test_func(request.user):
                            return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response


def handle_incoming_request_or_request(view, request, realm="", *args, **kwargs):
    """
    This is a helper function used by both 'validate_remote_server_authentication' and
    that does the nitty of determining if foreign servers are pre-authenticated. 
    Return the view if all goes well, otherwise respond with a 401.
    """

    # return view only when foreign servers are pre-authorized and the provided credentials match
    # what's on record in Node table
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        print(auth)
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(
                    auth[1]).decode('utf-8').rsplit(':', 1)
                print(uname, passwd)
                if Node.objects.all().filter(foreign_server_hostname=uname).exists():
                    entry = Node.objects.all().get(pk=uname)
                    if check_password(passwd, entry.foreign_server_password):
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # credential provided is invalid. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

#############################################################################
#


def validate_remote_server_authentication(realm=""):
    """
    A simple decorator that accepts incoming request only if the server that the request 
    is sent from is pre-authenticated. i.e: has an entry in Node table. Reject requests otherwise.

    If the header is present it is tested for basic authentication

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    Use is simple:

    @validate_remote_server_authentication()
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return handle_incoming_request_or_request(func, request,
                                                      realm, *args, **kwargs)
        return wrapper
    return view_decorator


def logged_in_or_basicauth(realm=""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth()
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated,
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
