from django.shortcuts import render

# This file is used to display web pages

def main_page(request):
    return render(request, 'mainPage.html')

def post_new(request):
    return render(request, 'posting.html')