from __future__ import annotations

from django.db import models

from content.models import ClassSession, Department


class ClassScheduleAlert(models.Model):
    """Отметка о том, что по подразделению/предмету уже отправлено уведомление
    об отсутствии будущих занятий (чтобы не слать его повторно каждый день).

    Запись удаляется, как только в расписании снова появляется будущая дата —
    следующее устаревание снова вызовет уведомление.

    Живёт в отдельном приложении (не content), чтобы деплой не задевал её:
    content дампится/перезаливается фикстурой на каждом деплое, а это —
    рантайм-состояние cron-команды notify_stale_class_sessions, а не
    редакционный контент.
    """

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='class_schedule_alerts',
        verbose_name='Подразделение',
    )
    subject = models.CharField('Предмет', max_length=20, choices=ClassSession.Subject.choices)
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление об устаревшем расписании'
        verbose_name_plural = 'Уведомления об устаревшем расписании'
        constraints = [
            models.UniqueConstraint(fields=['department', 'subject'], name='unique_class_schedule_alert'),
        ]

    def __str__(self) -> str:
        return f'{self.department.name} — {self.get_subject_display()} ({self.notified_at:%Y-%m-%d})'
