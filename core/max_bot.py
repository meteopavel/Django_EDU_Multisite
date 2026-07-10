"""
Минимальный клиент для MAX Bot API (https://dev.max.ru/docs-api).

Используется для отправки уведомлений в чат заказчиков, например
при устаревании расписания занятий (психология/медицина).
"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from pathlib import Path

import certifi
from django.conf import settings

MAX_API_BASE_URL = 'https://platform-api2.max.ru'

# Сертификат platform-api2.max.ru выпущен НУЦ Минцифры России (Russian Trusted
# Sub CA / Root CA) — этого корня нет в публичном списке certifi, поэтому
# добавляем его отдельным файлом (скачан с https://gu-st.ru, официальный
# источник Минцифры). Без него запросы падают с CERTIFICATE_VERIFY_FAILED.
_RUSSIAN_TRUSTED_CA = Path(__file__).resolve().parent / 'certs' / 'russian_trusted_ca.pem'

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
_SSL_CONTEXT.load_verify_locations(cafile=str(_RUSSIAN_TRUSTED_CA))


class MaxBotError(Exception):
    """Ошибка при обращении к MAX Bot API."""


def send_message(text: str, chat_id: str | None = None) -> None:
    """Отправляет текстовое сообщение в чат MAX через бота.

    Токен берётся из settings.MAX_BOT_TOKEN, chat_id — из
    settings.MAX_CHAT_ID, если не передан явно.
    """
    token = settings.MAX_BOT_TOKEN
    target_chat_id = chat_id or settings.MAX_CHAT_ID

    if not token:
        raise MaxBotError('MAX_BOT_TOKEN не задан в .env')
    if not target_chat_id:
        raise MaxBotError('MAX_CHAT_ID не задан в .env')

    url = f'{MAX_API_BASE_URL}/messages?chat_id={target_chat_id}'
    payload = json.dumps({'text': text}).encode('utf-8')
    request = urllib.request.Request(
        url,
        data=payload,
        method='POST',
        headers={
            'Authorization': token,
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=10, context=_SSL_CONTEXT) as response:
            if response.status >= 300:
                raise MaxBotError(f'MAX API вернул статус {response.status}')
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        raise MaxBotError(f'MAX API вернул ошибку {exc.code}: {body}') from exc
    except urllib.error.URLError as exc:
        raise MaxBotError(f'Не удалось связаться с MAX API: {exc.reason}') from exc


def get_updates(timeout: int = 20) -> dict:
    """Забирает накопленные события бота (long polling), в т.ч. chat_id
    групп, куда бота недавно добавили или где ему написали.

    Разовый вызов для настройки — узнать MAX_CHAT_ID.
    """
    token = settings.MAX_BOT_TOKEN
    if not token:
        raise MaxBotError('MAX_BOT_TOKEN не задан в .env')

    url = f'{MAX_API_BASE_URL}/updates?timeout={timeout}'
    request = urllib.request.Request(url, method='GET', headers={'Authorization': token})

    try:
        with urllib.request.urlopen(request, timeout=timeout + 10, context=_SSL_CONTEXT) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        raise MaxBotError(f'MAX API вернул ошибку {exc.code}: {body}') from exc
    except urllib.error.URLError as exc:
        raise MaxBotError(f'Не удалось связаться с MAX API: {exc.reason}') from exc
