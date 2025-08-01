#!/bin/bash

# Скрипт для аудиту залежностей
# Використання: ./audit.sh [service_name]

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
SERVICE_NAME=${1:-"all"}

# Валідні сервіси
VALID_SERVICES=("api-gateway" "ai-service" "auth-service" "analytics-service" "notification-service" "upwork-service" "all")

# Перевірка валідності сервісу
if [[ ! " ${VALID_SERVICES[@]} " =~ " ${SERVICE_NAME} " ]]; then
    log_error "Невідомий сервіс: $SERVICE_NAME"
    log_info "Валідні сервіси: ${VALID_SERVICES[*]}"
    exit 1
fi

# Функція перевірки наявності pip-audit
check_pip_audit() {
    if ! command -v pip-audit &> /dev/null; then
        log_warning "pip-audit не встановлено. Встановлюємо..."
        pip install pip-audit
    fi
}

# Функція аудиту залежностей для сервісу
audit_service_dependencies() {
    local service=$1
    
    log_info "Аудит залежностей для $service"
    
    # Створюємо тимчасовий файл з усіма залежностями сервісу
    local temp_file=$(mktemp)
    
    # Додаємо базові залежності
    if [ -f "requirements/base.txt" ]; then
        cat requirements/base.txt >> "$temp_file"
    fi
    
    # Додаємо специфічні залежності сервісу
    if [ -f "requirements/$service.txt" ]; then
        cat requirements/$service.txt >> "$temp_file"
    fi
    
    # Видаляємо коментарі та порожні рядки
    grep -v '^#' "$temp_file" | grep -v '^$' > "${temp_file}.clean"
    
    # Запускаємо аудит
    log_info "Перевірка безпеки залежностей..."
    if pip-audit -r "${temp_file}.clean" 2>/dev/null; then
        log_success "Вразливостей не знайдено для $service"
    else
        log_warning "Знайдено потенційні вразливості для $service"
    fi
    
    # Очищення
    rm -f "$temp_file" "${temp_file}.clean"
}

# Функція аудиту всіх залежностей
audit_all_dependencies() {
    log_info "Аудит всіх залежностей"
    
    # Перевіряємо базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Перевірка базових залежностей..."
        if pip-audit -r requirements/base.txt 2>/dev/null; then
            log_success "Вразливостей в базових залежностях не знайдено"
        else
            log_warning "Знайдено потенційні вразливості в базових залежностях"
        fi
    fi
    
    # Перевіряємо кожен сервіс
    for service in "${VALID_SERVICES[@]}"; do
        if [ "$service" != "all" ] && [ -f "requirements/$service.txt" ]; then
            audit_service_dependencies "$service"
        fi
    done
}

# Функція перевірки дублікатів
check_duplicates() {
    log_info "Перевірка дублікатів залежностей..."
    
    # Збираємо всі залежності
    local all_deps=$(find requirements -name "*.txt" -exec cat {} \; | grep -v '^#' | grep -v '^$' | grep -v '^-r' | sort)
    
    # Знаходимо дублікати
    local duplicates=$(echo "$all_deps" | cut -d'=' -f1 | sort | uniq -d)
    
    if [ -n "$duplicates" ]; then
        log_warning "Знайдено дублікати залежностей:"
        echo "$duplicates" | while read -r dep; do
            echo "  - $dep"
        done
    else
        log_success "Дублікатів не знайдено"
    fi
}

# Функція перевірки застарілих версій
check_outdated() {
    log_info "Перевірка застарілих версій..."
    
    # Перевіряємо тільки базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Перевірка оновлень для базових залежностей..."
        pip list --outdated --format=freeze | grep -f <(grep -v '^#' requirements/base.txt | cut -d'=' -f1) || true
    fi
}

# Головна логіка
main() {
    log_info "Початок аудиту залежностей..."
    log_info "Сервіс: $SERVICE_NAME"
    
    # Перевірка наявності requirements папки
    if [ ! -d "requirements" ]; then
        log_error "Папка requirements не знайдена!"
        exit 1
    fi
    
    # Перевірка pip-audit
    check_pip_audit
    
    # Перевірка дублікатів
    check_duplicates
    
    # Аудит залежностей
    if [ "$SERVICE_NAME" = "all" ]; then
        audit_all_dependencies
    else
        audit_service_dependencies "$SERVICE_NAME"
    fi
    
    # Перевірка застарілих версій
    check_outdated
    
    log_success "Аудит залежностей завершено!"
}

