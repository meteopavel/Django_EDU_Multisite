from django.db import migrations


def add_announcements(apps, schema_editor):
    Department = apps.get_model('content', 'Department')
    Announcement = apps.get_model('content', 'Announcement')

    try:
        irkutsk = Department.objects.get(slug='irkutsk')

        Announcement.objects.create(
            department=irkutsk,
            card_type='info',
            title='СРОЧНО!',
            text=(
                '<p><strong style="color: #C30027;">ПРИНИМАЕМ УЧЕНИКОВ ДРУГИХ АВТОШКОЛ НА СДАЧУ ЭКЗАМЕНА В ГИБДД!</strong></p>'
                '<p><strong>ТАК ВЫ БЫСТРЕЕ ПОПАДЕТЕ НА ЭКЗАМЕН!</strong></p>'
                '<p><strong>НОВЫЙ АВТОПАРК И ОПЫТНЫЕ ИНСТРУКТОРА!</strong></p>'
                '<p><strong>ДОСТУПНЫЕ ЦЕНЫ!</strong></p>'
            ),
            is_active=True,
            order=1,
        )

        Announcement.objects.create(
            department=irkutsk,
            card_type='announcement',
            title='Занятия в автошколе!',
            text=(
                '<p>14 июня с 9:00 до 12:00 в Автошколе будут проводиться занятия по <strong>Психологии</strong></p>'
                '<p>18 июня с 17:00 до 20:00 в Автошколе будут проводиться занятия по <strong>Медицине</strong></p>'
                '<p>Запись на занятия по телефону <strong>22-40-50</strong> либо при посещении офиса Автошколы</p>'
            ),
            is_active=True,
            order=2,
        )

    except Department.DoesNotExist:
        pass

    try:
        ustkut = Department.objects.get(slug='ustkut')

        Announcement.objects.create(
            department=ustkut,
            card_type='promo',
            title='ПОДАРОЧНЫЕ СЕРТИФИКАТЫ НА ОБУЧЕНИЕ ВОЖДЕНИЮ!',
            text=(
                '<p style="color: #666;">Подарите близким и любимым не очередной сувенир, '
                'а настоящую независимость и уверенность за рулём!</p>'
                '<ul>'
                '<li><strong style="color: #28a745;">✓ Практичный</strong> — навык на всю жизнь</li>'
                '<li><strong style="color: #28a745;">✓ Эмоциональный</strong> — первые самостоятельные поездки не забываются</li>'
                '<li><strong style="color: #28a745;">✓ Персональный</strong> — можно выбрать удобное время обучения</li>'
                '<li><strong style="color: #28a745;">✓ Универсальный</strong> — подходит и мужчинам, и женщинам</li>'
                '<li><strong style="color: #28a745;">✓ Профессиональный</strong> — получите профессию водителя</li>'
                '</ul>'
                '<p><strong>Современные автомобили, опытные инструктора, удобный график занятий</strong> — '
                'всё, чтобы уверенно получить права и сесть за руль.</p>'
                '<p style="color: #C30027;"><strong>Количество сертификатов ограничено — успейте порадовать близких!</strong></p>'
                '<p><strong>Тел.</strong> 89041197431 &nbsp;&nbsp; <strong>ул. Речников, 39</strong></p>'
            ),
            image='ads-ustkut.jpg',
            is_active=True,
            order=1,
        )

    except Department.DoesNotExist:
        pass


def remove_announcements(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')
    Announcement.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0043_announcement_model'),
    ]

    operations = [
        migrations.RunPython(add_announcements, remove_announcements),
    ]
