"""
Декораторы представлений контентного приложения.

Модуль содержит:
- декоратор для обычных страниц с автоматическим определением подразделения;
- декоратор для AJAX-представлений с рендерингом HTML или возвратом JSON.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from content.utils import get_department_by_host


def page_name(name: str, template_name: str) -> Callable:
    """Декорирует view, добавляя page_name, department и рендер шаблона страницы."""
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            department = get_department_by_host(request)
            context = view_func(request, department=department, *args, **kwargs)
            context.setdefault('page_name', name)
            context.setdefault('department', department)
            return render(request, template_name, context)
        return wrapper
    return decorator


def ajax_view(name: str | None = None, template_name: str | None = None) -> Callable:
    """Декорирует AJAX-view, разрешая подразделение и возвращая JSON или HTML."""
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            department = None
            department_slug = request.GET.get('department')
            if department_slug:
                from .models import Department
                try:
                    department = Department.objects.get(slug=department_slug)
                except Department.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Invalid department'}, status=400)
            if department is None:
                try:
                    department = get_department_by_host(request)
                except Exception:
                    return JsonResponse({'success': False, 'error': 'Department not resolved'}, status=400)
            try:
                result = view_func(request, department=department, *args, **kwargs)
            except Exception:
                return JsonResponse({'success': False, 'error': 'Internal error'}, status=500)
            if isinstance(result, dict) and template_name:
                context = result.copy()
                context.setdefault('section_name', name)
                context.setdefault('template_name', template_name)
                context.setdefault('department', department)
                html = render_to_string(template_name, context, request=request)
                return JsonResponse({'success': True, 'html': html})
            if isinstance(result, dict):
                return JsonResponse(result)
            return result
        return wrapper
    return decorator
