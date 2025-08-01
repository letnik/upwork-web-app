#!/bin/bash

# Централізований скрипт управління проектом Upwork AI Assistant
# Використання: ./manage.sh [команда] [опції]

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функції для виводу
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка аргументів
COMMAND=${1:-"help"}

# Функція очищення проекту
clean_project() {
    log_info "Очищення проекту..."
    
    # Видалення кешів
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -name "*.pyd" -delete 2>/dev/null || true
    
    # Видалення тимчасових файлів
    rm -rf .pytest_cache/ 2>/dev/null || true
    rm -f .coverage 2>/dev/null || true
    rm -rf dist/ 2>/dev/null || true
    rm -rf build/ 2>/dev/null || true
    rm -rf *.egg-info/ 2>/dev/null || true
    
    # Видалення логів
    find . -name "*.log" -delete 2>/dev/null || true
    
    log_success "Проект очищено!"
}

# Функція встановлення залежностей
install_dependencies() {
    log_info "Встановлення залежностей..."
    
    # Перевірка наявності віртуального середовища
    if [ ! -d ".venv" ]; then
        log_warning "Віртуальне середовище не знайдено. Створюємо..."
        python3.11 -m venv .venv
    fi
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Встановлення залежностей
    ./tools/scripts/dependencies/install.sh all base
    
    log_success "Залежності встановлено!"
}

# Функція аудиту безпеки
audit_security() {
    log_info "Аудит безпеки залежностей..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Запуск аудиту
    ./tools/scripts/dependencies/audit.sh all
    
    log_success "Аудит безпеки завершено!"
}

# Функція тестування
run_tests() {
    log_info "Запуск тестів..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Запуск тестів
    python -m pytest tests/ -v --tb=short
    
    log_success "Тести завершено!"
}

# Функція запуску проекту
start_project() {
    log_info "Запуск проекту..."
    
    # Запуск через існуючий скрипт
    ./tools/scripts/project/start_project.sh
    
    log_success "Проект запущено!"
}

# Функція зупинки проекту
stop_project() {
    log_info "Зупинка проекту..."
    
    # Зупинка Docker контейнерів
    docker compose -f docker/docker-compose.yml down
    
    log_success "Проект зупинено!"
}

# Функція перезапуску проекту
restart_project() {
    log_info "Перезапуск проекту..."
    
    stop_project
    start_project
    
    log_success "Проект перезапущено!"
}

# Функція перевірки статусу
check_status() {
    log_info "Перевірка статусу проекту..."
    
    # Перевірка Docker контейнерів
    docker compose -f docker/docker-compose.yml ps
    
    # Перевірка процесів
    echo ""
    log_info "Активні процеси:"
    ps aux | grep -E "(uvicorn|python)" | grep -v grep || echo "Немає активних процесів"
}

# Функція оновлення залежностей
update_dependencies() {
    log_info "Оновлення залежностей..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Оновлення pip
    pip install --upgrade pip
    
    # Оновлення залежностей
    pip install --upgrade -r requirements/base.txt
    
    log_success "Залежності оновлено!"
}

# Функція допомоги
show_help() {
    echo "Централізований скрипт управління проектом Upwork AI Assistant"
    echo ""
    echo "Використання: ./manage.sh [команда]"
    echo ""
    echo "Команди:"
    echo "  clean           - Очищення проекту (кеші, тимчасові файли)"
    echo "  install         - Встановлення залежностей"
    echo "  audit           - Аудит безпеки залежностей"
    echo "  test            - Запуск тестів"
    echo "  start           - Запуск проекту"
    echo "  stop            - Зупинка проекту"
    echo "  restart         - Перезапуск проекту"
    echo "  status          - Перевірка статусу проекту"
    echo "  update          - Оновлення залежностей"
    echo "  help            - Показати цю допомогу"
    echo ""
    echo "Приклади:"
    echo "  ./manage.sh clean"
    echo "  ./manage.sh install"
    echo "  ./manage.sh start"
    echo "  ./manage.sh status"
}

# Головна логіка
case $COMMAND in
    "clean")
        clean_project
        ;;
    "install")
        install_dependencies
        ;;
    "audit")
        audit_security
        ;;
    "test")
        run_tests
        ;;
    "start")
        start_project
        ;;
    "stop")
        stop_project
        ;;
    "restart")
        restart_project
        ;;
    "status")
        check_status
        ;;
    "update")
        update_dependencies
        ;;
    "help"|*)
        show_help
        ;;
esac 

