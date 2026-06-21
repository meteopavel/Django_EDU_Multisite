# API map: content, core, edu_multisite

Просканировано Python-файлов: 18
Включено в карту: 14
Пропущено без значимой API-информации: 4

Сводная статистика:
- модулей: 14
- классов: 33
- dataclass: 0
- функций: 22
- методов: 37
- констант: 22

---

# content/admin.py

Модуль:
Административные настройки контентного приложения.

Модуль содержит:
- регистрации моделей в Django admin;
- кастомные формы админки;
- inline-настройки связанных сущностей;
- вспомогательные методы отображения и сохранения файлов.

Классы:

- `DepartmentAdmin(admin.ModelAdmin)`
  Администрирование подразделений.

- `DepartmentDetailsAdminForm(forms.ModelForm)`
  Форма администрирования деталей подразделения с удобными JSON-полями.

- `DepartmentDetailsAdmin(admin.ModelAdmin)`
  Администрирование контактных, реквизитных и SEO-данных подразделения.
  Методы:
  - `get_fieldsets(self, request: HttpRequest, obj: DepartmentDetails | None = None) -> tuple[tuple[str, dict[str, Any]], ...]`
    Возвращает набор секций формы редактирования деталей подразделения.

- `HomePageSectionAdmin(admin.ModelAdmin)`
  Администрирование состава и порядка секций главной страницы.
  Методы:
  - `section_label(self, obj: HomePageSection) -> str`
    Возвращает человекочитаемое название секции.

- `MenuItemAdmin(admin.ModelAdmin)`
  Администрирование пунктов меню подразделений.
  Методы:
  - `departments_list(self, obj: MenuItem) -> str`
    Возвращает список подразделений, где отображается пункт меню.

- `NewsImageAdmin(admin.ModelAdmin)`
  Администрирование изображений новостей.

- `NewsImageInline(admin.TabularInline)`
  Inline-редактирование изображений новости.

- `NewsAdmin(admin.ModelAdmin)`
  Администрирование новостей и их галереи.

- `DocumentCategoryAdmin(admin.ModelAdmin)`
  Администрирование категорий документов.
  Методы:
  - `document_count(self, obj: DocumentCategory) -> int`
    Возвращает количество документов в категории.

- `DocumentAdminForm(forms.ModelForm)`
  Форма администрирования документа с множественным выбором секций отображения.
  Методы:
  - `__init__(self, *args: Any, **kwargs: Any) -> None`
    Инициализирует форму и подставляет текущие секции отображения документа.
  - `clean_display_in_sections(self) -> list[str]`
    Возвращает выбранные секции отображения документа.

- `DocumentDepartmentFilter(admin.SimpleListFilter)`
  Фильтр документов по подразделению в административном интерфейсе.
  Методы:
  - `lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[int, str]]`
    Возвращает список подразделений для фильтра.
  - `queryset(self, request: HttpRequest, queryset)`
    Фильтрует queryset по выбранному подразделению.

- `DocumentAdmin(admin.ModelAdmin)`
  Администрирование документов и их файлового размещения.
  Методы:
  - `get_readonly_fields(self, request: HttpRequest, obj: Document | None = None) -> list[str]`
    Возвращает список полей только для чтения.
  - `save_model(self, request: HttpRequest, obj: Document, form: forms.ModelForm, change: bool) -> None`
    Сохраняет документ и при необходимости перемещает файл в каталог подразделения.
  - `file_type_display(self, obj: Document) -> str`
    Возвращает человекочитаемое название типа файла.
  - `file_link(self, obj: Document) -> str`
    Возвращает HTML-ссылку на файл документа.

- `ServiceAdmin(admin.ModelAdmin)`
  Администрирование услуг подразделений.

- `ContentBlockAdminForm(forms.ModelForm)`
  Форма администрирования блока контента с валидацией секции документов.
  Методы:
  - `clean(self) -> dict[str, Any]`
    Проверяет обязательность выбора секции для блока типа documents.

- `ContentBlockInline(admin.TabularInline)`
  Inline-редактирование блоков контента материала.

- `MaterialAdmin(admin.ModelAdmin)`
  Администрирование материалов и их контентных блоков.

- `ExamInfoAdmin(admin.ModelAdmin)`
  Администрирование информации об экзаменах.
  Методы:
  - `is_expired_col(self, obj: ExamInfo) -> str`
    Возвращает HTML-индикатор актуальности экзамена.

- `AnnouncementAdmin(admin.ModelAdmin)`
  Администрирование объявлений и акций.

---

# content/apps.py

