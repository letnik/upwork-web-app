#!/bin/bash

# 🚀 Скрипт збірки Upwork AI Assistant
# Використання: ./scripts/build.sh [frontend|backend|all]

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
    log_error "Папка dist не існує. Створюю..."
    mkdir -p dist/{frontend,backend,docker,configs,scripts}
fi

# Функція збірки frontend
build_frontend() {
    log_info "🔨 Збірка frontend..."
    
    if [ ! -d "app/frontend" ]; then
        log_error "Папка app/frontend не існує!"
        return 1
    fi
    
    cd app/frontend
    
    # Перевірка чи встановлені залежності
    if [ ! -d "node_modules" ]; then
        log_info "📦 Встановлення залежностей..."
        npm install
    fi
    
    # Збірка проекту
    log_info "🏗️ Збірка React додатку..."
    npm run build
    
    # Копіювання зібраних файлів
    log_info "📁 Копіювання зібраних файлів..."
    rm -rf ../dist/frontend/*
    cp -r build/* ../dist/frontend/
    
    cd ..
    log_success "✅ Frontend зібрано успішно!"
}

# Функція збірки backend
build_backend() {
    log_info "🔨 Збірка backend..."
    
    if [ ! -d "app/backend" ]; then
        log_error "Папка app/backend не існує!"
        return 1
    fi
    
    cd app/backend
    
    # Створення архіву
    log_info "📦 Створення архіву backend..."
    tar -czf ../dist/backend/upwork-backend.tar.gz \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='tests' \
        --exclude='.git' \
        .
    
    # Копіювання конфігурацій
    log_info "📁 Копіювання конфігурацій..."
    cp requirements.txt ../dist/backend/
    
    if [ -d "config" ]; then
        cp -r config ../dist/backend/
    fi
    
    cd ..
    log_success "✅ Backend зібрано успішно!"
}

# Функція збірки Docker образів
build_docker() {
    log_info "🐳 Збірка Docker образів..."
    
    # Збірка frontend контейнера
    if [ -d "app/frontend" ]; then
        log_info "🏗️ Збірка frontend контейнера..."
        docker build -t upwork-frontend:latest app/frontend/
        docker save upwork-frontend:latest > dist/docker/frontend.tar
        log_success "✅ Frontend контейнер зібрано!"
    fi
    
    # Збірка backend контейнера
    if [ -d "app/backend" ]; then
        log_info "🏗️ Збірка backend контейнера..."
        docker build -t upwork-backend:latest app/backend/
        docker save upwork-backend:latest > dist/docker/backend.tar
        log_success "✅ Backend контейнер зібрано!"
    fi
    
    # Збірка nginx контейнера (якщо існує)
    if [ -d "nginx" ]; then
        log_info "🏗️ Збірка nginx контейнера..."
        docker build -t upwork-nginx:latest nginx/
        docker save upwork-nginx:latest > dist/docker/nginx.tar
        log_success "✅ Nginx контейнер зібрано!"
    fi
}

# Функція копіювання конфігурацій
copy_configs() {
    log_info "📋 Копіювання конфігурацій..."
    
    # Копіювання docker-compose
    if [ -f "docker/docker-compose.yml" ]; then
        cp docker/docker-compose.yml dist/docker/docker-compose.prod.yml
    fi
    
    # Копіювання nginx конфігурації (якщо існує)
    if [ -d "nginx" ]; then
        cp nginx/nginx.conf dist/configs/ 2>/dev/null || true
    fi
    
    # Створення прикладу .env.production
    if [ ! -f "dist/configs/.env.production" ]; then
        cat > dist/configs/.env.production << EOF
# Production змінні середовища
DATABASE_URL=postgresql://user:password@localhost:5432/upwork_app
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-production-secret-key
JWT_SECRET=your-production-jwt-secret
DEBUG=False
ENVIRONMENT=production
EOF
        log_warning "⚠️ Створено приклад .env.production. Відредагуйте змінні!"
    fi
    
    log_success "✅ Конфігурації скопійовано!"
}

# Функція копіювання скриптів
copy_scripts() {
    log_info "📜 Копіювання скриптів..."
    
    # Копіювання скриптів розгортання
    if [ -f "scripts/deploy.sh" ]; then
        cp scripts/deploy.sh dist/scripts/
    fi
    
    if [ -f "scripts/backup.sh" ]; then
        cp scripts/backup.sh dist/scripts/
    fi
    
    # Створення скрипту міграцій
    cat > dist/scripts/migrate.sh << 'EOF'
#!/bin/bash
# Скрипт для запуску міграцій бази даних

echo "🔄 Запуск міграцій бази даних..."

# Перевірка чи запущений backend контейнер
if docker ps | grep -q upwork-backend; then
    echo "📦 Запуск міграцій через Docker..."
    docker exec upwork-backend alembic upgrade head
else
    echo "⚠️ Backend контейнер не запущений. Запустіть спочатку docker-compose up -d"
fi

echo "✅ Міграції завершено!"
EOF
    
    chmod +x dist/scripts/migrate.sh
    log_success "✅ Скрипти скопійовано!"
}

# Головна функція
main() {
    log_info "🚀 Початок збірки Upwork AI Assistant..."
    
    case "${1:-all}" in
        "frontend")
            build_frontend
            ;;
        "backend")
            build_backend
            ;;
        "docker")
            build_docker
            ;;
        "all")
            build_frontend
            build_backend
            build_docker
            copy_configs
            copy_scripts
            ;;
        *)
            log_error "Невідомий параметр: $1"
            echo "Використання: $0 [frontend|backend|docker|all]"
            exit 1
            ;;
    esac
    
    log_success "🎉 Збірка завершена успішно!"
    log_info "📁 Зібраний проект знаходиться в папці: dist/"
}

# Запуск головної функції
main "$@" 