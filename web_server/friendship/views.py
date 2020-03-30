from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from friendship.models import FriendRequest, Friend, Follow
import json
import re
from nodes.models import Node
url_regex = re.compile(r"(http(s?))?://")
import requests
# author: Ida Hou
# http://service/friendrequest/handle endpoint handler
# POST requests accepts the friend request
# DELETE requests rejects the friend request
# requires same request body content as http://service/friendrequest


def handle_friend_request(request):
    # handle friend request acception
    if request.method != "POST" and request.method != "DELETE":
        return HttpResponse("Method not Allowed", status=405)

    body = request.body.decode('utf-8')
    body = json.loads(body)
    from_id = body.get("author", {}).get("id", None)
    to_id = body.get("friend", {}).get("id", None)
    if not from_id or not to_id:
        # Unprocessable Entity
        return HttpResponse("post request body missing fields", status=422)

    # strip protocol
    from_id = url_regex.sub('', from_id)
    to_id = url_regex.sub('', to_id)
    if request.method == 'POST':

        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():

            # delete the entry in FriendRequest
            FriendRequest.objects.filter(
                from_id=from_id).filter(to_id=to_id).delete()

            # if both way follows exist in Follow, real friendship established.
            # then remove both entries from Follow but add a row in Friend table
            if Follow.objects.filter(follower_id=to_id).filter(followee_id=from_id).exists():
                Follow.objects.filter(
                    follower_id=to_id).filter(followee_id=from_id).delete()
                new_friend = Friend(author_id=from_id, friend_id=to_id)
                new_friend.save()
                new_friend = Friend(author_id=to_id, friend_id=from_id)
                new_friend.save()
            else:
                new_follow = Follow(follower_id=from_id, followee_id=to_id)
                new_follow.save()

            return HttpResponse("Friend successfully added", status=200)
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


# author: Ida Hou
# to make a friend request, POST to http://service/friendrequest
def send_friend_request(request):
    # Make a friend request
    if request.method == 'POST':

        body = request.body.decode('utf-8')
        body = json.loads(body)
        from_id = body.get("author", {}).get("id", None)
        to_id = body.get("friend", {}).get("id", None)
        if not from_id or not to_id:
            # Unprocessable Entity
            return HttpResponse("post request body missing fields", status=422)
        from_id = url_regex.sub('', from_id)
        to_id = url_regex.sub('', to_id)
        # check duplication
        # could be friend request already existed
        # could be to_id already be followed by from_id
        # could be to_id already friended with from_id
        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():
            return HttpResponse("Friend Request Already exists", status=409)
        if Follow.objects.filter(follower_id=from_id).filter(followee_id=to_id).exists():
            return HttpResponse("{} Already Followed {}".format(from_id, to_id), status=409)
        if Friend.objects.filter(author_id=from_id).filter(friend_id=to_id).exists():
            return HttpResponse("{} Already Friended with {}".format(from_id, to_id), status=409)
        new_request = FriendRequest(from_id=from_id, to_id=to_id)
        new_request.save()

        return HttpResponse("Friend Request Successfully sent", status=200)

    return HttpResponse("You can only POST to the URL", status=405)

# author: Ida Hou
# http://service/friendrequest/{author_id}


def retrieve_friend_request_of_author_id(request, author_id):
    if request.method == "GET":
        # construct full url of author id

        host = request.get_host()
        author_id = host + "/author/" + str(author_id)
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


def FOAF_verification(request, author):

    auth_user = request.user.uid
    own_node = request.get_host()

    nodes = [own_node]
    for node in Node.objects.all():
        nodes.append(node.foreign_server_hostname)

    for node in nodes:

        # If the author is a friend of auth user return True
        if Friend.objects.filter(author_id=auth_user).filter(friend_id=author).exists():
            return True

        # not friends so check for FOAF
        else:
            # if the author is on the same host as auth user
            if node == own_node:
                author_friends = Friend.objects.filter(author_id=author)
                for friend in author_friends:
                    # getting the node of the friend
                    friend_node = friend.friend_id.split("/author/")[0]
                    friends_uuid = friend.friend_id.split("/author/")[-1]
                    # if friend of the author is on the same host as the auth user
                    # A -> A -> A
                    if friend_node == own_node:
                        # E.g Test <-> Lara <-> Bob
                        if Friend.objects.filter(author_id=auth_user).filter(friend_id=friend.friend_id).exists():
                            return True
                        else:
                            return False

                    # Since the friend is not on the same host as the auth user make a request to get friends from the other node
                    # A -> A -> B
                    else:
                        username = Node.objects.get(foreign_server_hostname=node).username_registered_on_foreign_server
                        password = Node.objects.get(foreign_server_hostname=node).password_registered_on_foreign_server
                        api = Node.objects.get(foreign_server_hostname=node).foreign_server_api_location
                        response = requests.get(
                            "http://{}/author/{}/friends".format(node, "{}/author/{}".format(api, author)),
                            auth=(username, password)
                        )
                        if response.status_code == 200:
                            friends_list = response.json()

                            for user in friends_list["authors"]:
                                if Friend.objects.filter(author_id=auth_user).filter(friend_id=user).exists():
                                    return True
                                else:
                                    return False

            # author's host is different from auth user
            else:
                username = Node.objects.get(foreign_server_hostname=node).username_registered_on_foreign_server
                password = Node.objects.get(foreign_server_hostname=node).password_registered_on_foreign_server
                api = Node.objects.get(foreign_server_hostname=node).foreign_server_api_location
                print(node, author, api)
                response = requests.get(
                    "http://{}/author/{}/friends".format(api, author),
                    auth=(username, password)
                )
                if response.status_code == 200:
                    friends_list = response.json()
                    for user in friends_list["authors"]:
                        # E.g Test <-> Lara <-> User
                        if Friend.objects.filter(author_id=auth_user).filter(friend_id=user).exists():
                            return True
                        else:
                            return False

    return False

