# 🚀 Upwork AI Assistant - AI-Powered Freelancing Platform

**Сучасна платформа для автоматизації роботи з Upwork через офіційний API з інтеграцією AI**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Зміст

1. [Огляд проекту](#-огляд-проекту)
2. [Архітектура](#️-архітектура)
3. [🚀 Швидкий запуск](#-швидкий-запуск)
4. [Поточний стан](#-поточний-стан)
5. [Тестування](#-тестування)
6. [Документація](#-документація)
7. [Розробка](#️-розробка)
8. [Безпека](#-безпека)
9. [Статистика проекту](#-статистика-проекту)
10. [Внесок](#-внесок)
11. [Ліцензія](#-ліцензія)

---

## 📋 Огляд проекту

**Upwork AI Assistant** - це інноваційна платформа для фрілансерів, яка автоматизує роботу з Upwork через офіційний API. Система використовує AI для генерації пропозицій, аналітики та оптимізації робочого процесу.

### 🎯 Ключові можливості

- 🤖 **AI Генерація пропозицій** - автоматичне створення якісних відгуків
- 🔍 **Розумний пошук вакансій** - фільтрація та ранжування за релевантністю
- 📊 **Детальна аналітика** - відстеження ефективності та статистики
- 🔐 **Максимальна безпека** - MFA, шифрування, OAuth 2.0
- 📱 **Сучасний веб-інтерфейс** - зручне управління через браузер
- 🔄 **Автоматизація** - автоматичні відгуки та ведення переписки
- 👥 **Мульти-користувацька система** - підтримка багатьох користувачів

---

## 🏗️ Архітектура

### **Мікросервісна архітектура:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Upwork Service │    │   AI Service    │    │ Analytics Svc   │
│   (FastAPI)     │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Сервіси:**

- **API Gateway** - маршрутизація та балансування навантаження
- **Auth Service** - авторизація, MFA, OAuth 2.0
- **Upwork Service** - інтеграція з Upwork API
- **AI Service** - генерація пропозицій та аналіз
- **Analytics Service** - збір та аналіз даних
- **Notification Service** - сповіщення та комунікація

---

## 🚀 Швидкий запуск

### **Вимоги:**
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (для frontend)

### **Автоматичний запуск (рекомендовано):**

```bash
# Клонування репозиторію
git clone https://github.com/your-username/upwork-ai-assistant.git
cd upwork-ai-assistant

# Запуск всього проекту однією командою
./tools/scripts/project/start_project.sh

# Відкрийте браузер: http://localhost:3000
```

**Скрипт автоматично:**
- ✅ Перевіряє залежності (Docker, Node.js, Python)
- ✅ Створює .env файл з базовими насташтуваннями
- ✅ Запускає PostgreSQL та Redis
- ✅ Запускає всі backend мікросервіси
- ✅ Встановлює залежності Frontend
- ✅ Запускає React додаток
- ✅ Показує статус та URL адреси

### **URL адреси після запуску:**

| Сервіс | URL | Опис |
|--------|-----|------|
| Frontend | http://localhost:3000 | React додаток |
| API Gateway | http://localhost:8000 | Основний API |
| API Docs | http://localhost:8000/docs | Swagger документація |
| Auth Service | http://localhost:8001 | Авторизація |
| AI Service | http://localhost:8003 | AI функції |
| Analytics | http://localhost:8004 | Аналітика |

### **Основні команди управління:**

```bash
# Запустити проект
./tools/scripts/project/start_project.sh

# Зупинити проект
./tools/scripts/project/start_project.sh stop

# Показати статус сервісів
./tools/scripts/project/start_project.sh status

# Перезапустити проект
./tools/scripts/project/start_project.sh restart

# Подивитися логи
./tools/scripts/project/start_project.sh logs

# Очистити все
./tools/scripts/project/start_project.sh cleanup
```

---

## 📊 Поточний стан

### **✅ Завершені етапи:**

1. **ЕТАП 1: БЕЗПЕКА ТА АВТОРИЗАЦІЯ** ✅
   - MFA (TOTP) реалізація
   - Password Reset функціональність
   - Session Management
   - Повна система авторизації

2. **ЕТАП 2.1: Proposal Creation Interface** ✅
   - Створення інтерфейсу пропозицій
   - Покроковий процес (3 етапи)
   - Збереження чернеток
   - Професійний UI

### **🔄 Поточний етап:**

**ЕТАП 2.2: Analytics Dashboard** - в процесі
- Створення аналітичної панелі
- Графіки та метрики
- Візуалізація даних

### **📋 Наступні етапи:**

- **ЕТАП 2.3:** Settings Page (покращення)
- **ЕТАП 3:** Аналітика (Local Analytics Engine)
- **ЕТАП 4:** Тестування
- **ЕТАП 5:** Документація

---

## 🧪 Тестування

### **Огляд тестів:**
- **Backend Unit**: 61 тест (98.4% покриття)
- **Frontend Unit**: 22 тести (96% покриття)
- **Security**: 15 тестів (100% покриття)
- **Загалом**: 98 тестів (85% покриття)

### **🚀 Швидкий запуск тестів:**
```bash
# Всі тести (рекомендовано)
npm test

# Або через shell скрипт
./tools/scripts/testing/run_tests.sh

# Конкретні типи
npm run test:backend          # Тільки backend
npm run test:frontend         # Тільки frontend  
npm run test:coverage         # З покриттям
npm run test:full             # ВСІ тести
```

### **📚 Документація тестів:**
- **[Детальний огляд всіх тестів](docs/TESTS_OVERVIEW.md)**
- **[Централізована документація тестів](tests/README.md)**

---

## 📚 Документація

### **Основна документація:**
- [📖 Проект огляд](docs/planning/PROJECT_OVERVIEW.md)
- [🏗️ Архітектура](docs/planning/ARCHITECTURE.md)
- [📋 Майстер-задачі](docs/planning/MASTER_TASKS.md)
- [🧪 Тестування](docs/planning/TESTING.md)
- [🔒 Test Security Guide](docs/planning/details/guides/development/test_security_guide.md) - **ОБОВ'ЯЗКОВИЙ**

### **Технічна документація:**
- [🔧 Налаштування середовища](docs/planning/details/guides/development/setup_environment.md)
- [🔐 Безпека](docs/planning/details/technical_details/security/security_implementation.md)
- [🐳 Docker конфігурація](docs/planning/details/technical_details/deployment/docker_configuration.md)
- [📊 API специфікації](docs/planning/details/technical_details/api/api_specifications.md)

### **Upwork інтеграція:**
- [🔗 План інтеграції](docs/analysis/upwork_api_integration_plan.md)
- [📖 Офіційний гід](docs/analysis/upwork_official_api_guide.md)
- [📝 Форма заявки](docs/newspaper/0001-upwork-api-application-checklist-v1.0.0.md)
- [🔗 OAuth Frontend Guide](docs/planning/details/guides/development/oauth_frontend_integration.md)

### **Інструкції для AI/розробників:**
- [🧑‍💻 Основні інструкції для AI](docs/instruction_ai/AI_CORE_INSTRUCTIONS.md)
- [📁 Управління файлами](docs/instruction_ai/FILE_MANAGEMENT.md)
- [🔄 Робочий процес](docs/instruction_ai/WORKFLOW_PROCESS.md)
- [✅ Чекліст відповідності](docs/instruction_ai/COMPLIANCE_CHECKLIST.md)

---

## 🛠️ Розробка

### **Структура проекту:**

```
upwork-ai-assistant/
├── app/                    # Основні додатки
│   ├── backend/           # Мікросервіси
│   │   ├── api-gateway/   # API Gateway
│   │   ├── services/      # Мікросервіси
│   │   └── shared/        # Спільні компоненти
│   └── frontend/          # React додаток
├── docs/                  # Документація
│   ├── planning/          # Планування проекту
│   ├── analysis/          # Аналіз та дослідження
│   └── newspaper/         # Звіти та нотатки
├── configs/               # Конфігурації
├── tools/                 # Інструменти розробки
└── tests/                 # Тести
```

### **Команди розробки:**

```bash
# Запуск тестів
pytest tests/

# Лінтер
flake8 app/backend/
black app/backend/

# Docker збірка
docker-compose build

# Розгортання
./tools/scripts/project/deploy.sh
```

---

## 🔐 Безпека

### **Компоненти безпеки:**

- **🔐 Многофакторна автентифікація (MFA)**
  - TOTP (Google Authenticator)
  - SMS верифікація
  - Backup коди

- **🔒 Шифрування даних**
  - Fernet шифрування токенів
  - bcrypt хешування паролів
  - JWT токени

- **🛡️ Моніторинг безпеки**
  - Логування всіх дій
  - Сповіщення про підозрілу активність
  - Rate limiting

---

## 📊 Статистика проекту

- **📁 Файлів:** 170+
- **🐍 Python файлів:** 15
- **📚 Документація:** 50+ файлів
- **🧪 Тести:** Покриття 80%+
- **🔧 Сервісів:** 6 мікросервісів
- **📦 Docker контейнерів:** 8

---

## 🤝 Внесок

### **Як внести свій внесок:**

1. **Fork** репозиторію
2. Створіть **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** зміни (`git commit -m 'Add amazing feature'`)
4. **Push** до branch (`git push origin feature/amazing-feature`)
5. Відкрийте **Pull Request**

### **Стандарти коду:**
- Python: PEP 8, Black, Flake8
- JavaScript: ESLint, Prettier
- Git: Conventional Commits
- Документація: Ukrainian language

---

## 📄 Ліцензія

Цей проект ліцензований під MIT License - дивіться файл [LICENSE](LICENSE) для деталей.

---

## 🙏 Подяки

- [Upwork](https://www.upwork.com/) - за офіційний API
- [OpenAI](https://openai.com/) - за AI можливості
- [FastAPI](https://fastapi.tiangolo.com/) - за чудовий фреймворк
- [React](https://reactjs.org/) - за frontend бібліотеку

---

**⭐ Якщо проект вам сподобався, поставте зірку!**

---

**Дата останнього оновлення: 2025-07-30**  
**Версія:** 2.1.0  
**Статус:** В активній розробці - Етап 2.2 (Analytics Dashboard) 