Модуль:
Конфигурация приложения content.

Классы:

- `ContentConfig(AppConfig)`
  Конфигурация Django-приложения content.

---

# content/constants.py

Модуль:
Константы контентного приложения.

Модуль содержит справочные наборы значений, используемые в моделях,
представлениях и шаблонах.

Константы:
- `EDUCATION_SECTION_CHOICES = [('osnovnye-svedeniya', 'Основные сведения'), ('struktura-upravleniya', 'Структура и органы управле…`

---

# content/context_processors.py

Модуль:
Контекстные процессоры контентного приложения.

Модуль содержит функции для:
- подстановки меню текущего подразделения;
- вычисления версии статики;
- передачи ключа Yandex Maps в шаблоны.

Функции:

- `menu_processor(request: HttpRequest) -> dict[str, Any]`
  Возвращает пункты меню для текущего подразделения или резервного подразделения.

- `static_version(request: HttpRequest) -> dict[str, str]`
  Возвращает версию статики по времени последнего изменения файлов static.

- `yandex_maps(request: HttpRequest) -> dict[str, str]`
  Возвращает ключ API Яндекс.Карт для использования в шаблонах.

---

# content/decorators.py

Модуль:
Декораторы представлений контентного приложения.

Модуль содержит:
- декоратор для обычных страниц с автоматическим определением подразделения;
- декоратор для AJAX-представлений с рендерингом HTML или возвратом JSON.

Функции:

- `page_name(name: str, template_name: str) -> Callable`
  Декорирует view, добавляя page_name, department и рендер шаблона страницы.

- `ajax_view(name: str | None = None, template_name: str | None = None) -> Callable`
  Декорирует AJAX-view, разрешая подразделение и возвращая JSON или HTML.

---

# content/models.py

Модуль:
Модели контентной и справочной структуры сайта.

Модуль содержит сущности для:
- подразделений и их реквизитов;
- секций главной страницы;
- услуг, меню, новостей и документов;
- материалов и блоков контента;
- экзаменационной информации.

Константы:
- `DEFAULT_HOME_SECTION_ORDER: list[str] = [HomeSectionChoices.HEADER_BANNER, HomeSectionChoices.ANNOUNCEMENTS, HomeSectionChoices.EXAM_INFO, …`

Классы:

- `Department(models.Model)`
  Подразделение организации, к которому привязываются контент и данные.
  Методы:
  - `__str__(self) -> str`
    Возвращает название подразделения.

- `DepartmentDetails(models.Model)`
  Расширенные реквизиты, контакты и SEO-данные подразделения.
  Методы:
  - `__str__(self) -> str`
    Возвращает краткое представление деталей подразделения.

- `HomeSectionChoices(models.TextChoices)`
  Ключи секций главной страницы подразделения.

- `HomePageSection(models.Model)`
  Настройка состава, порядка и видимости секций главной страницы.
  Поля:
  - `TEMPLATE_MAP: dict[str, str] = {HomeSectionChoices.HEADER_BANNER: 'content/blocks/home/header_banner.html', HomeSectionChoices.ANNOUNCEMENTS: 'content/blocks/home/announcements.html', HomeSectionChoices.EXAM_INFO: 'content/blocks/home/exam_info.html', HomeSectionChoices.LATEST_NEWS: 'content/blocks/home/latest_news.html', HomeSectionChoices.PRICING: 'content/blocks/home/pricing.html', HomeSectionChoices.EDUCATION_INFO: 'content/blocks/home/education_info.html', HomeSectionChoices.SERVICES: 'content/blocks/home/services.html', HomeSectionChoices.DOCUMENTS: 'content/blocks/home/documents.html', HomeSectionChoices.PARTNERS: 'content/blocks/home/partners.html', HomeSectionChoices.CONTACTS: 'content/blocks/home/contacts.html'}`
  Методы:
  - `__str__(self) -> str`
    Возвращает название секции в контексте подразделения.
  - `template_name(self) -> str`
    Возвращает путь к шаблону секции.

- `Service(models.Model)`
  Услуга подразделения с кратким описанием, типом и контактными данными.
  Поля:
  - `SERVICE_TYPES: list[tuple[str, str]] = [('parking', 'Автостоянка'), ('info_card', 'Информационная карточка (с описанием)'), ('custom', 'Произвольная услуга')]`
  Методы:
  - `__str__(self) -> str`
    Возвращает название услуги и подразделение.

- `MenuItem(models.Model)`
  Пункт меню, который может отображаться во всех или выбранных подразделениях.
  Методы:
  - `__str__(self) -> str`
    Возвращает пункт меню с указанием подразделений показа.

