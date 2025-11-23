from django.db import models
from django.shortcuts import render, get_object_or_404

from .models import Department, News
from .utils import get_host_map


def _get_department_by_host(request):
    host = request.get_host().lower()
    department_slug = get_host_map().get(host)
    return get_object_or_404(Department, slug=department_slug, is_active=True)


def home_view(request):
    department = _get_department_by_host(request)
    context = {
        'department': department,
    }
    return render(request, 'content/home.html', context)


def contacts_view(request):
    department = _get_department_by_host(request)
    context = {
        'department': department,
    }
    return render(request, 'content/contacts.html', context)


def news_list_view(request):
    department = _get_department_by_host(request)
    news_items = News.objects.filter(
        is_active=True
    ).filter(
        models.Q(departments__isnull=True) | models.Q(departments=department)
    ).distinct().order_by('-created_at')
    return render(request, 'content/news_list.html', {
        'news_items': news_items,
        'department': department
    })


def news_detail_view(request, slug):
    department = _get_department_by_host(request)
    news_item = get_object_or_404(
        News,
        slug=slug,
        is_active=True
    )
    if not (news_item.departments.count() == 0 or news_item.departments.filter(pk=department.pk).exists()):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    return render(request, 'content/news_detail.html', {
        'news': news_item,
        'department': department
    })