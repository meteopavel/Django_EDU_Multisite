"""
Проверяет контент сайта на события, о которых надо уведомить чат заказчиков
в MAX: окончания расписания занятий (психология/медицина) и предстоящих
экзаменов ГИБДД (предупреждение накануне, в последний будний день), прошедшие
экзамены в ГИБДД, старт и окончание акций.

Должна отправляться в 10:00 по Иркутску, только в будние дни. Чтобы не зависеть
от таймзоны, в которой настроен cron на сервере, команда сама проверяет текущее
время по Asia/Irkutsk (settings.TIME_ZONE) и ничего не делает вне этого окна —
предполагается, что cron запускает её каждый час (или чаще), а фильтрация
времени/дня происходит здесь.
"""

from __future__ import annotations

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import Announcement, ClassSession, Department, ExamInfo
from core.max_bot import MaxBotError, send_message
from schedule_alerts.models import (
    ClassScheduleAlert,
    ExamEndingAlert,
    ExamPassedAlert,
    PromoEventAlert,
    ScheduleEndingAlert,
)

NOTIFY_HOUR = 10  # по Asia/Irkutsk (settings.TIME_ZONE)

WEEKDAYS_RU = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница',
               'суббота', 'воскресенье']  # индекс = date.weekday()


def is_first_weekday_after(trigger: date, today: date) -> bool:
    """True, если сегодня — первый будний день не раньше trigger: все дни от
    trigger (включительно) до сегодня (не включая) были выходными.

    Уведомления ходят только в будние, поэтому событие алертится в первый
    будний запуск после своей даты — и никогда позже: новость на день позже
    уже не новость. Выходные при этом не теряются: суббота/воскресенье
    догоняются в понедельник.
    """
    day = trigger
    while day < today:
        if day.weekday() < 5:
            return False
        day += timedelta(days=1)
    return True


def next_weekday_after(day: date) -> date:
    """Следующий будний день после day (после пятницы — понедельник)."""
    return day + timedelta(days=3 if day.weekday() == 4 else 1)


def is_last_weekday(last_date: date, today: date) -> bool:
    """Сегодня — последний будний день перед окончанием чего-либо (акции,
    расписания, экзаменов): конец сегодня (будний день) или в ближайшие
    выходные — тогда предупреждаем в пятницу, чтобы у заказчика было время
    подготовить обновление."""
    return today <= last_date < next_weekday_after(today)


