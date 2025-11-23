from django.db import models

from .models import MenuItem, Department
from .utils import get_host_map


def menu_processor(request):
    host = request.get_host().lower()
    department_slug = get_host_map().get(host, 'bratsk')
    department = Department.objects.get(slug=department_slug, is_active=True)
    menu_items = MenuItem.objects.filter(
        is_active=True
    ).filter(
        models.Q(departments__isnull=True) | models.Q(departments=department)
    ).distinct().order_by('order')
    return {'menu_items': menu_items}