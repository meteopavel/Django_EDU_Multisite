"""
Корневые URL-маршруты проекта edu_multisite.

Модуль определяет:
- подключение административного интерфейса в режиме DEBUG;
- подключение маршрутов приложения content;
- раздачу static и media в режиме разработки.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [path('admin/', admin.site.urls)]

urlpatterns += [
    path('', include('content.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
