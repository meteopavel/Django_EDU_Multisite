from django.db import migrations


def fix_card_types(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')
    # "Занятия в автошколе!" должно быть в сетке (type=info), не на всю ширину
    Announcement.objects.filter(title='Занятия в автошколе!').update(card_type='info')


def reverse_fix(apps, schema_editor):
    Announcement = apps.get_model('content', 'Announcement')
    Announcement.objects.filter(title='Занятия в автошколе!').update(card_type='announcement')


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0045_announcement_irkutsk_promo'),
    ]

    operations = [
        migrations.RunPython(fix_card_types, reverse_fix),
    ]
