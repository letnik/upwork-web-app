#!/bin/bash

# Скрипт для отримання наступного доступного ID в newspaper
# Використання: ./tools/scripts/get_next_newspaper_id.sh [тип]
# Приклади: 
#   ./tools/scripts/get_next_newspaper_id.sh report
#   ./tools/scripts/get_next_newspaper_id.sh work_results

set -e

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

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Перевірка аргументів
if [ $# -lt 1 ]; then
    error "Використання: $0 [тип]"
    echo "Типи: report, work_results, steps_plan, update, security_documentation_backup"
    echo "Приклади:"
    echo "  $0 report"
    echo "  $0 work_results"
    echo "  $0 steps_plan"
    exit 1
fi

TYPE="$1"

# Визначення папки
case $TYPE in
    "report")
        FOLDER="docs/newspaper/report"
        ;;
    "work_results")
        FOLDER="docs/newspaper/report"
        ;;
    "steps_plan")
        FOLDER="docs/newspaper/report"
        ;;
    "update")
        FOLDER="docs/newspaper/report"
        ;;
    "research")
        FOLDER="docs/newspaper/research"
        ;;
    "security_documentation_backup")
        FOLDER="docs/newspaper/security_documentation_backup"
        ;;
    *)
        error "Невідомий тип: $TYPE"
        echo "Доступні типи: report, work_results, steps_plan, update, security_documentation_backup"
        exit 1
        ;;
esac

# Перевірка існування папки
if [ ! -d "$FOLDER" ]; then
    error "Папка не існує: $FOLDER"
    exit 1
fi

# Функція для витягування ID з назви файлу
extract_id() {
    local filename="$1"
    echo "$filename" | grep -o '^[0-9]\{4\}' || echo "0000"
}

# Функція для перевірки чи файл є спеціальним (README, _sandbox, тощо)
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

# Знаходження максимального ID в папці (тільки в основній папці, без backup)
MAX_ID=0
FOUND_FILES=false

# Шукаємо тільки в основній папці, ігноруючи backup папки
for file in "$FOLDER"/*.md; do
    if [ -f "$file" ]; then
        BASENAME=$(basename "$file")
        
        # Пропускаємо спеціальні файли
        if is_special_file "$BASENAME"; then
            continue
        fi
        
        # Пропускаємо файли в backup папках
        if [[ "$file" == *"/backup"* ]] || [[ "$file" == *"/backup_old"* ]]; then
            continue
        fi
        
        ID=$(extract_id "$BASENAME")
        if [ "$ID" != "0000" ]; then
            # Конвертуємо ID в число для порівняння
            ID_NUM=$((10#$ID))
            if [ "$ID_NUM" -gt "$MAX_ID" ]; then
                MAX_ID=$ID_NUM
            fi
            FOUND_FILES=true
        fi
    fi
done

# Додаткова перевірка на дублікати в основній папці
DUPLICATE_IDS=""
for file in "$FOLDER"/*.md; do
    if [ -f "$file" ]; then
        BASENAME=$(basename "$file")
        
        # Пропускаємо спеціальні файли та backup папки
        if is_special_file "$BASENAME" || [[ "$file" == *"/backup"* ]] || [[ "$file" == *"/backup_old"* ]]; then
            continue
        fi
        
        ID=$(extract_id "$BASENAME")
        if [ "$ID" != "0000" ]; then
            # Перевіряємо чи цей ID вже зустрічався
            if echo "$DUPLICATE_IDS" | grep -q "$ID"; then
                warn "Знайдено дублікат ID $ID в файлі $BASENAME"
            else
                DUPLICATE_IDS="$DUPLICATE_IDS $ID"
            fi
        fi
    fi
done

if [ "$FOUND_FILES" = false ]; then
    NEXT_ID="0001"
else
    NEXT_ID=$((MAX_ID + 1))
    NEXT_ID=$(printf "%04d" $NEXT_ID)
fi

# Додаткова перевірка: якщо наступний ID вже існує, знаходимо наступний вільний
while ls "$FOLDER"/${NEXT_ID}_*.md >/dev/null 2>&1 || ls "$FOLDER"/${NEXT_ID}-*.md >/dev/null 2>&1; do
    warn "ID $NEXT_ID вже використовується, шукаємо наступний..."
    NEXT_ID_NUM=$((10#$NEXT_ID))
    NEXT_ID_NUM=$((NEXT_ID_NUM + 1))
    NEXT_ID=$(printf "%04d" $NEXT_ID_NUM)
done

echo "$NEXT_ID" 