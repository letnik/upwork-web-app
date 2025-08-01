#!/bin/bash

# Скрипт для перевірки унікальності ID в newspaper
# Використання: ./tools/scripts/check_newspaper_ids.sh

set -e

echo "🔍 Перевірка унікальності ID в newspaper..."

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
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
    
    if ! command -v sort &> /dev/null; then
        error "sort не знайдено"
        exit 1
    fi
    
    if ! command -v uniq &> /dev/null; then
        error "uniq не знайдено"
        exit 1
    fi
    
    log "Всі залежності знайдено ✅"
}

# Функція для витягування ID з назви файлу
extract_id() {
    local filename="$1"
    echo "$filename" | grep -o '^[0-9]\{4\}' || echo ""
}

# Функція для перевірки чи файл є спеціальним
is_special_file() {
    local filename="$1"
    case "$filename" in
        "README.md"|"_sandbox.md"|"UPWORK_DEVELOPER_SETUP.md")
            return 0  # true - це спеціальний файл
            ;;
        *)
            return 1  # false - це звичайний файл
            ;;
    esac
}

# Функція для перевірки чи файл знаходиться в backup папці
is_backup_file() {
    local filepath="$1"
    if [[ "$filepath" == *"/backup"* ]] || [[ "$filepath" == *"/backup_old"* ]]; then
        return 0  # true - це backup файл
    else
        return 1  # false - це основний файл
    fi
}

# Знаходження всіх файлів в newspaper
find_newspaper_files() {
    log "Пошук файлів в newspaper..."
    
    newspaper_files=$(find docs/newspaper -name "*.md" -type f -not -name "README.md")
    count=$(echo "$newspaper_files" | wc -l)
    
    log "Знайдено $count файлів в newspaper"
    echo "$newspaper_files"
}

# Перевірка унікальності ID в папці
check_folder_ids() {
    local folder="$1"
    log "Перевірка ID в папці: $folder"
    
    # Знаходження всіх файлів в папці
    local files=$(find "$folder" -name "*.md" -type f -not -name "README.md" | sort)
    
    if [ -z "$files" ]; then
        info "Папка $folder порожня або не містить .md файлів"
        return
    fi
    
    # Розділення файлів на основні та backup
    local main_files=""
    local backup_files=""
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            if is_backup_file "$file"; then
                backup_files="$backup_files$file"$'\n'
            else
                main_files="$main_files$file"$'\n'
            fi
        fi
    done <<< "$files"
    
    # Перевірка основних файлів
    local main_ids=""
    local main_duplicates=""
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            local basename=$(basename "$file")
            if ! is_special_file "$basename"; then
                local id=$(extract_id "$basename")
                if [ -n "$id" ]; then
                    if echo "$main_ids" | grep -q "$id"; then
                        main_duplicates="$main_duplicates$id"$'\n'
                    else
                        main_ids="$main_ids$id"$'\n'
                    fi
                fi
            fi
        fi
    done <<< "$main_files"
    
    # Перевірка backup файлів
    local backup_ids=""
    local backup_duplicates=""
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            local basename=$(basename "$file")
            local id=$(extract_id "$basename")
            if [ -n "$id" ]; then
                if echo "$backup_ids" | grep -q "$id"; then
                    backup_duplicates="$backup_duplicates$id"$'\n'
                else
                    backup_ids="$backup_ids$id"$'\n'
                fi
            fi
        fi
    done <<< "$backup_files"
    
    # Виведення результатів
    if [ -n "$main_duplicates" ]; then
        error "Знайдено дублікати ID в основних файлах папки $folder:"
        echo "$main_duplicates" | sort | uniq | while read -r id; do
            if [ -n "$id" ]; then
                echo "  - ID $id використовується кілька разів в основних файлах"
            fi
        done
    else
        log "✅ Всі ID унікальні в основних файлах папки $folder"
    fi
    
    if [ -n "$backup_duplicates" ]; then
        warn "Знайдено дублікати ID в backup файлах папки $folder:"
        echo "$backup_duplicates" | sort | uniq | while read -r id; do
            if [ -n "$id" ]; then
                echo "  - ID $id використовується кілька разів в backup файлах"
            fi
        done
    fi
    
    # Показати статистику
    local main_count=$(echo "$main_files" | wc -l)
    local backup_count=$(echo "$backup_files" | wc -l)
    
    info "Статистика папки $folder:"
    echo "  - Основних файлів: $main_count"
    echo "  - Backup файлів: $backup_count"
    
    # Показати ID основних файлів
    if [ -n "$main_ids" ]; then
        info "ID основних файлів в $folder:"
        echo "$main_ids" | sort -n | while read -r id; do
            if [ -n "$id" ]; then
                echo "  - $id"
            fi
        done
    fi
}

