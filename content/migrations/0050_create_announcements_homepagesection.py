from django.db import migrations


def create_announcements_sections(apps, schema_editor):
    HomePageSection = apps.get_model('content', 'HomePageSection')

    # Для каждого подразделения, у которого есть EXAM_INFO,
    # добавляем ANNOUNCEMENTS прямо перед ней (order - 1)
    exam_sections = HomePageSection.objects.filter(section_key='exam_info')
    for exam_section in exam_sections:
        # Освобождаем место: сдвигаем exam_info на 1 вперёд
        exam_order = exam_section.order
        exam_section.order = exam_order + 1
        exam_section.save()

        HomePageSection.objects.get_or_create(
            department=exam_section.department,
            section_key='announcements',
            defaults={
                'is_enabled': True,
                'order': exam_order,
            },
        )


def remove_announcements_sections(apps, schema_editor):
    HomePageSection = apps.get_model('content', 'HomePageSection')
    # Восстанавливаем порядок exam_info
    for ann_section in HomePageSection.objects.filter(section_key='announcements'):
        exam_section = HomePageSection.objects.filter(
            department=ann_section.department, section_key='exam_info'
        ).first()
        if exam_section:
            exam_section.order = ann_section.order
            exam_section.save()
    HomePageSection.objects.filter(section_key='announcements').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0049_add_announcements_section'),
    ]

    operations = [
        migrations.RunPython(create_announcements_sections, remove_announcements_sections),
    ]
