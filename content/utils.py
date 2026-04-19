"""
Вспомогательные функции контентного приложения.

Модуль содержит утилиты для:
- определения подразделения по хосту;
- выборки и фильтрации новостей;
- группировки документов;
- вычисления диапазона месяцев экзаменов;
- кастомизации заголовков образовательных секций.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from core.host_parser import parse_host_map
from .models import Department, Document, ExamInfo, News


def get_host_map() -> dict[str, str]:
    """Возвращает словарь соответствия хостов и slug подразделений."""
    return parse_host_map(settings.HOST_TO_DEPARTMENT_MAP)


def get_department_by_host(request: HttpRequest) -> Department:
    """Определяет активное подразделение по хосту текущего запроса."""
    host_with_port = request.get_host()
    host = host_with_port.split(':')[0].lower()
    department_slug = get_host_map().get(host)
    return get_object_or_404(Department, slug=department_slug, is_active=True)


def get_news_for_department(department: Department | None, limit: int | None = None, year: int | None = None, partner_only: bool = False):
    """Возвращает новости подразделения с опциональной фильтрацией по году и лимиту."""
    if partner_only:
        qs = News.objects.filter(is_active=True, is_partner_news=True)
    else:
        qs = News.objects.filter(is_active=True, is_partner_news=False).filter(Q(departments__isnull=True) | Q(departments=department)).distinct()
    if year and not partner_only:
        qs = qs.filter(created_at__year=year)
    qs = qs.order_by('-created_at')
    if limit:
        qs = qs[:limit]
    return qs


def get_news_years(department: Department) -> list[int]:
    """Возвращает список годов, в которых есть новости подразделения."""
    return list(News.objects.filter(is_active=True).filter(Q(departments__isnull=True) | Q(departments=department)).distinct().dates('created_at', 'year', order='DESC').values_list('created_at__year', flat=True))


def split_documents_by_file_type(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    """Разделяет документы на изображения и прочие элементы."""
    image_docs = []
    other_docs = []
    for document in documents:
        if document.file_type == 'image':
            image_docs.append(document)
        else:
            other_docs.append(document)
    return image_docs, other_docs


def group_documents_by_category(documents: list[Document]) -> list[tuple[Any, list[Document]]]:
    """Группирует документы по категории с выделением группы «Прочее»."""
    categories_dict: dict[Any, list[Document]] = {}
    fallback_category = ('Прочее', 999)
    for document in documents:
        category = document.category if document.category is not None else fallback_category
        if category not in categories_dict:
            categories_dict[category] = []
        categories_dict[category].append(document)
    return sorted(categories_dict.items(), key=lambda item: (item[0][1], item[0][0]) if isinstance(item[0], tuple) else (item[0].order, item[0].name))


def get_exam_month_range(exams: list[ExamInfo]) -> str:
    """Возвращает человекочитаемый диапазон месяцев по датам экзаменов."""
    if not exams:
        return ''
    all_dates = []
    for exam in exams:
        if exam.theory_date:
            all_dates.append(exam.theory_date)
        if exam.practice_date:
            all_dates.append(exam.practice_date)
        if exam.gibdd_date:
            all_dates.append(exam.gibdd_date)
    if not all_dates:
        return ''
    min_date = min(all_dates)
    max_date = max(all_dates)
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь',
    }
    if min_date.month == max_date.month and min_date.year == max_date.year:
        return f'{months[min_date.month]} {min_date.year} г.'
    if min_date.year == max_date.year:
        return f'{months[min_date.month]}-{months[max_date.month]} {min_date.year} г.'
    return f'{months[min_date.month]} {min_date.year} - {months[max_date.month]} {max_date.year} г.'


def get_education_section_title(department_slug: str, base_slug: str, default_title: str) -> str:
    """Возвращает отображаемый заголовок образовательной секции с учётом кастомизаций."""
    if department_slug == 'irkutsk' and base_slug == 'materialno-tehnicheskoe-obespechenie':
        return 'Материально-техническое обеспечение и оснащенность образовательного процесса. Доступная среда'
    return default_title
