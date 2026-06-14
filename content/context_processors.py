"""
Контекстные процессоры контентного приложения.

Модуль содержит функции для:
- подстановки меню текущего подразделения;
- передачи ключа Yandex Maps в шаблоны.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models
from django.http import Http404, HttpRequest

from .models import Department, MenuItem
from .utils import get_department_by_host


def menu_processor(request: HttpRequest) -> dict[str, Any]:
    """Возвращает пункты меню для текущего подразделения или резервного подразделения."""
    try:
        department = get_department_by_host(request)
    except Http404:
        department = Department.objects.filter(slug='bratsk', is_active=True).first()
        if not department:
            return {'menu_items': MenuItem.objects.none()}
    menu_items = MenuItem.objects.filter(is_active=True).filter(models.Q(departments__isnull=True) | models.Q(departments=department)).distinct().order_by('order')
    return {'menu_items': menu_items}


def yandex_maps(request: HttpRequest) -> dict[str, str]:
    """Возвращает ключ API Яндекс.Карт для использования в шаблонах."""
    return {'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', '')}
