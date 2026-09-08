from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from .models import (
    ClassScheduleAlert,
    ExamEndingAlert,
    ExamPassedAlert,
    PromoEventAlert,
    ScheduleEndingAlert,
)


class ReadOnlyAlertAdmin(admin.ModelAdmin):
    """Общий вид для отметок об отправленных уведомлениях (только просмотр)."""

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(ClassScheduleAlert)
class ClassScheduleAlertAdmin(ReadOnlyAlertAdmin):
    """Список уже отправленных уведомлений об устаревшем расписании."""

    list_display = ['department', 'subject', 'notified_at']
    list_filter = ['department', 'subject']
    ordering = ['-notified_at']


@admin.register(ExamPassedAlert)
class ExamPassedAlertAdmin(ReadOnlyAlertAdmin):
    """Список уже отправленных уведомлений о прошедших экзаменах ГИБДД."""

    list_display = ['exam', 'notified_at']
    ordering = ['-notified_at']


@admin.register(PromoEventAlert)
class PromoEventAlertAdmin(ReadOnlyAlertAdmin):
    """Список уже отправленных уведомлений о старте акций и о том, что акция
    заканчивается."""

    list_display = ['announcement', 'event_type', 'event_date', 'notified_at']
    list_filter = ['event_type']
    ordering = ['-notified_at']


@admin.register(ScheduleEndingAlert)
class ScheduleEndingAlertAdmin(ReadOnlyAlertAdmin):
    """Список уже отправленных предупреждений об окончании расписания."""

    list_display = ['department', 'subject', 'last_date', 'notified_at']
    list_filter = ['department', 'subject']
    ordering = ['-notified_at']


@admin.register(ExamEndingAlert)
class ExamEndingAlertAdmin(ReadOnlyAlertAdmin):
    """Список уже отправленных предупреждений об окончании экзаменов."""

    list_display = ['department', 'last_date', 'notified_at']
    ordering = ['-notified_at']
