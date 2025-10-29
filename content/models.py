from django.db import models
from django.utils import timezone


class Department(models.Model):
    name = models.CharField('Подразделение', max_length=100)
    slug = models.SlugField('URL-часть', unique=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self):
        return self.name


class PageTemplate(models.Model):
    title = models.CharField('Название шаблона', max_length=100)
    slug = models.SlugField('Slug шаблона', unique=True)

    class Meta:
        verbose_name = 'Шаблон страницы'
        verbose_name_plural = 'Шаблоны страниц'

    def __str__(self):
        return self.title


class PageContent(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Подразделение')
    template = models.ForeignKey(PageTemplate, on_delete=models.CASCADE, verbose_name='Шаблон')
    content = models.TextField('Контент')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', default=timezone.now)
    updated_at = models.DateTimeField('Обновлён', default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:  # при создании
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Контент страницы'
        verbose_name_plural = 'Контент страниц'
        unique_together = ('department', 'template')

    def __str__(self):
        return f'{self.department} — {self.template}'