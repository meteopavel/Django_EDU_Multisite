from django.shortcuts import get_object_or_404
from django.utils import timezone

from .decorators import page_name, ajax_view
from .models import News, Document, Service, Material, EDUCATION_SECTION_CHOICES, ExamInfo
from .utils import get_news_for_department, get_news_years, get_exam_month_range


@page_name('Главная', 'content/pages/home.html')
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
    if details.show_exam_info:
        exams = ExamInfo.objects.filter(
            department=department
        ).order_by('gibdd_date', 'theory_date')
        today = timezone.now().date()
        visible_exams = []
        for exam in exams:
            if exam.gibdd_date and exam.gibdd_date >= today:
                visible_exams.append(exam)
        context['exam_preview'] = visible_exams
        context['has_exams'] = bool(visible_exams)
    context.update({
        'contacts_data': {
            'title': department.name,
            'address': details.address,
            'short_address': details.short_address,
            'phone': details.phone,
            'cellphone': details.cellphone,
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
        context['show_documents'] = details.show_documents

    if details.show_education_info:
        EDUCATION_SECTIONS = []
        for slug, title in EDUCATION_SECTION_CHOICES:
            if slug == 'documents':
                item_type = 'documents'
            else:
                item_type = 'material'
            EDUCATION_SECTIONS.append((title, slug, item_type))

        accordion_items = []
        for title, base_slug, item_type in EDUCATION_SECTIONS:
            if item_type == 'documents':
                accordion_items.append({
                    'title': title,
                    'type': 'documents'
                })
            elif item_type == 'material':
                full_slug = f'{department.slug}-{base_slug}'
                if Material.objects.filter(
                        department=department,
                        slug=full_slug,
                        is_active=True
                ).exists():
                    accordion_items.append({
                        'title': title,
                        'type': 'material',
                        'material_slug': full_slug
                    })

        context['education_accordion_items'] = accordion_items
        context['show_education_accordion'] = bool(accordion_items)
    return context


@ajax_view('Все новости', 'content/ajax/news/news_grid.html')
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


@ajax_view('Новость', 'content/ajax/news/news_detail.html')
def ajax_news_detail(request, department):
    slug = request.GET.get('slug')
    news_item = get_object_or_404(News, slug=slug, is_active=True)
    return {
        'news': news_item,
        'title': news_item.title
    }


@ajax_view('Документы', 'content/ajax/documents/documents_section.html')
def ajax_documents(request, department):
    all_docs = Document.objects.filter(
        department=department,
        is_active=True,
        display_in_sections__contains='documents'
    ).select_related('category').order_by('order', 'title')
    image_docs = []
    other_docs = []
    for doc in all_docs:
        if doc.file_type == 'image':
            image_docs.append(doc)
        else:
            other_docs.append(doc)
    categories_dict = {}
    for doc in other_docs:
        cat = doc.category
        if cat not in categories_dict:
            categories_dict[cat] = []
        categories_dict[cat].append(doc)
    sorted_categories = sorted(categories_dict.items(), key=lambda x: (x[0].order, x[0].name))
    return {
        'image_documents': image_docs,
        'other_documents_by_category': sorted_categories,
    }


@ajax_view('Описание материала', 'content/ajax/materials/material_description.html')
def ajax_material_description(request, department, **kwargs):
    material_slug = kwargs.get('material_slug')
    material = get_object_or_404(Material, slug=material_slug, is_active=True)
    base_slug = material_slug
    if '-' in material_slug:
        base_slug = material_slug.split('-', 1)[1]
    valid_sections = {slug for slug, _ in EDUCATION_SECTION_CHOICES}
    section_slug = base_slug if base_slug in valid_sections else None
    documents_context = {}
    if section_slug and section_slug != 'documents':  # 'documents' — отдельная секция
        documents = Document.objects.filter(
            department=department,
            is_active=True,
            display_in_sections__contains=section_slug
        ).select_related('category').order_by('category__order', 'order', 'title')
        image_docs = [d for d in documents if d.file_type == 'image']
        other_docs = [d for d in documents if d.file_type != 'image']
        categories_dict = {}
        for doc in other_docs:
            cat = doc.category or type('', (), {'name': 'Прочее', 'order': 999})()
            if cat not in categories_dict:
                categories_dict[cat] = []
            categories_dict[cat].append(doc)
        sorted_categories = sorted(
            categories_dict.items(),
            key=lambda x: (getattr(x[0], 'order', 999), getattr(x[0], 'name', ''))
        )
        documents_context = {
            'image_documents': image_docs,
            'other_documents_by_category': sorted_categories,
        }
    return {
        'material': material,
        **documents_context
    }


@ajax_view('Информация об экзаменах', 'content/ajax/exams/exam_info.html')
def ajax_exam_info(request, department):
    exams = ExamInfo.objects.filter(
        department=department
    ).order_by('group_number', 'gibdd_date')
    visible_exams = []
    for exam in exams:
        if exam.gibdd_date and exam.gibdd_date >= timezone.now().date():
            visible_exams.append(exam)
    month_range = get_exam_month_range(visible_exams)
    return {
        'exams': visible_exams,
        'has_exams': bool(visible_exams),
        'month_range': month_range,
    }
