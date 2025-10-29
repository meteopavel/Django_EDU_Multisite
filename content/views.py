from django.shortcuts import render, get_object_or_404

from .models import Department, PageTemplate, PageContent
from .utils import get_host_map


def page_view(request, slug=None):
    host = request.get_host().lower()
    department_slug = get_host_map().get(host)
    department = get_object_or_404(Department, slug=department_slug, is_active=True)
    template_slug = slug or 'home'
    template = get_object_or_404(PageTemplate, slug=template_slug)
    page_content = get_object_or_404(
        PageContent,
        department=department,
        template=template,
        is_active=True
    )
    all_pages = PageTemplate.objects.filter(
        pagecontent__department=department,
        pagecontent__is_active=True
    ).distinct()
    context = {
        'page': page_content,
        'department': department,
        'all_pages': all_pages,
    }
    return render(request, 'content/page.html', context)