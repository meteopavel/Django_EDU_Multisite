from functools import wraps
from django.shortcuts import render

def page_name(name, template_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            context = view_func(request, *args, **kwargs)
            context['page_name'] = name
            return render(request, template_name, context)
        return wrapper
    return decorator