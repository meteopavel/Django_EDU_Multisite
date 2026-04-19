"""
Собирает JSON-файлы паспорта проекта на основе api_map JSON.

Что делает:
1. Читает api_map JSON.
2. Автоматически генерирует project_passport/project.meta.json, если он отсутствует
   или если указан флаг --refresh-meta.
3. Собирает project_passport/project.public.json для фронтенда портфолио.

Использование:
    python tools/build_project_passport.py --project-root .
    python tools/build_project_passport.py --project-root . --api-map project_passport/api_map__content__core__edu_multisite.json
    python tools/build_project_passport.py --project-root . --refresh-meta
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PASSPORT_DIRNAME = 'project_passport'


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description='Собирает project.meta.json и project.public.json из api_map JSON.',
    )
    parser.add_argument(
        '--project-root',
        default='.',
        help='Корень проекта. По умолчанию текущая директория.',
    )
    parser.add_argument(
        '--passport-dir',
        default=None,
        help=(
            'Директория паспорта проекта. '
            f'По умолчанию <project-root>/{DEFAULT_PASSPORT_DIRNAME}.'
        ),
    )
    parser.add_argument(
        '--api-map',
        default=None,
        help=(
            'Путь к api_map JSON-файлу. '
            'Если не указан, скрипт попытается автоматически найти его в директории project_passport.'
        ),
    )
    parser.add_argument(
        '--project-id',
        default=None,
        help='Явный project id. Если не задан, будет выведен из имени директории проекта.',
    )
    parser.add_argument(
        '--refresh-meta',
        action='store_true',
        help='Пересоздать project.meta.json даже если он уже существует.',
    )
    return parser.parse_args()


def utc_now_iso() -> str:
    """Возвращает текущее UTC-время в ISO-формате."""
    return datetime.now(timezone.utc).isoformat()


def load_json_file(file_path: Path) -> dict[str, Any]:
    """Загружает JSON-файл в словарь."""
    try:
        return json.loads(file_path.read_text(encoding='utf-8'))
    except FileNotFoundError as error:
        raise SystemExit(f'Файл не найден: {file_path}') from error
    except json.JSONDecodeError as error:
        raise SystemExit(f'Некорректный JSON в файле {file_path}: {error}') from error


def write_json_file(file_path: Path, payload: dict[str, Any]) -> None:
    """Записывает словарь в JSON-файл."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )


def resolve_path(project_root: Path, raw_path: str) -> Path:
    """Разрешает путь относительно project_root, если он не абсолютный."""
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (project_root / path).resolve()


def resolve_passport_dir(project_root: Path, raw_passport_dir: str | None) -> Path:
    """Определяет директорию паспорта проекта."""
    if raw_passport_dir is None:
        return (project_root / DEFAULT_PASSPORT_DIRNAME).resolve()
    passport_dir = Path(raw_passport_dir)
    if passport_dir.is_absolute():
        return passport_dir.resolve()
    return (project_root / passport_dir).resolve()


def auto_detect_api_map(passport_dir: Path) -> Path:
    """Пытается автоматически найти api_map JSON в директории паспорта проекта."""
    candidates = sorted(
        path
        for path in passport_dir.glob('api_map__*.json')
        if path.is_file()
    )
    if not candidates:
        raise SystemExit(
            f'В директории {passport_dir} не найдено ни одного api_map JSON-файла. '
            'Сначала запусти extract_api_map.py или укажи --api-map явно.'
        )

    if len(candidates) == 1:
        return candidates[0]

    combined_candidates = [
        path
        for path in candidates
        if '__' in path.stem.removeprefix('api_map__')
    ]
    if len(combined_candidates) == 1:
        return combined_candidates[0]

    candidate_names = '\n'.join(f'- {path.name}' for path in candidates)
    raise SystemExit(
        'Найдено несколько api_map JSON-файлов. '
        'Укажи нужный через --api-map.\n'
        f'{candidate_names}'
    )


def path_relative_to_base(path: Path, base: Path) -> str:
    """Возвращает путь относительно base, если это возможно."""
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def slugify(value: str) -> str:
    """Преобразует строку в slug."""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', value.strip().lower()).strip('-')
    return slug or 'project'


