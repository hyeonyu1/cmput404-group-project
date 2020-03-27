from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib.auth import views as auth_views
from django.urls import reverse


class CustomLogin(auth_views.LoginView):
    def form_valid(self, form):
        login(self.request, form.get_user())
        # set expiration of the current login session
        # a single login is alive for 10hrs
        self.request.session.set_expiry(36000)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def profile(request,user_id):
    return render(request, 'users/profile.html', {'user_id':user_id})

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
