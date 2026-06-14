"""
Модели контентной и справочной структуры сайта.

Модуль содержит сущности для:
- подразделений и их реквизитов;
- секций главной страницы;
- услуг, меню, новостей и документов;
- материалов и блоков контента;
- экзаменационной информации.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from django.db import models
from django.utils import timezone

from .constants import EDUCATION_SECTION_CHOICES


class Department(models.Model):
    """Подразделение организации, к которому привязываются контент и данные."""

    name = models.CharField('Подразделение', max_length=100)
    slug = models.SlugField('URL-часть', unique=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'

    def __str__(self) -> str:
        """Возвращает название подразделения."""
        return self.name


class DepartmentDetails(models.Model):
    """Расширенные реквизиты, контакты и SEO-данные подразделения."""

    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name='details',
                                      verbose_name='Подразделение')
    address = models.TextField('Адрес', blank=True)
    short_address = models.CharField('Короткий адрес', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    cellphone = models.CharField('Сотовый телефон', max_length=50, blank=True)
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
    map_center = models.JSONField('Координаты центра (широта, долгота)', default=list, blank=True,
                                  help_text='Пример: [52.267482, 104.310026]')
    map_iframes = models.JSONField('Ссылки на карты (Google Embed)', default=list, blank=True)
    meta_title = models.CharField('SEO Title', max_length=100, blank=True)
    meta_description = models.CharField('SEO Description', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Детали подразделения'
        verbose_name_plural = 'Детали подразделений'

    def __str__(self) -> str:
        """Возвращает краткое представление деталей подразделения."""
        return f'Детали: {self.department.name}'


class HomeSectionChoices(models.TextChoices):
    """Ключи секций главной страницы подразделения."""

    HEADER_BANNER = 'header_banner', 'Главный баннер'
    ANNOUNCEMENTS = 'announcements', 'Объявления и акции'
    EXAM_INFO = 'exam_info', 'Экзамены и карточки'
    LATEST_NEWS = 'latest_news', 'Последние новости'
    PRICING = 'pricing', 'Стоимость'
    EDUCATION_INFO = 'education_info', 'Сведения об образовательной организации'
    SERVICES = 'services', 'Услуги'
    DOCUMENTS = 'documents', 'Документы'
    PARTNERS = 'partners', 'Партнёры'
    CONTACTS = 'contacts', 'Контакты'


DEFAULT_HOME_SECTION_ORDER: list[str] = [
    HomeSectionChoices.HEADER_BANNER,
    HomeSectionChoices.ANNOUNCEMENTS,
    HomeSectionChoices.EXAM_INFO,
    HomeSectionChoices.LATEST_NEWS,
    HomeSectionChoices.PRICING,
    HomeSectionChoices.EDUCATION_INFO,
    HomeSectionChoices.SERVICES,
    HomeSectionChoices.DOCUMENTS,
    HomeSectionChoices.PARTNERS,
    HomeSectionChoices.CONTACTS,
]


class HomePageSection(models.Model):
    """Настройка состава, порядка и видимости секций главной страницы."""

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='home_page_sections',
                                   verbose_name='Подразделение')
    section_key = models.CharField('Секция', max_length=50, choices=HomeSectionChoices.choices)
    is_enabled = models.BooleanField('Показывать', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    TEMPLATE_MAP: dict[str, str] = {
        HomeSectionChoices.HEADER_BANNER: 'content/blocks/home/header_banner.html',
        HomeSectionChoices.ANNOUNCEMENTS: 'content/blocks/home/announcements.html',
        HomeSectionChoices.EXAM_INFO: 'content/blocks/home/exam_info.html',
        HomeSectionChoices.LATEST_NEWS: 'content/blocks/home/latest_news.html',
        HomeSectionChoices.PRICING: 'content/blocks/home/pricing.html',
        HomeSectionChoices.EDUCATION_INFO: 'content/blocks/home/education_info.html',
        HomeSectionChoices.SERVICES: 'content/blocks/home/services.html',
        HomeSectionChoices.DOCUMENTS: 'content/blocks/home/documents.html',
        HomeSectionChoices.PARTNERS: 'content/blocks/home/partners.html',
        HomeSectionChoices.CONTACTS: 'content/blocks/home/contacts.html',
    }

    class Meta:
        verbose_name = 'Секция главной страницы'
        verbose_name_plural = 'Секции главной страницы'
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['department', 'section_key'], name='unique_home_section_per_department')]

    def __str__(self) -> str:
        """Возвращает название секции в контексте подразделения."""
        return f'{self.department.name} — {self.get_section_key_display()}'

    @property
    def template_name(self) -> str:
        """Возвращает путь к шаблону секции."""
        return self.TEMPLATE_MAP[self.section_key]


class Service(models.Model):
    """Услуга подразделения с кратким описанием, типом и контактными данными."""

    SERVICE_TYPES: list[tuple[str, str]] = [('parking', 'Автостоянка'),
                                            ('info_card', 'Информационная карточка (с описанием)'),
                                            ('custom', 'Произвольная услуга')]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='services',
                                   verbose_name='Подразделение')
    name = models.CharField('Название услуги', max_length=200)
    points = models.JSONField('Пункты (список строк)', default=list, blank=True,
                              help_text='Пример: ["Автостраховка ОСАГО", "Автостраховка КАСКО"]')
    slug = models.SlugField('URL-часть', max_length=200, blank=True)
    service_type = models.CharField('Тип услуги', max_length=20, choices=SERVICE_TYPES, default='info_card')
    icon_name = models.CharField('Имя иконки (без расширения)', max_length=50, blank=True,
                                 help_text='Например: "taxi", "insurance", "appraisal"')
    address = models.CharField('Адрес', max_length=300, blank=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    map_center = models.JSONField('Координаты', default=list, blank=True)
    description_material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='used_in_services', verbose_name='Материал с описанием')
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['department', 'order', 'name']

    def __str__(self) -> str:
        """Возвращает название услуги и подразделение."""
        return f'{self.name} ({self.department.name})'


class MenuItem(models.Model):
    """Пункт меню, который может отображаться во всех или выбранных подразделениях."""

    title = models.CharField('Название пункта', max_length=100)
    url = models.CharField('URL (относительный)', max_length=200)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    departments = models.ManyToManyField(Department, related_name='menu_items', verbose_name='Подразделения',
                                         blank=True,
                                         help_text='Выберите, в каких подразделениях будет отображаться этот пункт. Оставьте пустым — чтобы показывать во всех.')

    class Meta:
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ['order', 'title']

    def __str__(self) -> str:
        """Возвращает пункт меню с указанием подразделений показа."""
        if self.departments.exists():
            deps = ', '.join(d.name for d in self.departments.all())
            return f'{self.title} ({deps})'
        return f'{self.title} (все подразделения)'


class NewsImage(models.Model):
    """Изображение галереи, связанное с новостью."""

    news = models.ForeignKey('News', on_delete=models.CASCADE, related_name='gallery_images', verbose_name='Новость')
    image = models.ImageField('Изображение', upload_to='news/gallery/')
    description = models.CharField('Описание', max_length=255, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Изображение для галереи'
        verbose_name_plural = 'Изображения для галереи'

    def __str__(self) -> str:
        """Возвращает описание изображения или его идентификатор."""
        return self.description or f'Изображение {self.pk}'


class News(models.Model):
    """Новость сайта с текстом, медиа и привязкой к подразделениям."""

    joomla_id = models.IntegerField('ID из Joomla', unique=True, null=True, blank=True)
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('URL', unique=True, max_length=255)
    preview_text = models.TextField('Краткое описание', blank=True)
    content = models.TextField('Текст новости', blank=True)
    main_image = models.ImageField('Главная картинка', upload_to='news/main/', blank=True, null=True)
    video = models.FileField('Видео', upload_to='news/videos/', blank=True, null=True)
    is_partner_news = models.BooleanField('Партнёрская новость (отображается в секции "Партнёры")', default=False,
                                          help_text='Если отмечено — новость НЕ будет показываться в ленте новостей, а только в блоке "Наши партнёры".')
    departments = models.ManyToManyField('Department', related_name='news', blank=True,
                                         help_text='Оставьте пустым — будет отображаться во всех подразделениях')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Дата публикации')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self) -> str:
        """Возвращает заголовок новости."""
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Сохраняет новость и при необходимости заполняет дату публикации."""
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class DocumentCategory(models.Model):
    """Категория документов для группировки и сортировки."""

    name = models.CharField('Название категории', max_length=200, unique=True)
    slug = models.SlugField('Slug', max_length=200, unique=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория документа'
        verbose_name_plural = 'Категории документов'
        ordering = ['order', 'name']

    def __str__(self) -> str:
        """Возвращает название категории."""
        return self.name


class Document(models.Model):
    """Документ подразделения: файл, внешняя ссылка или информационный пункт."""

    DOCUMENT_TYPE_CHOICES: list[tuple[str, str]] = [('file', 'Файл (PDF/изображение)'), ('external', 'Внешняя ссылка'),
                                                    ('info', 'Информационный пункт (без файла)')]
    SECTIONS = EDUCATION_SECTION_CHOICES

    title = models.CharField('Название документа', max_length=255)
    document_type = models.CharField('Тип документа', max_length=10, choices=DOCUMENT_TYPE_CHOICES, default='file')
    display_in_sections = models.JSONField('Отображать в разделах', default=list, blank=True,
                                           help_text='Выберите разделы, где документ будет отображаться')
    file = models.FileField('Файл', upload_to='documents/', blank=True, null=True)
    external_url = models.URLField('Внешняя ссылка', blank=True)
    file_type = models.CharField('Тип файла', max_length=10, choices=[('pdf', 'PDF'), ('image', 'Изображение')],
                                 blank=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='documents', verbose_name='Категория')
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='documents',
                                   verbose_name='Подразделение')
    order = models.PositiveSmallIntegerField('Порядок в категории', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата добавления', default=timezone.now)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['department', 'category__order', 'order', 'title']

    def __str__(self) -> str:
        """Возвращает название документа и подразделение."""
        return f'{self.title} ({self.department.name})'

    def get_display_url(self) -> str | None:
        """Возвращает URL файла или внешней ссылки для отображения."""
        if self.document_type == 'file' and self.file:
            return self.file.url
        if self.document_type == 'external' and self.external_url:
            return self.external_url
        return None

    def is_external(self) -> bool:
        """Проверяет, является ли документ внешней ссылкой."""
        return self.document_type == 'external'

    def is_info_only(self) -> bool:
        """Проверяет, является ли документ информационным пунктом без файла."""
        return self.document_type == 'info'

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Сохраняет документ и автоматически определяет тип загруженного файла."""
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
    """Контентный материал подразделения с отдельным slug и статусом активности."""

    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self) -> str:
        """Возвращает заголовок материала."""
        return self.title


class ContentBlock(models.Model):
    """Упорядоченный блок контента, входящий в состав материала."""

    BLOCK_TYPES: list[tuple[str, str]] = [('heading', 'Заголовок'), ('paragraph', 'Абзац'), ('list', 'Список'),
                                          ('image', 'Изображение'), ('video', 'Видео'), ('quote', 'Цитата'),
                                          ('documents', 'Документы')]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField('Тип блока', max_length=20, choices=BLOCK_TYPES)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    text = models.TextField('Текст', blank=True)
    items = models.JSONField('Элементы списка', default=list, blank=True)
    image = models.ImageField('Изображение', upload_to='materials/images/', blank=True)
    video = models.FileField('Видео', upload_to='materials/videos/', blank=True)
    video_url = models.URLField('Ссылка на видео (YouTube/Vimeo)', blank=True)
    documents_section = models.CharField('Раздел документов', max_length=50, blank=True,
                                         help_text='Например: mtob, basic_info и т.д. Должен совпадать со значениями в Document.SECTIONS')

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        """Возвращает краткое представление блока материала."""
        return f'{self.material.title} — {self.block_type} #{self.order}'


class ExamInfo(models.Model):
    """Информация об экзаменах группы с вычислением актуальности и времени сбора."""

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='exam_info',
                                   verbose_name='Подразделение')
    group_number = models.PositiveSmallIntegerField('Номер группы')
    theory_date = models.DateField('Дата теоретического экзамена')
    practice_date = models.DateField('Дата практического экзамена', blank=True, null=True)
    gibdd_date = models.DateField('Дата экзамена в ГИБДД', blank=True, null=True)
    gibdd_time = models.TimeField('Время экзамена в ГИБДД', blank=True, null=True)

    class Meta:
        verbose_name = 'Информация об экзамене'
        verbose_name_plural = 'Информация об экзаменах'
        ordering = ['group_number', 'gibdd_date']

    def __str__(self) -> str:
        """Возвращает номер группы и дату экзамена в ГИБДД."""
        return f'Группа {self.group_number} ({self.gibdd_date})'

    @property
    def gathering_time(self) -> time | None:
        """Возвращает время сбора за час до экзамена в ГИБДД."""
        if not self.gibdd_time:
            return None
        dt = datetime.combine(date.today(), self.gibdd_time)
        gathering_dt = dt - timedelta(hours=1)
        return gathering_dt.time()

    def is_expired(self) -> bool:
        """Проверяет, прошла ли дата экзамена в ГИБДД."""
        today = timezone.now().date()
        if self.gibdd_date:
            return self.gibdd_date < today
        return False

    def should_be_visible(self) -> bool:
        """Проверяет, должна ли запись отображаться как актуальная."""
        return not self.is_expired()


class Announcement(models.Model):
    """Объявление, акция или информационная карточка для секции exam_info."""

    class CardType(models.TextChoices):
        INFO = 'info', 'Карточка в сетке (маленькая)'
        ANNOUNCEMENT = 'announcement', 'Объявление (на всю ширину)'
        PROMO = 'promo', 'Акция / Сертификат (с изображением, на всю ширину)'

    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='announcements',
        verbose_name='Подразделение',
    )
    card_type = models.CharField('Тип карточки', max_length=20, choices=CardType.choices, default=CardType.ANNOUNCEMENT)
    title = models.CharField('Заголовок', max_length=255)
    text = models.TextField('Текст (HTML)', blank=True, help_text='Допустим HTML-разметка: p, strong, ul, li и др.')
    image = models.ImageField('Изображение', upload_to='announcements/', blank=True, null=True,
                              help_text='Только для типа «Акция / Сертификат».')
    is_active = models.BooleanField('Показывать', default=True)
    expires_at = models.DateField('Показывать до (включительно)', blank=True, null=True,
                                  help_text='Оставьте пустым — будет показываться бессрочно.')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Объявление / Акция'
        verbose_name_plural = 'Объявления и акции'
        ordering = ['order', '-id']

    def __str__(self) -> str:
        return f'{self.department.name} — {self.title}'
