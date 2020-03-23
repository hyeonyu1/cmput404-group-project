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




# FOAF verification involves the 3 hosts of the 3 friends A->B->C
# assuming A B C reside on different hosts.
# and in the same server
def FOAF_verification(request, author_id):

    auth_user = request.user.uid

    # nodes = [request.get_host()]
    nodes = []
    for node in Node.objects.all():
        nodes.append(node.foreign_server_hostname)
    print("nodes = ", nodes)

    response = requests.get(
        "http://{}/author/{}/posts".format("127.0.0.1:5000", "39345efe95024a8bbe688dc904d906e5"),
        auth=("user@user.com", "user_password")
    )
    print(response.text)

    response = requests.get(
            "http://{}/author/{}/friends".format("127.0.0.1:5000", "127.0.0.1:5000/author/39345efe95024a8bbe688dc904d906e5"),
            auth=("user@user.com", "user_password")
        )
        # this should be json of all friend relationship
    print(response.text)
    # friends = Friend.objects.all()
    # for i in friends:
    #     print(i.friend_id)
    #
    # response = requests.get(
    #     "http://127.0.0.1:5000/author/39345efe95024a8bbe688dc904d906e5/friends",
    #     auth=("user@user.com", "user_password")
    # )
    # # this should be json of all friend relationship
    # print(response.text)
    #
    # for node in nodes:
    #
    #     #deals with friendship
    #     if Friend.objects.filter(author_id=auth_user).filter(friend_id=node + "/author/" + author_id).exists():
    #         return True
    #
    #     # deals with FOAF
    #     print(node)
    #     response = requests.get(
    #         "http://{}/author/{}/friends".format(node, "127.0.0.1:5000/author/39345efe95024a8bbe688dc904d906e5"),
    #         auth=("user@user.com", "user_password")
    #     )
    #     # this should be json of all friend relationship
    #     print(response.text)
    #     # gets all of author's friend
    #     author_friends = Friend.objects.filter(author_id=auth_user)
    #     # for friend_of_author in author_friends:
    #     #     # getting friends of authors friend
    #     #     friend_of_authors_friend = Friend.objects.filter(
    #     #         author_id=friend_of_author.friend_id).values('friend_id')
    #     #     for friend in friend_of_authors_friend:
    #     #         print(friend)
    #     #         if request.user.uid == friend['friend_id']:
    #     #             print("friends of friends")
    #     #             return True
    #     #         else:
    #     #             print("here")
    #     #             friends_uuid = friend['friend_id']
    #     #             if friends_uuid[-1] == "/":
    #     #                 friends_uuid = friends_uuid[:-1]
    #     #             friends_uuid = friends_uuid.split("/")[-1]
    #     #             print("friends_uuid", friends_uuid)
    #     #             print(node)
    #     #             response = requests.get(
    #     #                 "http://{}/author/{}/friends".format(node, friends_uuid),
    #     #                 auth=(node.username_registered_on_foreign_server, node.password_registered_on_foreign_server)
    #     #             )
    #     #             # this should be json of all friend relationship
    #     #             print(response)
    #     #             for remote_friend in response:
    #     #                 print(remote_friend)
    #
    #
    #
    #
    #
    #
    #

    return False
