"""
Конфигурация приложения content.
"""

from django.apps import AppConfig


class ContentConfig(AppConfig):
    """Конфигурация Django-приложения content."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
