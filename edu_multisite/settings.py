"""
Настройки Django-проекта edu_multisite.

Модуль определяет:
- базовые настройки проекта;
- подключённые приложения и middleware;
- шаблоны и context processors;
- параметры базы данных;
- статические и медиа-файлы;
- мультидоменную конфигурацию через HOST_TO_DEPARTMENT_MAP.
"""

from __future__ import annotations

import os
from pathlib import Path

from core.host_parser import get_allowed_hosts_from_map

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG_VALUE') == 'True'
HOST_TO_DEPARTMENT_MAP = os.getenv('HOST_TO_DEPARTMENT_MAP', '')
YANDEX_MAPS_API_KEY = os.getenv('YANDEX_MAPS_API_KEY', '')

MAX_BOT_TOKEN = os.getenv('MAX_BOT_TOKEN', '')
MAX_CHAT_ID = os.getenv('MAX_CHAT_ID', '')

ALLOWED_HOSTS = get_allowed_hosts_from_map(HOST_TO_DEPARTMENT_MAP)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'content',
    'schedule_alerts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edu_multisite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'content.context_processors.menu_processor',
                'content.context_processors.static_version',
                'content.context_processors.yandex_maps',
            ],
        },
    },
]

WSGI_APPLICATION = 'edu_multisite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Irkutsk'
USE_I18N = True
USE_L10N = True
USE_TZ = True

if DEBUG:
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [BASE_DIR / 'static']

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

    INSTALLED_APPS += ['livereload']

    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
        '::1',
    ]
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.getenv('PROD_STATIC_ROOT')

    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.getenv('PROD_MEDIA_ROOT')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
