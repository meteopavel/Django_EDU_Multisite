"""
Административные настройки контентного приложения.

Модуль содержит:
- регистрации моделей в Django admin;
- кастомные формы админки;
- inline-настройки связанных сущностей;
- вспомогательные методы отображения и сохранения файлов.
"""

from __future__ import annotations

import os
import shutil
from typing import Any

from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.utils.html import format_html

from .models import Department, DepartmentDetails, HomePageSection, MenuItem, NewsImage, News, Document, DocumentCategory, Service, ContentBlock, Material, ExamInfo, Announcement


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Администрирование подразделений."""
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


class DepartmentDetailsAdminForm(forms.ModelForm):
    """Форма администрирования деталей подразделения с удобными JSON-полями."""

    class Meta:
        model = DepartmentDetails
        fields = '__all__'
        widgets = {
            'schedule': forms.Textarea(attrs={'rows': 6, 'placeholder': '[{"days": ["ПН", "ВТ"], "hours": "9:00–18:00"}]'}),
            'map_iframes': forms.Textarea(attrs={'rows': 4, 'placeholder': '["https://...", "https://..."]'}),
        }


@admin.register(DepartmentDetails)
class DepartmentDetailsAdmin(admin.ModelAdmin):
    """Администрирование контактных, реквизитных и SEO-данных подразделения."""
    form = DepartmentDetailsAdminForm
    list_display = ('department', 'phone', 'email', 'cellphone', 'inn')
    search_fields = ('department__name', 'address', 'email')

    def get_fieldsets(self, request: HttpRequest, obj: DepartmentDetails | None = None) -> tuple[tuple[str, dict[str, Any]], ...]:
        """Возвращает набор секций формы редактирования деталей подразделения."""
        all_fields = [field.name for field in DepartmentDetails._meta.fields]
        show_fields = [field for field in all_fields if field.startswith('show_')]
        return (
            ('Основное', {'fields': ('department',) + tuple(show_fields)}),
            ('Контакты', {'fields': ('address', 'short_address', 'phone', 'cellphone', 'email', 'website'), 'classes': ('collapse',)}),
            ('Реквизиты', {'fields': ('recipient_name', 'inn', 'kpp', 'legal_address', 'bank', 'bik', 'corr_account', 'settlement_account', 'payment_purpose'), 'classes': ('collapse',)}),
            ('Расписание и карты', {'fields': ('schedule', 'map_iframes', 'map_center'), 'classes': ('collapse',)}),
            ('SEO', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
        )


@admin.register(HomePageSection)
class HomePageSectionAdmin(admin.ModelAdmin):
    """Администрирование состава и порядка секций главной страницы."""
    list_display = ('department', 'section_label', 'is_enabled', 'order')
    list_filter = ('department', 'is_enabled', 'section_key')
    search_fields = ('department__name',)
    ordering = ('department', 'order', 'id')

    @admin.display(description='Секция', ordering='section_key')
    def section_label(self, obj: HomePageSection) -> str:
        """Возвращает человекочитаемое название секции."""
        return obj.get_section_key_display()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Администрирование пунктов меню подразделений."""
    list_display = ('title', 'url', 'order', 'is_active', 'departments_list')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    filter_horizontal = ('departments',)

    def departments_list(self, obj: MenuItem) -> str:
        """Возвращает список подразделений, где отображается пункт меню."""
        if obj.departments.exists():
            return ', '.join(department.name for department in obj.departments.all())
        return 'Все подразделения'

    departments_list.short_description = 'Отображается в'


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    """Администрирование изображений новостей."""
    list_display = ('description', 'order')
    list_editable = ('order',)


