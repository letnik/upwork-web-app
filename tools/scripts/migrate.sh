#!/bin/bash

# 🔄 Скрипт для запуску міграцій бази даних
# Використання: ./scripts/migrate.sh

set -e  # Зупинка при помилці

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функції для логування
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

log_info "🔄 Запуск міграцій бази даних..."

# Перевірка чи існує папка backend
if [ ! -d "app/backend" ]; then
    log_error "Папка app/backend не існує!"
    exit 1
fi

# Перевірка чи запущений backend контейнер
if docker ps | grep -q upwork-backend; then
    log_info "📦 Запуск міграцій через Docker..."
    docker exec upwork-backend alembic upgrade head
    log_success "✅ Міграції через Docker завершено!"
elif docker ps | grep -q backend; then
    log_info "📦 Запуск міграцій через Docker (альтернативна назва)..."
    docker exec backend alembic upgrade head
    log_success "✅ Міграції через Docker завершено!"
else
    log_warning "⚠️ Backend контейнер не запущений."
    log_info "🔧 Спроба локального запуску міграцій..."
    
    # Перехід в папку backend
    cd app/backend
    
    # Перевірка чи встановлені залежності
    if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
        log_warning "⚠️ Віртуальне середовище не знайдено. Створення..."
        python3 -m venv venv
    fi
    
    # Активація віртуального середовища
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Встановлення залежностей
    log_info "📦 Встановлення залежностей..."
    pip install -r requirements.txt
    
    # Запуск міграцій
    log_info "🔄 Запуск міграцій..."
    alembic upgrade head
    
    log_success "✅ Локальні міграції завершено!"
fi

log_success "🎉 Всі міграції успішно виконано!" 