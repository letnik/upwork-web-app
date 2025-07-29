#!/bin/bash

# 🚀 Скрипт розгортання Upwork AI Assistant
# Використання: ./scripts/deploy.sh [local|staging|production]

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

# Перевірка чи існує папка dist
if [ ! -d "dist" ]; then
    log_error "Папка dist не існує! Спочатку запустіть збірку: ./scripts/build.sh"
    exit 1
fi

# Функція локального розгортання
deploy_local() {
    log_info "🏠 Локальне розгортання..."
    
    # Перевірка чи встановлений Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker не встановлений!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не встановлений!"
        exit 1
    fi
    
    # Зупинка існуючих контейнерів
    log_info "🛑 Зупинка існуючих контейнерів..."
    docker-compose -f configs/docker/docker-compose.yml down 2>/dev/null || true
    
    # Запуск контейнерів
    log_info "🚀 Запуск контейнерів..."
    docker-compose -f configs/docker/docker-compose.yml up -d
    
    # Очікування запуску сервісів
    log_info "⏳ Очікування запуску сервісів..."
    sleep 10
    
    # Перевірка статусу
    log_info "📊 Перевірка статусу сервісів..."
    docker-compose ps
    
    log_success "✅ Локальне розгортання завершено!"
    log_info "🌐 Frontend: http://localhost:3000"
    log_info "🔌 Backend API: http://localhost:8000"
    log_info "📚 API документація: http://localhost:8000/docs"
}

# Функція розробки (без Docker)
deploy_dev() {
    log_info "🔧 Розробка (локальний запуск)..."
    
    # Перевірка чи існують папки
    if [ ! -d "app/backend" ]; then
        log_error "Папка app/backend не існує!"
        exit 1
    fi
    
    if [ ! -d "app/frontend" ]; then
        log_error "Папка app/frontend не існує!"
        exit 1
    fi
    
    # Запуск тільки бази даних та Redis
    log_info "🐳 Запуск бази даних та Redis..."
    docker-compose -f configs/docker/docker-compose.yml up postgres redis -d
    
    # Інструкції для розробки
    log_success "✅ База даних та Redis запущені!"
    log_info "📝 Для повної розробки запустіть в окремих терміналах:"
    log_info "   Термінал 1: cd app/backend && uvicorn src.main:app --reload"
    log_info "   Термінал 2: cd app/frontend && npm start"
    log_info "🌐 Frontend буде доступний: http://localhost:3000"
    log_info "🔌 Backend API буде доступний: http://localhost:8000"
}

# Функція staging розгортання
deploy_staging() {
    log_info "🧪 Staging розгортання..."
    
    # Перевірка змінних середовища
    if [ ! -f ".env.staging" ]; then
        log_error "Файл .env.staging не знайдено!"
        exit 1
    fi
    
    # Завантаження змінних середовища
    export $(cat .env.staging | xargs)
    
    # Розгортання через docker-compose
    docker-compose -f docker-compose.staging.yml up -d
    
    log_success "✅ Staging розгортання завершено!"
}

# Функція production розгортання
deploy_production() {
    log_info "🏭 Production розгортання..."
    
    # Перевірка чи ми в production середовищі
    if [ "$ENVIRONMENT" != "production" ]; then
        log_warning "⚠️ Увага! Ви розгортаєте в production середовище!"
        read -p "Продовжити? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Розгортання скасовано."
            exit 0
        fi
    fi
    
    # Перевірка змінних середовища
    if [ ! -f ".env.production" ]; then
        log_error "Файл .env.production не знайдено!"
        exit 1
    fi
    
    # Завантаження змінних середовища
    export $(cat .env.production | xargs)
    
    # Створення backup перед розгортанням
    log_info "💾 Створення backup..."
    ./scripts/backup.sh
    
    # Розгортання через docker-compose
    docker-compose -f docker-compose.production.yml up -d
    
    # Запуск міграцій
    log_info "🔄 Запуск міграцій бази даних..."
    ./scripts/migrate.sh
    
    log_success "✅ Production розгортання завершено!"
}

# Функція перевірки здоров'я сервісів
health_check() {
    log_info "🏥 Перевірка здоров'я сервісів..."
    
    # Перевірка backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✅ Backend працює"
    else
        log_error "❌ Backend не відповідає"
        return 1
    fi
    
    # Перевірка frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "✅ Frontend працює"
    else
        log_error "❌ Frontend не відповідає"
        return 1
    fi
    
    # Перевірка бази даних
    if docker exec upwork-postgres pg_isready > /dev/null 2>&1; then
        log_success "✅ База даних працює"
    else
        log_error "❌ База даних не відповідає"
        return 1
    fi
    
    log_success "🎉 Всі сервіси працюють нормально!"
}

# Функція відкату
rollback() {
    log_warning "🔄 Відкат до попередньої версії..."
    
    # Зупинка поточних контейнерів
    docker-compose down
    
    # Відновлення з backup
    if [ -f "backup-latest.tar.gz" ]; then
        log_info "📦 Відновлення з backup..."
        tar -xzf backup-latest.tar.gz
        log_success "✅ Відкат завершено!"
    else
        log_error "❌ Backup не знайдено!"
        exit 1
    fi
}

# Головна функція
main() {
    log_info "🚀 Початок розгортання Upwork AI Assistant..."
    
    case "${1:-local}" in
        "local")
            deploy_local
            health_check
            ;;
        "dev")
            deploy_dev
            ;;
        "staging")
            deploy_staging
            health_check
            ;;
        "production")
            deploy_production
            health_check
            ;;
        "rollback")
            rollback
            ;;
        "health")
            health_check
            ;;
        *)
            log_error "Невідомий параметр: $1"
            echo "Використання: $0 [local|dev|staging|production|rollback|health]"
            exit 1
            ;;
    esac
    
    log_success "🎉 Розгортання завершено успішно!"
}

# Запуск головної функції
main "$@" 