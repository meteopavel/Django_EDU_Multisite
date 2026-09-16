from __future__ import annotations

from django.db import models

from content.models import ClassSession

# Все отметки дедупа хранятся значениями (слаг подразделения, предмет,
# номера групп, даты) — без FK на модели приложения content: при деплое
# контент перезаливается фикстурой, и FK-связи каскадно удаляли бы отметки
# вместе с контентом, из-за чего отправленные уведомления повторялись после
# каждого деплоя.


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

    department_slug = models.CharField('Слаг подразделения', max_length=50)
    subject = models.CharField('Предмет', max_length=20, choices=ClassSession.Subject.choices)
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление об устаревшем расписании'
        verbose_name_plural = 'Уведомления об устаревшем расписании'
        constraints = [
            models.UniqueConstraint(fields=['department_slug', 'subject'], name='unique_class_schedule_alert'),
        ]

    def __str__(self) -> str:
        return f'{self.department_slug} — {self.get_subject_display()} ({self.notified_at:%Y-%m-%d})'


class ExamPassedAlert(models.Model):
    """Отметка об отправке уведомления «в группе прошёл экзамен в ГИБДД» по
    конкретному экзамену — группе с датой ГИБДД (чтобы не слать повторно).
    """

    department_slug = models.CharField('Слаг подразделения', max_length=50)
    group_number = models.PositiveSmallIntegerField('Номер группы')
    gibdd_date = models.DateField('Дата экзамена в ГИБДД')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление о прошедшем экзамене'
        verbose_name_plural = 'Уведомления о прошедших экзаменах'
        constraints = [
            models.UniqueConstraint(
                fields=['department_slug', 'group_number', 'gibdd_date'],
                name='unique_exam_passed_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.department_slug} — группа {self.group_number}, ГИБДД {self.gibdd_date:%Y-%m-%d}'


class PromoEventAlert(models.Model):
    """Отметка об отправке уведомления о событии акции: старт отложенной
    акции и предупреждение, что акция заканчивается (в последний будний день
    показа).

    Ключ уникальности включает дату события (starts_at или expires_at): запись
    акции (Announcement card_type='promo') правится на месте каждый месяц с новыми
    датами, и по новым датам уведомления должны срабатывать заново. Название
    акции хранится копией только для читаемости, в ключ не входит.
    """

    class EventType(models.TextChoices):
        STARTED = 'started', 'Акция стартовала'
        ENDING = 'ending', 'Акция заканчивается'

    department_slug = models.CharField('Слаг подразделения', max_length=50)
    promo_title = models.CharField('Название акции', max_length=255)
    event_type = models.CharField('Событие', max_length=10, choices=EventType.choices)
    event_date = models.DateField('Дата события (starts_at / expires_at)')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление о событии акции'
        verbose_name_plural = 'Уведомления о событиях акций'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['department_slug', 'event_type', 'event_date'],
                name='unique_promo_event_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.promo_title} — {self.get_event_type_display()} {self.event_date:%Y-%m-%d}'


class ScheduleEndingAlert(models.Model):
    """Отметка об отправке предупреждения, что расписание занятий по предмету
    заканчивается (в последний будний день последнего занятия).

    Ключ включает дату последнего занятия: когда даты добавят и расписание
    снова подойдёт к концу, предупреждение придёт заново.
    """

    department_slug = models.CharField('Слаг подразделения', max_length=50)
    subject = models.CharField('Предмет', max_length=20, choices=ClassSession.Subject.choices)
    last_date = models.DateField('Дата последнего занятия')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Предупреждение об окончании расписания'
        verbose_name_plural = 'Предупреждения об окончании расписания'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['department_slug', 'subject', 'last_date'],
                name='unique_schedule_ending_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.department_slug} — {self.get_subject_display()} заканчивается {self.last_date:%Y-%m-%d}'


class ExamEndingAlert(models.Model):
    """Отметка об отправке предупреждения, что предстоящие экзамены на сайте
    заканчиваются (в последний будний день последнего экзамена ГИБДД).
    """

    department_slug = models.CharField('Слаг подразделения', max_length=50)
    last_date = models.DateField('Дата последнего экзамена ГИБДД')
    notified_at = models.DateTimeField('Отправлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Предупреждение об окончании экзаменов'
        verbose_name_plural = 'Предупреждения об окончании экзаменов'
        ordering = ['-notified_at']
        constraints = [
            models.UniqueConstraint(
                fields=['department_slug', 'last_date'],
                name='unique_exam_ending_alert',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.department_slug} — экзамены заканчиваются {self.last_date:%Y-%m-%d}'
