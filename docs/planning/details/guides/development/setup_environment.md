# Налаштування Development Environment

> **Покроковий гід по налаштуванню середовища розробки для проекту Upwork AI Assistant**

---

## Зміст

1. [Вимоги](#вимоги)
2. [Встановлення інструментів](#встановлення-інструментів)
3. [Налаштування проекту](#налаштування-проекту)
4. [Запуск сервісів](#запуск-сервісів)
5. [Перевірка налаштування](#перевірка-налаштування)
6. [Розв'язання проблем](#розвязання-проблем)

---

## Вимоги

### **Системні вимоги**
- **OS**: macOS 12+, Ubuntu 20.04+, Windows 10+
- **RAM**: Мінімум 8GB (рекомендовано 16GB)
- **Storage**: Мінімум 10GB вільного місця
- **CPU**: Мінімум 4 ядра

### **Програмне забезпечення**
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **VS Code**: 1.70+ (рекомендовано)

---

## Встановлення інструментів

### **1. Встановлення Python**

#### **macOS (з Homebrew)**
```bash
# Встановити Homebrew (якщо не встановлено)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Встановити Python
brew install python@3.11

# Перевірити версію
python3 --version
```

#### **Ubuntu/Debian**
```bash
# Оновити пакети
sudo apt update

# Встановити Python
sudo apt install python3.11 python3.11-venv python3.11-dev

# Перевірити версію
python3.11 --version
```

#### **Windows**
```bash
# Завантажити з python.org
# https://www.python.org/downloads/

# Або через Chocolatey
choco install python311

# Перевірити версію
python --version
```

### **2. Встановлення Node.js**

#### **macOS (з Homebrew)**
```bash
brew install node@18

# Перевірити версію
node --version
npm --version
```

#### **Ubuntu/Debian**
```bash
# Додати NodeSource репозиторій
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Встановити Node.js
sudo apt install nodejs

# Перевірити версію
node --version
npm --version
```

#### **Windows**
```bash
# Завантажити з nodejs.org
# https://nodejs.org/

# Або через Chocolatey
choco install nodejs

# Перевірити версію
node --version
npm --version
```

### **3. Встановлення Docker**

#### **macOS**
```bash
# Завантажити Docker Desktop
# https://www.docker.com/products/docker-desktop

# Або через Homebrew
brew install --cask docker
```

#### **Ubuntu/Debian**
```bash
# Встановити Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Додати користувача до групи docker
sudo usermod -aG docker $USER

# Перезавантажити систему або вийти/увійти
```

#### **Windows**
```bash
# Завантажити Docker Desktop
# https://www.docker.com/products/docker-desktop

# Увімкнути WSL2 якщо потрібно
```

### **4. Встановлення Git**

#### **macOS**
```bash
brew install git
```

#### **Ubuntu/Debian**
```bash
sudo apt install git
```

#### **Windows**
```bash
# Завантажити з git-scm.com
# https://git-scm.com/

# Або через Chocolatey
choco install git
```

### **5. Встановлення VS Code**

#### **macOS**
```bash
brew install --cask visual-studio-code
```

#### **Ubuntu/Debian**
```bash
# Додати репозиторій
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

# Встановити VS Code
sudo apt update
sudo apt install code
```

#### **Windows**
```bash
# Завантажити з code.visualstudio.com
# https://code.visualstudio.com/

# Або через Chocolatey
choco install vscode
```

---

## Налаштування проекту

### **1. Клонування репозиторію**
```bash
# Клонувати проект
git clone https://github.com/your-org/upwork-ai-assistant.git
cd upwork-ai-assistant

# Перевірити структуру
ls -la
```

### **2. Налаштування Backend**

#### **Створення віртуального середовища**
```bash
# Перейти в папку backend
cd backend

# Створити віртуальне середовище
python3.11 -m venv venv

# Активувати віртуальне середовище
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Перевірити активацію
which python  # macOS/Linux
where python  # Windows
```

#### **Встановлення залежностей**
```bash
# Оновити pip
pip install --upgrade pip

# Встановити залежності
pip install -r requirements.txt

# Перевірити встановлення
pip list
```

#### **Налаштування змінних середовища**
```bash
# Створити файл .env
cp .env.example .env

# Відредагувати .env файл
nano .env  # або code .env
```

**Приклад .env файлу:**
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/upwork_ai_dev

# Redis
REDIS_URL=redis://localhost:6379

# AI APIs
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# Upwork API
UPWORK_CLIENT_ID=your_upwork_client_id
UPWORK_CLIENT_SECRET=your_upwork_client_secret

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Environment
ENVIRONMENT=development
DEBUG=true
```

### **3. Налаштування Frontend**

#### **Встановлення залежностей**
```bash
# Перейти в папку frontend
cd ../frontend

# Встановити залежності
npm install

# Перевірити встановлення
npm list
```

#### **Налаштування змінних середовища**
```bash
# Створити файл .env
cp .env.example .env

# Відредагувати .env файл
nano .env  # або code .env
```

**Приклад .env файлу:**
```env
# API
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Environment
REACT_APP_ENVIRONMENT=development
REACT_APP_DEBUG=true
```

### **4. Налаштування Docker**

#### **Створення docker-compose.yml**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: upwork_ai_dev
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=postgresql://user:password@postgres:5432/upwork_ai_dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm start

volumes:
  postgres_data:
  redis_data:
```

---

## Запуск сервісів

### **1. Запуск з Docker (рекомендовано)**

#### **Запуск всіх сервісів**
```bash
# Запустити всі сервіси
docker-compose -f docker-compose.dev.yml up -d

# Перевірити статус
docker-compose -f docker-compose.dev.yml ps

# Подивитися логи
docker-compose -f docker-compose.dev.yml logs -f
```

#### **Запуск окремих сервісів**
```bash
# Тільки база даних та Redis
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Backend
docker-compose -f docker-compose.dev.yml up -d backend

# Frontend
docker-compose -f docker-compose.dev.yml up -d frontend
```

### **2. Запуск локально**

#### **Запуск бази даних та Redis**
```bash
# Запустити тільки базу даних та Redis
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Дочекатися запуску
sleep 10
```

#### **Запуск Backend**
```bash
# Перейти в папку backend
cd backend

# Активувати віртуальне середовище
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate # Windows

# Запустити сервер
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Запуск Frontend**
```bash
# Новий термінал
# Перейти в папку frontend
cd frontend

# Запустити dev сервер
npm start
```

### **3. Перевірка доступу**

#### **Backend API**
```bash
# Перевірити health check
curl http://localhost:8000/health

# Перевірити документацію API
open http://localhost:8000/docs
```

#### **Frontend**
```bash
# Відкрити в браузері
open http://localhost:3000
```

---

## Перевірка налаштування

### **1. Перевірка Backend**
```bash
# Тести
cd backend
source venv/bin/activate
pytest tests/ -v

# Лінтер
flake8 src/
black src/
isort src/
```

### **2. Перевірка Frontend**
```bash
# Тести
cd frontend
npm test

# Лінтер
npm run lint
npm run format
```

### **3. Перевірка Docker**
```bash
# Перевірити зображення
docker images

# Перевірити контейнери
docker ps

# Перевірити мережі
docker network ls
```

### **4. Перевірка бази даних**
```bash
# Підключитися до PostgreSQL
docker exec -it upwork-ai-assistant_postgres_1 psql -U user -d upwork_ai_dev

# Перевірити таблиці
\dt

# Вийти
\q
```

### **5. Перевірка Redis**
```bash
# Підключитися до Redis
docker exec -it upwork-ai-assistant_redis_1 redis-cli

# Перевірити ключі
KEYS *

# Вийти
exit
```

---

## Розв'язання проблем

### **1. Проблеми з Python**
```bash
# Перевірити версію Python
python --version

# Якщо потрібна інша версія
pyenv install 3.11.0
pyenv global 3.11.0
```

### **2. Проблеми з Node.js**
```bash
# Перевірити версію Node.js
node --version

# Якщо потрібна інша версія
nvm install 18
nvm use 18
```

### **3. Проблеми з Docker**
```bash
# Перезапустити Docker
# macOS: Restart Docker Desktop
# Linux: sudo systemctl restart docker
# Windows: Restart Docker Desktop

# Очистити Docker
docker system prune -a
```

### **4. Проблеми з портами**
```bash
# Перевірити зайняті порти
lsof -i :8000  # macOS/Linux
netstat -an | findstr :8000  # Windows

# Зупинити процес
kill -9 <PID>
```

### **5. Проблеми з базою даних**
```bash
# Перезапустити PostgreSQL
docker-compose -f docker-compose.dev.yml restart postgres

# Очистити дані
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres
```

### **6. Проблеми з залежностями**
```bash
# Backend
cd backend
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Корисні команди

### **Docker команди**
```bash
# Запуск
docker-compose -f docker-compose.dev.yml up -d

# Зупинка
docker-compose -f docker-compose.dev.yml down

# Перезапуск
docker-compose -f docker-compose.dev.yml restart

# Логи
docker-compose -f docker-compose.dev.yml logs -f [service]

# Shell в контейнері
docker-compose -f docker-compose.dev.yml exec [service] bash
```

### **Git команди**
```bash
# Статус
git status

# Додати зміни
git add .

# Коміт
git commit -m "feat: add new feature"

# Push
git push origin main

# Pull
git pull origin main
```

### **VS Code команди**
```bash
# Відкрити проект
code .

# Відкрити термінал
Ctrl+` (Cmd+` на macOS)

# Пошук файлів
Ctrl+P (Cmd+P на macOS)

# Пошук в коді
Ctrl+Shift+F (Cmd+Shift+F на macOS)
```

---

## Пов'язані документи

### Основні документи
- [План проекту](../PROJECT_OVERVIEW.md)
- [Всі завдання](../MASTER_TASKS.md)
- [Загальний огляд](../PROJECT_OVERVIEW.md)

### Технічні гіди
- [OAuth2 Integration](oauth2_integration.md)
- [OpenAI Integration](openai_integration.md)
- [Database Migrations](database_migrations.md)
- [Testing Guide](testing_guide.md)

### Deployment гіди
- [Docker Setup](../deployment/docker_setup.md)
- [Production Deployment](../deployment/production_deployment.md)
- [Monitoring Setup](../deployment/monitoring_setup.md)

---

**Статус**: Створено  
**Версія**: 1.0.0  
**Останнє оновлення**: 2024-12-19 20:00 