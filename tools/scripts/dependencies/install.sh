#!/bin/bash

# Скрипт для встановлення залежностей
# Використання: ./install.sh [service_name] [environment]

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
ENVIRONMENT=${2:-"base"}

# Валідні сервіси
VALID_SERVICES=("api-gateway" "ai-service" "auth-service" "analytics-service" "notification-service" "upwork-service" "all")

# Валідні середовища
VALID_ENVIRONMENTS=("base" "dev" "test" "prod")

# Перевірка валідності сервісу
if [[ ! " ${VALID_SERVICES[@]} " =~ " ${SERVICE_NAME} " ]]; then
    log_error "Невідомий сервіс: $SERVICE_NAME"
    log_info "Валідні сервіси: ${VALID_SERVICES[*]}"
    exit 1
fi

# Перевірка валідності середовища
if [[ ! " ${VALID_ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    log_error "Невідоме середовище: $ENVIRONMENT"
    log_info "Валідні середовища: ${VALID_ENVIRONMENTS[*]}"
    exit 1
fi

# Функція встановлення залежностей для сервісу
install_service_dependencies() {
    local service=$1
    local env=$2
    
    log_info "Встановлення залежностей для $service в середовищі $env"
    
    # Базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Встановлення базових залежностей..."
        pip install -r requirements/base.txt
    fi
    
    # Специфічні залежності сервісу
    if [ -f "requirements/$service.txt" ]; then
        log_info "Встановлення специфічних залежностей для $service..."
        pip install -r requirements/$service.txt
    fi
    
    # Environment-specific залежності
    if [ -f "requirements/$env.txt" ]; then
        log_info "Встановлення залежностей для середовища $env..."
        pip install -r requirements/$env.txt
    fi
    
    log_success "Залежності для $service встановлено успішно!"
}

# Функція встановлення всіх залежностей
install_all_dependencies() {
    local env=$1
    
    log_info "Встановлення всіх залежностей в середовищі $env"
    
    # Базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Встановлення базових залежностей..."
        pip3 install -r requirements/base.txt
    fi
    
    # Всі специфічні залежності сервісів
    for service in "${VALID_SERVICES[@]}"; do
        if [ "$service" != "all" ] && [ -f "requirements/$service.txt" ]; then
            log_info "Встановлення залежностей для $service..."
            pip3 install -r requirements/$service.txt
        fi
    done
    
    # Environment-specific залежності
    if [ -f "requirements/$env.txt" ]; then
        log_info "Встановлення залежностей для середовища $env..."
        pip3 install -r requirements/$env.txt
    fi
    
    log_success "Всі залежності встановлено успішно!"
}

# Головна логіка
main() {
    log_info "Початок встановлення залежностей..."
    log_info "Сервіс: $SERVICE_NAME"
    log_info "Середовище: $ENVIRONMENT"
    
    # Перевірка наявності requirements папки
    if [ ! -d "requirements" ]; then
        log_error "Папка requirements не знайдена!"
        exit 1
    fi
    
    # Встановлення залежностей
    if [ "$SERVICE_NAME" = "all" ]; then
        install_all_dependencies "$ENVIRONMENT"
    else
        install_service_dependencies "$SERVICE_NAME" "$ENVIRONMENT"
    fi
    
    log_success "Встановлення залежностей завершено!"
}

# Запуск головної функції
main "$@" 

# Скрипт для встановлення залежностей
# Використання: ./install.sh [service_name] [environment]

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
ENVIRONMENT=${2:-"base"}

# Валідні сервіси
VALID_SERVICES=("api-gateway" "ai-service" "auth-service" "analytics-service" "notification-service" "upwork-service" "all")

# Валідні середовища
VALID_ENVIRONMENTS=("base" "dev" "test" "prod")

# Перевірка валідності сервісу
if [[ ! " ${VALID_SERVICES[@]} " =~ " ${SERVICE_NAME} " ]]; then
    log_error "Невідомий сервіс: $SERVICE_NAME"
    log_info "Валідні сервіси: ${VALID_SERVICES[*]}"
    exit 1
fi

# Перевірка валідності середовища
if [[ ! " ${VALID_ENVIRONMENTS[@]} " =~ " ${ENVIRONMENT} " ]]; then
    log_error "Невідоме середовище: $ENVIRONMENT"
    log_info "Валідні середовища: ${VALID_ENVIRONMENTS[*]}"
    exit 1
fi

# Функція встановлення залежностей для сервісу
install_service_dependencies() {
    local service=$1
    local env=$2
    
    log_info "Встановлення залежностей для $service в середовищі $env"
    
    # Базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Встановлення базових залежностей..."
        pip install -r requirements/base.txt
    fi
    
    # Специфічні залежності сервісу
    if [ -f "requirements/$service.txt" ]; then
        log_info "Встановлення специфічних залежностей для $service..."
        pip install -r requirements/$service.txt
    fi
    
    # Environment-specific залежності
    if [ -f "requirements/$env.txt" ]; then
        log_info "Встановлення залежностей для середовища $env..."
        pip install -r requirements/$env.txt
    fi
    
    log_success "Залежності для $service встановлено успішно!"
}

# Функція встановлення всіх залежностей
install_all_dependencies() {
    local env=$1
    
    log_info "Встановлення всіх залежностей в середовищі $env"
    
    # Базові залежності
    if [ -f "requirements/base.txt" ]; then
        log_info "Встановлення базових залежностей..."
        pip install -r requirements/base.txt
    fi
    
    # Всі специфічні залежності сервісів
    for service in "${VALID_SERVICES[@]}"; do
        if [ "$service" != "all" ] && [ -f "requirements/$service.txt" ]; then
            log_info "Встановлення залежностей для $service..."
            pip install -r requirements/$service.txt
        fi
    done
    
    # Environment-specific залежності
    if [ -f "requirements/$env.txt" ]; then
        log_info "Встановлення залежностей для середовища $env..."
        pip install -r requirements/$env.txt
    fi
    
    log_success "Всі залежності встановлено успішно!"
}

# Головна логіка
main() {
    log_info "Початок встановлення залежностей..."
    log_info "Сервіс: $SERVICE_NAME"
    log_info "Середовище: $ENVIRONMENT"
    
    # Перевірка наявності requirements папки
    if [ ! -d "requirements" ]; then
        log_error "Папка requirements не знайдена!"
        exit 1
    fi
    
    # Встановлення залежностей
    if [ "$SERVICE_NAME" = "all" ]; then
        install_all_dependencies "$ENVIRONMENT"
    else
        install_service_dependencies "$SERVICE_NAME" "$ENVIRONMENT"
    fi
    
    log_success "Встановлення залежностей завершено!"
}

# Запуск головної функції
main "$@" 