- `NewsImage(models.Model)`
  Изображение галереи, связанное с новостью.
  Методы:
  - `save(self, *args, **kwargs)`
    Нет докстринга.
  - `__str__(self) -> str`
    Возвращает описание изображения или его идентификатор.

- `News(models.Model)`
  Новость сайта с текстом, медиа и привязкой к подразделениям.
  Методы:
  - `__str__(self) -> str`
    Возвращает заголовок новости.
  - `save(self, *args: Any, **kwargs: Any) -> None`
    Сохраняет новость и при необходимости заполняет дату публикации.

- `DocumentCategory(models.Model)`
  Категория документов для группировки и сортировки.
  Методы:
  - `__str__(self) -> str`
    Возвращает название категории.

- `Document(models.Model)`
  Документ подразделения: файл, внешняя ссылка или информационный пункт.
  Поля:
  - `DOCUMENT_TYPE_CHOICES: list[tuple[str, str]] = [('file', 'Файл (PDF/изображение)'), ('external', 'Внешняя ссылка'), ('info', 'Информационный пункт (без файла)')]`
  Методы:
  - `__str__(self) -> str`
    Возвращает название документа и подразделение.
  - `get_display_url(self) -> str | None`
    Возвращает URL файла или внешней ссылки для отображения.
  - `is_external(self) -> bool`
    Проверяет, является ли документ внешней ссылкой.
  - `is_info_only(self) -> bool`
    Проверяет, является ли документ информационным пунктом без файла.
  - `save(self, *args: Any, **kwargs: Any) -> None`
    Сохраняет документ и автоматически определяет тип загруженного файла.

- `Material(models.Model)`
  Контентный материал подразделения с отдельным slug и статусом активности.
  Методы:
  - `__str__(self) -> str`
    Возвращает заголовок материала.

- `ContentBlock(models.Model)`
  Упорядоченный блок контента, входящий в состав материала.
  Поля:
  - `BLOCK_TYPES: list[tuple[str, str]] = [('heading', 'Заголовок'), ('paragraph', 'Абзац'), ('list', 'Список'), ('image', 'Изображение'), ('video', 'Видео'), ('quote', 'Цитата'), ('documents', 'Документы')]`
  Методы:
  - `__str__(self) -> str`
    Возвращает краткое представление блока материала.

- `ExamInfo(models.Model)`
  Информация об экзаменах группы с вычислением актуальности и времени сбора.
  Методы:
  - `__str__(self) -> str`
    Возвращает номер группы и дату экзамена в ГИБДД.
  - `gathering_time(self) -> time | None`
    Возвращает время сбора за час до экзамена в ГИБДД.
  - `is_expired(self) -> bool`
    Проверяет, прошла ли дата экзамена в ГИБДД.
  - `should_be_visible(self) -> bool`
    Проверяет, должна ли запись отображаться как актуальная.

- `Announcement(models.Model)`
  Объявление, акция или информационная карточка для секции exam_info.
  Методы:
  - `__str__(self) -> str`
    Нет докстринга.

---

# content/templatetags/document_tags.py

Модуль:
Шаблонные теги для работы с документами.

Модуль содержит inclusion tag для вывода документов подразделения
по выбранной секции с разделением на изображения и прочие документы.

Функции:

- `documents_for_section(department: Department, section_slug: str) -> dict[str, Any]`
  Возвращает документы секции, разделённые на изображения и категории прочих файлов.

---

# content/urls.py

Модуль:
URL-маршруты контентного приложения.

Модуль определяет:
- главную страницу подразделения;
- AJAX-эндпоинты новостей;
- AJAX-эндпоинты документов, материалов и экзаменов.

---

# content/utils.py

Модуль:
Вспомогательные функции контентного приложения.

Модуль содержит утилиты для:
- определения подразделения по хосту;
- выборки и фильтрации новостей;
- группировки документов;
- вычисления диапазона месяцев экзаменов;
- кастомизации заголовков образовательных секций.

Функции:

- `get_host_map() -> dict[str, str]`
  Возвращает словарь соответствия хостов и slug подразделений.

- `get_department_by_host(request: HttpRequest) -> Department`
  Определяет активное подразделение по хосту текущего запроса.

- `get_news_for_department(department: Department | None, limit: int | None = None, year: int | None = None, partner_only: bool = False)`
  Возвращает новости подразделения с опциональной фильтрацией по году и лимиту.

- `get_news_years(department: Department) -> list[int]`
  Возвращает список годов, в которых есть новости подразделения.

