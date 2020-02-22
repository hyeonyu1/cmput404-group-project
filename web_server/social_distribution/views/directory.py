from django.shortcuts import render

# This file is used to display web pages

def main_page(request):
    return render(request, 'mainPage.html')
