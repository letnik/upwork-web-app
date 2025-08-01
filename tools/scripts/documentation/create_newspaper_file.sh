#!/bin/bash

# Скрипт для автоматичного створення файлів в newspaper
# Використання: ./tools/scripts/create_newspaper_file.sh [тип] [назва]
# Приклади: 
#   ./tools/scripts/create_newspaper_file.sh report "testing-report"
#   ./tools/scripts/create_newspaper_file.sh work_results "auth-service-implementation"

set -e

echo "🚀 Автоматичне створення файлу в newspaper..."

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
if [ $# -lt 2 ]; then
    error "Використання: $0 [тип] [назва]"
    echo "Типи: report, work_results, steps_plan, update, security_documentation_backup"
    echo "Приклади:"
    echo "  $0 report 'testing-report'"
    echo "  $0 work_results 'auth-service-implementation'"
    echo "  $0 steps_plan 'next-steps-plan'"
    exit 1
fi

TYPE="$1"
NAME="$2"
CURRENT_DATE=$(date +"%Y-%m-%d")

# Визначення папки та наступного ID
case $TYPE in
    "report")
        FOLDER="docs/newspaper/report"
        TEMPLATE="report"
        ;;
    "work_results")
        FOLDER="docs/newspaper/report"
        TEMPLATE="work_results"
        ;;
    "steps_plan")
        FOLDER="docs/newspaper/report"
        TEMPLATE="steps_plan"
        ;;
    "update")
        FOLDER="docs/newspaper/report"
        TEMPLATE="report"
        ;;
    "research")
        FOLDER="docs/newspaper/research"
        TEMPLATE="research"
        ;;
    "security_documentation_backup")
        FOLDER="docs/newspaper/security_documentation_backup"
        TEMPLATE="report"
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

# Отримання наступного ID
log "Отримання наступного ID для $FOLDER..."

# Використання нового скрипта для отримання ID
NEXT_ID=$(./tools/scripts/documentation/get_next_newspaper_id.sh "$TYPE")

if [ -z "$NEXT_ID" ]; then
    error "Не вдалося отримати наступний ID"
    exit 1
fi

log "Наступний ID: $NEXT_ID"

# Перевірка кількості файлів в report
if [ "$TYPE" = "work_results" ] || [ "$TYPE" = "steps_plan" ] || [ "$TYPE" = "update" ] || [ "$TYPE" = "report" ]; then
    CURRENT_FILES=$(find "$FOLDER" -maxdepth 1 -type f -name "*.md" | grep -v "_old" | wc -l)
    if [ "$CURRENT_FILES" -ge 10 ]; then
        warning "⚠️  Попередження: В папці report вже $CURRENT_FILES файлів (максимум 10)"
        warning "   Старі файли будуть переміщені в _old після створення нового файлу"
    fi
fi

# Створення назви файлу (без версії)
FILENAME="${NEXT_ID}_${TYPE}_${NAME}.md"
FILEPATH="$FOLDER/$FILENAME"

# Перевірка чи файл вже існує
if [ -f "$FILEPATH" ]; then
    error "Файл вже існує: $FILEPATH"
    exit 1
fi

# Створення шаблону
log "Створення файлу: $FILEPATH"

case $TEMPLATE in
    "report")
        cat > "$FILEPATH" << EOF
# $NAME

## 📋 **Загальна інформація**

**Дата**: $CURRENT_DATE  
**Тип роботи**: [Тестування/Документація/Аналіз]  
**Статус**: 🚧 В процесі

## 🎯 **Мета роботи**

[Опис мети роботи]

## ✅ **Виконані завдання**

- [ ] Завдання 1
- [ ] Завдання 2

## 📊 **Результати**

[Що було досягнуто]

## 🎯 **Висновки та рекомендації**

[Основні висновки]

**Статус**: 🚧 В процесі  
**Наступний етап**: [Опис наступного етапу]  
**Дата**: $CURRENT_DATE
EOF
        ;;
    "work_results")
        cat > "$FILEPATH" << EOF
# Звіт про $NAME - $CURRENT_DATE

## ✅ **Виконані завдання**

- [x] Завдання 1
- [x] Завдання 2

## 📊 **Результати**

- Створено компонент X
- Реалізовано функціонал Y

## 🚀 **Наступні кроки**

- [ ] Наступне завдання

## 📋 **Технічні деталі**

[Технічні деталі реалізації]

**Статус**: ✅ Завершено  
**Дата**: $CURRENT_DATE
EOF
        ;;
    "steps_plan")
        cat > "$FILEPATH" << EOF
# План $NAME

**Дата**: $CURRENT_DATE  
**Основа**: [MASTER_TASKS.md](../../planning/MASTER_TASKS.md)  
**Статус**: Готовий до виконання

## 📋 **Детальний план дій**

### **ТИЖДЕНЬ 1: Назва модуля**

#### **День 1-2: Опис завдання**
**Завдання:**
- [ ] Завдання 1
- [ ] Завдання 2

**Результат:**
[Що буде досягнуто]

## 🔧 **Технічні деталі**

[Технічні деталі плану]

## 📈 **Метрики успіху**

[Ключові показники]

**Статус**: Готовий до виконання  
**Дата**: $CURRENT_DATE
EOF
        ;;
esac

log "✅ Файл створено: $FILEPATH"

# Показ створеного файлу
echo ""
info "Створений файл:"
echo "  Тип: $TYPE"
echo "  ID: $NEXT_ID"
echo "  Назва: $NAME"
echo "  Шлях: $FILEPATH"
echo ""

log "Файл готовий для редагування! 🎉" 