class Command(BaseCommand):
    help = (
        'Уведомляет в MAX об устаревшем расписании занятий, прошедших '
        'экзаменах ГИБДД и старте/окончании акций'
    )

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
        self.check_stale_class_sessions(today)
        self.check_passed_exams(today)
        self.check_exam_endings(today)
        self.check_promo_events(today)

    def send(self, text: str) -> bool:
        """Отправляет сообщение в MAX; False — если не удалось."""
        try:
            send_message(text)
        except MaxBotError as exc:
            self.stderr.write(f'Не удалось отправить уведомление в MAX: {exc}')
            return False
        return True

    def check_stale_class_sessions(self, today: date) -> None:
        """Расписание занятий (психология/медицина): предупреждение, что оно
        заканчивается (в последний будний день последнего занятия), а если
        будущих дат не осталось — повторное уведомление по факту."""
        departments = Department.objects.filter(is_active=True)

        for department in departments:
            for subject, subject_label in ClassSession.Subject.choices:
                sessions = ClassSession.objects.filter(department=department, subject=subject)
                if not sessions.exists():
                    continue  # подразделение не пользуется этим расписанием

                last_session = sessions.filter(date__gte=today).order_by('-date').first()
                alert = ClassScheduleAlert.objects.filter(department=department, subject=subject).first()

                if last_session:
                    if alert:
                        alert.delete()  # даты появились — «закончились» снято

                    last_date = last_session.date
                    if is_last_weekday(last_date, today) and not ScheduleEndingAlert.objects.filter(
                        department=department, subject=subject, last_date=last_date,
                    ).exists():
                        if last_date == today:
                            tail = f'сегодня ({last_date:%d.%m.%Y})'
                        else:
                            tail = f'в {WEEKDAYS_RU[last_date.weekday()]} {last_date:%d.%m.%Y}'
                        text = (
                            f'⏰ «{department.name}»: последнее занятие по предмету '
                            f'«{subject_label}» — {tail}. Новых дат после него не запланировано.'
                        )
                        if self.send(text):
                            ScheduleEndingAlert.objects.create(
                                department=department, subject=subject, last_date=last_date,
                            )
                            self.stdout.write(
                                f'Отправлено уведомление: расписание {department.name} / {subject_label} заканчивается'
                            )
                    continue

                if alert:
                    continue  # уже уведомляли, ждём пока добавят новые даты

                text = (
                    f'⚠️ «{department.name}»: закончились будущие даты занятий '
                    f'по предмету «{subject_label}».'
                )
                if self.send(text):
                    ClassScheduleAlert.objects.create(department=department, subject=subject)
                    self.stdout.write(f'Отправлено уведомление: {department.name} / {subject_label}')

    def check_passed_exams(self, today: date) -> None:
        """Дата экзамена в ГИБДД прошла — сообщить, сколько предстоящих
        экзаменов ещё показано на сайте (и для каких групп)."""
        exams = ExamInfo.objects.filter(gibdd_date__isnull=False, gibdd_date__lt=today)

        for exam in exams:
            if ExamPassedAlert.objects.filter(exam=exam).exists():
                continue  # уже уведомляли

            # Экзамен «прошёл» начиная со дня, следующего за gibdd_date.
            if not is_first_weekday_after(exam.gibdd_date + timedelta(days=1), today):
                continue  # будний день после экзамена уже был — новость протухла

            # Зеркально фильтру сайта (home_view / ajax_exam_info): предстоящие —
            # только записи с заполненной будущей датой ГИБДД.
            upcoming = ExamInfo.objects.filter(
                department=exam.department, gibdd_date__isnull=False, gibdd_date__gte=today,
            )
            if upcoming.exists():
                groups = ', '.join(str(item.group_number) for item in upcoming)
                remaining = f'Предстоящих экзаменов на сайте: {upcoming.count()} — группы {groups}.'
            else:
                remaining = 'Предстоящих экзаменов на сайте не осталось.'

            text = (
                f'🏁 В группе {exam.group_number} прошёл экзамен в ГИБДД '
                f'({exam.gibdd_date:%d.%m.%Y}). {remaining}'
            )
            if self.send(text):
                ExamPassedAlert.objects.create(exam=exam)
                self.stdout.write(f'Отправлено уведомление: экзамен ГИБДД группы {exam.group_number} прошёл')

    def check_exam_endings(self, today: date) -> None:
        """Последний предстоящий экзамен ГИБДД на сайте — предупредить в его
        последний будний день, что после него раздел опустеет."""
        for department in Department.objects.filter(is_active=True):
            upcoming = ExamInfo.objects.filter(
                department=department, gibdd_date__isnull=False, gibdd_date__gte=today,
            ).order_by('gibdd_date', 'group_number')
            if not upcoming.exists():
                continue

            last_date = upcoming.last().gibdd_date
            if not is_last_weekday(last_date, today):
                continue
            if ExamEndingAlert.objects.filter(department=department, last_date=last_date).exists():
                continue  # уже уведомляли

            groups = ', '.join(
                str(exam.group_number) for exam in upcoming if exam.gibdd_date == last_date
            )
            if last_date == today:
                tail = f'сегодня ({last_date:%d.%m.%Y})'
            else:
                tail = f'в {WEEKDAYS_RU[last_date.weekday()]} {last_date:%d.%m.%Y}'
            text = (
                f'🏁 Последний предстоящий экзамен — {tail}, группы {groups}. '
                f'После этого предстоящих экзаменов на сайте не останется.'
            )
            if self.send(text):
                ExamEndingAlert.objects.create(department=department, last_date=last_date)
                self.stdout.write(
                    f'Отправлено уведомление: предстоящие экзамены {department.name} заканчиваются'
                )

    def check_promo_events(self, today: date) -> None:
        """Старт отложенной акции (наступил starts_at) и предупреждение, что
        акция заканчивается (в её последний будний день показа) — с названием
        акции из Announcement.title."""
        promos = Announcement.objects.filter(is_active=True, card_type=Announcement.CardType.PROMO)

        for promo in promos:
            if (
                promo.starts_at is not None
                and promo.starts_at <= today
                and is_first_weekday_after(promo.starts_at, today)
                and not PromoEventAlert.objects.filter(
                    announcement=promo, event_type=PromoEventAlert.EventType.STARTED,
                    event_date=promo.starts_at,
                ).exists()
            ):
                text = f'🚀 Стартовала отложенная акция: «{promo.title}»'
                if promo.expires_at is not None:
                    text += f' (до {promo.expires_at:%d.%m.%Y} включительно)'
                text += '.'
                if self.send(text):
                    PromoEventAlert.objects.create(
                        announcement=promo, event_type=PromoEventAlert.EventType.STARTED,
                        event_date=promo.starts_at,
                    )
                    self.stdout.write(f'Отправлено уведомление: акция стартовала — {promo.title}')

            if (
                promo.expires_at is not None
                and is_last_weekday(promo.expires_at, today)
                and not PromoEventAlert.objects.filter(
                    announcement=promo, event_type=PromoEventAlert.EventType.ENDING,
                    event_date=promo.expires_at,
                ).exists()
            ):
                if promo.expires_at == today:
                    tail = f'сегодня последний день показа ({promo.expires_at:%d.%m.%Y})'
                else:
                    weekday = WEEKDAYS_RU[promo.expires_at.weekday()]
                    tail = f'последний день показа — в {weekday} {promo.expires_at:%d.%m.%Y}'
                text = (
                    f'🏁 Заканчивается акция: «{promo.title}» — {tail}. '
                    f'После этого баннер и цены на сайте вернутся к обычному виду.'
                )
                if self.send(text):
                    PromoEventAlert.objects.create(
                        announcement=promo, event_type=PromoEventAlert.EventType.ENDING,
                        event_date=promo.expires_at,
                    )
                    self.stdout.write(f'Отправлено уведомление: акция заканчивается — {promo.title}')
