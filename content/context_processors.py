from pathlib import Path

from django.conf import settings
from django.db import models
from django.http import Http404

from .models import MenuItem
from .utils import get_department_by_host


def menu_processor(request):
    try:
        department = get_department_by_host(request)
    except Http404:
        from .models import Department
        department = Department.objects.filter(slug='bratsk', is_active=True).first()
        if not department:
            return {'menu_items': MenuItem.objects.none()}
    menu_items = MenuItem.objects.filter(
        is_active=True
    ).filter(
        models.Q(departments__isnull=True) | models.Q(departments=department)
    ).distinct().order_by('order')
    return {'menu_items': menu_items}


def static_version(request):
    static_dir = Path(settings.BASE_DIR) / 'static'
    try:
        files = list(static_dir.rglob('*'))
        if files:
            latest = max(f.stat().st_mtime for f in files if f.is_file())
            return {'STATIC_VERSION': str(int(latest))}
    except:
        pass

    return {'STATIC_VERSION': '1'}