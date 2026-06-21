"""
WSGI-конфигурация проекта edu_multisite.

Модуль:
- подготавливает sys.path для окружения хостинга;
- загружает переменные окружения из .env;
- инициализирует WSGI-приложение Django.

Переменная окружения HOSTING_ROOT задаёт корень проекта на хостинге.
Если не задана, используется расположение этого файла.
"""

import os
import sys
import platform


HOSTING_ROOT = os.environ.get(
    'HOSTING_ROOT',
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
python_version = ".".join(platform.python_version_tuple()[:2])

sys.path.insert(0, HOSTING_ROOT)
sys.path.insert(0, os.path.join(HOSTING_ROOT, 'edu_multisite'))
sys.path.insert(0, os.path.join(HOSTING_ROOT, '..', 'django', 'lib',
                                'python{0}'.format(python_version), 'site-packages'))
os.environ["DJANGO_SETTINGS_MODULE"] = "edu_multisite.settings"

from dotenv import load_dotenv

load_dotenv(os.path.join(HOSTING_ROOT, '..', '.env'))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
