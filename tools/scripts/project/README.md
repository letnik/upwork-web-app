# 🚀 Project Scripts - Управління проектом

> **Скрипти для загального управління проектом Upwork AI Assistant**

---

## 📋 Огляд

Папка `project/` містить скрипти для управління проектом на високому рівні:

- **Запуск проекту** - повний цикл запуску
- **Збірка проекту** - компіляція та підготовка
- **Розгортання** - деплой в різні середовища
- **Міграції** - управління базою даних

---

## 📁 Доступні скрипти

### **start_project.sh** - Запуск проекту
**Призначення**: Повний запуск проекту з перевіркою залежностей

**Використання:**
```bash
# Запуск проекту
./tools/scripts/project/start_project.sh

# З опціями
./tools/scripts/project/start_project.sh start    # Запуск
./tools/scripts/project/start_project.sh stop     # Зупинка
./tools/scripts/project/start_project.sh restart  # Перезапуск
./tools/scripts/project/start_project.sh status   # Статус
./tools/scripts/project/start_project.sh logs     # Логи
./tools/scripts/project/start_project.sh cleanup  # Очищення
```

**Функціональність:**
- ✅ Перевірка залежностей (Docker, Node.js, Python)
- ✅ Створення .env файлу
- ✅ Запуск PostgreSQL та Redis
- ✅ Запуск всіх мікросервісів
- ✅ Встановлення frontend залежностей
- ✅ Запуск React додатку
- ✅ Показ статусу та URL адрес

### **build.sh** - Збірка проекту
**Призначення**: Збірка проекту для різних середовищ

**Використання:**
```bash
# Збірка всього проекту
./tools/scripts/project/build.sh all

# Збірка конкретних компонентів
./tools/scripts/project/build.sh backend
./tools/scripts/project/build.sh frontend
./tools/scripts/project/build.sh docker
```

**Функціональність:**
- ✅ Збірка backend (Python)
- ✅ Збірка frontend (React)
- ✅ Створення Docker образів
- ✅ Оптимізація для production
- ✅ Створення артефактів

### **deploy.sh** - Розгортання
**Призначення**: Розгортання проекту в різні середовища

**Використання:**
```bash
# Розгортання в різні середовища
./tools/scripts/project/deploy.sh local      # Локальне
./tools/scripts/project/deploy.sh dev        # Розробка
./tools/scripts/project/deploy.sh staging    # Staging
./tools/scripts/project/deploy.sh production # Production
```

**Функціональність:**
- ✅ Перевірка середовища
- ✅ Backup перед розгортанням
- ✅ Збірка артефактів
- ✅ Розгортання сервісів
- ✅ Health check після розгортання
- ✅ Rollback при помилках

### **migrate.sh** - Міграції БД
**Призначення**: Управління міграціями бази даних

**Використання:**
```bash
# Запуск міграцій
./tools/scripts/project/migrate.sh

# Створення нової міграції
./tools/scripts/project/migrate.sh create "опис міграції"

# Відкат міграції
./tools/scripts/project/migrate.sh rollback

# Статус міграцій
./tools/scripts/project/migrate.sh status
```

**Функціональність:**
- ✅ Автоматичне виявлення міграцій
- ✅ Безпечне виконання
- ✅ Backup перед міграцією
- ✅ Відкат при помилках
- ✅ Логування процесу

---

## 🚀 Швидкий старт

### **Повний цикл розробки:**
```bash
# 1. Запуск проекту
./tools/scripts/project/start_project.sh

# 2. Збірка для тестування
./tools/scripts/project/build.sh all

# 3. Розгортання в dev
./tools/scripts/project/deploy.sh dev

# 4. Міграції БД
./tools/scripts/project/migrate.sh
```

### **Production розгортання:**
```bash
# 1. Збірка для production
./tools/scripts/project/build.sh all

# 2. Розгортання
./tools/scripts/project/deploy.sh production

# 3. Перевірка
./tools/scripts/project/start_project.sh status
```

---

## 🔧 Налаштування

### **Змінні середовища:**
```bash
# .env файл
PROJECT_ENV=development
DOCKER_COMPOSE_FILE=docker-compose.yml
BACKEND_PORT=8000
FRONTEND_PORT=3000
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

### **Конфігурація:**
```bash
# configs/project/
├── development.yml
├── staging.yml
├── production.yml
└── docker-compose.yml
```

---

## 📊 Моніторинг

### **Статус сервісів:**
```bash
# Перевірка статусу
./tools/scripts/project/start_project.sh status

# Логи сервісів
./tools/scripts/project/start_project.sh logs

# Health check
curl http://localhost:8000/health
```

### **Метрики:**
- **Uptime**: Час роботи сервісів
- **Response time**: Час відповіді API
- **Error rate**: Частота помилок
- **Resource usage**: Використання ресурсів

---

## 🎯 Переваги

### **✅ Автоматизація:**
- **Один скрипт** для повного запуску
- **Автоматична перевірка** залежностей
- **Безпечне розгортання** з rollback

### **✅ Надійність:**
- **Backup перед змінами**
- **Health check після розгортання**
- **Логування всіх операцій**

### **✅ Зручність:**
- **Простий інтерфейс** команд
- **Детальна документація**
- **Приклади використання**

---

**Статус**: Активний  
**Версія**: 1.0.0  
**Останнє оновлення**: 2025-01-30 