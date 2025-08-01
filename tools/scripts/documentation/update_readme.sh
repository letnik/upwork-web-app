#!/bin/bash

# Скрипт для оновлення README файлів та перевірки посилань
# Використання: ./tools/scripts/update_readme.sh

set -e

echo "🔍 Оновлення README файлів та перевірка посилань..."

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функція для логування
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка наявності необхідних інструментів
check_dependencies() {
    log "Перевірка залежностей..."
    
    if ! command -v find &> /dev/null; then
        error "find не знайдено"
        exit 1
    fi
    
    if ! command -v grep &> /dev/null; then
        error "grep не знайдено"
        exit 1
    fi
    
    log "Всі залежності знайдено ✅"
}

# Знаходження всіх README файлів
find_readme_files() {
    log "Пошук README файлів..."
    
    readme_files=$(find . -name "README.md" -type f -not -path "./app/frontend/node_modules/*" -not -path "./.venv/*" -not -path "./venv/*")
    count=$(echo "$readme_files" | wc -l)
    
    log "Знайдено $count README файлів:"
    echo "$readme_files" | while read -r file; do
        echo "  - $file"
    done
    
    echo "$readme_files"
}

# Перевірка посилань в файлі
check_links() {
    local file="$1"
    log "Перевірка посилань в $file"
    
    # Знаходження всіх посилань формату [текст](шлях)
    links=$(grep -o '\[[^]]*\]([^)]*)' "$file" 2>/dev/null | sed 's/\[[^]]*\]//g' | sed 's/^(\|)$//g' || true)
    
    if [ -n "$links" ]; then
        echo "$links" | while read -r link; do
            if [[ "$link" == http* ]]; then
                # Зовнішні посилання - пропускаємо
                continue
            elif [[ "$link" == \#* ]]; then
                # Якірні посилання - пропускаємо
                continue
            else
                # Внутрішні посилання
                if [ ! -f "$link" ] && [ ! -d "$link" ]; then
                    warn "Посилання не знайдено: $link в файлі $file"
                fi
            fi
        done
    fi
}

# Оновлення дати в README файлах
update_dates() {
    local file="$1"
    local current_date=$(date +"%Y-%m-%d")
    
    # Оновлення дати останнього оновлення
    if grep -q "Дата останнього оновлення:" "$file"; then
        sed -i.bak "s/Дата останнього оновлення:.*/Дата останнього оновлення: $current_date/" "$file"
        log "Оновлено дату в $file"
    fi
    
    # Оновлення дати в заголовку
    if grep -q "ДАТА:" "$file"; then
        sed -i.bak "s/ДАТА:.*/ДАТА: $current_date/" "$file"
        log "Оновлено дату в заголовку $file"
    fi
}

# Основна функція
main() {
    log "Початок оновлення README файлів..."
    
    check_dependencies
    
    # Знаходження всіх README файлів
    readme_files=$(find_readme_files)
    
    # Обробка кожного файлу
    echo "$readme_files" | while read -r file; do
        if [ -n "$file" ]; then
            log "Обробка файлу: $file"
            
            # Перевірка посилань
            check_links "$file"
            
            # Оновлення дат
            update_dates "$file"
            
            # Видалення backup файлів
            if [ -f "${file}.bak" ]; then
                rm "${file}.bak"
            fi
        fi
    done
    
    log "Оновлення завершено ✅"
    
    # Підсумкова статистика
    echo ""
    log "Підсумкова статистика:"
    echo "  - Оброблено README файлів: $(echo "$readme_files" | wc -l)"
    echo "  - Оновлено дат: $(echo "$readme_files" | wc -l)"
    echo ""
    log "Рекомендації:"
    echo "  1. Перевірте всі попередження про посилання"
    echo "  2. Оновіть статуси компонентів (✅ 🚧 ❌)"
    echo "  3. Перевірте актуальність технічної документації"
}

# Запуск основної функції
main "$@" 