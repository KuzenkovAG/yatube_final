from django.core.paginator import Paginator


def create_paginator(request, objects, limit):
    """Create paginator."""
    paginator = Paginator(objects, limit)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
