from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from friendship.models import FriendRequest, Friend, Follow
from nodes.models import Node
from django.contrib.auth.decorators import login_required
import json
import re
import base64
import requests
from social_distribution.utils.basic_auth import validate_remote_server_authentication
from urllib.parse import quote
url_regex = re.compile(r"(http(s?))?://")

# author: Ida Hou
# http://service/friendrequest/handle endpoint handler
# POST requests accepts the friend request
# DELETE requests rejects the friend request
# requires same request body content as http://service/friendrequest

# internal endpoint


def handle_friend_request(request):
    # handle friend request acception
    if request.method != "POST" and request.method != "DELETE":
        return HttpResponse("Method not Allowed", status=405)

    body = request.body.decode('utf-8')
    body = json.loads(body)
    from_id = body.get("author", {}).get("id", None)
    from_host = body.get("author", {}).get("host", None)

    to_id = body.get("friend", {}).get("id", None)
    to_host = body.get("friend", {}).get("host", None)
    if not from_id or not to_id or not from_host or not to_host:
        # Unprocessable Entity
        return HttpResponse("post request body missing fields", status=422)

    # strip protocol
    from_id = url_regex.sub('', from_id)
    to_id = url_regex.sub('', to_id)
    from_host = url_regex.sub('', from_host).rstrip("/")
    to_host = url_regex.sub('', to_host).rstrip("/")
    if request.method == 'POST':

        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():

            # delete the entry in FriendRequest
            FriendRequest.objects.filter(
                from_id=from_id).filter(to_id=to_id).delete()

            if Friend.objects.filter(author_id=from_id).filter(friend_id=to_id).exists():
                return HttpResponse("Friendship already exists!", status=409)
            # if B accepts A's friend request, then B and A are friends
            new_friend = Friend(author_id=from_id, friend_id=to_id)
            new_friend.save()
            new_friend = Friend(author_id=to_id, friend_id=from_id)
            new_friend.save()
            # if request is from remote author
            # we need to send friend request back as "confirmation"
            if from_host != request.get_host():

                return send_friend_request_to_foreign_friend(body.get("author"), body.get("friend"), from_host)

            return HttpResponse("Friend successfully added", status=201)
        else:
            return HttpResponse("No such friend request", status=404)

    # handle friend request rejection
    elif request.method == 'DELETE':
        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():
            # delete the entry in FriendRequest
            FriendRequest.objects.filter(
                from_id=from_id).filter(to_id=to_id).delete()
            return HttpResponse("Friend request successfully rejected", status=200)
        else:
            return HttpResponse("No such friend request", status=404)


def send_friend_request_to_foreign_friend(friend_info, author_info, foreign_server):

    if not Node.objects.filter(foreign_server_hostname=foreign_server).exists():
        return HttpResponse("Not Authenticated with Remote Server", status=401)
    node = Node.objects.get(foreign_server_hostname=foreign_server)

    data = {}
    data["query"] = "friendrequest"
    data["author"] = author_info
    data["friend"] = friend_info
    json_data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print(data)
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    url = "http://{}/friendrequest".format(
        node.foreign_server_api_location.rstrip("/"))
    if node.append_slash:
        url += "/"
    response = requests.post(
        url, headers=headers, auth=(node.username_registered_on_foreign_server, node.password_registered_on_foreign_server), data=json_data)

    return HttpResponse(response.text, status=response.status_code)


