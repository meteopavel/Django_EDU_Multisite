from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404

from core.host_parser import parse_host_map
from .models import News, Department


def get_host_map():
    return parse_host_map(settings.HOST_TO_DEPARTMENT_MAP)


def get_department_by_host(request):
    host_with_port = request.get_host()
    host = host_with_port.split(':')[0].lower()
    department_slug = get_host_map().get(host)
    return get_object_or_404(Department, slug=department_slug, is_active=True)


def get_news_for_department(department, limit=None, year=None, partner_only=False):
    if partner_only:
        qs = News.objects.filter(
            is_active=True,
            is_partner_news=True
        )
    else:
        qs = News.objects.filter(
            is_active=True,
            is_partner_news=False
        ).filter(
            Q(departments__isnull=True) | Q(departments=department)
        ).distinct()
    if year and not partner_only:
        qs = qs.filter(created_at__year=year)
    qs = qs.order_by('-created_at')
    if limit:
        qs = qs[:limit]
    return qs


def get_news_years(department):
    return list(
        News.objects.filter(
            is_active=True
        ).filter(
            Q(departments__isnull=True) | Q(departments=department)
        ).distinct()
        .dates('created_at', 'year', order='DESC')
        .values_list('created_at__year', flat=True)
    )


def get_exam_month_range(exams):
    if not exams:
        return ""
    all_dates = []
    for exam in exams:
        if exam.theory_date:
            all_dates.append(exam.theory_date)
        if exam.practice_date:
            all_dates.append(exam.practice_date)
        if exam.gibdd_date:
            all_dates.append(exam.gibdd_date)
    if not all_dates:
        return ""
    min_date = min(all_dates)
    max_date = max(all_dates)
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    if min_date.month == max_date.month and min_date.year == max_date.year:
        return f"{months[min_date.month]} {min_date.year} г."
    if min_date.year == max_date.year:
        return f"{months[min_date.month]}-{months[max_date.month]} {min_date.year} г."
    return f"{months[min_date.month]} {min_date.year} - {months[max_date.month]} {max_date.year} г."


def get_education_section_title(department_slug, base_slug, default_title):
    if (
        department_slug == 'irkutsk'
        and base_slug == 'materialno-tehnicheskoe-obespechenie'
    ):
        return 'Материально-техническое обеспечение и оснащенность образовательного процесса. Доступная среда'
    return default_title