- `split_documents_by_file_type(documents: list[Document]) -> tuple[list[Document], list[Document]]`
  Разделяет документы на изображения и прочие элементы.

- `group_documents_by_category(documents: list[Document]) -> list[tuple[Any, list[Document]]]`
  Группирует документы по категории с выделением группы «Прочее».

- `get_exam_month_range(exams: list[ExamInfo]) -> str`
  Возвращает человекочитаемый диапазон месяцев по датам экзаменов.

- `get_education_section_title(department_slug: str, base_slug: str, default_title: str) -> str`
  Возвращает отображаемый заголовок образовательной секции с учётом кастомизаций.

---

# content/views.py

Модуль:
Представления контентного раздела сайта.

Модуль содержит:
- главную страницу подразделения;
- AJAX-список и детали новостей;
- AJAX-секции документов и материалов;
- AJAX-вывод информации об экзаменах.

Функции:

- `home_view(request: HttpRequest, department: Department) -> dict[str, Any]`
  Собирает контекст главной страницы подразделения по включённым секциям.

- `ajax_all_news(request: HttpRequest, department: Department) -> dict[str, Any]`
  Возвращает контекст AJAX-списка новостей с фильтрацией по году.

- `ajax_news_detail(request: HttpRequest, department: Department) -> dict[str, Any]`
  Возвращает контекст детального AJAX-представления одной новости.

- `ajax_documents(request: HttpRequest, department: Department) -> dict[str, Any]`
  Возвращает контекст AJAX-секции документов подразделения.

- `ajax_material_description(request: HttpRequest, department: Department, **kwargs: Any) -> dict[str, Any]`
  Возвращает контекст AJAX-описания материала и связанных документов секции.

- `ajax_exam_info(request: HttpRequest, department: Department) -> dict[str, Any]`
  Возвращает контекст AJAX-блока с актуальными экзаменами подразделения.

---

# core/host_parser.py

Модуль:
Утилиты разбора конфигурации соответствия хостов и подразделений.

Модуль используется для:
- преобразования строковой карты хостов в словарь;
- получения списка допустимых хостов для настроек Django.

Функции:

- `parse_host_map(raw_map: str) -> dict[str, str]`
  Преобразует строковую карту хостов в словарь вида {host: department_slug}.

- `get_allowed_hosts_from_map(raw_map: str) -> list[str]`
  Возвращает список хостов из конфигурационной карты.

---

# edu_multisite/settings.py

Модуль:
Настройки Django-проекта edu_multisite.

Модуль определяет:
- базовые настройки проекта;
- подключённые приложения и middleware;
- шаблоны и context processors;
- параметры базы данных;
- статические и медиа-файлы;
- мультидоменную конфигурацию через HOST_TO_DEPARTMENT_MAP.

Константы:
- `BASE_DIR = Path(__file__).resolve().parent.parent`
- `SECRET_KEY = os.getenv('SECRET_KEY')`
- `DEBUG = os.getenv('DEBUG_VALUE') == 'True'`
- `HOST_TO_DEPARTMENT_MAP = os.getenv('HOST_TO_DEPARTMENT_MAP', '')`
- `YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY', '')`
- `ALLOWED_HOSTS = get_allowed_hosts_from_map(HOST_TO_DEPARTMENT_MAP)`
- `INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sess…`
- `MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddle…`
- `ROOT_URLCONF = 'edu_multisite.urls'`
- `TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], '…`
- `WSGI_APPLICATION = 'edu_multisite.wsgi.application'`
- `DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': os.getenv('DB_NAME'), 'USER': os.getenv(…`
- `AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'dj…`
- `LANGUAGE_CODE = 'ru'`
- `TIME_ZONE = 'Asia/Irkutsk'`
- `USE_I18N = True`
- `USE_L10N = True`
- `USE_TZ = True`
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`

---

# edu_multisite/urls.py

Модуль:
Корневые URL-маршруты проекта edu_multisite.

Модуль определяет:
- подключение административного интерфейса в режиме DEBUG;
- подключение маршрутов приложения content;
- раздачу static и media в режиме разработки.

---

# edu_multisite/wsgi.py

Модуль:
WSGI-конфигурация проекта edu_multisite.

Модуль:
- подготавливает sys.path для окружения хостинга;
- загружает переменные окружения из .env;
- инициализирует WSGI-приложение Django.

Переменная окружения HOSTING_ROOT задаёт корень проекта на хостинге.
Если не задана, используется расположение этого файла.

Константы:
- `HOSTING_ROOT = os.environ.get('HOSTING_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`