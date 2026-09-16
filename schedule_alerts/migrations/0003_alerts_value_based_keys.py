# Перевод отметок дедупа со связей на контент (FK каскадно удалялись при
# деплой-перезаливе контента, из-за чего уведомления повторялись после каждого
# деплоя) на значимые ключи: слаг подразделения + предмет/группа/дата.
#
# Таблицы пересоздаются целиком (а не альтерятся): MySQL не даёт дропнуть
# unique-индекс, пока на него опирается FK-ограничение (ошибка 1553), а
# построчный перенос этой зависимости не стоит усложнения. Отметки — данные
# возрастом в дни, поэтому после пересоздания состояние дедупа восстанавливается
# из текущего контента: устаревшим расписаниям и прошедшим экзаменам отметки
# создаются сразу, чтобы после фикса не повторялись уже отправленные уведомления.

from django.db import migrations, models
from django.utils import timezone


def seed(apps, schema_editor):
    Department = apps.get_model('content', 'Department')
    ClassSession = apps.get_model('content', 'ClassSession')
    ExamInfo = apps.get_model('content', 'ExamInfo')
    ClassScheduleAlert = apps.get_model('schedule_alerts', 'ClassScheduleAlert')
    ExamPassedAlert = apps.get_model('schedule_alerts', 'ExamPassedAlert')

    today = timezone.localtime().date()
    for department in Department.objects.filter(is_active=True):
        for subject in ('psychology', 'medicine'):
            has_sessions = ClassSession.objects.filter(
                department=department, subject=subject,
            ).exists()
            has_future = ClassSession.objects.filter(
                department=department, subject=subject, date__gte=today,
            ).exists()
            if has_sessions and not has_future:
                ClassScheduleAlert.objects.create(department_slug=department.slug, subject=subject)

    for exam in ExamInfo.objects.filter(gibdd_date__isnull=False, gibdd_date__lt=today):
        ExamPassedAlert.objects.create(
            department_slug=exam.department.slug,
            group_number=exam.group_number, gibdd_date=exam.gibdd_date,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0056_delete_classschedulealert'),
        ('schedule_alerts', '0002_auto_20260908_1542'),
    ]

    operations = [
        migrations.DeleteModel(name='ClassScheduleAlert'),
        migrations.DeleteModel(name='ExamPassedAlert'),
        migrations.DeleteModel(name='PromoEventAlert'),
        migrations.DeleteModel(name='ScheduleEndingAlert'),
        migrations.DeleteModel(name='ExamEndingAlert'),
        migrations.CreateModel(
            name='ClassScheduleAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_slug', models.CharField(max_length=50, verbose_name='Слаг подразделения')),
                ('subject', models.CharField(choices=[('psychology', 'Психология'), ('medicine', 'Медицина')], max_length=20, verbose_name='Предмет')),
                ('notified_at', models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')),
            ],
            options={
                'verbose_name': 'Уведомление об устаревшем расписании',
                'verbose_name_plural': 'Уведомления об устаревшем расписании',
            },
        ),
        migrations.CreateModel(
            name='ExamPassedAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_slug', models.CharField(max_length=50, verbose_name='Слаг подразделения')),
                ('group_number', models.PositiveSmallIntegerField(verbose_name='Номер группы')),
                ('gibdd_date', models.DateField(verbose_name='Дата экзамена в ГИБДД')),
                ('notified_at', models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')),
            ],
            options={
                'verbose_name': 'Уведомление о прошедшем экзамене',
                'verbose_name_plural': 'Уведомления о прошедших экзаменах',
            },
        ),
        migrations.CreateModel(
            name='PromoEventAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_slug', models.CharField(max_length=50, verbose_name='Слаг подразделения')),
                ('promo_title', models.CharField(max_length=255, verbose_name='Название акции')),
                ('event_type', models.CharField(choices=[('started', 'Акция стартовала'), ('ending', 'Акция заканчивается')], max_length=10, verbose_name='Событие')),
                ('event_date', models.DateField(verbose_name='Дата события (starts_at / expires_at)')),
                ('notified_at', models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')),
            ],
            options={
                'verbose_name': 'Уведомление о событии акции',
                'verbose_name_plural': 'Уведомления о событиях акций',
                'ordering': ['-notified_at'],
            },
        ),
        migrations.CreateModel(
            name='ScheduleEndingAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_slug', models.CharField(max_length=50, verbose_name='Слаг подразделения')),
                ('subject', models.CharField(choices=[('psychology', 'Психология'), ('medicine', 'Медицина')], max_length=20, verbose_name='Предмет')),
                ('last_date', models.DateField(verbose_name='Дата последнего занятия')),
                ('notified_at', models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')),
            ],
            options={
                'verbose_name': 'Предупреждение об окончании расписания',
                'verbose_name_plural': 'Предупреждения об окончании расписания',
                'ordering': ['-notified_at'],
            },
        ),
        migrations.CreateModel(
            name='ExamEndingAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_slug', models.CharField(max_length=50, verbose_name='Слаг подразделения')),
                ('last_date', models.DateField(verbose_name='Дата последнего экзамена ГИБДД')),
                ('notified_at', models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')),
            ],
            options={
                'verbose_name': 'Предупреждение об окончании экзаменов',
                'verbose_name_plural': 'Предупреждения об окончании экзаменов',
                'ordering': ['-notified_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='classschedulealert',
            constraint=models.UniqueConstraint(fields=('department_slug', 'subject'), name='unique_class_schedule_alert'),
        ),
        migrations.AddConstraint(
            model_name='exampassedalert',
            constraint=models.UniqueConstraint(fields=('department_slug', 'group_number', 'gibdd_date'), name='unique_exam_passed_alert'),
        ),
        migrations.AddConstraint(
            model_name='promoeventalert',
            constraint=models.UniqueConstraint(fields=('department_slug', 'event_type', 'event_date'), name='unique_promo_event_alert'),
        ),
        migrations.AddConstraint(
            model_name='scheduleendingalert',
            constraint=models.UniqueConstraint(fields=('department_slug', 'subject', 'last_date'), name='unique_schedule_ending_alert'),
        ),
        migrations.AddConstraint(
            model_name='examendingalert',
            constraint=models.UniqueConstraint(fields=('department_slug', 'last_date'), name='unique_exam_ending_alert'),
        ),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
