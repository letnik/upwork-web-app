#!/bin/bash

# Скрипт оновлення Python до версії 3.11+
# Використання: ./upgrade_python.sh

set -e

echo "🐍 Оновлення Python до версії 3.11+"
echo "===================================="

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функція для перевірки команди
check_command() {
    local command=$1
    if command -v $command &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Функція для перевірки версії Python
check_python_version() {
    local version=$(python3.11 --version 2>&1 | cut -d' ' -f2)
    echo "Поточна версія Python: $version"
    
    if [[ "$version" == 3.11* ]] || [[ "$version" == 3.12* ]]; then
        echo -e "${GREEN}✅ Python вже оновлений до потрібної версії!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Потрібно оновити Python до версії 3.11+${NC}"
        return 1
    fi
}

echo ""
echo "🔍 Перевірка поточної версії Python:"
check_python_version

if [ $? -eq 0 ]; then
    exit 0
fi

echo ""
echo "🔧 Вибір методу оновлення:"

# Перевіряємо доступні методи
if check_command "brew"; then
    echo -e "${GREEN}✅ Homebrew знайдено${NC}"
    METHOD="homebrew"
elif check_command "pyenv"; then
    echo -e "${GREEN}✅ pyenv знайдено${NC}"
    METHOD="pyenv"
elif check_command "conda"; then
    echo -e "${GREEN}✅ Conda знайдено${NC}"
    METHOD="conda"
else
    echo -e "${YELLOW}⚠️ Не знайдено Homebrew, pyenv або conda${NC}"
    echo "Встановіть один з цих менеджерів пакетів:"
    echo "  - Homebrew: https://brew.sh/"
    echo "  - pyenv: https://github.com/pyenv/pyenv"
    echo "  - Conda: https://docs.conda.io/"
    exit 1
fi

echo ""
echo "🚀 Оновлення Python за допомогою $METHOD:"

case $METHOD in
    "homebrew")
        echo -e "${BLUE}📦 Встановлення Python 3.11 через Homebrew...${NC}"
        brew install python@3.11
        
        echo -e "${BLUE}🔗 Створення символічного посилання...${NC}"
        brew link python@3.11
        
        echo -e "${BLUE}📋 Оновлення PATH...${NC}"
        echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        ;;
        
    "pyenv")
        echo -e "${BLUE}📦 Встановлення Python 3.11 через pyenv...${NC}"
        pyenv install 3.11.0
        
        echo -e "${BLUE}🔗 Встановлення як глобальної версії...${NC}"
        pyenv global 3.11.0
        
        echo -e "${BLUE}📋 Оновлення shell...${NC}"
        eval "$(pyenv init -)"
        ;;
        
    "conda")
        echo -e "${BLUE}📦 Встановлення Python 3.11 через Conda...${NC}"
        conda create -n python311 python=3.11 -y
        
        echo -e "${BLUE}🔗 Активація середовища...${NC}"
        conda activate python311
        ;;
esac

echo ""
echo "🔍 Перевірка оновленої версії:"
if check_python_version; then
    echo -e "${GREEN}🎉 Python успішно оновлений!${NC}"
    
    echo ""
    echo "📋 Наступні кроки:"
    echo "1. Перезапустіть термінал"
    echo "2. Перевірте версію: python3.11 --version"
    echo "3. Оновіть віртуальне середовище проекту:"
    echo "   cd /path/to/project"
    echo "   python3.11 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements/base.txt"
    
else
    echo -e "${RED}❌ Помилка оновлення Python${NC}"
    echo "Спробуйте встановити Python 3.11 вручну:"
    echo "https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "📊 Додаткова інформація:"
echo "- Python 3.11 має покращену продуктивність"
echo "- Підтримка нових функцій мови"
echo "- Кращі повідомлення про помилки"
echo "- Оптимізації для AI/ML бібліотек" 