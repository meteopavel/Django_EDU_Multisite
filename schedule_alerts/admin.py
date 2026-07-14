from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from .models import ClassScheduleAlert


@admin.register(ClassScheduleAlert)
class ClassScheduleAlertAdmin(admin.ModelAdmin):
    """Список уже отправленных уведомлений об устаревшем расписании (только просмотр)."""
    list_display = ['department', 'subject', 'notified_at']
    list_filter = ['department', 'subject']
    ordering = ['-notified_at']

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: ClassScheduleAlert | None = None) -> bool:
        return False
