#!/bin/bash

# Скрипт для управління файлами в папці report
# Обмежує кількість файлів до 10, решту переміщує в _old

REPORT_DIR="docs/newspaper/report"
OLD_DIR="$REPORT_DIR/_old"
MAX_FILES=10

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для логування
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Перевірка існування папок
check_directories() {
    if [ ! -d "$REPORT_DIR" ]; then
        error "Папка $REPORT_DIR не існує!"
        exit 1
    fi
    
    if [ ! -d "$OLD_DIR" ]; then
        log "Створюю папку $OLD_DIR"
        mkdir -p "$OLD_DIR"
    fi
}

# Отримання списку файлів (крім _old)
get_report_files() {
    find "$REPORT_DIR" -maxdepth 1 -type f -name "*.md" | grep -v "_old" | sort
}

# Підрахунок кількості файлів
count_files() {
    get_report_files | wc -l
}

# Переміщення старих файлів в _old
move_old_files() {
    local file_count=$(count_files)
    
    if [ "$file_count" -gt "$MAX_FILES" ]; then
        local files_to_move=$((file_count - MAX_FILES))
        log "Знайдено $file_count файлів, максимум $MAX_FILES. Переміщую $files_to_move файлів в _old"
        
        # Отримуємо список файлів для переміщення (найстаріші)
        local files_to_move_list=$(get_report_files | head -n "$files_to_move")
        
        for file in $files_to_move_list; do
            local filename=$(basename "$file")
            log "Переміщую $filename в _old"
            mv "$file" "$OLD_DIR/"
            success "Файл $filename переміщено в _old"
        done
    else
        log "Кількість файлів ($file_count) не перевищує ліміт ($MAX_FILES)"
    fi
}

# Показ статистики
show_stats() {
    local current_files=$(count_files)
    local old_files=$(find "$OLD_DIR" -type f -name "*.md" | wc -l)
    
    echo
    echo "📊 Статистика папки report:"
    echo "   Поточні файли: $current_files/$MAX_FILES"
    echo "   Файли в _old: $old_files"
    echo
}

# Показ списку файлів
list_files() {
    echo "📁 Поточні файли в report:"
    get_report_files | while read -r file; do
        local filename=$(basename "$file")
        local size=$(du -h "$file" | cut -f1)
        local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "   $filename ($size, $date)"
    done
    
    echo
    echo "📁 Файли в _old:"
    find "$OLD_DIR" -type f -name "*.md" | while read -r file; do
        local filename=$(basename "$file")
        local size=$(du -h "$file" | cut -f1)
        local date=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file")
        echo "   $filename ($size, $date)"
    done
}

# Очищення _old (видалення файлів старіше 30 днів)
cleanup_old() {
    local days=30
    log "Очищення файлів в _old старіше $days днів"
    
    local deleted_count=0
    find "$OLD_DIR" -type f -name "*.md" -mtime +$days | while read -r file; do
        local filename=$(basename "$file")
        log "Видаляю старий файл: $filename"
        rm "$file"
        deleted_count=$((deleted_count + 1))
    done
    
    if [ "$deleted_count" -gt 0 ]; then
        success "Видалено $deleted_count старих файлів"
    else
        log "Старих файлів для видалення не знайдено"
    fi
}

# Головна функція
main() {
    case "${1:-auto}" in
        "auto")
            log "Автоматичне управління файлами в report"
            check_directories
            move_old_files
            show_stats
            ;;
        "stats")
            check_directories
            show_stats
            list_files
            ;;
        "list")
            check_directories
            list_files
            ;;
        "cleanup")
            check_directories
            cleanup_old
            ;;
        "help"|"-h"|"--help")
            echo "Використання: $0 [команда]"
            echo
            echo "Команди:"
            echo "  auto     - Автоматичне управління (за замовчуванням)"
            echo "  stats    - Показати статистику"
            echo "  list     - Показати список файлів"
            echo "  cleanup  - Очистити старі файли в _old"
            echo "  help     - Показати цю довідку"
            echo
            echo "Налаштування:"
            echo "  Максимум файлів в report: $MAX_FILES"
            echo "  Папка report: $REPORT_DIR"
            echo "  Папка _old: $OLD_DIR"
            ;;
        *)
            error "Невідома команда: $1"
            echo "Використайте '$0 help' для довідки"
            exit 1
            ;;
    esac
}

# Запуск скрипта
main "$@" 