# Перевірка формату ID
check_id_format() {
    local folder="$1"
    log "Перевірка формату ID в папці: $folder"
    
    local files=$(find "$folder" -name "*.md" -type f -not -name "README.md")
    local format_errors=0
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            local basename=$(basename "$file")
            
            # Пропускаємо спеціальні файли
            if is_special_file "$basename"; then
                continue
            fi
            
            local id=$(extract_id "$basename")
            
            if [ -n "$id" ]; then
                # Перевірка формату (4 цифри)
                if ! echo "$id" | grep -qE '^[0-9]{4}$'; then
                    warn "Неправильний формат ID в файлі $file: $id"
                    format_errors=$((format_errors + 1))
                fi
            else
                warn "Файл без ID: $file"
                format_errors=$((format_errors + 1))
            fi
        fi
    done <<< "$files"
    
    if [ $format_errors -eq 0 ]; then
        log "✅ Всі ID мають правильний формат в папці $folder"
    fi
}

# Знаходження наступного доступного ID (тільки в основних файлах)
find_next_available_id() {
    local folder="$1"
    
    local files=$(find "$folder" -name "*.md" -type f -not -name "README.md")
    local max_id=0
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            # Пропускаємо backup файли та спеціальні файли
            if is_backup_file "$file"; then
                continue
            fi
            
            local basename=$(basename "$file")
            if is_special_file "$basename"; then
                continue
            fi
            
            local id=$(extract_id "$basename")
            
            if [ -n "$id" ]; then
                # Конвертуємо ID в число для порівняння
                local id_num=$((10#$id))
                if [ "$id_num" -gt "$max_id" ]; then
                    max_id=$id_num
                fi
            fi
        fi
    done <<< "$files"
    
    local next_id=$((max_id + 1))
    printf "%04d" $next_id
}

# Основна функція
main() {
    log "Початок перевірки унікальності ID в newspaper..."
    
    check_dependencies
    
    # Знаходження всіх файлів
    newspaper_files=$(find_newspaper_files)
    
    # Перевірка кожної папки
    local folders=("docs/newspaper/report" "docs/newspaper/research")
    
    for folder in "${folders[@]}"; do
        if [ -d "$folder" ]; then
            echo ""
            check_folder_ids "$folder"
            check_id_format "$folder"
            
            # Знайти наступний доступний ID
            next_id=$(find_next_available_id "$folder")
            info "Наступний доступний ID в $folder: $next_id"
        else
            warn "Папка не знайдена: $folder"
        fi
    done
    
    log "Перевірка завершена ✅"
    
    # Підсумкова статистика
    echo ""
    log "Підсумкова статистика:"
    echo "  - Перевірено папок: ${#folders[@]}"
    echo "  - Знайдено файлів: $(echo "$newspaper_files" | wc -l)"
    echo ""
    log "Рекомендації:"
    echo "  1. Використовуйте унікальні ID в кожній папці"
    echo "  2. Дотримуйтеся формату 4-значного номера (0001, 0002, ...)"
    echo "  3. Перевіряйте ID перед створенням нового файлу"
    echo "  4. Використовуйте наступний доступний ID"
    echo "  5. Backup файли не впливають на генерацію нових ID"
}

# Запуск основної функції
main "$@" 