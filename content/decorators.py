from functools import wraps
from django.shortcuts import render

from content.utils import get_department_by_host


def page_name(name, template_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            department = get_department_by_host(request)
            context = view_func(request, department=department, *args, **kwargs)
            context.setdefault('page_name', name)
            context.setdefault('department', department)
            return render(request, template_name, context)
        return wrapper
    return decorator