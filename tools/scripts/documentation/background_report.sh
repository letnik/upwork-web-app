#!/bin/bash

# 🚀 ФОНОВИЙ СКРИПТ ДЛЯ СТВОРЕННЯ ЗВІТІВ
# Використання: ./tools/scripts/documentation/background_report.sh [тип] [назва] [опис] &
# Приклади: 
#   ./tools/scripts/documentation/background_report.sh update "quick-fix" "Швидке виправлення" &
#   ./tools/scripts/documentation/background_report.sh work_results "daily-work" "Щоденна робота" &

set -e

# Кольори для виводу
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Функція для логування
log() {
    echo -e "${GREEN}[BG]${NC} $1"
}

# Перевірка аргументів
if [ $# -lt 3 ]; then
    echo -e "${RED}[ERROR]${NC} Використання: $0 [тип] [назва] [опис]"
    echo "Типи: update, work_results, steps_plan, research"
    echo "Приклади:"
    echo "  $0 update 'quick-fix' 'Швидке виправлення'"
    echo "  $0 work_results 'daily-work' 'Щоденна робота'"
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
        echo -e "${RED}[ERROR]${NC} Невідомий тип: $TYPE"
        exit 1
        ;;
esac

# Отримання наступного ID
NEXT_ID=$(./tools/scripts/documentation/get_next_newspaper_id.sh "$TYPE")

if [ -z "$NEXT_ID" ]; then
    echo -e "${RED}[ERROR]${NC} Не вдалося отримати наступний ID"
    exit 1
fi

# Створення назви файлу
FILENAME="${NEXT_ID}_${TYPE}_${NAME}.md"
FILEPATH="$FOLDER/$FILENAME"

# Створення мінімального шаблону
log "Створення фонового звіту: $FILENAME"

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

- [ ] Завдання 1
- [ ] Завдання 2

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

## 📊 **Результати**

[Результати дослідження]

**Статус**: 🔬 В процесі  
**Дата**: $CURRENT_DATE $CURRENT_TIME
EOF
        ;;
esac

log "✅ Фоновий звіт створено: $FILEPATH"
echo "📄 ID: $NEXT_ID | Тип: $TYPE | Назва: $NAME" 