# 🛠️ SCRIPTS - Інструменти та скрипти проекту

> **Всі скрипти для автоматизації Upwork AI Assistant**

---

## 🏛️ Правила для скриптів автоматизації

### **Критичні принципи:**
- **Структура**: Всі скрипти організовані за призначенням (project/, development/, testing/, deployment/, documentation/)
- **Документація**: Кожен скрипт має README з прикладами використання
- **Безпека**: Скрипти не містять секретів, використовують .env файли
- **Портабельність**: Скрипти працюють на Linux/macOS/Windows (через WSL)
- **Версійність**: Всі зміни в скриптах відстежуються в git
- **Тестування**: Скрипти тестуються перед комітом

### **Правила створення скриптів:**
- **Назва**: Описова, з підкресленнями (наприклад: `create_newspaper_file.sh`)
- **Шебанг**: Завжди `#!/bin/bash` або `#!/usr/bin/env bash`
- **Права**: `chmod +x` для всіх скриптів
- **Логування**: Використовувати кольорові повідомлення (log_info, log_success, log_error)
- **Валідація**: Перевіряти аргументи та умови виконання
- **Помилки**: `set -e` для зупинки при помилках

### **Чекліст для ревʼю скриптів:**
- [ ] Скрипт в правильній папці за призначенням
- [ ] Має описову назву
- [ ] Містить shebang та права на виконання
- [ ] Використовує кольорове логування
- [ ] Валідує аргументи
- [ ] Обробляє помилки
- [ ] Документований в README
- [ ] Тестований на різних ОС
- [ ] Не містить секретів
- [ ] Використовує .env для конфігурації

### **Автоматизація через manage.sh:**
```bash
# Використовувати централізований скрипт управління
./tools/scripts/project/manage.sh start    # Запуск проекту
./tools/scripts/project/manage.sh stop     # Зупинка проекту
./tools/scripts/project/manage.sh clean    # Очищення
./tools/scripts/project/manage.sh install  # Встановлення залежностей
./tools/scripts/project/manage.sh audit    # Аудит безпеки
```