# Запуск головної функції
main "$@" 

# Скрипт для аудиту залежностей
# Використання: ./audit.sh [service_name]

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
SERVICE_NAME=${1:-"all"}

# Валідні сервіси
VALID_SERVICES=("api-gateway" "ai-service" "auth-service" "analytics-service" "notification-service" "upwork-service" "all")

# Перевірка валідності сервісу
if [[ ! " ${VALID_SERVICES[@]} " =~ " ${SERVICE_NAME} " ]]; then
    log_error "Невідомий сервіс: $SERVICE_NAME"
    log_info "Валідні сервіси: ${VALID_SERVICES[*]}"
    exit 1
fi

# Функція перевірки наявності pip-audit
check_pip_audit() {
    if ! command -v pip-audit &> /dev/null; then
        log_warning "pip-audit не встановлено. Встановлюємо..."
        pip install pip-audit
    fi
}

# Функція аудиту залежностей для сервісу
audit_service_dependencies() {
    local service=$1
    
    log_info "Аудит залежностей для $service"
    
    # Створюємо тимчасовий файл з усіма залежностями сервісу
    local temp_file=$(mktemp)
    
    # Додаємо базові залежності
    if [ -f "requirements/base.txt" ]; then
        cat requirements/base.txt >> "$temp_file"
    fi
    
    # Додаємо специфічні залежності сервісу
    if [ -f "requirements/$service.txt" ]; then
        cat requirements/$service.txt >> "$temp_file"
    fi
    
    # Видаляємо коментарі та порожні рядки
    grep -v '^#' "$temp_file" | grep -v '^$' > "${temp_file}.clean"
    
    # Запускаємо аудит
    log_info "Перевірка безпеки залежностей..."
    if pip-audit -r "${temp_file}.clean" 2>/dev/null; then
        log_success "Вразливостей не знайдено для $service"
    else
        log_warning "Знайдено потенційні вразливості для $service"
    fi
    
    # Очищення
    rm -f "$temp_file" "${temp_file}.clean"
}

# Функція аудиту всіх залежностей
audit_all_dependencies() {
    log_info "Аудит всіх залежностей"
    
    # Перевіряємо базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Перевірка базових залежностей..."
        if pip-audit -r requirements/base.txt 2>/dev/null; then
            log_success "Вразливостей в базових залежностях не знайдено"
        else
            log_warning "Знайдено потенційні вразливості в базових залежностях"
        fi
    fi
    
    # Перевіряємо кожен сервіс
    for service in "${VALID_SERVICES[@]}"; do
        if [ "$service" != "all" ] && [ -f "requirements/$service.txt" ]; then
            audit_service_dependencies "$service"
        fi
    done
}

# Функція перевірки дублікатів
check_duplicates() {
    log_info "Перевірка дублікатів залежностей..."
    
    # Збираємо всі залежності
    local all_deps=$(find requirements -name "*.txt" -exec cat {} \; | grep -v '^#' | grep -v '^$' | grep -v '^-r' | sort)
    
    # Знаходимо дублікати
    local duplicates=$(echo "$all_deps" | cut -d'=' -f1 | sort | uniq -d)
    
    if [ -n "$duplicates" ]; then
        log_warning "Знайдено дублікати залежностей:"
        echo "$duplicates" | while read -r dep; do
            echo "  - $dep"
        done
    else
        log_success "Дублікатів не знайдено"
    fi
}

# Функція перевірки застарілих версій
check_outdated() {
    log_info "Перевірка застарілих версій..."
    
    # Перевіряємо тільки базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Перевірка оновлень для базових залежностей..."
        pip list --outdated --format=freeze | grep -f <(grep -v '^#' requirements/base.txt | cut -d'=' -f1) || true
    fi
}

# Головна логіка
main() {
    log_info "Початок аудиту залежностей..."
    log_info "Сервіс: $SERVICE_NAME"
    
    # Перевірка наявності requirements папки
    if [ ! -d "requirements" ]; then
        log_error "Папка requirements не знайдена!"
        exit 1
    fi
    
    # Перевірка pip-audit
    check_pip_audit
    
    # Перевірка дублікатів
    check_duplicates
    
    # Аудит залежностей
    if [ "$SERVICE_NAME" = "all" ]; then
        audit_all_dependencies
    else
        audit_service_dependencies "$SERVICE_NAME"
    fi
    
    # Перевірка застарілих версій
    check_outdated
    
    log_success "Аудит залежностей завершено!"
}

# Запуск головної функції
main "$@" 