# Централізований скрипт управління проектом Upwork AI Assistant
# Використання: ./manage.sh [команда] [опції]

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функції для виводу
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка аргументів
COMMAND=${1:-"help"}

# Функція очищення проекту
clean_project() {
    log_info "Очищення проекту..."
    
    # Видалення кешів
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "*.pyo" -delete 2>/dev/null || true
    find . -name "*.pyd" -delete 2>/dev/null || true
    
    # Видалення тимчасових файлів
    rm -rf .pytest_cache/ 2>/dev/null || true
    rm -f .coverage 2>/dev/null || true
    rm -rf dist/ 2>/dev/null || true
    rm -rf build/ 2>/dev/null || true
    rm -rf *.egg-info/ 2>/dev/null || true
    
    # Видалення логів
    find . -name "*.log" -delete 2>/dev/null || true
    
    log_success "Проект очищено!"
}

# Функція встановлення залежностей
install_dependencies() {
    log_info "Встановлення залежностей..."
    
    # Перевірка наявності віртуального середовища
    if [ ! -d ".venv" ]; then
        log_warning "Віртуальне середовище не знайдено. Створюємо..."
        python3.11 -m venv .venv
    fi
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Встановлення залежностей
    ./tools/scripts/dependencies/install.sh all base
    
    log_success "Залежності встановлено!"
}

# Функція аудиту безпеки
audit_security() {
    log_info "Аудит безпеки залежностей..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Запуск аудиту
    ./tools/scripts/dependencies/audit.sh all
    
    log_success "Аудит безпеки завершено!"
}

# Функція тестування
run_tests() {
    log_info "Запуск тестів..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Запуск тестів
    python -m pytest tests/ -v --tb=short
    
    log_success "Тести завершено!"
}

# Функція запуску проекту
start_project() {
    log_info "Запуск проекту..."
    
    # Запуск через існуючий скрипт
    ./tools/scripts/project/start_project.sh
    
    log_success "Проект запущено!"
}

# Функція зупинки проекту
stop_project() {
    log_info "Зупинка проекту..."
    
    # Зупинка Docker контейнерів
    docker compose -f docker/docker-compose.yml down
    
    log_success "Проект зупинено!"
}

# Функція перезапуску проекту
restart_project() {
    log_info "Перезапуск проекту..."
    
    stop_project
    start_project
    
    log_success "Проект перезапущено!"
}

# Функція перевірки статусу
check_status() {
    log_info "Перевірка статусу проекту..."
    
    # Перевірка Docker контейнерів
    docker compose -f docker/docker-compose.yml ps
    
    # Перевірка процесів
    echo ""
    log_info "Активні процеси:"
    ps aux | grep -E "(uvicorn|python)" | grep -v grep || echo "Немає активних процесів"
}

# Функція оновлення залежностей
update_dependencies() {
    log_info "Оновлення залежностей..."
    
    # Активація віртуального середовища
    source .venv/bin/activate
    
    # Оновлення pip
    pip install --upgrade pip
    
    # Оновлення залежностей
    pip install --upgrade -r requirements/base.txt
    
    log_success "Залежності оновлено!"
}

# Функція допомоги
show_help() {
    echo "Централізований скрипт управління проектом Upwork AI Assistant"
    echo ""
    echo "Використання: ./manage.sh [команда]"
    echo ""
    echo "Команди:"
    echo "  clean           - Очищення проекту (кеші, тимчасові файли)"
    echo "  install         - Встановлення залежностей"
    echo "  audit           - Аудит безпеки залежностей"
    echo "  test            - Запуск тестів"
    echo "  start           - Запуск проекту"
    echo "  stop            - Зупинка проекту"
    echo "  restart         - Перезапуск проекту"
    echo "  status          - Перевірка статусу проекту"
    echo "  update          - Оновлення залежностей"
    echo "  help            - Показати цю допомогу"
    echo ""
    echo "Приклади:"
    echo "  ./manage.sh clean"
    echo "  ./manage.sh install"
    echo "  ./manage.sh start"
    echo "  ./manage.sh status"
}

# Головна логіка
case $COMMAND in
    "clean")
        clean_project
        ;;
    "install")
        install_dependencies
        ;;
    "audit")
        audit_security
        ;;
    "test")
        run_tests
        ;;
    "start")
        start_project
        ;;
    "stop")
        stop_project
        ;;
    "restart")
        restart_project
        ;;
    "status")
        check_status
        ;;
    "update")
        update_dependencies
        ;;
    "help"|*)
        show_help
        ;;
esac 