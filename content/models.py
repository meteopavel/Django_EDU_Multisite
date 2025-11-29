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


class DepartmentDetails(models.Model):
    department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='Подразделение'
    )

    address = models.TextField('Адрес', blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    website = models.URLField('Сайт', blank=True)

    inn = models.CharField('ИНН', max_length=12, blank=True)
    kpp = models.CharField('КПП', max_length=15, blank=True)
    legal_address = models.TextField('Юридический адрес', blank=True)

    meta_title = models.CharField('SEO Title', max_length=100, blank=True)
    meta_description = models.CharField('SEO Description', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Детали подразделения'
        verbose_name_plural = 'Детали подразделений'

    def __str__(self):
        return f'Детали: {self.department.name}'


class MenuItem(models.Model):
    title = models.CharField('Название пункта', max_length=100)
    url = models.CharField('URL (относительный)', max_length=200)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    departments = models.ManyToManyField(
        Department,
        related_name='menu_items',
        verbose_name='Подразделения',
        blank=True,
        help_text='Выберите, в каких подразделениях будет отображаться этот пункт. Оставьте пустым — чтобы показывать во всех.'
    )

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'title']

    def __str__(self):
        if self.departments.exists():
            deps = ', '.join(d.name for d in self.departments.all())
            return f'{self.title} ({deps})'
        return f'{self.title} (все подразделения)'


class NewsImage(models.Model):
    news = models.ForeignKey(
        'News',
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Новость'
    )
    image = models.ImageField('Изображение', upload_to='news/gallery/')
    description = models.CharField('Описание', max_length=255, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Изображение для галереи'
        verbose_name_plural = 'Изображения для галереи'

    def __str__(self):
        return self.description or f'Изображение {self.pk}'


class News(models.Model):
    joomla_id = models.IntegerField('ID из Joomla', unique=True, null=True, blank=True)
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('URL', unique=True, max_length=255)
    preview_text = models.TextField('Краткое описание', blank=True)
    content = models.TextField('Текст новости')

    main_image = models.ImageField('Главная картинка', upload_to='news/main/', blank=True, null=True)
    video = models.FileField('Видео', upload_to='news/videos/', blank=True, null=True)

    departments = models.ManyToManyField(
        'Department',
        related_name='news',
        blank=True,
        help_text='Оставьте пустым — будет отображаться во всех подразделениях'
    )

    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата публикации')

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DocumentCategory(models.Model):
    name = models.CharField('Название категории', max_length=200, unique=True)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория документа'
        verbose_name_plural = 'Категории документов'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('file', 'Файл (PDF/изображение)'),
        ('external', 'Внешняя ссылка'),
        ('info', 'Информационный пункт (без файла)'),
    ]

    title = models.CharField('Название документа', max_length=255)
    document_type = models.CharField(
        'Тип документа',
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        default='file'
    )
    file = models.FileField('Файл', upload_to='documents/', blank=True, null=True)
    external_url = models.URLField('Внешняя ссылка', blank=True)
    file_type = models.CharField('Тип файла', max_length=10, choices=[
        ('pdf', 'PDF'),
        ('image', 'Изображение'),
    ], blank=True)
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Категория'
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Подразделение'
    )

    order = models.PositiveSmallIntegerField('Порядок в категории', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата добавления', default=timezone.now)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['department', 'category__order', 'order', 'title']

    def __str__(self):
        return f"{self.title} ({self.department.name})"

    def get_display_url(self):
        """Возвращает URL для отображения в шаблоне."""
        if self.document_type == 'file' and self.file:
            return self.file.url
        elif self.document_type == 'external' and self.external_url:
            return self.external_url
        return None

    def is_external(self):
        return self.document_type == 'external'

    def is_info_only(self):
        return self.document_type == 'info'

    def save(self, *args, **kwargs):
        if self.document_type == 'file' and self.file:
            ext = self.file.name.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                self.file_type = 'image'
            elif ext == 'pdf':
                self.file_type = 'pdf'
            else:
                self.file_type = ''
        else:
            self.file_type = ''
        super().save(*args, **kwargs)
