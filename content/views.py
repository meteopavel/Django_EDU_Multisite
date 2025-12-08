from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .decorators import page_name
from .models import News, DocumentCategory, Document
from .utils import get_news_for_department, get_news_years


@page_name('Главная', 'content/home.html')
def home_view(request, department):
    latest_news = get_news_for_department(department, limit=3)
    return {'latest_news': latest_news}


@page_name('Новости', 'content/news_list.html')
def news_list_view(request, department):
    all_years = get_news_years(department)
    selected_year = request.GET.get('year')
    if selected_year and selected_year.isdigit():
        selected_year = int(selected_year)
    else:
        selected_year = all_years[0] if all_years else None
    news_items = get_news_for_department(department, year=selected_year)
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
        'selected_year': selected_year,
        'year_display_groups': year_display_groups,
    }


@page_name('Новость', 'content/news_detail.html')
def news_detail_view(request, department, slug):
    news_item = get_object_or_404(News, slug=slug, is_active=True)
    return {'news': news_item}


@page_name('Документы', 'content/document_list.html')
def document_list(request, department):
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
    return {'categories': categories}


@page_name('Контакты', 'content/contacts.html')
def contacts_view(request, department):
    return {}