## 📋 Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Категорії скриптів](#категорії-скриптів)
4. [Швидкий старт](#швидкий-старт)
5. [Документація](#документація)

---

## 📋 Огляд

Папка `tools/scripts/` містить всі скрипти для автоматизації проекту, організовані за призначенням:

- **`project/`** - Скрипти для управління проектом
- **`development/`** - Скрипти для розробки
- **`testing/`** - Скрипти для тестування
- **`deployment/`** - Скрипти для розгортання
- **`documentation/`** - Скрипти для документації

---

## 📁 Структура

```
tools/scripts/
├── project/                 # 🚀 Управління проектом
│   ├── start_project.sh    # Запуск проекту
│   ├── build.sh            # Збірка проекту
│   ├── deploy.sh           # Розгортання
│   └── migrate.sh          # Міграції БД
├── development/             # 🔧 Розробка
│   ├── check_links.sh      # Перевірка посилань
│   └── setup_dev.sh        # Налаштування розробки
├── testing/                 # 🧪 Тестування
│   ├── run_tests.sh        # Запуск всіх тестів
│   ├── test_backend.sh     # Backend тести
│   └── test_frontend.sh    # Frontend тести
├── deployment/              # 🚀 Розгортання
│   ├── deploy_prod.sh      # Production розгортання
│   ├── backup.sh           # Backup системи
│   └── health_check.sh     # Перевірка здоров'я
├── documentation/           # 📚 Документація
│   ├── create_newspaper_file.sh # Створення звітів
│   ├── get_next_newspaper_id.sh # ID генерація
│   ├── check_newspaper_ids.sh   # Перевірка ID
│   └── update_readme.sh    # Оновлення README
└── README.md               # Цей файл
```

---

## 🎯 Категорії скриптів

### **🚀 Project - Управління проектом**
Скрипти для загального управління проектом:

- **[start_project.sh](project/start_project.sh)** - Запуск всього проекту
- **[build.sh](project/build.sh)** - Збірка проекту
- **[deploy.sh](project/deploy.sh)** - Розгортання
- **[migrate.sh](project/migrate.sh)** - Міграції бази даних

**Використання:**
```bash
# Запуск проекту
./tools/scripts/project/start_project.sh

# Збірка
./tools/scripts/project/build.sh

# Розгортання
./tools/scripts/project/deploy.sh production
```

### **🔧 Development - Розробка**
Скрипти для розробки та налагодження:

- **[check_links.sh](development/check_links.sh)** - Перевірка посилань в README
- **[setup_dev.sh](development/setup_dev.sh)** - Налаштування середовища розробки

**Використання:**
```bash
# Перевірка посилань
./tools/scripts/development/check_links.sh

# Налаштування розробки
./tools/scripts/development/setup_dev.sh
```

### **🧪 Testing - Тестування**
Скрипти для запуску тестів:

- **[run_tests.sh](testing/run_tests.sh)** - Універсальний скрипт тестування
- **[test_backend.sh](testing/test_backend.sh)** - Backend тести
- **[test_frontend.sh](testing/test_frontend.sh)** - Frontend тести

**Використання:**
```bash
# Всі тести
./tools/scripts/testing/run_tests.sh

# Конкретні типи
./tools/scripts/testing/run_tests.sh backend
./tools/scripts/testing/run_tests.sh frontend
./tools/scripts/testing/run_tests.sh coverage
./tools/scripts/testing/run_tests.sh full
```

### **🚀 Deployment - Розгортання**
Скрипти для розгортання та моніторингу:

- **[deploy_prod.sh](deployment/deploy_prod.sh)** - Production розгортання
- **[backup.sh](deployment/backup.sh)** - Backup системи
- **[health_check.sh](deployment/health_check.sh)** - Перевірка здоров'я

**Використання:**
```bash
# Production розгортання
./tools/scripts/deployment/deploy_prod.sh

# Backup
./tools/scripts/deployment/backup.sh

# Health check
./tools/scripts/deployment/health_check.sh
```

### **📚 Documentation - Документація**
Скрипти для управління документацією:

- **[create_newspaper_file.sh](documentation/create_newspaper_file.sh)** - Створення звітів
- **[get_next_newspaper_id.sh](documentation/get_next_newspaper_id.sh)** - Генерація ID
- **[check_newspaper_ids.sh](documentation/check_newspaper_ids.sh)** - Перевірка ID
- **[update_readme.sh](documentation/update_readme.sh)** - Оновлення README

**Використання:**
```bash
# Створення звіту
./tools/scripts/documentation/create_newspaper_file.sh report "назва-звіту"

# Отримання наступного ID
./tools/scripts/documentation/get_next_newspaper_id.sh

# Перевірка ID
./tools/scripts/documentation/check_newspaper_ids.sh
```

---

## 🚀 Швидкий старт

### **Основні команди:**
```bash
# Запуск проекту
./tools/scripts/project/start_project.sh

# Запуск тестів
./tools/scripts/testing/run_tests.sh

# Перевірка посилань
./tools/scripts/development/check_links.sh

# Створення звіту
./tools/scripts/documentation/create_newspaper_file.sh report "назва"
```

### **NPM альтернативи:**
```bash
# Тестування (з кореневої папки)
npm test                    # Всі тести
npm run test:backend        # Backend тести
npm run test:frontend       # Frontend тести
npm run test:coverage       # З покриттям
npm run test:full           # Всі тести
```

---

## 📚 Документація

### **Детальна документація:**
- **[Project Scripts](project/README.md)** - Скрипти управління проектом
- **[Development Scripts](development/README.md)** - Скрипти розробки
- **[Testing Scripts](testing/README.md)** - Скрипти тестування
- **[Deployment Scripts](deployment/README.md)** - Скрипти розгортання
- **[Documentation Scripts](documentation/README.md)** - Скрипти документації

### **Корисні посилання:**
- **[Головна документація проекту](../../docs/README.md)**
- **[Тестування проекту](../../tests/README.md)**
- **[CI/CD Pipeline](../../.github/workflows/test.yml)**

---

## 🔧 Налаштування

### **Права на виконання:**
```bash
# Надати права на всі скрипти
chmod +x tools/scripts/**/*.sh

# Або конкретному скрипту
chmod +x tools/scripts/testing/run_tests.sh
```

### **Автодоповнення:**
```bash
# Додати до .bashrc або .zshrc
alias scripts='cd tools/scripts'
alias test='./tools/scripts/testing/run_tests.sh'
alias deploy='./tools/scripts/project/deploy.sh'
```

---

## 🎯 Переваги організації

### **✅ Чітка структура:**
- **Легко знайти** потрібний скрипт
- **Логічна організація** за призначенням
- **Масштабованість** для нових скриптів

### **✅ Зручність використання:**
- **Стандартизовані команди** для кожного типу
- **Детальна документація** для кожного скрипта
- **Приклади використання** в README

### **✅ Підтримка:**
- **Легко додавати** нові скрипти
- **Просто оновлювати** існуючі
- **Автоматична документація** структури

---

**Статус**: Активний  
**Версія**: 2.0.0  
**Останнє оновлення**: 2025-01-30 