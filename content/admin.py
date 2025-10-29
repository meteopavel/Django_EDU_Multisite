from django.contrib import admin
from .models import Department, PageTemplate, PageContent


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)


class PageContentInline(admin.TabularInline):
    model = PageContent
    extra = 1
    fields = ('content', 'is_active')
    verbose_name = 'Контент для типа сайта'
    verbose_name_plural = 'Контент для разных типов сайта'


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('template', 'department', 'is_active', 'updated_at')
    list_filter = ('department', 'template', 'is_active')
    search_fields = ('content', 'department__name', 'template__title')
    list_editable = ('is_active',)
    ordering = ('department', 'template')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('department', 'template', 'is_active')
        }),
        ('Контент', {
            'fields': ('content',)
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department', 'template')