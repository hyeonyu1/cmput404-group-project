from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib.auth import views as auth_views
from django.urls import reverse
from friendship.models import Friend
from nodes.models import Node
import requests
from users.models import Author


class CustomLogin(auth_views.LoginView):
    def form_valid(self, form):
        login(self.request, form.get_user())
        # set expiration of the current login session
        # a single login is alive for 10hrs
        self.request.session.set_expiry(36000)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def profile(request, user_id):
    if Author.is_uid_local(user_id):
        # @todo , this template expects a uuid in order to render, it should be able to handle a uid
        invalidate_friends(request.get_host(), user_id)
        return render(request, 'users/profile.html', {'user_id': Author.extract_uuid_from_uid(user_id)})
    # @todo, see above, we dont yet have a profile viewing template that handles uids
    return HttpResponse('The profile you are attempting to view is for a foreign author, which is unsupported at this time', status=404)


def invalidate_friends(host, user_id):
    author_id = host + "/author/" + user_id
    if not Friend.objects.filter(author_id=author_id).exists():
        return
    friends = Friend.objects.filter(author_id=author_id)
    for friend in friends:
        splits = friend.friend_id.split("/")
        friend_host = splits[0]
        if host != friend_host:
            if Node.objects.filter(pk=friend_host).exists():
                node = Node.objects.get(foreign_server_hostname=friend_host)
                # quoted_author_id = quote(
                #     author_id, safe='~()*!.\'')
                headers = {"Content-Type": "application/json",
                           "Accept": "application/json"}
                url = "https://{}/friends/{}".format(
                    friend.friend_id, author_id)
                res = requests.get(url, headers=headers, auth=(
                    node.username_registered_on_foreign_server, node.password_registered_on_foreign_server))
                if res.status_code >= 200 and res.status_code < 300:
                    res = res.json()

                    # if they are friends
                    if not res["friends"]:
                        if Friend.objects.filter(author_id=author_id).filter(friend_id=friend.friend_id).exists():
                            Friend.objects.filter(author_id=author_id).filter(
                                friend_id=friend.friend_id).delete()
                            Friend.objects.filter(author_id=friend.friend_id).filter(
                                friend_id=author_id).delete()


@login_required
def add_friend(request):
    return render(request, 'users/add_friend.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # wait for admin permission to activate account
            user.is_active = False
            host = request.get_host()
            url = host + "/author/" + str(user.id.hex)
            # set user url
            user.url = url
            # set user id
            # format: 127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013
            user.uid = url
            # set user host
            user.host = host

            # update database entry of current user
            user.save()
            return redirect('login')

    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def mandala(request):
    return render(request, 'users/mandala.html')
