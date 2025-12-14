import os
import shutil

from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Department, DepartmentDetails, MenuItem, NewsImage, News, Document, DocumentCategory, Service, \
    ContentBlock, Material


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


class DepartmentDetailsAdminForm(forms.ModelForm):
    class Meta:
        model = DepartmentDetails
        fields = '__all__'
        widgets = {
            'schedule': forms.Textarea(attrs={'rows': 6, 'placeholder': '[{"days": ["ПН", "ВТ"], "hours": "9:00–18:00"}]'}),
            'map_iframes': forms.Textarea(attrs={'rows': 4, 'placeholder': '["https://...", "https://..."]'}),
        }

@admin.register(DepartmentDetails)
class DepartmentDetailsAdmin(admin.ModelAdmin):
    form = DepartmentDetailsAdminForm
    list_display = ('department', 'phone', 'email', 'inn', 'show_contacts')
    search_fields = ('department__name', 'address', 'email')

    def get_fieldsets(self, request, obj=None):
        all_fields = [f.name for f in DepartmentDetails._meta.fields]
        show_fields = [f for f in all_fields if f.startswith('show_')]
        return (
            ('Основное', {
                'fields': ('department',) + tuple(show_fields),
            }),
            ('Контакты', {
                'fields': ('address', 'short_address', 'phone', 'email', 'website'),
                'classes': ('collapse',)
            }),
            ('Реквизиты', {
                'fields': ('recipient_name', 'inn', 'kpp', 'legal_address', 'bank', 'bik', 'corr_account',
                           'settlement_account', 'payment_purpose'),
                'classes': ('collapse',)
            }),
            ('Расписание и карты', {
                'fields': ('schedule', 'map_iframes', 'map_center'),
                'classes': ('collapse',)
            }),
            ('SEO', {
                'fields': ('meta_title', 'meta_description'),
                'classes': ('collapse',)
            }),
        )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active', 'departments_list')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    filter_horizontal = ('departments',)  # ← красивый виджет выбора

    def departments_list(self, obj):
        if obj.departments.exists():
            return ', '.join(d.name for d in obj.departments.all())
        return 'Все подразделения'

    departments_list.short_description = 'Отображается в'


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ('description', 'order')
    list_editable = ('order',)


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active', 'departments', 'is_partner_news')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NewsImageInline]


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'document_count']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['order', 'name']

    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Документов'


class DocumentAdminForm(forms.ModelForm):
    display_in_sections = forms.MultipleChoiceField(
        choices=Document.SECTIONS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Отображать в разделах'
    )

    class Meta:
        model = Document
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.display_in_sections:
            self.fields['display_in_sections'].initial = self.instance.display_in_sections

    def clean_display_in_sections(self):
        return self.cleaned_data.get('display_in_sections', [])


class DocumentDepartmentFilter(admin.SimpleListFilter):
    title = 'Подразделение'
    parameter_name = 'department'

    def lookups(self, request, model_admin):
        return [(d.id, d.name) for d in Department.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(departments__id=self.value())
        return queryset


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'category', 'document_type', 'file_link', 'is_active', 'order']
    list_filter = ['department', 'category', 'document_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title']
    form = DocumentAdminForm
    fields = [
        'title',
        'document_type',
        'file',
        'external_url',
        'file_type',
        'category',
        'department',
        'display_in_sections',
        'order',
        'is_active',
        'created_at',
    ]
    ordering = ['department', 'category__order', 'order', 'title']

    def get_readonly_fields(self, request, obj=None):
        return ['file_type']

    def file_link(self, obj):
        url = obj.get_display_url()
        if url:
            if obj.is_external():
                return format_html('<a href="{}" target="_blank" rel="noopener">Внешняя ссылка</a>', url)
            else:
                return format_html('<a href="{}" target="_blank">Открыть</a>', url)
        return "— (информационный пункт)"

    file_link.short_description = 'Ссылка'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.file:
            dept_slug = obj.department.slug
            filename = os.path.basename(obj.file.name)
            ext = filename.split('.')[-1].lower()

            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                target_dir = f'documents/{dept_slug}_images/'
            else:
                target_dir = f'documents/{dept_slug}/'

            new_relative_path = os.path.join(target_dir, filename)
            new_full_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)

            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)

            old_full_path = obj.file.path
            if old_full_path != new_full_path:
                shutil.move(old_full_path, new_full_path)
                obj.file.name = new_relative_path
                obj.save(update_fields=['file'])

    def file_type_display(self, obj):
        return obj.get_file_type_display()
    file_type_display.short_description = 'Тип'

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Открыть</a>', obj.file.url)
        return "—"
    file_link.short_description = 'Файл'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'service_type', 'icon_name', 'description_material']
    list_filter = ['department', 'service_type']
    search_fields = ['name']
    fields = [
        'department',
        'name',
        'slug',
        'service_type',
        'icon_name',
        'address',
        'phone',
        'map_center',
        'description_material',
        'points',
        'order',
        'is_active',
    ]
    ordering = ['department', 'order']


class ContentBlockInline(admin.TabularInline):
    model = ContentBlock
    extra = 1

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    inlines = [ContentBlockInline]