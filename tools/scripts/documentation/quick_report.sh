#!/bin/bash

# 🚀 ШВИДКИЙ СКРИПТ ДЛЯ СТВОРЕННЯ ЗВІТІВ
# Використання: ./tools/scripts/documentation/quick_report.sh [тип] [назва] [опис]
# Приклади: 
#   ./tools/scripts/documentation/quick_report.sh update "security-fix" "Виправлено вразливість в auth"
#   ./tools/scripts/documentation/quick_report.sh work_results "api-integration" "Інтеграція з Upwork API"

set -e

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для логування
log() {
    echo -e "${GREEN}[QUICK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Перевірка аргументів
if [ $# -lt 3 ]; then
    error "Використання: $0 [тип] [назва] [опис]"
    echo "Типи: update, work_results, steps_plan, research"
    echo "Приклади:"
    echo "  $0 update 'security-fix' 'Виправлено вразливість в auth'"
    echo "  $0 work_results 'api-integration' 'Інтеграція з Upwork API'"
    echo "  $0 steps_plan 'next-phase' 'План наступної фази розробки'"
    exit 1
fi

TYPE="$1"
NAME="$2"
DESCRIPTION="$3"
CURRENT_DATE=$(date +"%Y-%m-%d")
CURRENT_TIME=$(date +"%H:%M")

# Визначення папки
case $TYPE in
    "update"|"work_results"|"steps_plan")
        FOLDER="docs/newspaper/report"
        ;;
    "research")
        FOLDER="docs/newspaper/research"
        ;;
    *)
        error "Невідомий тип: $TYPE"
        echo "Доступні типи: update, work_results, steps_plan, research"
        exit 1
        ;;
esac

# Отримання наступного ID (швидко)
NEXT_ID=$(./tools/scripts/documentation/get_next_newspaper_id.sh "$TYPE")

if [ -z "$NEXT_ID" ]; then
    error "Не вдалося отримати наступний ID"
    exit 1
fi

# Створення назви файлу
FILENAME="${NEXT_ID}_${TYPE}_${NAME}.md"
FILEPATH="$FOLDER/$FILENAME"

# Створення мінімального шаблону
log "Створення швидкого звіту: $FILENAME"

case $TYPE in
    "update")
        cat > "$FILEPATH" << EOF
# $NAME

**Дата**: $CURRENT_DATE $CURRENT_TIME  
**Тип**: Оновлення  
**Статус**: ✅ Завершено

## 📋 **Опис**

$DESCRIPTION

## ✅ **Виконані дії**

- [x] Основна дія
- [x] Додаткові дії

## 📊 **Результат**

[Короткий опис результату]

**Статус**: ✅ Завершено  
**Дата**: $CURRENT_DATE $CURRENT_TIME
EOF
        ;;
    "work_results")
        cat > "$FILEPATH" << EOF
# Звіт про $NAME

**Дата**: $CURRENT_DATE $CURRENT_TIME  
**Тип**: Результати роботи  
**Статус**: ✅ Завершено

## 📋 **Опис роботи**

$DESCRIPTION

## ✅ **Виконані завдання**

- [x] Основне завдання
- [x] Додаткові завдання

## 📊 **Результати**

[Що було досягнуто]

**Статус**: ✅ Завершено  
**Дата**: $CURRENT_DATE $CURRENT_TIME
EOF
        ;;
    "steps_plan")
        cat > "$FILEPATH" << EOF
# План $NAME

**Дата**: $CURRENT_DATE $CURRENT_TIME  
**Тип**: План дій  
**Статус**: 🚧 В процесі

## 📋 **Опис плану**

$DESCRIPTION

## 📋 **План дій**

### **Етап 1: Підготовка**
- [ ] Завдання 1
- [ ] Завдання 2

### **Етап 2: Реалізація**
- [ ] Завдання 3
- [ ] Завдання 4

**Статус**: 🚧 В процесі  
**Дата**: $CURRENT_DATE $CURRENT_TIME
EOF
        ;;
    "research")
        cat > "$FILEPATH" << EOF
# Дослідження $NAME

**Дата**: $CURRENT_DATE $CURRENT_TIME  
**Тип**: Дослідження  
**Статус**: 🔬 В процесі

## 📋 **Мета дослідження**

$DESCRIPTION

## 🔍 **Методологія**

[Опис методу дослідження]

## 📊 **Результати**

[Результати дослідження]

**Статус**: 🔬 В процесі  
**Дата**: $CURRENT_DATE $CURRENT_TIME
EOF
        ;;
esac

log "✅ Швидкий звіт створено: $FILEPATH"

# Показ створеного файлу
echo ""
echo "📄 Створений файл:"
echo "  Тип: $TYPE"
echo "  ID: $NEXT_ID"
echo "  Назва: $NAME"
echo "  Шлях: $FILEPATH"
echo "  Опис: $DESCRIPTION"
echo ""

log "Звіт готовий! Можна редагувати далі 🎉" 