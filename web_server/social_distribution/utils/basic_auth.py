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


def handle_incoming_request_or_request(view, request, test_func, realm="", *args, **kwargs):
    """
    This is a helper function used by both 'validate_remote_server_authentication' and
    that does the nitty of determining if foreign servers are pre-authenticated. 
    Return the view if all goes well, otherwise respond with a 401.
    """
    print(request)
    # for request from local server, test if the Authhor is logged in
    if test_func(request.user):
        # Already logged in, just return the view.
        return view(request, *args, **kwargs)
    # return view only when foreign servers are pre-authorized and the provided credentials match
    # what's on record in Node table
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(
                    auth[1]).decode('utf-8').rsplit(':', 1)
                # for internal request, try to authenticate local Author
                user = authenticate(username=uname, password=passwd)

                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        if test_func(request.user):
                            return view(request, *args, **kwargs)
                # incoming requests from foreign server
                foreign_server_hostname = request.get_host()
                if Node.objects.all().filter(foreign_server_hostname=foreign_server_hostname).filter(foreign_server_username=uname).exists():
                    entry = Node.objects.all().get(pk=foreign_server_hostname)
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
                                                      lambda u: u.is_authenticated,
                                                      realm, *args, **kwargs)
        return wrapper
    return view_decorator
