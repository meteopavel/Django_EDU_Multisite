from django import template
from content.models import Document, DocumentCategory

register = template.Library()

@register.inclusion_tag('content/ajax/documents/documents_section.html')
def documents_for_section(department, section_slug):
    """
    Возвращает документы для раздела, разделённые на:
    - изображения (для отображения в сетке),
    - остальные (по категориям).
    """
    documents_qs = Document.objects.filter(
        department=department,
        is_active=True,
        display_in_sections__contains=section_slug
    ).select_related('category').order_by('category__order', 'order', 'title')

    # Разделяем на изображения и остальное
    image_docs = []
    other_docs = []

    for doc in documents_qs:
        if doc.file_type == 'image':
            image_docs.append(doc)
        else:
            other_docs.append(doc)

    # Группируем "остальное" по категориям
    categories_dict = {}
    for doc in other_docs:
        cat = doc.category or DocumentCategory(id=0, name="Прочее", order=999)
        if cat not in categories_dict:
            categories_dict[cat] = []
        categories_dict[cat].append(doc)

    # Сортируем категории
    sorted_categories = sorted(
        categories_dict.items(),
        key=lambda x: (x[0].order, x[0].name)
    )

    return {
        'image_documents': image_docs,
        'other_documents_by_category': sorted_categories,
    }