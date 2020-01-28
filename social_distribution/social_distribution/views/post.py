from django.shortcuts import render


def get_public_posts(request, page, size):
    # All posts marked as public on the server
    return None


def get_single_post(request, post_id):
    # Get a single post
    return None


def auth_posts(request):
    # Posts that are visible to the currently authenticated user
    # Create a post to the currently authenticated user
    return None


def get_user_public_posts(request, author_id):
    # Get all publicly visible posts to current user
    return None
