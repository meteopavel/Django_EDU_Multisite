"""
Контекстные процессоры контентного приложения.

Модуль содержит функции для:
- подстановки меню текущего подразделения;
- вычисления версии статики;
- передачи ключа Yandex Maps в шаблоны.
"""

from __future__ import annotations

from pathlib import Path
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


def static_version(request: HttpRequest) -> dict[str, str]:
    """Возвращает версию статики по времени последнего изменения файлов static."""
    static_dir = Path(settings.BASE_DIR) / 'static'
    try:
        files = list(static_dir.rglob('*'))
        if files:
            latest = max(f.stat().st_mtime for f in files if f.is_file())
            return {'STATIC_VERSION': str(int(latest))}
    except Exception:
        pass
    return {'STATIC_VERSION': '1'}


def yandex_maps(request: HttpRequest) -> dict[str, str]:
    """Возвращает ключ API Яндекс.Карт для использования в шаблонах."""
    return {'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', '')}
