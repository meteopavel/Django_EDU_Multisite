from datetime import date
from django.db import migrations


def set_expiry_dates(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')

    # Занятия в автошколе: последняя дата 18 июня 2026
    Announcement.objects.filter(title='Занятия в автошколе!').update(expires_at=date(2026, 6, 19))

    # Режим работы в праздничные дни: актуально до 12 мая 2026
    Announcement.objects.filter(title='Режим работы в праздничные дни').update(expires_at=date(2026, 5, 13))

    # Акция, Сертификат, СРОЧНО! — бессрочно (expires_at=NULL, уже так)


def reverse_expiry(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')
    Announcement.objects.all().update(expires_at=None)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0047_announcement_expires_at'),
    ]

    operations = [
        migrations.RunPython(set_expiry_dates, reverse_expiry),
    ]