def titleize_slug(slug: str) -> str:
    """Преобразует slug в читаемый title."""
    acronym_map = {
        'api': 'API',
        'cli': 'CLI',
        'llm': 'LLM',
        'docx': 'DOCX',
        'csv': 'CSV',
        'json': 'JSON',
        'cms': 'CMS',
        'django': 'Django',
    }
    words = re.split(r'[-_]+', slug)
    title_words = []
    for word in words:
        if not word:
            continue
        lower = word.lower()
        title_words.append(acronym_map.get(lower, lower.capitalize()))
    return ' '.join(title_words) or 'Project'


def join_human_list(items: list[str]) -> str:
    """Собирает список строк в человекочитаемую строку."""
    filtered = [item for item in items if item]
    if not filtered:
        return ''
    if len(filtered) == 1:
        return filtered[0]
    if len(filtered) == 2:
        return f'{filtered[0]} и {filtered[1]}'
    return f'{", ".join(filtered[:-1])} и {filtered[-1]}'


def deep_merge(base: Any, override: Any) -> Any:
    """
    Рекурсивно объединяет структуры.
    Значения из override имеют приоритет.
    Для списков и скаляров override полностью заменяет base.
    """
    if isinstance(base, dict) and isinstance(override, dict):
        merged: dict[str, Any] = dict(base)
        for key, value in override.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
    return override


def collect_text_blobs(api_map_data: dict[str, Any]) -> list[str]:
    """Собирает текстовые фрагменты из api_map для эвристик."""
    blobs: list[str] = []
    blobs.extend(api_map_data.get('targets', []))
    blobs.append(api_map_data.get('target', '') or '')

    for module in api_map_data.get('modules', []):
        blobs.append(module.get('path', ''))
        blobs.append(module.get('module_docstring', '') or '')
        blobs.append(module.get('module_summary', '') or '')

        for constant in module.get('constants', []):
            blobs.append(constant.get('name', ''))
            blobs.append(constant.get('value_repr', '') or '')

        for function_data in module.get('functions', []):
            blobs.append(function_data.get('name', ''))
            blobs.append(function_data.get('signature', ''))
            blobs.append(function_data.get('docstring', '') or '')

        for class_data in module.get('classes', []):
            blobs.append(class_data.get('name', ''))
            blobs.append(class_data.get('signature', ''))
            blobs.append(class_data.get('docstring', '') or '')

            for field in class_data.get('fields', []):
                blobs.append(field.get('name', ''))
                blobs.append(field.get('annotation', '') or '')

            for method_data in class_data.get('methods', []):
                blobs.append(method_data.get('name', ''))
                blobs.append(method_data.get('signature', ''))
                blobs.append(method_data.get('docstring', '') or '')

    return blobs


