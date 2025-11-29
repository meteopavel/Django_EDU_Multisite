from django.db import models
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404

from .decorators import page_name
from .models import Department, News, DocumentCategory, Document
from .utils import get_host_map


def _get_department_by_host(request):
    host = request.get_host().lower()
    department_slug = get_host_map().get(host)
    return get_object_or_404(Department, slug=department_slug, is_active=True)


@page_name('Главная', 'content/home.html')
def home_view(request):
    department = _get_department_by_host(request)
    return {
        'department': department,
    }


@page_name('Контакты', 'content/contacts.html')
def contacts_view(request):
    department = _get_department_by_host(request)
    return {
        'department': department,
    }


@page_name('Новости', 'content/news_list.html')
def news_list_view(request):
    department = _get_department_by_host(request)
    news_items = News.objects.filter(
        is_active=True
    ).filter(
        models.Q(departments__isnull=True) | models.Q(departments=department)
    ).distinct().order_by('-created_at')
    return {
        'news_items': news_items,
        'department': department
    }


@page_name('Новость', 'content/news_detail.html')
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
    return {
        'news': news_item,
        'department': department
    }


@page_name('Документы', 'content/document_list.html')
def document_list(request):
    department = _get_department_by_host(request)
    categories = DocumentCategory.objects.filter(
        documents__department=department,
        documents__is_active=True
    ).distinct().prefetch_related(
        Prefetch(
            'documents',
            queryset=Document.objects.filter(
                department=department,
                is_active=True
            ).order_by('order', 'title'),
            to_attr='filtered_docs'
        )
    ).order_by('order', 'name')
    return {
        'department': department,
        'categories': categories,
    }