"""
Шаблонные теги для работы с документами.

Модуль содержит inclusion tag для вывода документов подразделения
по выбранной секции с разделением на изображения и прочие документы,
и фильтр версионирования URL медиа-файлов.
"""

from __future__ import annotations

import os
from typing import Any

from django import template

from content.models import Document, DocumentCategory, Department

register = template.Library()


@register.filter
def versioned_url(field_file) -> str:
    """URL файла из /media/ с версией по mtime файла.

    Хостинг кэширует /media/ на год без ревалидации: при замене файла
    с тем же именем вернувшиеся посетители видят старую версию из кэша
    браузера. Версия в URL принудительно пробивает кэш.
    """
    if not field_file:
        return ''
    url = field_file.url
    try:
        mtime = int(os.path.getmtime(field_file.path))
    except (NotImplementedError, ValueError, OSError):
        return url
    return f'{url}?v={mtime}'


@register.inclusion_tag('content/ajax/documents/documents_section.html')
def documents_for_section(department: Department, section_slug: str) -> dict[str, Any]:
    """Возвращает документы секции, разделённые на изображения и категории прочих файлов."""
    documents_qs = Document.objects.filter(department=department, is_active=True, display_in_sections__contains=section_slug).select_related('category').order_by('category__order', 'order', 'title')
    image_docs = []
    other_docs = []
    for doc in documents_qs:
        if doc.file_type == 'image':
            image_docs.append(doc)
        else:
            other_docs.append(doc)
    categories_dict = {}
    for doc in other_docs:
        cat = doc.category or DocumentCategory(id=0, name='Прочее', order=999)
        if cat not in categories_dict:
            categories_dict[cat] = []
        categories_dict[cat].append(doc)
    sorted_categories = sorted(categories_dict.items(), key=lambda x: (x[0].order, x[0].name))
    return {'image_documents': image_docs, 'other_documents_by_category': sorted_categories}
