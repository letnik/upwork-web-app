#!/bin/bash

# 🔗 Скрипт для перевірки посилань в README файлах
# Використання: ./tools/scripts/check_links.sh

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для виводу заголовків
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🔗 $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Функція для виводу успіху
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функція для виводу попередження
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Функція для виводу помилки
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функція для перевірки файлу
check_file() {
    local file="$1"
    local file_dir=$(dirname "$file")
    local broken_links=0
    local total_links=0
    
    print_header "Перевірка файлу: $file"
    
    # Знаходимо всі посилання в файлі
    while IFS= read -r line; do
        # Шукаємо посилання формату [текст](шлях)
        if [[ $line =~ \[([^\]]+)\]\(([^)]+)\) ]]; then
            local link_text="${BASH_REMATCH[1]}"
            local link_path="${BASH_REMATCH[2]}"
            ((total_links++))
            
            # Обробляємо різні типи посилань
            if [[ $link_path == http* ]]; then
                # Зовнішні посилання - пропускаємо
                print_warning "Зовнішнє посилання: $link_text -> $link_path"
            elif [[ $link_path == \#* ]]; then
                # Якорі - перевіряємо чи існує в файлі
                local anchor="${link_path#\#}"
                if ! grep -q "^##.*$anchor" "$file" && ! grep -q "^###.*$anchor" "$file"; then
                    print_error "Не знайдено якір: $anchor в $file"
                    ((broken_links++))
                else
                    print_success "Якір знайдено: $anchor"
                fi
            else
                # Внутрішні файли
                local full_path=""
                if [[ $link_path == /* ]]; then
                    # Абсолютний шлях від кореня проекту
                    full_path=".$link_path"
                else
                    # Відносний шлях
                    full_path="$file_dir/$link_path"
                fi
                
                # Перевіряємо чи існує файл
                if [[ -f "$full_path" ]]; then
                    print_success "Файл існує: $link_text -> $full_path"
                else
                    print_error "Файл не знайдено: $link_text -> $full_path"
                    ((broken_links++))
                fi
            fi
        fi
    done < "$file"
    
    echo ""
    if [ $broken_links -eq 0 ]; then
        print_success "Всі посилання працюють! ($total_links посилань)"
    else
        print_error "Знайдено $broken_links зламаних посилань з $total_links"
    fi
    
    return $broken_links
}

# Головна функція
main() {
    print_header "Перевірка посилань в README файлах"
    
    local total_broken=0
    local total_files=0
    
    # Знаходимо всі README файли
    while IFS= read -r file; do
        if [[ -f "$file" ]]; then
            ((total_files++))
            check_file "$file"
            if [ $? -gt 0 ]; then
                ((total_broken++))
            fi
            echo ""
        fi
    done < <(find . -name "README.md" -type f | grep -v node_modules | sort)
    
    echo ""
    print_header "Підсумок перевірки"
    echo "Перевірено файлів: $total_files"
    echo "Файлів з помилками: $total_broken"
    
    if [ $total_broken -eq 0 ]; then
        print_success "🎉 Всі посилання працюють!"
        exit 0
    else
        print_error "❌ Знайдено файли з зламаними посиланнями"
        exit 1
    fi
}

# Запуск головної функції
main "$@" 