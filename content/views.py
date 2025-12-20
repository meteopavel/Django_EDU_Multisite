from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from .decorators import page_name, ajax_view
from .models import News, DocumentCategory, Document, Service, Material
from .utils import get_news_for_department, get_news_years


@page_name('Главная', 'content/home.html')
def home_view(request, department):
    details = department.details
    context = details.get_section_flags()
    context['partner_news'] = get_news_for_department(
        department=None,
        limit=3,
        partner_only=True
    )
    if details.show_services:
        services = Service.objects.filter(department=department, is_active=True).order_by('order')
        context['services'] = services
        context['services_with_desc'] = [
            {
                'id': s.id,
                'name': s.name,
                'icon_name': s.icon_name,
            }
            for s in services
        ]
    context.update({
        'contacts_data': {
            'title': department.name,
            'address': details.address,
            'short_address': details.short_address,
            'phone': details.phone,
            'email': details.email,
            'map_center': details.map_center
        },
        'schedule': details.schedule,
        'requisites': {
            'recipient_name': details.recipient_name,
            'inn': details.inn,
            'kpp': details.kpp,
            'bank': details.bank,
            'bik': details.bik,
            'corr_account': details.corr_account,
            'settlement_account': details.settlement_account,
            'payment_purpose': details.payment_purpose,
        },
        'map_iframes': details.map_iframes,
    })

    if details.show_latest_news:
        context['latest_news'] = get_news_for_department(department, limit=3)

    if details.show_documents:
        if department.slug == 'region':
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
            context['document_categories'] = categories
            context['load_documents_on_page'] = True
        else:
            context['load_documents_on_page'] = False
    return context


@ajax_view('Все новости', 'content/inc/news_grid.inc.html')
def ajax_all_news(request, department):
    all_years = get_news_years(department)
    selected_year = request.GET.get('year')
    if selected_year and selected_year.isdigit():
        selected_year = int(selected_year)
    else:
        selected_year = all_years[0] if all_years else None
    news_items = get_news_for_department(department, year=selected_year)
    if all_years and selected_year == all_years[0]:
        year_display_groups = (
            [('year', all_years[0]), ('year', all_years[1]), ('ellipsis', None),
             ('year', all_years[-2]), ('year', all_years[-1])]
            if len(all_years) > 4 else
            [('year', y) for y in all_years]
        )
    else:
        year_display_groups = [('year', y) for y in all_years]
    return {
        'news_items': news_items,
        'selected_year': selected_year,
        'year_display_groups': year_display_groups,
    }


@ajax_view('Документы', 'content/inc/documents_section.inc.html')
def ajax_documents(request, department):
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
    return {'categories': categories,}


@ajax_view('Описание материала', 'content/inc/material_description.html')
def ajax_material_description(request, department, **kwargs):
    material_slug = kwargs.get('material_slug')
    print(material_slug)
    material = get_object_or_404(Material, slug=material_slug, is_active=True)
    return {'material': material}


@ajax_view('Новость', 'content/inc/news_detail.inc.html')
def ajax_news_detail(request, department):
    slug = request.GET.get('slug')
    news_item = get_object_or_404(News, slug=slug, is_active=True)
    return {
        'news': news_item,
        'title': news_item.title
    }