def detect_features(api_map_data: dict[str, Any]) -> dict[str, bool]:
    """Определяет ключевые особенности проекта по api_map."""
    modules = api_map_data.get('modules', [])
    module_paths = [module.get('path', '') for module in modules]
    module_paths_lower = [path.lower() for path in module_paths]
    text_blob = '\n'.join(collect_text_blobs(api_map_data)).lower()

    has_django = (
        'django' in text_blob
        or any(path.endswith('/settings.py') for path in module_paths_lower)
        or any(path.endswith('/models.py') for path in module_paths_lower)
        or any(path.endswith('/admin.py') for path in module_paths_lower)
    )
    has_django_admin = any(path.endswith('/admin.py') for path in module_paths_lower)
    has_django_models = any(path.endswith('/models.py') for path in module_paths_lower)
    has_django_views = any(path.endswith('/views.py') for path in module_paths_lower)
    has_django_urls = any(path.endswith('/urls.py') for path in module_paths_lower)
    has_django_settings = any(path.endswith('/settings.py') for path in module_paths_lower)
    has_wsgi = any(path.endswith('/wsgi.py') for path in module_paths_lower)
    has_template_tags = any('/templatetags/' in path for path in module_paths_lower)
    has_context_processors = any(path.endswith('/context_processors.py') for path in module_paths_lower)
    has_utils = any(path.endswith('/utils.py') for path in module_paths_lower)
    has_decorators = any(path.endswith('/decorators.py') for path in module_paths_lower)
    has_forms = 'modelform' in text_blob or any('/forms.py' in path for path in module_paths_lower)
    has_env_config = '.env' in text_blob or 'os.getenv' in text_blob or 'environ' in text_blob
    has_mysql = 'django.db.backends.mysql' in text_blob or 'mysql' in text_blob
    has_json = 'json' in text_blob
    has_yandex_maps = 'yandex' in text_blob or 'яндекс' in text_blob
    has_host_routing = 'host_to_department_map' in text_blob or 'parse_host_map' in text_blob
    has_multisite = has_host_routing or 'department' in text_blob or 'подразделен' in text_blob
    has_news = 'news' in text_blob or 'новост' in text_blob
    has_documents = 'document' in text_blob or 'документ' in text_blob
    has_exam_info = 'exam' in text_blob or 'экзам' in text_blob
    has_services = 'service' in text_blob or 'услуг' in text_blob
    has_menu = 'menu' in text_blob or 'меню' in text_blob
    has_ajax = 'ajax' in text_blob
    has_admin_forms = has_django_admin and has_forms

    return {
        'has_django': has_django,
        'has_django_admin': has_django_admin,
        'has_django_models': has_django_models,
        'has_django_views': has_django_views,
        'has_django_urls': has_django_urls,
        'has_django_settings': has_django_settings,
        'has_wsgi': has_wsgi,
        'has_template_tags': has_template_tags,
        'has_context_processors': has_context_processors,
        'has_utils': has_utils,
        'has_decorators': has_decorators,
        'has_forms': has_forms,
        'has_env_config': has_env_config,
        'has_mysql': has_mysql,
        'has_json': has_json,
        'has_yandex_maps': has_yandex_maps,
        'has_host_routing': has_host_routing,
        'has_multisite': has_multisite,
        'has_news': has_news,
        'has_documents': has_documents,
        'has_exam_info': has_exam_info,
        'has_services': has_services,
        'has_menu': has_menu,
        'has_ajax': has_ajax,
        'has_admin_forms': has_admin_forms,
    }


def infer_project_id(project_root: Path, explicit_project_id: str | None) -> str:
    """Определяет project id."""
    if explicit_project_id:
        return slugify(explicit_project_id)
    return slugify(project_root.resolve().name)


def infer_title(project_id: str, features: dict[str, bool]) -> str:
    """Строит читаемый title проекта."""
    if features['has_django'] and features['has_multisite'] and features['has_documents']:
        return 'Django Multisite Content Platform'
    if features['has_django'] and features['has_multisite']:
        return 'Django Multisite Web Platform'
    if features['has_django'] and features['has_documents'] and features['has_news']:
        return 'Django Content Management Platform'
    if features['has_django']:
        return 'Django Web Project'
    return titleize_slug(project_id)


def infer_tagline(features: dict[str, bool]) -> str:
    """Строит короткий tagline проекта."""
    if features['has_django'] and features['has_multisite'] and features['has_documents']:
        return (
            'Django-платформа для мультисайтового управления подразделениями, '
            'контентом, документами и информационными разделами.'
        )
    if features['has_django'] and features['has_multisite']:
        return 'Django-проект с мультидоменной маршрутизацией и раздельным контентом подразделений.'
    if features['has_django']:
        return 'Django-проект с формализованной API-картой и структурированным техпрофилем.'
    return 'Python-проект с формализованной API-картой и проектным паспортом.'


