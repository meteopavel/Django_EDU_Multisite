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
    short_address = models.CharField('Короткий адрес', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    website = models.URLField('Сайт', blank=True)

    inn = models.CharField('ИНН', max_length=12, blank=True)
    kpp = models.CharField('КПП', max_length=15, blank=True)
    legal_address = models.TextField('Юридический адрес', blank=True)
    recipient_name = models.CharField('Наименование получателя', max_length=200, blank=True)
    bank = models.TextField('Банк получателя', blank=True)
    bik = models.CharField('БИК', max_length=9, blank=True)
    corr_account = models.CharField('Корр. счёт', max_length=20, blank=True)
    settlement_account = models.CharField('Расч. счёт', max_length=20, blank=True)
    payment_purpose = models.CharField('Назначение платежа', max_length=300, blank=True)

    schedule = models.JSONField('Режим работы', default=list, blank=True)

    map_center = models.JSONField(
        'Координаты центра (широта, долгота)',
        default=list,
        blank=True,
        help_text='Пример: [52.267482, 104.310026]'
    )
    map_iframes = models.JSONField('Ссылки на карты (Google Embed)', default=list, blank=True)

    show_latest_news = models.BooleanField('Показывать последние новости', default=True)
    show_services = models.BooleanField('Показывать услуги', default=False)
    show_partners = models.BooleanField('Показывать партнёров', default=False)
    show_documents = models.BooleanField('Показывать документы', default=True)
    show_contacts = models.BooleanField('Показывать контакты', default=True)
    show_header_banner = models.BooleanField('Показывать главный баннер', default=False)
    show_exam_info = models.BooleanField('Показывать акции и экзамены', default=False)
    show_education_info = models.BooleanField('Показывать сведения об образовательной организации', default=False)

    meta_title = models.CharField('SEO Title', max_length=100, blank=True)
    meta_description = models.CharField('SEO Description', max_length=255, blank=True)

    def get_section_flags(self):
        return {
            field.name: getattr(self, field.name)
            for field in self._meta.fields
            if field.name.startswith('show_')
        }

    class Meta:
        verbose_name = 'Детали подразделения'
        verbose_name_plural = 'Детали подразделений'

    def __str__(self):
        return f'Детали: {self.department.name}'


class Service(models.Model):
    SERVICE_TYPES = [
        ('parking', 'Автостоянка'),
        ('info_card', 'Информационная карточка (с описанием)'),
        ('custom', 'Произвольная услуга'),
    ]
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Подразделение'
    )
    name = models.CharField('Название услуги', max_length=200)
    points = models.JSONField(
        'Пункты (список строк)',
        default=list,
        blank=True,
        help_text='Пример: ["Автостраховка ОСАГО", "Автостраховка КАСКО"]'
    )
    slug = models.SlugField('URL-часть', max_length=200, blank=True)
    service_type = models.CharField(
        'Тип услуги',
        max_length=20,
        choices=SERVICE_TYPES,
        default='info_card'
    )
    icon_name = models.CharField(
        'Имя иконки (без расширения)',
        max_length=50,
        blank=True,
        help_text='Например: "taxi", "insurance", "appraisal"'
    )

    address = models.CharField('Адрес', max_length=300, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    map_center = models.JSONField('Координаты', default=list, blank=True)

    description_material = models.ForeignKey(
        'Material',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_in_services',
        verbose_name='Материал с описанием'
    )

    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['department', 'order', 'name']

    def __str__(self):
        return f'{self.name} ({self.department.name})'



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
    content = models.TextField('Текст новости', blank=True)

    main_image = models.ImageField('Главная картинка', upload_to='news/main/', blank=True, null=True)
    video = models.FileField('Видео', upload_to='news/videos/', blank=True, null=True)

    is_partner_news = models.BooleanField(
        'Партнёрская новость (отображается в секции "Партнёры")',
        default=False,
        help_text='Если отмечено — новость НЕ будет показываться в ленте новостей, '
                  'а только в блоке "Наши партнёры".'
    )

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

    SECTIONS = [
        ('education', 'Образование'),
        ('paid_services', 'Платные образовательные услуги'),
        ('finance', 'Финансово-хозяйственная деятельность'),
        ('mtob', 'Материально-техническое обеспечение'),
        ('structure', 'Структура и управление'),
        ('basic_info', 'Основные сведения'),
        ('other', 'Прочее'),
    ]

    title = models.CharField('Название документа', max_length=255)
    document_type = models.CharField(
        'Тип документа',
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        default='file'
    )
    display_in_sections = models.JSONField(
        'Отображать в разделах',
        default=list,
        blank=True,
        help_text='Выберите разделы, где документ будет отображаться'
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


class Material(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self):
        return self.title


class ContentBlock(models.Model):
    BLOCK_TYPES = [
        ('heading', 'Заголовок'),
        ('paragraph', 'Абзац'),
        ('list', 'Список'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('quote', 'Цитата'),
    ]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField('Тип блока', max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    # Для текстовых блоков
    text = models.TextField('Текст', blank=True)

    # Для списка
    items = models.JSONField('Элементы списка', default=list, blank=True)

    # Для медиа
    image = models.ImageField('Изображение', upload_to='materials/images/', blank=True)
    video = models.FileField('Видео', upload_to='materials/videos/', blank=True)
    video_url = models.URLField('Ссылка на видео (YouTube/Vimeo)', blank=True)

    class Meta:
        ordering = ['order']
