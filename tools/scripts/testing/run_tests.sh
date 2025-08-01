#!/bin/bash

# 🧪 Універсальний скрипт тестування для Upwork AI Assistant
# Підтримує: unit, integration, e2e, performance, security тести

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функції для виводу
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Додаткові функції для покращеного тестування
print_coverage() {
    echo -e "${GREEN}📊 $1${NC}"
}

print_performance() {
    echo -e "${YELLOW}⚡ $1${NC}"
}

print_security() {
    echo -e "${RED}🔒 $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🎯 $1${NC}"
}

print_step() {
    echo -e "${CYAN}🔧 $1${NC}"
}

# Функція допомоги
show_help() {
    echo "🧪 Універсальний скрипт тестування"
    echo ""
    echo "Використання:"
    echo "  $0 [тип_тестів] [опції]"
    echo ""
    echo "Типи тестів:"
    echo "  all          - Всі тести (за замовчуванням)"
    echo "  unit         - Unit тести (backend + frontend)"
    echo "  backend      - Backend unit тести"
    echo "  frontend     - Frontend unit тести"
    echo "  integration  - Integration тести"
    echo "  e2e          - End-to-End тести"
    echo "  performance  - Performance тести"
    echo "  security     - Security тести"
    echo "  coverage     - Тести з покриттям"
    echo ""
    echo "Опції:"
    echo "  --watch      - Watch режим (тільки для unit тестів)"
    echo "  --debug      - Debug режим"
    echo "  --verbose    - Детальний вивід"
    echo "  --parallel   - Паралельне виконання"
    echo ""
    echo "Приклади:"
    echo "  $0                    # Всі тести"
    echo "  $0 backend            # Backend unit тести"
    echo "  $0 frontend --watch   # Frontend тести в watch режимі"
    echo "  $0 integration --verbose # Integration тести з детальним виводом"
}

# Функція перевірки залежностей
check_dependencies() {
    print_info "Перевірка залежностей..."
    
    # Перевіряємо Python
    if ! command -v python3.11 &> /dev/null; then
        print_error "Python 3.11 не знайдено"
        exit 1
    fi
    
    # Перевіряємо Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js не знайдено"
        exit 1
    fi
    
    # Перевіряємо npm
    if ! command -v npm &> /dev/null; then
        print_error "npm не знайдено"
        exit 1
    fi
    
    print_success "Всі залежності знайдено"
}

# Функція налаштування середовища
setup_environment() {
    print_info "Налаштування тестового середовища..."
    
    # Перевіряємо чи існує віртуальне середовище
    if [ -d "app/backend/venv" ]; then
        print_info "Активація віртуального середовища..."
        source app/backend/venv/bin/activate
    else
        print_warning "Віртуальне середовище не знайдено в app/backend/venv"
        print_info "Створюємо нове віртуальне середовище..."
        cd app/backend
        python3.11 -m venv venv
        source venv/bin/activate
        pip install -r requirements/dev.txt
        cd ../..
    fi
    
    # Встановлюємо frontend залежності
    if [ ! -d "app/frontend/node_modules" ]; then
        print_info "Встановлення frontend залежностей..."
        cd app/frontend
        npm install
        cd ../..
    fi
    
    print_success "Середовище налаштовано"
}

# Функція запуску backend тестів
run_backend_tests() {
    local options="$1"
    print_info "Запуск Backend тестів..."
    
    cd tests/unit/backend
    
    # Перевіряємо чи встановлений pytest
    if ! python -c "import pytest" &> /dev/null; then
        print_warning "pytest не знайдено. Встановлюємо..."
        pip install pytest pytest-asyncio pytest-cov
    fi
    
    # Запускаємо тести
    if [ "$options" = "coverage" ]; then
        print_info "Запуск pytest з покриттям..."
        python -m pytest -v --cov=. --cov-report=html --cov-report=term
        print_success "Backend тести з покриттям завершено!"
    else
        print_info "Запуск pytest..."
        python -m pytest -v
        print_success "Backend тести завершено!"
    fi
    
    cd ../../..
}

# Функція запуску frontend тестів
run_frontend_tests() {
    local options="$1"
    print_info "Запуск Frontend тестів..."
    
    cd app/frontend
    
    if [ "$options" = "watch" ]; then
        print_info "Запуск тестів в watch режимі..."
        npm test -- --watch
    elif [ "$options" = "coverage" ]; then
        print_info "Запуск тестів з покриттям..."
        npm test -- --coverage
    else
        print_info "Запуск тестів..."
        npm test
    fi
    
    print_success "Frontend тести завершено!"
    cd ../..
}

# Функція запуску integration тестів
run_integration_tests() {
    local options="$1"
    print_info "Запуск Integration тестів..."
    
    if [ ! -d "tests/integration" ] || [ -z "$(ls -A tests/integration)" ]; then
        print_warning "Integration тести ще не реалізовані"
        print_info "Дивіться tests/integration/README.md для планів"
        return 0
    fi
    
    cd tests/integration
    
    if [ "$options" = "verbose" ]; then
        python -m pytest -v --tb=long
    else
        python -m pytest -v
    fi
    
    print_success "Integration тести завершено!"
    cd ../..
}

