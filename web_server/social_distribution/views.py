from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django.conf import settings


def home(request):
    if request.method == 'GET':
        # return redirect(reverse('stream'))
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            return redirect(reverse('login'))
    else:
        return HttpResponse('404 Error', status=404)


def github(request):
    if request.method == 'GET':
        context = {}
        try:
            context['github'] = request.user.github.split('github.com/')[1]
        except:
            print("Your github profile could not be loaded.")
        return JsonResponse(context)

def landing_page(request):
    context = {
        'post_viewing_url': reverse('view_post', args=['00000000000000000000000000000000']).replace('00000000000000000000000000000000/', ''),
        'local_hostname': settings.HOSTNAME
    }
    return render(request, 'home.html', context)