def infer_summary(features: dict[str, bool], api_map_data: dict[str, Any]) -> str:
    """Строит summary проекта."""
    parts: list[str] = []

    if features['has_django']:
        parts.append(
            'Проект реализован на Django и организован как набор приложений '
            'с выделенными слоями моделей, представлений, маршрутизации и административного интерфейса.'
        )

    if features['has_multisite'] or features['has_host_routing']:
        parts.append(
            'Поддерживается мультидоменная логика, при которой активное подразделение '
            'определяется по хосту и влияет на выдачу контента.'
        )

    if features['has_documents'] or features['has_news'] or features['has_services']:
        content_parts: list[str] = []
        if features['has_news']:
            content_parts.append('новости')
        if features['has_documents']:
            content_parts.append('документы')
        if features['has_services']:
            content_parts.append('услуги')
        if features['has_exam_info']:
            content_parts.append('экзаменационные блоки')

        if content_parts:
            parts.append(
                'Проект включает предметные сущности и интерфейсы для разделов: '
                f'{join_human_list(content_parts)}.'
            )

    if features['has_django_admin']:
        parts.append(
            'Для управления данными используется расширенный Django admin '
            'с кастомными формами, фильтрами и inline-конфигурациями.'
        )

    if features['has_context_processors'] or features['has_template_tags'] or features['has_ajax']:
        ui_parts: list[str] = []
        if features['has_context_processors']:
            ui_parts.append('context processors')
        if features['has_template_tags']:
            ui_parts.append('template tags')
        if features['has_ajax']:
            ui_parts.append('AJAX-представления')
        parts.append(
            'На уровне шаблонов и UI-логики используются '
            f'{join_human_list(ui_parts)}.'
        )

    if not parts:
        stats = api_map_data.get('stats', {})
        return (
            'Python-проект с формализованной API-картой, пригодной для автоматической '
            f'сборки техпрофиля и портфельного представления. '
            f'В карте: {stats.get("modules", 0)} модулей, '
            f'{stats.get("functions", 0)} функций и {stats.get("classes", 0)} классов.'
        )

    return ' '.join(parts)


def infer_stack(features: dict[str, bool]) -> list[str]:
    """Определяет стек проекта."""
    stack = ['Python']
    if features['has_django']:
        stack.append('Django')
    if features['has_mysql']:
        stack.append('MySQL')
    if features['has_env_config']:
        stack.append('dotenv/env')
    if features['has_json']:
        stack.append('JSON')
    if features['has_yandex_maps']:
        stack.append('Yandex Maps API')
    return stack


def infer_domain(features: dict[str, bool]) -> list[str]:
    """Определяет доменные теги проекта."""
    domain: list[str] = []
    if features['has_django']:
        domain.extend(['web', 'django'])
    else:
        domain.append('python')

    if features['has_multisite']:
        domain.append('multisite')
    if features['has_documents'] or features['has_news'] or features['has_services']:
        domain.append('content-management')
    if features['has_django_admin']:
        domain.append('admin')
    if features['has_host_routing']:
        domain.append('domain-routing')

    seen: set[str] = set()
    result: list[str] = []
    for item in domain:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def infer_highlights(features: dict[str, bool]) -> list[str]:
    """Определяет highlights проекта."""
    highlights: list[str] = []

    if features['has_multisite'] or features['has_host_routing']:
        highlights.append('Мультидоменное определение подразделения по хосту запроса.')

    if features['has_django_admin']:
        highlights.append('Расширенный Django admin для управления контентом и связанными сущностями.')

    if features['has_documents']:
        highlights.append('Управление документами и их отображением по секциям и подразделениям.')

    if features['has_news']:
        highlights.append('Поддержка новостных разделов и AJAX-выдачи контента.')

    if features['has_exam_info']:
        highlights.append('Отдельный блок данных для экзаменационной информации и её актуальности.')

    if features['has_context_processors']:
        highlights.append('Контекстные процессоры для меню, версионирования статики и внешних ключей.')

    if features['has_template_tags']:
        highlights.append('Выделенные template tags для подготовки данных на уровне шаблонов.')

    if features['has_yandex_maps']:
        highlights.append('Интеграция с Yandex Maps API через настройки и шаблонный контекст.')

    return highlights


def infer_layers(api_map_data: dict[str, Any]) -> list[str]:
    """Определяет архитектурные слои проекта по путям модулей."""
    layers: list[str] = []
    seen: set[str] = set()

    for module in api_map_data.get('modules', []):
        path = module.get('path', '')
        path_lower = path.lower()
        layer = None

        if path_lower.endswith('/settings.py'):
            layer = 'project-settings'
        elif path_lower.endswith('/urls.py'):
            if path_lower.count('/') == 1:
                layer = 'app-routing'
            else:
                layer = 'project-routing'
        elif path_lower.endswith('/wsgi.py'):
            layer = 'deployment-entrypoint'
        elif path_lower.endswith('/admin.py'):
            layer = 'django-admin'
        elif path_lower.endswith('/models.py'):
            layer = 'domain-models'
        elif path_lower.endswith('/views.py'):
            layer = 'views'
        elif path_lower.endswith('/context_processors.py'):
            layer = 'context-processors'
        elif '/templatetags/' in path_lower:
            layer = 'template-tags'
        elif path_lower.endswith('/decorators.py'):
            layer = 'view-decorators'
        elif path_lower.endswith('/utils.py'):
            layer = 'utils'
        elif path_lower.startswith('core/'):
            layer = 'core-infrastructure'
        elif path_lower.startswith('content/'):
            layer = 'content-app'

        if layer and layer not in seen:
            seen.add(layer)
            layers.append(layer)

    return layers