# author: Ida Hou
# to make a friend request, POST to http://service/friendrequest
@validate_remote_server_authentication()
def send_friend_request(request):
    # Make a friend request
    if request.method == 'POST':
        # parse request body
        body = request.body.decode('utf-8')
        body = json.loads(body)
        from_id = body.get("author", {}).get("id", None)
        from_host = body.get("author", {}).get("host", None)
        to_id = body.get("friend", {}).get("id", None)
        to_host = body.get("friend", {}).get("host", None)
        if not from_id or not to_id or not from_host or not to_host:
            # Unprocessable Entity
            return HttpResponse("post request body missing fields", status=422)
        # strip protocol
        from_id = url_regex.sub('', from_id)
        to_id = url_regex.sub('', to_id)

        # if friend request already existed
        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():

            return HttpResponse("Friend Request Already exists", status=409)
        # strip protocol for hostname
        from_host = url_regex.sub('', from_host).rstrip("/")
        to_host = url_regex.sub('', to_host).rstrip("/")
        # if friendship already existed
        if Friend.objects.filter(author_id=from_id).filter(friend_id=to_id).exists():
            return HttpResponse("Friendship already exists!", status=409)
        # handle outgoing request from local author
        if from_host == request.get_host():
            new_request = FriendRequest(from_id=from_id, to_id=to_id)
            new_request.save()
            # friend request from local author to local author
            if to_host != request.get_host():
                # retrieve basic auth credential from Node table
                return send_friend_request_to_foreign_friend(body.get("friend"), body.get("author"), to_host)
            return HttpResponse("Friend Request Successfully sent", status=201)
        # handle incoming friend request from remote server
        else:
            # now foreign author B is sending local author A an FriendRequest, However, on our local system
            # there is already FriendRequest sent from A to B.
            # that's means that B accepted A's request and B is sending A "confirmation request"
            # this case, we should just delete FriendRequest entry from A to B and friend A and B

            if FriendRequest.objects.filter(from_id=to_id).filter(to_id=from_id).exists():
                FriendRequest.objects.filter(
                    from_id=to_id).filter(to_id=from_id).delete()
                new_friend = Friend(author_id=from_id, friend_id=to_id)
                new_friend.save()
                new_friend = Friend(author_id=to_id, friend_id=from_id)
                new_friend.save()

                return HttpResponse("{} and {} become friend".format(from_id, to_id), status=201)
            # this is a pure friend request from remote author B to local author A -> create an entry in FriendRequest table
            # pending for local author A to handle
            else:
                new_request = FriendRequest(from_id=from_id, to_id=to_id)
                new_request.save()
                return HttpResponse("Friend Request Successfully sent", status=201)

        return HttpResponse("Friend Request Successfully sent", status=201)

    return HttpResponse("You can only POST to the URL", status=405)

# author: Ida Hou
# http://service/friendrequest/{author_id}

# internal endpoints


def retrieve_friend_request_of_author_id(request, author_id):
    if request.method == "GET":
        # construct full url of author id

        host = request.get_host()
        author_id = host + "/author/" + str(author_id)
        invalidate_friend_requests(author_id)
        response_data = {}
        response_data["query"] = "retrieve_friend_requests"
        response_data["author"] = author_id
        # a list of author ids who send friend request to current author_id
        response_data["request"] = []
        if FriendRequest.objects.filter(to_id=author_id).exists():
            # get friend id from Friend table
            requests = FriendRequest.objects.filter(
                to_id=author_id)
            for request in requests:
                response_data["request"].append(request.from_id)
        return JsonResponse(response_data)

    return HttpResponse("You can only GET the URL", status=405)

# author : Ida Hou
# invalidate outgoing friend requests of an author by calling foreign servers'
# https://service/authorid/friend/authorid2 endpoint


def invalidate_friend_requests(author_id):
    # if there are no outgoing friendrequests -> do nothing
    if not FriendRequest.objects.filter(from_id=author_id).exists():
        return

    author_id = url_regex.sub('', author_id)
    author_id = author_id.rstrip("/")
    friend_requests = FriendRequest.objects.filter(from_id=author_id)

    hostname = author_id.split("/")[0]
    for request in friend_requests:
        to_host = request.to_id.split("/")[0]
        to_author_id = request.to_id.split("/")[2]

        # foreign requests -> call foreign server endpoint to validate
        print("\n")
        print("\n")
        print("\n")
        print("\n")
        print("\n")
        print(hostname, to_host, to_author_id)
        # testing-mandala-2.herokuapp.com testing-mandala.herokuapp.com ea9c2f9a980d4fe18a2988770417be19
        print("\n")
        print("\n")
        print("\n")
        print("\n")
        if hostname != to_host:
            if Node.objects.filter(pk=to_host).exists():
                node = Node.objects.get(foreign_server_hostname=to_host)
                # quoted_author_id = quote(
                #     author_id, safe='~()*!.\'')
                headers = {"Content-Type: application/json",
                           "Accept: application/json"}
                url = "https://{}/author/{}/friends/{}".format(
                    node.foreign_server_api_location.rstrip("/"), to_author_id, author_id)
                res = requests.get(url, headers=headers, auth=(
                    node.username_registered_on_foreign_server, node.password_registered_on_foreign_server))
                if res.status_code >= 200 and res.status_code < 300:
                    res = res.josn()
                    print("\n")
                    print("\n")
                    print("\n")
                    print("\n")
                    print("\n")
                    print(res)
                    print("\n")
                    print("\n")
                    print("\n")
                    print("\n")
                    print("\n")
                    # if they are friends
                    if res["friends"]:
                        if FriendRequest.objects.filter(from_id=author_id).filter(to_id=request.to_id).exists():
                            FriendRequest.objects.filter(from_id=author_id).filter(
                                to_id=request.to_id).delete()
                            if not Friend.objects.filter(author_id=author_id).filter(friend_id=request.to_id).exists():
                                new_friend = Friend(
                                    author_id=author_id, friend_id=request.to_id)
                                new_friend.save()
                                new_friend = Friend(
                                    author_id=request.to_id, friend_id=author_id)
                                new_friend.save()
