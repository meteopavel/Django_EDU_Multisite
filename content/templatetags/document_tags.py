from django import template
from content.models import Document

register = template.Library()

@register.inclusion_tag('content/inc/documents_section.inc.html')
def documents_for_section(department, section_slug):
    """
    Выводит список документов для указанного раздела и подразделения.
    """
    documents = Document.objects.filter(
        department=department,
        is_active=True,
        display_in_sections__contains=section_slug
    ).order_by('order')

    return {
        'documents': documents,
        'section_slug': section_slug,
        'department': department,
    }