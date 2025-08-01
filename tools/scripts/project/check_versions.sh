#!/bin/bash

# Скрипт перевірки версій технологій проекту
# Використання: ./check_versions.sh

set -e

echo "🔍 Перевірка версій технологій проекту Upwork AI Assistant"
echo "=========================================================="

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функція для перевірки версії
check_version() {
    local name=$1
    local current_version=$2
    local required_version=$3
    
    echo -n "📦 $name: "
    
    # Використовуємо sort -V для правильного порівняння версій
    if printf '%s\n' "$required_version" "$current_version" | sort -V | head -n1 | grep -q "$required_version"; then
        echo -e "${GREEN}✅ $current_version${NC}"
        return 0
    else
        echo -e "${RED}❌ $current_version (потрібно: $required_version)${NC}"
        return 1
    fi
}

# Функція для перевірки наявності команди
check_command() {
    local command=$1
    local name=$2
    
    if command -v $command &> /dev/null; then
        echo -e "${GREEN}✅ $name знайдено${NC}"
        return 0
    else
        echo -e "${RED}❌ $name не знайдено${NC}"
        return 1
    fi
}

echo ""
echo "🐍 Python перевірка:"
python_version=$("/opt/homebrew/bin/python3.11" --version 2>&1 | cut -d' ' -f2)
check_version "Python" "$python_version" "3.11"

echo ""
echo "🟢 Node.js перевірка:"
node_version=$(node --version 2>&1 | cut -d'v' -f2)
check_version "Node.js" "$node_version" "18.0.0"

echo ""
echo "📦 npm перевірка:"
npm_version=$(npm --version 2>&1)
check_version "npm" "$npm_version" "9.0"

echo ""
echo "🐳 Docker перевірка:"
if command -v docker &> /dev/null; then
    docker_version=$(docker --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✅ Docker: $docker_version${NC}"
else
    echo -e "${YELLOW}⚠️ Docker не знайдено${NC}"
fi

echo ""
echo "🐳 Docker Compose перевірка:"
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version 2>&1 | cut -d' ' -f3 | cut -d',' -f1)
    echo -e "${GREEN}✅ Docker Compose: $compose_version${NC}"
else
    echo -e "${YELLOW}⚠️ Docker Compose не знайдено${NC}"
fi

echo ""
echo "📁 Перевірка структури проекту:"

# Перевірка основних папок
required_dirs=(
    "app/backend/services/auth-service"
    "app/backend/services/upwork-service"
    "app/backend/services/ai-service"
    "app/backend/services/analytics-service"
    "app/backend/services/notification-service"
    "app/frontend/src"
    "tests/unit/backend"
    "tests/unit/frontend"
    "requirements"
    "docker"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ $dir${NC}"
    else
        echo -e "${RED}❌ $dir відсутній${NC}"
    fi
done

echo ""
echo "📄 Перевірка основних файлів:"

# Перевірка основних файлів
required_files=(
    "requirements/base.txt"
    "requirements/auth-service.txt"
    "requirements/ai-service.txt"
    "requirements/analytics-service.txt"
    "app/frontend/package.json"
    "docker/docker-compose.yml"
    "package.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file відсутній${NC}"
    fi
done

echo ""
echo "🧪 Перевірка тестів:"

# Перевірка тестів
test_files=(
    "tests/unit/backend/test_models.py"
    "tests/unit/frontend/App.test.tsx"
    "tests/unit/backend/conftest.py"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${YELLOW}⚠️ $file відсутній${NC}"
    fi
done

echo ""
echo "🔧 Перевірка конфігурацій:"

# Перевірка конфігурацій
config_files=(
    "app/backend/shared/config/settings.py"
    "app/backend/shared/config/logging.py"
    "app/frontend/tsconfig.json"
    "app/frontend/jest.config.js"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${YELLOW}⚠️ $file відсутній${NC}"
    fi
done

echo ""
echo "📊 Підсумок перевірки:"

# Підрахунок проблем
issues=0
warnings=0

# Перевірка Python версії
if [[ "$python_version" < "3.11" ]]; then
    ((issues++))
fi

# Перевірка наявності основних команд
if ! command -v node &> /dev/null; then
    ((issues++))
fi

if ! command -v npm &> /dev/null; then
    ((issues++))
fi

echo -e "${YELLOW}⚠️ Попереджень: $warnings${NC}"
echo -e "${RED}❌ Проблем: $issues${NC}"

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}🎉 Всі перевірки пройдені успішно!${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Знайдено проблеми, які потребують виправлення${NC}"
    exit 1
fi 