def build_feature_flags(features: dict[str, bool]) -> list[str]:
    """Преобразует словарь feature flags в список сигналов."""
    mapping = {
        'has_django': 'django_project',
        'has_django_admin': 'django_admin',
        'has_django_models': 'django_models',
        'has_django_views': 'django_views',
        'has_django_urls': 'django_routing',
        'has_django_settings': 'django_settings',
        'has_wsgi': 'wsgi_entrypoint',
        'has_template_tags': 'template_tags',
        'has_context_processors': 'context_processors',
        'has_utils': 'utility_module',
        'has_decorators': 'custom_view_decorators',
        'has_forms': 'forms_layer',
        'has_env_config': 'env_config',
        'has_mysql': 'mysql_backend',
        'has_yandex_maps': 'yandex_maps_integration',
        'has_host_routing': 'host_based_routing',
        'has_multisite': 'multisite_content',
        'has_news': 'news_content',
        'has_documents': 'documents_content',
        'has_exam_info': 'exam_info_content',
        'has_services': 'services_content',
        'has_menu': 'menu_content',
        'has_ajax': 'ajax_views',
        'has_admin_forms': 'admin_customization',
    }
    return [
        public_name
        for feature_name, public_name in mapping.items()
        if features.get(feature_name)
    ]


def select_key_modules(api_map_data: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    """Выбирает наиболее содержательные модули для короткого техпрофиля."""
    scored_modules: list[tuple[int, dict[str, Any]]] = []
    for module in api_map_data.get('modules', []):
        module_stats = module.get('stats', {})
        score = (
            module_stats.get('functions', 0)
            + module_stats.get('methods', 0)
            + module_stats.get('classes', 0) * 2
            + module_stats.get('constants', 0)
        )
        scored_modules.append((score, module))

    scored_modules.sort(
        key=lambda item: (item[0], item[1].get('path', '')),
        reverse=True,
    )

    result: list[dict[str, Any]] = []
    for _, module in scored_modules[:limit]:
        result.append(
            {
                'path': module.get('path'),
                'summary': module.get('module_summary'),
                'stats': module.get('stats', {}),
            },
        )
    return result


def build_inferred_meta(
    api_map_data: dict[str, Any],
    project_root: Path,
    project_id: str,
) -> dict[str, Any]:
    """Строит автоматически выведенный draft project.meta.json."""
    features = detect_features(api_map_data)
    title = infer_title(project_id, features)

    return {
        'schema_version': '1.0',
        'generated_at': utc_now_iso(),
        'generated_by': 'tools/build_project_passport.py',
        'auto_generated': True,
        'review_status': 'draft',
        'id': project_id,
        'title': title,
        'tagline': infer_tagline(features),
        'summary': infer_summary(features, api_map_data),
        'status': 'active',
        'visibility': 'private_code',
        'role': 'solo_developer',
        'domain': infer_domain(features),
        'stack': infer_stack(features),
        'links': {
            'repo': None,
            'demo': None,
            'details': f'/projects/{project_id}',
        },
        'highlights': infer_highlights(features),
        'public_artifacts': [
            'api_map_json',
            'api_map_markdown',
            'project_meta_json',
            'project_public_json',
        ],
        'notes': {
            'project_root': '.',
            'source_target': api_map_data.get('target'),
            'source_targets': api_map_data.get('targets', []),
            'scanned_python_files': api_map_data.get('scanned_python_files'),
            'files_count': api_map_data.get('files_count'),
        },
    }


def build_public_payload(
    meta: dict[str, Any],
    api_map_data: dict[str, Any],
    project_root: Path,
    api_map_file: Path,
    meta_file: Path,
    public_file: Path,
) -> dict[str, Any]:
    """Собирает публичный JSON для портфолио."""
    features = detect_features(api_map_data)
    stats = api_map_data.get('stats', {})
    markdown_candidate = api_map_file.with_suffix('.md')

    public_artifacts = {
        'api_map_json': path_relative_to_base(api_map_file, project_root),
        'api_map_markdown': (
            path_relative_to_base(markdown_candidate, project_root)
            if markdown_candidate.exists()
            else None
        ),
        'project_meta_json': path_relative_to_base(meta_file, project_root),
        'project_public_json': path_relative_to_base(public_file, project_root),
    }

    return {
        'schema_version': '1.0',
        'generated_at': utc_now_iso(),
        'generated_by': 'tools/build_project_passport.py',
        'id': meta.get('id'),
        'title': meta.get('title'),
        'tagline': meta.get('tagline'),
        'summary': meta.get('summary'),
        'status': meta.get('status'),
        'visibility': meta.get('visibility'),
        'role': meta.get('role'),
        'domain': meta.get('domain', []),
        'stack': meta.get('stack', []),
        'links': meta.get('links', {}),
        'highlights': meta.get('highlights', []),
        'signals': build_feature_flags(features),
        'tech_profile': {
            'python_files': api_map_data.get('files_count', 0),
            'scanned_python_files': api_map_data.get('scanned_python_files', 0),
            'classes': stats.get('classes', 0),
            'dataclasses': stats.get('dataclasses', 0),
            'functions': stats.get('functions', 0),
            'methods': stats.get('methods', 0),
            'constants': stats.get('constants', 0),
            'has_django': features['has_django'],
            'has_django_admin': features['has_django_admin'],
            'has_django_models': features['has_django_models'],
            'has_django_views': features['has_django_views'],
            'has_multisite': features['has_multisite'],
            'has_host_routing': features['has_host_routing'],
            'has_documents': features['has_documents'],
            'has_news': features['has_news'],
            'has_exam_info': features['has_exam_info'],
            'has_api_map': True,
        },
        'architecture': {
            'target': api_map_data.get('target'),
            'targets': api_map_data.get('targets', []),
            'layers': infer_layers(api_map_data),
            'key_modules': select_key_modules(api_map_data),
        },
        'artifacts': public_artifacts,
        'source': {
            'api_map_schema_version': api_map_data.get('schema_version'),
            'api_map_generated_at': api_map_data.get('generated_at'),
            'api_map_generator': api_map_data.get('generator'),
            'meta_auto_generated': meta.get('auto_generated', False),
            'meta_review_status': meta.get('review_status'),
        },
    }


def main() -> None:
    """Точка входа."""
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        raise SystemExit(f'Корень проекта не найден: {project_root}')

    passport_dir = resolve_passport_dir(project_root, args.passport_dir)
    passport_dir.mkdir(parents=True, exist_ok=True)

    if args.api_map:
        api_map_file = resolve_path(project_root, args.api_map)
    else:
        api_map_file = auto_detect_api_map(passport_dir)

    if not api_map_file.exists():
        raise SystemExit(f'Файл api_map не найден: {api_map_file}')

    meta_file = passport_dir / 'project.meta.json'
    public_file = passport_dir / 'project.public.json'

    api_map_data = load_json_file(api_map_file)
    project_id = infer_project_id(project_root, args.project_id)

    inferred_meta = build_inferred_meta(
        api_map_data=api_map_data,
        project_root=project_root,
        project_id=project_id,
    )

    if meta_file.exists() and not args.refresh_meta:
        existing_meta = load_json_file(meta_file)
        merged_meta = deep_merge(inferred_meta, existing_meta)
        meta_was_generated = False
    else:
        merged_meta = inferred_meta
        write_json_file(meta_file, merged_meta)
        meta_was_generated = True

    public_payload = build_public_payload(
        meta=merged_meta,
        api_map_data=api_map_data,
        project_root=project_root,
        api_map_file=api_map_file,
        meta_file=meta_file,
        public_file=public_file,
    )
    write_json_file(public_file, public_payload)

    print('Готово:')
    if meta_was_generated:
        print(f'- создан meta: {meta_file}')
    else:
        print(f'- использован существующий meta: {meta_file}')
    print(f'- создан public: {public_file}')


if __name__ == '__main__':
    main()
