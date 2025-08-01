#!/bin/bash

# Скрипт для перевірки структури проекту
# Виявляє проблеми з Dockerfile, імпортами, файлами кешу та інше

set -e

echo "🔍 Перевірка структури проекту..."

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функція для виводу помилок
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Функція для виводу успіху
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функція для виводу попереджень
warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Перевірка дублікатів CMD в Dockerfile
echo "📋 Перевірка Dockerfile на дублікати CMD..."
dockerfile_issues=0

for dockerfile in $(find . -name "Dockerfile" -not -path "./docs/*" -not -path "./node_modules/*" -not -path "./app/frontend/node_modules/*" -not -path "./app/backend/venv/*" -not -path "./.venv/*"); do
    cmd_count=$(grep -c "CMD" "$dockerfile" || echo "0")
    if [ "$cmd_count" -gt 1 ]; then
        error "Дублікат CMD в $dockerfile ($cmd_count знайдено)"
        dockerfile_issues=$((dockerfile_issues + 1))
    else
        success "Dockerfile $dockerfile - OK"
    fi
done

# Перевірка неіснуючих імпортів (тільки в нашому коді)
echo "📋 Перевірка імпортів..."
import_issues=0

# Знаходимо тільки наші Python файли, виключаючи venv та node_modules
for py_file in $(find . -name "*.py" -not -path "./docs/*" -not -path "./app/backend/venv/*" -not -path "./.venv/*" -not -path "./.venv_python311/*" -not -path "./tools/.venv/*" -not -path "./node_modules/*" -not -path "./app/frontend/node_modules/*" | grep -E "(app/|tests/)"); do
    while IFS= read -r line; do
        if [[ $line =~ ^from\ \.([a-zA-Z_]+)\ import ]]; then
            module_name="${BASH_REMATCH[1]}"
            module_file="$(dirname "$py_file")/${module_name}.py"
            if [ ! -f "$module_file" ]; then
                error "Неіснуючий імпорт: $line в $py_file"
                import_issues=$((import_issues + 1))
            fi
        fi
    done < "$py_file"
done

# Перевірка файлів кешу (тільки в нашому коді)
echo "📋 Перевірка файлів кешу..."
cache_issues=0

# Перевіряємо тільки .coverage та .pytest_cache в нашому коді
if find . -name ".coverage" -not -path "./docs/*" -not -path "./node_modules/*" -not -path "./app/frontend/node_modules/*" -not -path "./app/backend/venv/*" -not -path "./.venv/*" -not -path "./.venv_python311/*" -not -path "./tools/.venv/*" | grep -q .; then
    error "Знайдено файли кешу: .coverage"
    cache_issues=$((cache_issues + 1))
else
    success "Файли кешу .coverage - OK"
fi

if find . -name ".pytest_cache" -type d -not -path "./docs/*" -not -path "./node_modules/*" -not -path "./app/frontend/node_modules/*" -not -path "./app/backend/venv/*" -not -path "./.venv/*" -not -path "./.venv_python311/*" -not -path "./tools/.venv/*" | grep -q .; then
    error "Знайдено файли кешу: .pytest_cache"
    cache_issues=$((cache_issues + 1))
else
    success "Файли кешу .pytest_cache - OK"
fi

# Перевірка порожніх файлів (тільки в нашому коді)
echo "📋 Перевірка порожніх файлів..."
empty_issues=0

for file in $(find . -type f -size 0 -not -path "./docs/*" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./app/frontend/node_modules/*" -not -path "./app/backend/venv/*" -not -path "./.venv/*" -not -path "./.venv_python311/*" -not -path "./tools/.venv/*" | grep -E "(app/|tests/)"); do
    if [[ "$file" != *".gitkeep"* ]]; then
        warning "Порожній файл: $file"
        empty_issues=$((empty_issues + 1))
    fi
done

# Перевірка .gitignore правил
echo "📋 Перевірка .gitignore..."
gitignore_issues=0

required_patterns=("logs/" "exports/" "sessions/" "*.log")
for pattern in "${required_patterns[@]}"; do
    if ! grep -q "$pattern" .gitignore; then
        warning "Відсутнє правило в .gitignore: $pattern"
        gitignore_issues=$((gitignore_issues + 1))
    else
        success ".gitignore містить: $pattern"
    fi
done

# Підсумок
echo ""
echo "📊 ПІДСУМОК ПЕРЕВІРКИ:"
echo "======================"

if [ $dockerfile_issues -eq 0 ] && [ $import_issues -eq 0 ] && [ $cache_issues -eq 0 ] && [ $empty_issues -eq 0 ] && [ $gitignore_issues -eq 0 ]; then
    success "Всі перевірки пройшли успішно! 🎉"
    exit 0
else
    echo ""
    echo "Знайдено проблем:"
    [ $dockerfile_issues -gt 0 ] && error "Dockerfile проблем: $dockerfile_issues"
    [ $import_issues -gt 0 ] && error "Проблем з імпортами: $import_issues"
    [ $cache_issues -gt 0 ] && error "Файлів кешу: $cache_issues"
    [ $empty_issues -gt 0 ] && warning "Порожніх файлів: $empty_issues"
    [ $gitignore_issues -gt 0 ] && warning "Проблем з .gitignore: $gitignore_issues"
    echo ""
    error "Структура проекту потребує виправлення!"
    exit 1
fi 