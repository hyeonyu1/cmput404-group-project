from django.shortcuts import render
from django.http import HttpResponse

# to make a friend request, POST to http://service/friendrequest
def send_friend_request(request):
    # Make a friend request
    return HttpResponse("POST to http://service/friendrequest")