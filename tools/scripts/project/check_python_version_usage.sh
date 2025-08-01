#!/bin/bash

# Скрипт перевірки використання Python 3.11 у всіх файлах проекту
# Використання: ./check_python_version_usage.sh

set -e

echo "🔍 Перевірка використання Python 3.11 у всіх файлах проекту"
echo "============================================================="

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для перевірки файлів
check_file() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file"; then
            echo -e "${RED}❌ $file - $description${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $file - $description${NC}"
            return 0
        fi
    else
        echo -e "${YELLOW}⚠️ $file - файл не знайдено${NC}"
        return 0
    fi
}

# Функція для перевірки правильного використання
check_correct_usage() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file"; then
            echo -e "${GREEN}✅ $file - $description${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ $file - $description (не знайдено)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️ $file - файл не знайдено${NC}"
        return 0
    fi
}

echo ""
echo "🐍 Перевірка використання Python 3.11:"

# Перевірка package.json
check_correct_usage "package.json" "python3.11" "використовує python3.11"

# Перевірка скриптів проекту
check_correct_usage "tools/scripts/project/start_project.sh" "python3.11" "використовує python3.11"
check_correct_usage "tools/scripts/project/migrate.sh" "python3.11" "використовує python3.11"
check_correct_usage "tools/scripts/project/manage.sh" "python3.11" "використовує python3.11"
check_correct_usage "tools/scripts/project/upgrade_python.sh" "python3.11" "використовує python3.11"

echo ""
echo "🚫 Перевірка застарілих посилань на Python 3.9:"

# Перевірка застарілих посилань
check_file "package.json" "python3 -m pytest" "використовує python3 замість python3.11"
check_file "tools/scripts/project/start_project.sh" "python3 -m venv" "використовує python3 замість python3.11"
check_file "tools/scripts/project/migrate.sh" "python3 -m venv" "використовує python3 замість python3.11"
check_file "tools/scripts/project/manage.sh" "python3 -m venv" "використовує python3 замість python3.11"

echo ""
echo "🐳 Перевірка Docker файлів:"

# Перевірка Docker файлів
check_correct_usage "app/backend/api-gateway/Dockerfile" "FROM python:3.11" "використовує Python 3.11"
check_correct_usage "app/backend/services/auth-service/Dockerfile" "FROM python:3.11" "використовує Python 3.11"
check_correct_usage "app/backend/services/upwork-service/Dockerfile" "FROM python:3.11" "використовує Python 3.11"
check_correct_usage "app/backend/services/ai-service/Dockerfile" "FROM python:3.11" "використовує Python 3.11"
check_correct_usage "app/backend/services/analytics-service/Dockerfile" "FROM python:3.11" "використовує Python 3.11"
check_correct_usage "app/backend/services/notification-service/Dockerfile" "FROM python:3.11" "використовує Python 3.11"

echo ""
echo "📚 Перевірка документації:"

# Перевірка документації
check_correct_usage "README.md" "Python 3.11" "згадує Python 3.11"
check_correct_usage "docs/planning/README.md" "Python 3.11" "згадує Python 3.11"
check_correct_usage "docs/planning/ARCHITECTURE.md" "Python 3.11" "згадує Python 3.11"

echo ""
echo "🔧 Перевірка CI/CD:"

# Перевірка CI/CD
check_correct_usage ".github/workflows/test.yml" "Python 3.11" "використовує Python 3.11"

echo ""
echo "📊 Підсумок перевірки:"

# Підрахунок результатів
total_files=0
correct_files=0
incorrect_files=0

# Перевірка всіх Python файлів на використання python3 замість python3.11
echo ""
echo "🔍 Детальна перевірка Python файлів:"

# Знаходимо всі файли, які можуть містити посилання на Python
find . -name "*.py" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" -o -name "*.md" | grep -v ".git" | grep -v "node_modules" | while read -r file; do
    if grep -l "python3 -m" "$file" > /dev/null 2>&1; then
        echo -e "${RED}❌ $file - використовує python3 замість python3.11${NC}"
        ((incorrect_files++))
    elif grep -l "python3.11" "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $file - правильно використовує python3.11${NC}"
        ((correct_files++))
    fi
    ((total_files++))
done

echo ""
echo "📈 Статистика:"
echo -e "${GREEN}✅ Правильних файлів: $correct_files${NC}"
echo -e "${RED}❌ Неправильних файлів: $incorrect_files${NC}"
echo -e "${BLUE}📊 Загальна кількість: $total_files${NC}"

if [ $incorrect_files -eq 0 ]; then
    echo -e "${GREEN}🎉 Всі файли правильно використовують Python 3.11!${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Знайдено файли, які потребують оновлення до Python 3.11${NC}"
    exit 1
fi 