from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from friendship.models import FriendRequest, Friend, Follow
import json
import re
url_regex = re.compile(r"(http(s?))?://")

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
        if FriendRequest.objects.filter(from_id=from_id).filter(to_id=to_id).exists():
            return HttpResponse("Friend Request Already exists", status=200)

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
