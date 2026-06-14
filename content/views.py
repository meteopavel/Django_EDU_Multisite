"""
Представления контентного раздела сайта.

Модуль содержит:
- главную страницу подразделения;
- AJAX-список и детали новостей;
- AJAX-секции документов и материалов;
- AJAX-вывод информации об экзаменах.
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .constants import EDUCATION_SECTION_CHOICES
from .decorators import page_name, ajax_view
from .models import Department, News, Document, Service, Material, ExamInfo, HomeSectionChoices, Announcement
from .utils import get_news_for_department, get_news_years, split_documents_by_file_type, group_documents_by_category, \
                   get_exam_month_range, get_education_section_title



@page_name('Главная', 'content/pages/home.html')
def home_view(request: HttpRequest, department: Department) -> dict[str, Any]:
    """Собирает контекст главной страницы подразделения по включённым секциям."""
    details = department.details
    home_sections = list(department.home_page_sections.filter(is_enabled=True).order_by('order', 'id'))
    enabled_section_keys = {section.section_key for section in home_sections}
    context: dict[str, Any] = {
        'home_sections': home_sections,
        'contacts_data': {
            'title': department.name,
            'address': details.address,
            'short_address': details.short_address,
            'phone': details.phone,
            'cellphone': details.cellphone,
            'email': details.email,
            'map_center': details.map_center,
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
    }
    if HomeSectionChoices.PARTNERS in enabled_section_keys:
        context['partner_news'] = get_news_for_department(department=None, limit=3, partner_only=True)
    if HomeSectionChoices.SERVICES in enabled_section_keys:
        services = Service.objects.filter(department=department, is_active=True).order_by('order')
        context['services'] = services
        context['services_with_desc'] = [{'id': service.id, 'name': service.name, 'icon_name': service.icon_name} for service in services]
    if HomeSectionChoices.ANNOUNCEMENTS in enabled_section_keys:
        today = timezone.now().date()
        context['above_announcements'] = Announcement.objects.filter(
            department=department, is_active=True,
            card_type__in=['promo', 'announcement'],
        ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=today))
    if HomeSectionChoices.EXAM_INFO in enabled_section_keys:
        exams = ExamInfo.objects.filter(department=department).order_by('gibdd_date', 'theory_date')
        today = timezone.now().date()
        visible_exams = [exam for exam in exams if exam.gibdd_date and exam.gibdd_date >= today]
        context['exam_preview'] = visible_exams
        context['has_exams'] = bool(visible_exams)
        context['grid_cards'] = Announcement.objects.filter(
            department=department, is_active=True, card_type='info',
        ).filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=today))
    if HomeSectionChoices.LATEST_NEWS in enabled_section_keys:
        context['latest_news'] = get_news_for_department(department, limit=3)
    if HomeSectionChoices.DOCUMENTS in enabled_section_keys:
        pass
    if HomeSectionChoices.EDUCATION_INFO in enabled_section_keys:
        accordion_items: list[dict[str, Any]] = []
        for base_slug, default_title in EDUCATION_SECTION_CHOICES:
            title = get_education_section_title(department.slug, base_slug, default_title)
            if base_slug == 'documents':
                accordion_items.append({'title': title, 'type': 'documents'})
                continue
            full_slug = f'{department.slug}-{base_slug}'
            if Material.objects.filter(department=department, slug=full_slug, is_active=True).exists():
                accordion_items.append({'title': title, 'type': 'material', 'material_slug': full_slug})
        context['education_accordion_items'] = accordion_items
        context['show_education_accordion'] = bool(accordion_items)
    return context


@ajax_view('Все новости', 'content/ajax/news/news_grid.html')
def ajax_all_news(request: HttpRequest, department: Department) -> dict[str, Any]:
    """Возвращает контекст AJAX-списка новостей с фильтрацией по году."""
    all_years = get_news_years(department)
    selected_year = request.GET.get('year')
    if selected_year and selected_year.isdigit():
        selected_year_value: int | None = int(selected_year)
    else:
        selected_year_value = all_years[0] if all_years else None
    news_items = get_news_for_department(department, year=selected_year_value)
    if all_years and selected_year_value == all_years[0]:
        year_display_groups = [('year', all_years[0]), ('year', all_years[1]), ('ellipsis', None), ('year', all_years[-2]), ('year', all_years[-1])] if len(all_years) > 4 else [('year', year) for year in all_years]
    else:
        year_display_groups = [('year', year) for year in all_years]
    return {'news_items': news_items, 'selected_year': selected_year_value, 'year_display_groups': year_display_groups}


@ajax_view('Новость', 'content/ajax/news/news_detail.html')
def ajax_news_detail(request: HttpRequest, department: Department) -> dict[str, Any]:
    """Возвращает контекст детального AJAX-представления одной новости."""
    slug = request.GET.get('slug')
    news_item = get_object_or_404(News, slug=slug, is_active=True)
    return {'news': news_item, 'title': news_item.title}


@ajax_view('Документы', 'content/ajax/documents/documents_section.html')
def ajax_documents(request: HttpRequest, department: Department) -> dict[str, Any]:
    """Возвращает контекст AJAX-секции документов подразделения."""
    all_docs = list(Document.objects.filter(department=department, is_active=True, display_in_sections__contains='documents').select_related('category').order_by('order', 'title'))
    image_docs, other_docs = split_documents_by_file_type(all_docs)
    sorted_categories = group_documents_by_category(other_docs)
    return {'image_documents': image_docs, 'other_documents_by_category': sorted_categories}


@ajax_view('Описание материала', 'content/ajax/materials/material_description.html')
def ajax_material_description(request: HttpRequest, department: Department, **kwargs: Any) -> dict[str, Any]:
    """Возвращает контекст AJAX-описания материала и связанных документов секции."""
    material_slug = kwargs.get('material_slug')
    material = get_object_or_404(Material, slug=material_slug, is_active=True)
    base_slug = material_slug
    if '-' in material_slug:
        base_slug = material_slug.split('-', 1)[1]
    valid_sections = {slug for slug, _ in EDUCATION_SECTION_CHOICES}
    section_slug = base_slug if base_slug in valid_sections else None
    documents_context: dict[str, Any] = {}
    if section_slug and section_slug != 'documents':
        documents = list(Document.objects.filter(department=department, is_active=True, display_in_sections__contains=section_slug).select_related('category').order_by('category__order', 'order', 'title'))
        image_docs, other_docs = split_documents_by_file_type(documents)
        sorted_categories = group_documents_by_category(other_docs)
        documents_context = {'image_documents': image_docs, 'other_documents_by_category': sorted_categories}
    return {'material': material, **documents_context}


@ajax_view('Информация об экзаменах', 'content/ajax/exams/exam_info.html')
def ajax_exam_info(request: HttpRequest, department: Department) -> dict[str, Any]:
    """Возвращает контекст AJAX-блока с актуальными экзаменами подразделения."""
    exams = ExamInfo.objects.filter(department=department).order_by('group_number', 'gibdd_date')
    today = timezone.now().date()
    visible_exams = [exam for exam in exams if exam.gibdd_date and exam.gibdd_date >= today]
    month_range = get_exam_month_range(visible_exams)
    return {'exams': visible_exams, 'has_exams': bool(visible_exams), 'month_range': month_range}