class NewsImageInline(admin.TabularInline):
    """Inline-редактирование изображений новости."""
    model = NewsImage
    extra = 1

    class Media:
        js = ('js/admin_multi_image_upload.js',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Администрирование новостей и их галереи."""
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active', 'departments', 'is_partner_news')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NewsImageInline]


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    """Администрирование категорий документов."""
    list_display = ['name', 'slug', 'order', 'document_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['order', 'name']

    def document_count(self, obj: DocumentCategory) -> int:
        """Возвращает количество документов в категории."""
        return obj.documents.count()

    document_count.short_description = 'Документов'


class DocumentAdminForm(forms.ModelForm):
    """Форма администрирования документа с множественным выбором секций отображения."""
    display_in_sections = forms.MultipleChoiceField(choices=Document.SECTIONS, widget=forms.CheckboxSelectMultiple, required=False, label='Отображать в разделах')

    class Meta:
        model = Document
        fields = '__all__'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализирует форму и подставляет текущие секции отображения документа."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.display_in_sections:
            self.fields['display_in_sections'].initial = self.instance.display_in_sections

    def clean_display_in_sections(self) -> list[str]:
        """Возвращает выбранные секции отображения документа."""
        return self.cleaned_data.get('display_in_sections', [])


class DocumentDepartmentFilter(admin.SimpleListFilter):
    """Фильтр документов по подразделению в административном интерфейсе."""
    title = 'Подразделение'
    parameter_name = 'department'

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[int, str]]:
        """Возвращает список подразделений для фильтра."""
        return [(department.id, department.name) for department in Department.objects.all()]

    def queryset(self, request: HttpRequest, queryset):
        """Фильтрует queryset по выбранному подразделению."""
        if self.value():
            return queryset.filter(departments__id=self.value())
        return queryset


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Администрирование документов и их файлового размещения."""
    list_display = ['title', 'department', 'category', 'document_type', 'file_link', 'is_active', 'order']
    list_filter = ['department', 'category', 'document_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title']
    form = DocumentAdminForm
    fields = ['title', 'document_type', 'file', 'external_url', 'file_type', 'category', 'department', 'display_in_sections', 'order', 'is_active', 'created_at']
    ordering = ['department', 'category__order', 'order', 'title']

    def get_readonly_fields(self, request: HttpRequest, obj: Document | None = None) -> list[str]:
        """Возвращает список полей только для чтения."""
        return ['file_type']

    def save_model(self, request: HttpRequest, obj: Document, form: forms.ModelForm, change: bool) -> None:
        """Сохраняет документ и при необходимости перемещает файл в каталог подразделения."""
        super().save_model(request, obj, form, change)
        if obj.file:
            dept_slug = obj.department.slug
            filename = os.path.basename(obj.file.name)
            ext = filename.split('.')[-1].lower()
            target_dir = f'documents/{dept_slug}_images/' if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else f'documents/{dept_slug}/'
            new_relative_path = os.path.join(target_dir, filename)
            new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
            old_full_path = obj.file.path
            if old_full_path != new_full_path:
                shutil.move(old_full_path, new_full_path)
                obj.file.name = new_relative_path
                obj.save(update_fields=['file'])

    def file_type_display(self, obj: Document) -> str:
        """Возвращает человекочитаемое название типа файла."""
        return obj.get_file_type_display()

    file_type_display.short_description = 'Тип'

    def file_link(self, obj: Document) -> str:
        """Возвращает HTML-ссылку на файл документа."""
        if obj.file:
            return format_html('<a href="{}" target="_blank">Открыть</a>', obj.file.url)
        return '—'

    file_link.short_description = 'Файл'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Администрирование услуг подразделений."""
    list_display = ['name', 'department', 'service_type', 'icon_name', 'description_material']
    list_filter = ['department', 'service_type']
    search_fields = ['name']
    fields = ['department', 'name', 'slug', 'service_type', 'icon_name', 'address', 'phone', 'map_center', 'description_material', 'points', 'order', 'is_active']
    ordering = ['department', 'order']


class ContentBlockAdminForm(forms.ModelForm):
    """Форма администрирования блока контента с валидацией секции документов."""
    documents_section = forms.ChoiceField(choices=[('', '---')] + list(Document.SECTIONS), required=False, label='Раздел для документов', help_text='Выберите, какие документы отобразить (только для блока "Документы")')

    class Meta:
        model = ContentBlock
        fields = '__all__'

    def clean(self) -> dict[str, Any]:
        """Проверяет обязательность выбора секции для блока типа documents."""
        cleaned_data = super().clean()
        block_type = cleaned_data.get('block_type')
        documents_section = cleaned_data.get('documents_section')
        if block_type == 'documents' and not documents_section:
            raise forms.ValidationError({'documents_section': 'Для блока "Документы" обязательно выберите раздел.'})
        return cleaned_data


class ContentBlockInline(admin.TabularInline):
    """Inline-редактирование блоков контента материала."""
    model = ContentBlock
    form = ContentBlockAdminForm
    extra = 1
    fields = ('block_type', 'order', 'text', 'items', 'image', 'video', 'video_url', 'documents_section')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Администрирование материалов и их контентных блоков."""
    inlines = [ContentBlockInline]
    list_display = ['title', 'department']
    list_filter = ['department']


@admin.register(ExamInfo)
class ExamInfoAdmin(admin.ModelAdmin):
    """Администрирование информации об экзаменах."""
    list_display = ['group_number', 'theory_date', 'practice_date', 'gibdd_date', 'gibdd_time', 'is_expired_col']
    search_fields = ['group_number']
    ordering = ['group_number', 'gibdd_date']
    fieldsets = (
        ('Основная информация', {'fields': ('department', 'group_number'), 'description': 'Информация для одной группы'}),
        ('Даты экзаменов', {'fields': ('theory_date', 'practice_date', 'gibdd_date', 'gibdd_time'), 'description': 'Практический экзамен обычно на следующий день после теоретического. Сбор за час до ГИБДД.'}),
    )

    def is_expired_col(self, obj: ExamInfo) -> str:
        """Возвращает HTML-индикатор актуальности экзамена."""
        if obj.is_expired():
            return format_html('<span style="color: red; font-weight: bold;">✓ Просрочен</span>')
        return format_html('<span style="color: green; font-weight: bold;">✓ Актуален</span>')

    is_expired_col.short_description = 'Статус'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Администрирование объявлений и акций."""
    list_display = ['title', 'department', 'card_type', 'is_active', 'expires_at', 'order']
    list_editable = ['is_active', 'expires_at', 'order']
    list_filter = ['department', 'card_type', 'is_active']
    search_fields = ['title', 'text']
    fieldsets = (
        ('Основное', {'fields': ('department', 'card_type', 'title', 'is_active', 'expires_at', 'order')}),
        ('Содержимое', {'fields': ('text', 'image'), 'description': 'Изображение используется только для типа «Акция / Сертификат».'}),
    )
