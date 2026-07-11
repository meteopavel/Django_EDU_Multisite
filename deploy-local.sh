#!/bin/bash
#===============================================================================
# DEPLOY SCRIPT FOR Django_EDU_Multisite
#===============================================================================
#
# 📋 НАЗНАЧЕНИЕ:
#   Автоматизирует деплой: код → фикстуры → медиа
#
# 🚀 ИСПОЛЬЗОВАНИЕ:
#   ./deploy-local.sh                    # коммит с сообщением по умолчанию
#   ./deploy-local.sh "Твое сообщение"   # коммит с кастомным сообщением
#
# ⚙️  ТРЕБОВАНИЯ:
#   1. Файл .env в корне проекта с переменными:
#        - RSYNC_USER, RSYNC_HOST, RSYNC_PATH (обязательно)
#        - RSYNC_PASSWORD — тот же пароль, что от панели/FTP-доступа Timeweb;
#          используется как резервный путь (FTPS), если SSH/rsync не сработает
#   2. Python, git, rsync — в PATH
#   3. lftp: brew install lftp (нужен только для резервного пути через FTPS)
#   4. meteopavel/tools/deploy_helpers.sh — общий файл с хелперами, лежит
#      в соседнем проекте meteopavel (../meteopavel/tools/)
#
# 🔐 БЕЗОПАСНОСТЬ:
#   - .env должен быть в .gitignore
#   - Не коммитьте этот скрипт с паролями, если проект публичный
#
#===============================================================================

set -e  # Останавливать скрипт при любой ошибке

# ================= КОНСТАНТЫ =================
DEFAULT_COMMIT_MSG="Update info"
ENV_FILE="$(git rev-parse --show-toplevel)/.env"

# ================= ФУНКЦИИ =================

# Чтение переменной из .env
get_env() {
    local var_name="$1"
    local env_file="$2"

    if [[ ! -f "$env_file" ]]; then
        echo ""
        return
    fi

    grep -E "^${var_name}=" "$env_file" 2>/dev/null | head -1 | cut -d'=' -f2-
}

# Проверка: переменная не пустая
require_env() {
    local var_name="$1"
    local var_value="$2"

    if [[ -z "$var_value" ]]; then
        echo "❌ Ошибка: переменная $var_name не найдена или пустая в $ENV_FILE"
        exit 1
    fi
}

# Общие функции (run_with_heartbeat, timeout_run, rsync_via_tunnel,
# rsync_or_ftps_fallback) — используются во всех проектах, см. сам файл.
source "$(dirname "$(git rev-parse --show-toplevel)")/meteopavel/tools/deploy_helpers.sh"

# ================= ЗАГРУЗКА ПЕРЕМЕННЫХ =================

# Читаем все обязательные переменные
RSYNC_USER=$(get_env "RSYNC_USER" "$ENV_FILE")
RSYNC_HOST=$(get_env "RSYNC_HOST" "$ENV_FILE")
RSYNC_PATH=$(get_env "RSYNC_PATH" "$ENV_FILE")
RSYNC_PASSWORD=$(get_env "RSYNC_PASSWORD" "$ENV_FILE")

# Строгая проверка: если хоть одна переменная пустая — стоп
require_env "RSYNC_USER" "$RSYNC_USER"
require_env "RSYNC_HOST" "$RSYNC_HOST"
require_env "RSYNC_PATH" "$RSYNC_PATH"
require_env "RSYNC_PASSWORD" "$RSYNC_PASSWORD"

# Сообщение коммита: аргумент или константа по умолчанию
COMMIT_MSG="${1:-$DEFAULT_COMMIT_MSG}"

# ================= ПРОВЕРКА SSH-КЛЮЧА ДЛЯ GITHUB =================
echo "🔐 Проверка SSH-ключа для GitHub..."

# Проверяем соединение: ключ должен подгрузиться автоматически из конфиг + Keychain
SSH_TEST=$(ssh -T -o ConnectTimeout=5 git@github.com 2>&1) || true

if echo "$SSH_TEST" | grep -q "You've successfully authenticated"; then
    echo "✅ GitHub: аутентификация успешна"
else
    echo "❌ Не удалось подключиться к GitHub по SSH"
    echo "💡 Диагностика: $SSH_TEST"
    echo "💡 Убедитесь, что ключ добавлен: ssh-add --apple-use-keychain ~/.ssh/github"
    exit 1
fi
echo "----------------------------------------"

# ================= ДЕПЛОЙ =================

echo "🚀 Деплой: '$COMMIT_MSG'"
echo "📁 Проект: $(git rev-parse --show-toplevel)"
echo "----------------------------------------"

# 🪪 Паспорт проекта
echo "🪪 Обновляем паспорт проекта..."
.venv/bin/python tools/extract_api_map.py content core edu_multisite \
    --project-root .
.venv/bin/python tools/build_project_passport.py --project-root .
echo "✅ Паспорт проекта обновлён."

# 1️⃣ Коммит и пуш кода
echo "📦 Этап 1/3: Коммит изменений кода..."
git add .

if ! git diff --staged --quiet; then
    git commit -m "$COMMIT_MSG"
    git push
    echo "✅ Код закоммичен и отправлен"
else
    echo "⚠️ Нет изменений для коммита (код)"
fi

# 2️⃣ Дамп контента и отдельный коммит фикстуры
echo "💾 Этап 2/3: Обновление фикстур..."

DB_HOST=$(get_env "DB_HOST" "$ENV_FILE")
DB_PORT=$(get_env "DB_PORT" "$ENV_FILE")
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"

if ! nc -z -w3 "$DB_HOST" "$DB_PORT" 2>/dev/null; then
    echo "❌ MySQL недоступен на ${DB_HOST}:${DB_PORT} — запустите базу и повторите деплой"
    exit 1
fi
echo "✅ MySQL доступен"

.venv/bin/python manage.py dumpdata content --indent=2 > content/fixtures/content.json

git add content/fixtures/content.json

if ! git diff --staged --quiet; then
    git commit -m "Update content"
    git push
    echo "✅ Фикстуры закоммичены и отправлены"
else
    echo "⚠️ Фикстура не изменилась"
fi

# 3️⃣ Деплой на сервер по SSH
echo "🖥️  Этап 3/4: Деплой на сервер..."
run_with_heartbeat "деплой на сервере" \
    ssh -i ~/.ssh/timeweb_shared -o StrictHostKeyChecking=no \
        -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 \
        "${RSYNC_USER}@${RSYNC_HOST}" \
        "cd /home/c/cj82062/DjangoVOA/public_html && bash deploy.sh"
echo "✅ Сервер обновлён"

# 4️⃣ Синхронизация медиа: SSH/rsync основной путь, FTPS — резерв на случай сбоя
echo "📤 Этап 4/4: Синхронизация медиа..."
rsync_or_ftps_fallback "${RSYNC_USER}" "${RSYNC_HOST}" \
    media/ "${RSYNC_PATH}" "${RSYNC_PASSWORD}"

echo "----------------------------------------"
echo "✅ Деплой завершён успешно!"