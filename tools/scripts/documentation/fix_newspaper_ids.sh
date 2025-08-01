#!/bin/bash

# Скрипт для виправлення дублікатів ID в newspaper
# Використання: ./tools/scripts/fix_newspaper_ids.sh [тип] [--dry-run]
# Приклади: 
#   ./tools/scripts/fix_newspaper_ids.sh report --dry-run
#   ./tools/scripts/fix_newspaper_ids.sh work_results

set -e

echo "🔧 Виправлення дублікатів ID в newspaper..."

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

# Перевірка аргументів
if [ $# -lt 1 ]; then
    error "Використання: $0 [тип] [--dry-run]"
    echo "Типи: report, work_results, steps_plan, all"
    echo "Приклади:"
    echo "  $0 report --dry-run"
    echo "  $0 work_results"
    echo "  $0 all"
    exit 1
fi

TYPE="$1"
DRY_RUN=false

if [ "$2" = "--dry-run" ]; then
    DRY_RUN=true
    warn "Режим тестування (--dry-run) - файли не будуть змінені"
fi

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

# Функція для отримання наступного вільного ID
get_next_free_id() {
    local folder="$1"
    local used_ids="$2"
    local next_id=1
    
    while echo "$used_ids" | grep -q "^$(printf "%04d" $next_id)$"; do
        next_id=$((next_id + 1))
    done
    
    printf "%04d" $next_id
}

# Функція для виправлення дублікатів в папці
fix_duplicates_in_folder() {
    local folder="$1"
    log "Перевірка дублікатів в папці: $folder"
    
    # Знаходження всіх основних файлів (без backup)
    local main_files=""
    local files=$(find "$folder" -name "*.md" -type f -not -name "README.md" | sort)
    
    while IFS= read -r file; do
        if [ -n "$file" ] && ! is_backup_file "$file"; then
            local basename=$(basename "$file")
            if ! is_special_file "$basename"; then
                main_files="$main_files$file"$'\n'
            fi
        fi
    done <<< "$files"
    
    if [ -z "$main_files" ]; then
        info "Немає файлів для перевірки в $folder"
        return
    fi
    
    # Збір всіх ID та знаходження дублікатів
    local id_map=""
    local duplicates=""
    
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            local basename=$(basename "$file")
            local id=$(extract_id "$basename")
            
            if [ -n "$id" ]; then
                if echo "$id_map" | grep -q "^$id:"; then
                    # Це дублікат
                    duplicates="$duplicates$file:$id"$'\n'
                else
                    # Перший раз зустрічаємо цей ID
                    id_map="$id_map$id:$file"$'\n'
                fi
            fi
        fi
    done <<< "$main_files"
    
    if [ -z "$duplicates" ]; then
        log "✅ Дублікатів не знайдено в $folder"
        return
    fi
    
    # Виправлення дублікатів
    warn "Знайдено дублікати в $folder:"
    
    while IFS= read -r duplicate; do
        if [ -n "$duplicate" ]; then
            local file=$(echo "$duplicate" | cut -d: -f1)
            local old_id=$(echo "$duplicate" | cut -d: -f2)
            local basename=$(basename "$file")
            local dirname=$(dirname "$file")
            
            # Отримання назви файлу без ID
            local name_without_id=$(echo "$basename" | sed 's/^[0-9]\{4\}-//')
            
            # Отримання наступного вільного ID
            local used_ids=$(echo "$id_map" | cut -d: -f1 | sort -n)
            local new_id=$(get_next_free_id "$folder" "$used_ids")
            
            # Створення нової назви файлу
            local new_basename="${new_id}-${name_without_id}"
            local new_filepath="$dirname/$new_basename"
            
            warn "  Перейменування: $basename -> $new_basename (ID: $old_id -> $new_id)"
            
            if [ "$DRY_RUN" = false ]; then
                if mv "$file" "$new_filepath"; then
                    log "  ✅ Файл перейменовано: $new_basename"
                    # Оновлюємо id_map з новим ID
                    id_map="$id_map$new_id:$new_filepath"$'\n'
                else
                    error "  ❌ Помилка перейменування: $file"
                fi
            fi
        fi
    done <<< "$duplicates"
}

# Основна функція
main() {
    log "Початок виправлення дублікатів ID в newspaper..."
    
    # Визначення папок для обробки
    local folders=()
    
    case $TYPE in
        "report")
            folders=("docs/newspaper/report")
            ;;
        "work_results")
            folders=("docs/newspaper/report")
            ;;
        "steps_plan")
            folders=("docs/newspaper/report")
            ;;
        "all")
            folders=("docs/newspaper/report" "docs/newspaper/research")
            ;;
        *)
            error "Невідомий тип: $TYPE"
            echo "Доступні типи: report, work_results, steps_plan, all"
            exit 1
            ;;
    esac
    
    # Обробка кожної папки
    for folder in "${folders[@]}"; do
        if [ -d "$folder" ]; then
            echo ""
            fix_duplicates_in_folder "$folder"
        else
            warn "Папка не знайдена: $folder"
        fi
    done
    
    log "Виправлення завершено ✅"
    
    if [ "$DRY_RUN" = true ]; then
        echo ""
        warn "Це був тестовий запуск. Для реального виправлення запустіть без --dry-run"
    fi
    
    echo ""
    log "Рекомендації:"
    echo "  1. Запустіть ./tools/scripts/check_newspaper_ids.sh для перевірки результатів"
    echo "  2. Перевірте, що всі посилання на файли все ще працюють"
    echo "  3. Зробіть backup перед виправленням, якщо потрібно"
}

# Запуск основної функції
main "$@" 