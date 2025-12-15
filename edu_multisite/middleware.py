import re
from django.utils.deprecation import MiddlewareMixin

class StaticCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Только для статических файлов
        if request.path.startswith('/static/') and response.status_code == 200:
            # Если имя файла содержит хеш (например, main.a1b2c3d4.css)
            if re.search(r'/[a-f0-9]{8,}\.(css|js|png|jpg|jpeg|gif|ico|svg|woff2)$', request.path):
                response['Cache-Control'] = 'public, immutable, max-age=31536000'
                response['Expires'] = 'Tue, 31 Dec 2030 23:59:59 GMT'  # очень далеко в будущем
            else:
                # Для остальных — 1 день
                response['Cache-Control'] = 'public, max-age=86400'
                response['Expires'] = 'Tue, 31 Dec 2025 23:59:59 GMT'  # на 1 день

        return response