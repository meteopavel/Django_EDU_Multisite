"""
Разовая команда для настройки: показывает события, накопленные ботом MAX,
чтобы найти chat_id нужной группы.

Использование:
  1. Убедитесь, что бот уже добавлен в чат заказчиков.
  2. Напишите любое сообщение в этом чате (или заново добавьте бота).
  3. Запустите: python manage.py max_get_chat_id
  4. Найдите в выводе событие с нужным чатом и скопируйте его chat_id в .env.
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.max_bot import MaxBotError, get_updates


class Command(BaseCommand):
    help = 'Показывает последние обновления MAX-бота, чтобы найти chat_id группы'

    def handle(self, *args: object, **options: object) -> None:
        try:
            updates = get_updates()
        except MaxBotError as exc:
            self.stderr.write(str(exc))
            return

        self.stdout.write(json.dumps(updates, ensure_ascii=False, indent=2))
