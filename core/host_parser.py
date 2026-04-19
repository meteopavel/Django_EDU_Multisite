"""
Утилиты разбора конфигурации соответствия хостов и подразделений.

Модуль используется для:
- преобразования строковой карты хостов в словарь;
- получения списка допустимых хостов для настроек Django.
"""

from __future__ import annotations


def parse_host_map(raw_map: str) -> dict[str, str]:
    """Преобразует строковую карту хостов в словарь вида {host: department_slug}."""
    host_map: dict[str, str] = {}
    raw_map = raw_map.strip().replace('\\', '')
    if not raw_map:
        return host_map
    for line in raw_map.splitlines():
        line = line.strip()
        if not line or ':' not in line:
            continue
        slug, hosts_str = line.split(':', 1)
        slug = slug.strip()
        hosts = [host.strip() for host in hosts_str.split(',') if host.strip()]
        for host_with_port in hosts:
            host = host_with_port.split(':')[0].lower()
            host_map[host] = slug
    return host_map


def get_allowed_hosts_from_map(raw_map: str) -> list[str]:
    """Возвращает список хостов из конфигурационной карты."""
    return list(parse_host_map(raw_map).keys())
