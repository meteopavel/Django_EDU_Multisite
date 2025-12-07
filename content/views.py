from django.db import models
from django.db.models import Prefetch, Q
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
    news_items = News.objects.filter(
        is_active=True
    ).filter(
        Q(departments__isnull=True) | Q(departments=department)
    ).distinct().order_by('-created_at')[:3]
    return {
        'department': department,
        'latest_news': news_items,
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
    base_news = News.objects.filter(
        is_active=True
    ).filter(
        models.Q(departments__isnull=True) | models.Q(departments=department)
    ).distinct()
    all_years = list(
        base_news.dates('created_at', 'year', order='DESC')
        .values_list('created_at__year', flat=True)
    )
    selected_year = request.GET.get('year')
    if selected_year and selected_year.isdigit():
        selected_year = int(selected_year)
    else:
        selected_year = all_years[0] if all_years else None
    news_items = base_news.filter(created_at__year=selected_year).order_by(
        '-created_at') if selected_year else base_news.none()
    if selected_year == (all_years[0] if all_years else None):
        if len(all_years) <= 4:
            year_display_groups = [('year', y) for y in all_years]
        else:
            year_display_groups = [
                ('year', all_years[0]),
                ('year', all_years[1]),
                ('ellipsis', None),
                ('year', all_years[-2]),
                ('year', all_years[-1]),
            ]
    else:
        year_display_groups = [('year', y) for y in all_years]
    return {
        'news_items': news_items,
        'department': department,
        'selected_year': selected_year,
        'year_display_groups': year_display_groups,
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