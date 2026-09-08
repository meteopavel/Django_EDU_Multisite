from __future__ import annotations

from django.db import models

from content.models import Announcement, ClassSession, Department, ExamInfo


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


class ExamPassedAlert(models.Model):
    """Отметка об отправке уведомления «в группе прошёл экзамен в ГИБДД» по
    конкретному экзамену (чтобы не слать его повторно на следующих запусках).

    Живёт здесь по той же причине, что и ClassScheduleAlert: это рантайм-состояние
    cron-команды, а не редакционный контент — приложение content при деплое
    перезаливается фикстурой.
    """

    exam = models.ForeignKey(
        ExamInfo, on_delete=models.CASCADE, related_name='passed_alerts',
        verbose_name='Экзамен',
    )
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление о прошедшем экзамене'
        verbose_name_plural = 'Уведомления о прошедших экзаменах'
        constraints = [
            models.UniqueConstraint(fields=['exam'], name='unique_exam_passed_alert'),
        ]

    def __str__(self) -> str:
        return f'Группа {self.exam.group_number} — ГИБДД {self.exam.gibdd_date} ({self.notified_at:%Y-%m-%d})'


class PromoEventAlert(models.Model):
    """Отметка об отправке уведомления о событии акции: старт отложенной
    акции и предупреждение, что акция заканчивается (в последний будний день
    показа).

    Ключ уникальности включает дату события (starts_at или expires_at): запись
    акции (Announcement card_type='promo') правится на месте каждый месяц с новыми
    датами, и по новым датам уведомления должны срабатывать заново.
    """

    class EventType(models.TextChoices):
        STARTED = 'started', 'Акция стартовала'
        ENDING = 'ending', 'Акция заканчивается'

    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name='promo_event_alerts',
        verbose_name='Акция',
    )
    event_type = models.CharField('Событие', max_length=10, choices=EventType.choices)
    event_date = models.DateField('Дата события (starts_at / expires_at)')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление о событии акции'
        verbose_name_plural = 'Уведомления о событиях акций'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['announcement', 'event_type', 'event_date'],
                name='unique_promo_event_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.announcement.title} — {self.get_event_type_display()} {self.event_date:%Y-%m-%d}'


class ScheduleEndingAlert(models.Model):
    """Отметка об отправке предупреждения, что расписание занятий по предмету
    заканчивается (в последний будний день последнего занятия).

    Ключ включает дату последнего занятия: когда даты добавят и расписание
    снова подойдёт к концу, предупреждение придёт заново.
    """

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='schedule_ending_alerts',
        verbose_name='Подразделение',
    )
    subject = models.CharField('Предмет', max_length=20, choices=ClassSession.Subject.choices)
    last_date = models.DateField('Дата последнего занятия')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Предупреждение об окончании расписания'
        verbose_name_plural = 'Предупреждения об окончании расписания'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'subject', 'last_date'],
                name='unique_schedule_ending_alert',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'{self.department.name} — {self.get_subject_display()} '
            f'заканчивается {self.last_date:%Y-%m-%d}'
        )


class ExamEndingAlert(models.Model):
    """Отметка об отправке предупреждения, что предстоящие экзамены на сайте
    заканчиваются (в последний будний день последнего экзамена ГИБДД).
    """

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='exam_ending_alerts',
        verbose_name='Подразделение',
    )
    last_date = models.DateField('Дата последнего экзамена ГИБДД')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Предупреждение об окончании экзаменов'
        verbose_name_plural = 'Предупреждения об окончании экзаменов'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['department', 'last_date'],
                name='unique_exam_ending_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.department.name} — экзамены заканчиваются {self.last_date:%Y-%m-%d}'
