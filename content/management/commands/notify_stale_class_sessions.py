"""
Проверяет расписание занятий (психология/медицина) на устаревание и шлёт
уведомление в MAX-чат заказчиков, если у подразделения закончились
будущие даты по предмету, которым оно пользуется.

Должна отправляться в 10:00 по Иркутску, только в будние дни. Чтобы не зависеть
от таймзоны, в которой настроен cron на сервере, команда сама проверяет текущее
время по Asia/Irkutsk (settings.TIME_ZONE) и ничего не делает вне этого окна —
предполагается, что cron запускает её каждый час (или чаще), а фильтрация
времени/дня происходит здесь.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import ClassScheduleAlert, ClassSession, Department
from core.max_bot import MaxBotError, send_message

NOTIFY_HOUR = 10  # по Asia/Irkutsk (settings.TIME_ZONE)


class Command(BaseCommand):
    help = 'Уведомляет в MAX о подразделениях без будущих занятий по психологии/медицине'

    def add_arguments(self, parser: object) -> None:
        parser.add_argument(
            '--force', action='store_true',
            help='Игнорировать проверку времени/дня недели (для ручного запуска и тестов).',
        )

    def handle(self, *args: object, **options: object) -> None:
        now = timezone.localtime()
        if not options['force'] and (now.hour != NOTIFY_HOUR or now.weekday() >= 5):
            return

        today = timezone.localdate()
        departments = Department.objects.filter(is_active=True)

        for department in departments:
            for subject, subject_label in ClassSession.Subject.choices:
                sessions = ClassSession.objects.filter(department=department, subject=subject)
                if not sessions.exists():
                    continue  # подразделение не пользуется этим расписанием

                has_future = sessions.filter(date__gte=today).exists()
                alert = ClassScheduleAlert.objects.filter(department=department, subject=subject).first()

                if has_future:
                    if alert:
                        alert.delete()
                    continue

                if alert:
                    continue  # уже уведомляли, ждём пока добавят новые даты

                text = (
                    f'⚠️ «{department.name}»: закончились будущие даты занятий по предмету '
                    f'«{subject_label}». Добавьте новые даты в админке (ClassSession).'
                )
                try:
                    send_message(text)
                except MaxBotError as exc:
                    self.stderr.write(f'Не удалось отправить уведомление в MAX: {exc}')
                    continue

                ClassScheduleAlert.objects.create(department=department, subject=subject)
                self.stdout.write(f'Отправлено уведомление: {department.name} / {subject_label}')
