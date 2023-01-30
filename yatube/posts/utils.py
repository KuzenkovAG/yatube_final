from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


def create_paginator(request, objects, limit):
    """Create paginator."""
    paginator = Paginator(objects, limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_author_object(username):
    User = get_user_model()
    return get_object_or_404(User, username=username)
