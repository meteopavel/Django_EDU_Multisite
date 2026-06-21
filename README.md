# Django Multisite Content Platform

[![Python](https://k2bz83mrsg.cdn.twcstorage.ru/images/shields/voa_django/python.svg)](https://docs.python.org/3/)
[![Django](https://k2bz83mrsg.cdn.twcstorage.ru/images/shields/voa_django/django.svg)](https://docs.djangoproject.com/en/stable/)
[![MySQL](https://k2bz83mrsg.cdn.twcstorage.ru/images/shields/voa_django/mysql.svg)](https://dev.mysql.com/doc/)
[![Pillow](https://k2bz83mrsg.cdn.twcstorage.ru/images/shields/voa_django/pillow.svg)](https://pillow.readthedocs.io/)

Django-платформа для мультисайтового управления подразделениями, контентом, документами и информационными разделами. Активное подразделение определяется по хосту запроса и влияет на выдачу контента: одно приложение обслуживает несколько доменов с разным наполнением.

Проект разработан и развёрнут в production для реального заказчика.

## Возможности

- Мультидоменное определение подразделения по хосту запроса
- Расширенный Django admin для управления контентом и связанными сущностями (кастомные формы, фильтры, inline-конфигурации)
- Управление документами и их отображением по секциям и подразделениям
- Новостные разделы с AJAX-выдачей контента
- Отдельный блок данных для экзаменационной информации и её актуальности
- Контекстные процессоры для меню, версионирования статики и внешних ключей
- Template tags для подготовки данных на уровне шаблонов
- Интеграция с Yandex Maps API через настройки и шаблонный контекст

## Стек

- Python, Django 3.2
- MySQL 8.0
- PyMySQL, python-dotenv, Pillow, BeautifulSoup4
- Yandex Maps API

## Локальный запуск

Требуется Python 3 и Docker (для базы данных).

1. Клонировать репозиторий и создать виртуальное окружение:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Создать файл `.env` в корне проекта (пример переменных):

   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DB_NAME=edu_multisite
   DB_USER=root
   DB_PASSWORD=rootpass
   DB_HOST=127.0.0.1
   DB_PORT=3306
   YANDEX_MAPS_API_KEY=your-api-key
   ```

3. Поднять базу данных:

   ```bash
   docker-compose up -d
   ```

4. Применить миграции и запустить сервер:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Структура проекта

```
edu_multisite/   — настройки проекта, корневые urls, wsgi
content/         — основное приложение: модели, admin, views,
                   context_processors, templatetags, urls
core/            — определение подразделения по хосту (host_parser)
templates/       — Jinja/Django-шаблоны
static/          — статические файлы
```

## Деплой

Развёртывание на shared-хостинге выполняется через `deploy-local.sh` (синхронизация по rsync).

## Автор

Павел Найдёнов — [meteopavel.space](https://meteopavel.space)
