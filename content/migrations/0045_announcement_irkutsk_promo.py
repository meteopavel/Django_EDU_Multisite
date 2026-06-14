from django.db import migrations


def add_irkutsk_promo(apps, schema_editor):
    Department = apps.get_model('content', 'Department')
    Announcement = apps.get_model('content', 'Announcement')

    try:
        irkutsk = Department.objects.get(slug='irkutsk')
    except Department.DoesNotExist:
        return

    Announcement.objects.create(
        department=irkutsk,
        card_type='promo',
        title='АКЦИЯ ДО 10 ИЮНЯ: ТЕОРИЯ БЕСПЛАТНО!',
        text=(
            '<p style="color: #666;">Начните обучение в Автошколе ВОА уже сейчас! '
            '<strong>Только до 10 июня 2026 года</strong> мы полностью оплачиваем теоретический курс за вас.</p>'
            '<p style="color: #C30027; font-weight: bold; font-size: 1.3em;">Ваша выгода — 8000 рублей!</p>'
            '<ul>'
            '<li><strong style="color: #28a745;">Теория бесплатно</strong> — мы оплачиваем теоретический курс за вас</li>'
            '<li><strong style="color: #28a745;">Выгодный старт</strong> — начните обучение без лишних затрат</li>'
            '<li><strong style="color: #28a745;">Больше практики</strong> — сэкономленные деньги можно направить на дополнительные часы вождения</li>'
            '</ul>'
            '<p style="padding: 10px; background: #f8f9fa; border-left: 4px solid #C30027; border-radius: 4px;">'
            '<strong>Успейте записаться до 10.06.2026!</strong><br>'
            'Количество мест по акции ограничено.'
            '</p>'
        ),
        image='ads-irkutsk-2.jpg',
        is_active=True,
        order=0,
    )

    Announcement.objects.create(
        department=irkutsk,
        card_type='announcement',
        title='Режим работы в праздничные дни',
        text=(
            '<p>1, 2, 3, 9, 10, 11 мая — не рабочие дни</p>'
            '<p>4, 5, 6, 7, 8 мая — рабочие дни</p>'
            '<p>8 мая работаем до 18:00</p>'
            '<p>С 12 мая Автошкола ВОА работает по расписанию.</p>'
            '<p style="color: #666;">Желающим записаться на вождение на майские праздники, '
            'просьба произвести оплату заблаговременно.</p>'
            '<p style="color: #666;">Запись на вождения производится в соответствии с графиками.</p>'
            '<hr style="margin: 12px 0; border-color: #eee;">'
            '<p><strong>Занятия по теории:</strong></p>'
            '<p>02.05.2026 — по расписанию в 9:00</p>'
            '<p>09.05.2026 — занятий не будет.</p>'
        ),
        is_active=True,
        order=3,
    )


def remove_irkutsk_promo(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')
    Announcement.objects.filter(
        title__in=['АКЦИЯ ДО 10 ИЮНЯ: ТЕОРИЯ БЕСПЛАТНО!', 'Режим работы в праздничные дни']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0044_announcement_initial_data'),
    ]

    operations = [
        migrations.RunPython(add_irkutsk_promo, remove_irkutsk_promo),
    ]
