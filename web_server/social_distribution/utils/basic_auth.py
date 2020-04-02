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
    deny_response = ""
    request.remote_server_authenticated = False

    # If the user is already authenticated on the local server, then we are fine, and we let them proceed
    if test_func(request.user):
        # Already logged in, just return the view.
        return view(request, *args, **kwargs)
    else:
        deny_response += "You were not logged in to the local server."

    # Otherwise, return view only when foreign servers are pre-authorized and the provided credentials match
    # what's on record in Node table
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We only support basic authentication for now.
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(
                    auth[1]).decode('utf-8').rsplit(':', 1)

                # This code would allow credentials of local authors to remotely authorize,
                # This use case is not supported for now

                # for internal request, try to authenticate local Author
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        if test_func(request.user):
                            return view(request, *args, **kwargs)

                # Check if the credentials are valid for the host requesting them
                if Node.objects.all().filter(foreign_server_username=uname).exists():
                    entry = Node.objects.all().get(foreign_server_username=uname)

                    if check_password(passwd, entry.foreign_server_password):
                        request.remote_server_authenticated = True
                        return view(request, *args, **kwargs)
                    else:
                        deny_response += " The provided password for your server authentication was invalid"
                else:
                    deny_response += f" There was no registered node with username '{uname}'"
            else:
                deny_response += f" You sent authorization headers for type {auth[0].lower()}, the only supported type is 'basic'."
        else:
            deny_response += " You sent authorization headers that were improperly formatted."
    else:
        deny_response += " You did not send any other authorization headers."

    # Either they did not provide an authorization header or
    # credential provided is invalid. Send a 401
    # back to them to ask them to authenticate.
    response = HttpResponse(deny_response)
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

#############################################################################


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
