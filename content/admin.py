from django.contrib import admin
from .models import Department, DepartmentDetails, MenuItem, NewsImage, News


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DepartmentDetails)
class DepartmentDetailsAdmin(admin.ModelAdmin):
    list_display = ('department', 'phone', 'email', 'inn')
    search_fields = ('department__name', 'address', 'email')
    fieldsets = (
        ('Основное', {
            'fields': ('department',)
        }),
        ('Контакты', {
            'fields': ('address', 'phone', 'email', 'website'),
            'classes': ('collapse',)
        }),
        ('Реквизиты', {
            'fields': ('inn', 'kpp', 'legal_address'),
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
    list_filter = ('is_active', 'departments')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [NewsImageInline]