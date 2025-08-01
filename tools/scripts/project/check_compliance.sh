#!/bin/bash

# Скрипт перевірки відповідності інструкціям
# Використання: ./tools/scripts/project/check_compliance.sh

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Функції для виводу
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Змінні
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TOTAL_ISSUES=0

echo "🔍 Перевірка відповідності інструкціям..."
echo "📁 Проект: $PROJECT_ROOT"
echo ""

# Функція перевірки структури проекту
check_structure() {
    log "📋 Перевірка структури проекту..."
    
    if [ -f "$PROJECT_ROOT/tools/scripts/project/validate_structure.sh" ]; then
        cd "$PROJECT_ROOT"
        if ./tools/scripts/project/validate_structure.sh; then
            success "✅ Структура проекту - OK"
        else
            error "❌ Структура проекту потребує виправлення"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    else
        error "❌ Скрипт validate_structure.sh не знайдено"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки ID в newspaper
check_newspaper_ids() {
    log "📰 Перевірка ID в newspaper..."
    
    if [ -f "$PROJECT_ROOT/tools/scripts/documentation/check_newspaper_ids.sh" ]; then
        cd "$PROJECT_ROOT"
        if ./tools/scripts/documentation/check_newspaper_ids.sh; then
            success "✅ ID в newspaper - OK"
        else
            error "❌ Проблеми з ID в newspaper"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    else
        error "❌ Скрипт check_newspaper_ids.sh не знайдено"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки тестів
check_tests() {
    log "🧪 Перевірка тестів..."
    
    if [ -f "$PROJECT_ROOT/tools/scripts/testing/run_tests.sh" ]; then
        cd "$PROJECT_ROOT"
        if ./tools/scripts/testing/run_tests.sh; then
            success "✅ Тести - OK"
        else
            warn "⚠️ Тести потребують уваги"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    else
        warn "⚠️ Скрипт run_tests.sh не знайдено"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки версії
check_version() {
    log "📦 Перевірка версії проекту..."
    
    if [ -f "$PROJECT_ROOT/VERSION" ]; then
        VERSION=$(cat "$PROJECT_ROOT/VERSION")
        info "📋 Поточна версія: $VERSION"
        success "✅ Файл VERSION існує"
    else
        error "❌ Файл VERSION не знайдено"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки .gitignore
check_gitignore() {
    log "🔒 Перевірка .gitignore..."
    
    if [ -f "$PROJECT_ROOT/.gitignore" ]; then
        # Перевірка критичних правил
        if grep -q "logs/" "$PROJECT_ROOT/.gitignore" && \
           grep -q "exports/" "$PROJECT_ROOT/.gitignore" && \
           grep -q "sessions/" "$PROJECT_ROOT/.gitignore" && \
           grep -q "\*.log" "$PROJECT_ROOT/.gitignore"; then
            success "✅ .gitignore містить всі критичні правила"
        else
            error "❌ .gitignore не містить всіх критичних правил"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    else
        error "❌ Файл .gitignore не знайдено"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки залежностей
check_dependencies() {
    log "📦 Перевірка залежностей..."
    
    if [ -d "$PROJECT_ROOT/requirements" ]; then
        success "✅ Папка requirements існує"
        
        # Перевірка базових файлів
        if [ -f "$PROJECT_ROOT/requirements/base.txt" ]; then
            success "✅ requirements/base.txt існує"
        else
            error "❌ requirements/base.txt не знайдено"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
        
        # Перевірка сервісних файлів
        SERVICES=("api-gateway" "auth-service" "ai-service" "analytics-service" "notification-service" "upwork-service")
        for service in "${SERVICES[@]}"; do
            if [ -f "$PROJECT_ROOT/requirements/$service.txt" ]; then
                success "✅ requirements/$service.txt існує"
            else
                warn "⚠️ requirements/$service.txt не знайдено"
            fi
        done
    else
        error "❌ Папка requirements не знайдена"
        TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    fi
    echo ""
}

# Функція перевірки документації
check_documentation() {
    log "📚 Перевірка документації..."
    
    # Перевірка критичних файлів інструкцій
    CRITICAL_FILES=(
        "docs/instruction_ai/AI_ASSISTANT_INSTRUCTIONS.md"
        "docs/instruction_ai/NEWSPAPER_ID_MANAGEMENT_INSTRUCTIONS.md"
        "docs/instruction_ai/COMPLIANCE_RULES.md"
        "docs/instruction_ai/WORKFLOW_INSTRUCTIONS.md"
    )
    
    for file in "${CRITICAL_FILES[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            success "✅ $file існує"
        else
            error "❌ $file не знайдено"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    done
    echo ""
}

# Функція перевірки скриптів
check_scripts() {
    log "🔧 Перевірка скриптів..."
    
    # Перевірка критичних скриптів
    CRITICAL_SCRIPTS=(
        "tools/scripts/project/validate_structure.sh"
        "tools/scripts/documentation/check_newspaper_ids.sh"
        "tools/scripts/documentation/create_newspaper_file.sh"
        "tools/scripts/documentation/get_next_newspaper_id.sh"
        "tools/scripts/dependencies/install.sh"
    )
    
    for script in "${CRITICAL_SCRIPTS[@]}"; do
        if [ -f "$PROJECT_ROOT/$script" ]; then
            if [ -x "$PROJECT_ROOT/$script" ]; then
                success "✅ $script існує та виконуваний"
            else
                warn "⚠️ $script існує, але не виконуваний"
                TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
            fi
        else
            error "❌ $script не знайдено"
            TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
    done
    echo ""
}

# Головна функція
main() {
    echo "🚀 Початок перевірки відповідності інструкціям..."
    echo "=================================================="
    echo ""
    
    # Виконання всіх перевірок
    check_structure
    check_newspaper_ids
    check_tests
    check_version
    check_gitignore
    check_dependencies
    check_documentation
    check_scripts
    
    # Підсумок
    echo "=================================================="
    echo "📊 ПІДСУМОК ПЕРЕВІРКИ:"
    echo ""
    
    if [ "$TOTAL_ISSUES" -eq 0 ]; then
        success "🎉 Всі перевірки пройшли успішно!"
        success "✅ Проект повністю відповідає інструкціям"
        exit 0
    else
        error "❌ Знайдено $TOTAL_ISSUES проблем"
        warn "⚠️ Проект потребує виправлення перед продовженням"
        echo ""
        echo "🔧 Рекомендації:"
        echo "1. Виправити всі виявлені проблеми"
        echo "2. Запустити перевірку ще раз"
        echo "3. Документувати зміни"
        exit 1
    fi
}

# Запуск головної функції
main "$@" 