# Функція запуску E2E тестів
run_e2e_tests() {
    local options="$1"
    print_info "Запуск E2E тестів..."
    
    if [ ! -d "tests/e2e" ] || [ -z "$(ls -A tests/e2e)" ]; then
        print_warning "E2E тести ще не реалізовані"
        print_info "Дивіться tests/e2e/README.md для планів"
        return 0
    fi
    
    cd tests/e2e
    
    # Перевіряємо чи встановлений Playwright
    if ! python -c "import playwright" &> /dev/null; then
        print_warning "Playwright не знайдено. Встановлюємо..."
        pip install playwright
        playwright install
    fi
    
    if [ "$options" = "verbose" ]; then
        python -m pytest -v --tb=long
    else
        python -m pytest -v
    fi
    
    print_success "E2E тести завершено!"
    cd ../..
}

# Функція запуску performance тестів
run_performance_tests() {
    local options="$1"
    print_info "Запуск Performance тестів..."
    
    if [ ! -d "tests/performance" ] || [ -z "$(ls -A tests/performance)" ]; then
        print_warning "Performance тести ще не реалізовані"
        print_info "Дивіться tests/performance/README.md для планів"
        return 0
    fi
    
    cd tests/performance
    
    # Перевіряємо чи встановлений Locust
    if ! python -c "import locust" &> /dev/null; then
        print_warning "Locust не знайдено. Встановлюємо..."
        pip install locust
    fi
    
    if [ "$options" = "verbose" ]; then
        python -m pytest -v --tb=long
    else
        python -m pytest -v
    fi
    
    print_success "Performance тести завершено!"
    cd ../..
}

# Функція запуску security тестів
run_security_tests() {
    local options="$1"
    print_info "Запуск Security тестів..."
    
    if [ ! -d "tests/security" ] || [ -z "$(ls -A tests/security)" ]; then
        print_warning "Security тести ще не реалізовані"
        print_info "Дивіться tests/security/README.md для планів"
        return 0
    fi
    
    cd tests/security
    
    if [ "$options" = "verbose" ]; then
        python -m pytest -v --tb=long
    else
        python -m pytest -v
    fi
    
    print_success "Security тести завершено!"
    cd ../..
}

# Функція генерації звіту
generate_report() {
    local test_type="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    print_info "Генерація звіту про тестування..."
    
    # Створюємо звіт
    cat > "test-results/report_${test_type}_$(date +%Y%m%d_%H%M%S).md" << EOF
# 📊 Звіт про тестування: ${test_type}

**Дата**: ${timestamp}  
**Тип тестів**: ${test_type}  
**Статус**: ✅ Завершено

## 📈 Результати

- **Тип тестів**: ${test_type}
- **Час виконання**: $(date +%H:%M:%S)
- **Статус**: Успішно

## 🔧 Технічні деталі

- **Python версія**: $(python --version)
- **Node.js версія**: $(node --version)
- **npm версія**: $(npm --version)

## 📋 Наступні кроки

1. Переглянути результати тестів
2. Виправити помилки (якщо є)
3. Оновити документацію
4. Запустити CI/CD pipeline

---
**Згенеровано автоматично**: ${timestamp}
EOF
    
    print_success "Звіт згенеровано в test-results/"
}

# Головна функція
main() {
    local test_type="${1:-all}"
    local options="${2:-}"
    
    echo "========================================"
    echo "🧪 Запуск тестування: ${test_type}"
    echo "========================================"
    
    # Показуємо допомогу
    if [ "$test_type" = "help" ] || [ "$test_type" = "-h" ] || [ "$test_type" = "--help" ]; then
        show_help
        exit 0
    fi
    
    # Створюємо директорію для результатів
    mkdir -p test-results
    
    # Перевіряємо залежності
    check_dependencies
    
    # Налаштовуємо середовище
    setup_environment
    
    # Запускаємо тести залежно від типу
    case $test_type in
        "all")
            run_backend_tests "$options"
            run_frontend_tests "$options"
            run_integration_tests "$options"
            run_e2e_tests "$options"
            run_performance_tests "$options"
            run_security_tests "$options"
            ;;
        "unit")
            run_backend_tests "$options"
            run_frontend_tests "$options"
            ;;
        "backend")
            run_backend_tests "$options"
            ;;
        "frontend")
            run_frontend_tests "$options"
            ;;
        "integration")
            run_integration_tests "$options"
            ;;
        "e2e")
            run_e2e_tests "$options"
            ;;
        "performance")
            run_performance_tests "$options"
            ;;
        "security")
            run_security_tests "$options"
            ;;
        "coverage")
            run_backend_tests "coverage"
            run_frontend_tests "coverage"
            ;;
        *)
            print_error "Невідомий тип тестів: $test_type"
            show_help
            exit 1
            ;;
    esac
    
    # Генеруємо звіт
    generate_report "$test_type"
    
    echo "========================================"
    print_success "Тестування завершено успішно!"
    echo "========================================"
}

# Запускаємо головну функцію
main "$@" 