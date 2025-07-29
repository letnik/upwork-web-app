# 🚀 Upwork Web App - AI-Powered Freelancing Platform

**Сучасна платформа для автоматизації роботи з Upwork через офіційний API з інтеграцією AI**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Огляд проекту

**Upwork Web App** - це інноваційна платформа для фрілансерів, яка автоматизує роботу з Upwork через офіційний API. Система використовує AI для генерації пропозицій, аналітики та оптимізації робочого процесу.

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

## 🚀 Швидкий старт

### **Вимоги:**
- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (для frontend)
- Upwork Developer Account
- OpenAI API Key

### **Встановлення:**

```bash
# Клонування репозиторію
git clone https://github.com/your-username/upwork-web-app.git
cd upwork-web-app

# Запуск через Docker
docker-compose up -d

# Або локальне встановлення
cd app/backend
pip install -r requirements.txt
python -m uvicorn api-gateway.src.main:app --reload
```

### **Налаштування:**

1. **Upwork API:**
   ```bash
   # Отримайте API ключі на https://www.upwork.com/developer/keys/
   export UPWORK_CLIENT_ID="your_client_id"
   export UPWORK_CLIENT_SECRET="your_client_secret"
   ```

2. **OpenAI API:**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. **База даних:**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/upwork_app"
   ```

---

## 📚 Документація

### **Основна документація:**
- [📖 Проект огляд](docs/planning/PROJECT_OVERVIEW.md)
- [🏗️ Архітектура](docs/planning/ARCHITECTURE.md)
- [📋 Майстер-задачі](docs/planning/MASTER_TASKS.md)
- [🧪 Тестування](docs/planning/TESTING.md)

### **Технічна документація:**
- [🔧 Налаштування середовища](docs/planning/details/guides/development/setup_environment.md)
- [🔐 Безпека](docs/planning/details/technical_details/security/security_implementation.md)
- [🐳 Docker конфігурація](docs/planning/details/technical_details/deployment/docker_configuration.md)
- [📊 API специфікації](docs/planning/details/technical_details/api/api_specifications.md)

### **Upwork інтеграція:**
- [🔗 План інтеграції](docs/analysis/upwork_api_integration_plan.md)
- [📖 Офіційний гід](docs/analysis/upwork_official_api_guide.md)
- [📝 Форма заявки](docs/newspaper/upwork_api_application_checklist_v1.0.0.md)

---

## 🛠️ Розробка

### **Структура проекту:**

```
upwork-web-app/
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
./tools/scripts/deploy.sh
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

## 📞 Контакти

- **Автор:** [Ваше ім'я]
- **Email:** [your.email@example.com]
- **GitHub:** [@your-username]
- **LinkedIn:** [your-linkedin]

---

## 🙏 Подяки

- [Upwork](https://www.upwork.com/) - за офіційний API
- [OpenAI](https://openai.com/) - за AI можливості
- [FastAPI](https://fastapi.tiangolo.com/) - за чудовий фреймворк
- [React](https://reactjs.org/) - за frontend бібліотеку

---

**⭐ Якщо проект вам сподобався, поставте зірку!**

---

**Дата останнього оновлення:** 2024-12-19  
**Версія:** 1.0.0  
**Статус:** В розробці 