import os
import sys
import platform

# Путь к вашему виртуальному окружению
VENV_PATH = '/home/c/cj82062/DjangoVOA/django'

# Активируем виртуальное окружение
activate_this = os.path.join(VENV_PATH, 'bin', 'activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})
else:
    # Если activate_this.py нет (в новых версиях), просто добавляем путь
    sys.path.insert(0, os.path.join(VENV_PATH, 'lib', 'python3.10', 'site-packages'))


sys.path.insert(0, '/home/c/cj82062/DjangoVOA/public_html')
sys.path.insert(0, '/home/c/cj82062/DjangoVOA/public_html/edu_multisite')
python_version = ".".join(platform.python_version_tuple()[:2])
sys.path.insert(0, '/home/c/cj82062/DjangoVOA//django/lib/python{0}/site-packages'.format(python_version))
os.environ["DJANGO_SETTINGS_MODULE"] = "edu_multisite.settings"

from dotenv import load_dotenv
load_dotenv('/home/c/cj82062/DjangoVOA/.env')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()