# 🤖 Основні інструкції для AI асистентів

> **Ключові принципи та правила для роботи з проектом**

---

## 🏛️ **Критичні правила структури проекту**

- **Тести**: Всі тести (unit, integration, security) зберігаються ТІЛЬКИ в папці `tests/`. Заборонено тести в сервісах, shared, production-коді.
- **Залежності**: Всі Python залежності централізовано в папці `requirements/`. Заборонено requirements.txt в сервісах!
- **Документація**: README — один на папку, не дублювати. Звіти — тільки в newspaper/report.
- **Кеші, .venv, dist, .coverage**: Не тримати в репозиторії. Див. `.gitignore`.
- **Dockerfile**: Всі сервіси використовують централізовані requirements.
- **Автоматизація**: Використовувати скрипти з `tools/scripts/project/manage.sh`.
- **Версія проекту**: Зберігається в файлі `VERSION`.

**Чекліст для ревʼю AI/Dev:**
- [ ] Тести тільки в `tests/`
- [ ] Залежності тільки через requirements/
- [ ] Dockerfile не містить requirements.txt
- [ ] README не дублюються
- [ ] Кеші/venv/dist не в репозиторії
- [ ] Оновлено VERSION
- [ ] Дотримано інструкцій для AI/Dev
- [ ] Дотримано MVP логіки та обмежень
- [ ] Не додані зайві функції поза MVP

---

## 🎯 **Ключові принципи**

### **📋 Документація - Головний план розробки**
- 📋 **MASTER_TASKS.md** - ГЛАВНИЙ ФАЙЛ з усіма завданнями та їх статусом
- 📋 **PROJECT_OVERVIEW.md** - загальний огляд проекту та стратегія
- 📋 **ARCHITECTURE.md** - технічна архітектура системи
- 📋 **Документація керує розробкою** - всі зміни мають відповідати планам
- 📋 **Версіонування** - семантичне версіонування X.Y.Z
- 📋 **Навігація** - зміст з якорями + посилання між документами
- 📋 **Лаконічність** - відповіді короткі та без дублювання інформації
- 📋 **Короткі звіти** - звіти мають бути якомога коротшими та лаконічними

### **🔐 Безпека**
- 🔐 **Повна ізоляція даних** - кожен користувач бачить тільки свої дані
- 🔐 **OAuth 2.0 + MFA** - обов'язкова двофакторна автентифікація
- 🔐 **Шифрування токенів** - всі чутливі дані зашифровані
- 🔐 **Rate limiting** - захист від зловживань

### **🎯 MVP Логіка**
- 🎯 **Дотримання обмежень** - профілі (10), шаблони (10), чернетки (100)
- 🎯 **Часові ліміти** - 100 запитів/день, 30 сек між запитами
- 🎯 **Ключові принципи** - НЕ генерація одразу, тільки при запиті
- 🎯 **Мінімальність** - тільки необхідні функції, без "nice to have"

### **🧪 Тестування**
- 🧪 **Обов'язкове тестування** - після кожної реалізованої задачі
- 🧪 **Unit тести** - для всіх нових функцій та middleware
- 🧪 **Інтеграційні тести** - для перевірки взаємодії компонентів
- 🧪 **Тести безпеки** - для перевірки захисту від атак
- 🧪 **Автоматичне тестування** - `pytest` для всіх змін

### **⚙️ Технічний стек**
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL
- **Безпека**: JWT, bcrypt, Fernet шифрування, pyotp (MFA)
- **AI/ML**: OpenAI GPT-4, Claude, Scikit-learn
- **Frontend**: React.js, TypeScript, Material-UI
- **Інфраструктура**: Docker, Nginx, Prometheus

---

## 📁 **Структура документації**

```
docs/
├── planning/                          # Плани та стратегія
│   ├── PROJECT_OVERVIEW.md           # Головний огляд (основний)
│   ├── MASTER_TASKS.md               # ГЛАВНИЙ ФАЙЛ - всі завдання та статус
│   ├── ARCHITECTURE.md               # Архітектура системи
│   ├── GUIDES.md                     # Практичні гайди
│   ├── NAVIGATION.md                 # Швидка навігація
│   └── details/                      # Детальні плани
├── analysis/                         # Аналіз та дослідження
├── newspaper/                        # Звіти та оновлення
│   ├── report/                       # Звіти про виконану роботу
│   ├── research/                     # Дослідження та аналіз
│   └── README.md                     # Головний файл документації
└── instruction_ai/                   # Інструкції для AI
    ├── README.md                     # Огляд інструкцій
    ├── AI_CORE_INSTRUCTIONS.md       # Основні інструкції (цей файл)
    ├── MVP_COMPLIANCE_INSTRUCTIONS.md # MVP логіка та обмеження
    ├── FILE_MANAGEMENT.md            # Управління файлами
    ├── WORKFLOW_PROCESS.md           # Робочий процес
    └── COMPLIANCE_CHECKLIST.md       # Чекліст відповідності
```

---

## 🔄 **Робочий процес**

### **Перед початком роботи:**
1. **Ознайомитися з завданнями** в `docs/planning/MASTER_TASKS.md`
2. **Перевірити MVP логіку** в `docs/instruction_ai/MVP_COMPLIANCE_INSTRUCTIONS.md`
3. **Перевірити поточний стан** проекту
4. **Ознайомитися з архітектурою** в `docs/planning/ARCHITECTURE.md`
5. **Перевірити існуючі файли** в newspaper

### **Під час роботи:**
1. **Дотримуватися принципів** документації
2. **Використовувати скрипти** для створення файлів
3. **Тестувати після кожної зміни**
4. **Документувати зміни**

### **Після завершення:**
1. **Запустити всі тести**
2. **Перевірити структуру проекту**
3. **Оновити версію**
4. **Зробити коміт та пуш**
5. **Створити звіт** (тільки за запитом користувача)

---

## 🚨 **Критичні заборони**

### **НЕ робити:**
- ❌ Створювати звіти автоматично після завершення завдань
- ❌ Створювати звіти без прямого запиту користувача
- ❌ Створювати звіти "для документації" без запиту
- ❌ Створювати файли в newspaper вручну через `edit_file`
- ❌ Ігнорувати скрипти для управління ID
- ❌ Пропускати тестування після змін
- ❌ Забувати оновлювати версію та комітити зміни

### **ОБОВ'ЯЗКОВО:**
- ✅ Використовувати скрипти для newspaper файлів
- ✅ Тестувати після змін
- ✅ Оновлювати версію та комітити
- ✅ Документувати зміни
- ✅ Дотримуватися принципів безпеки

---

## 📚 **Корисні посилання**

### **Основні документи:**
- **[MASTER_TASKS.md](../planning/MASTER_TASKS.md)** - Головний файл з завданнями
- **[PROJECT_OVERVIEW.md](../planning/PROJECT_OVERVIEW.md)** - Огляд проекту
- **[ARCHITECTURE.md](../planning/ARCHITECTURE.md)** - Архітектура системи

### **Інструкції:**
- **[FILE_MANAGEMENT.md](FILE_MANAGEMENT.md)** - Управління файлами
- **[WORKFLOW_PROCESS.md](WORKFLOW_PROCESS.md)** - Робочий процес
- **[COMPLIANCE_CHECKLIST.md](COMPLIANCE_CHECKLIST.md)** - Чекліст відповідності

### **Скрипти:**
- **[tools/scripts/project/manage.sh](../../tools/scripts/project/manage.sh)** - Управління проектом
- **[tools/scripts/documentation/create_newspaper_file.sh](../../tools/scripts/documentation/create_newspaper_file.sh)** - Створення файлів
- **[tools/scripts/testing/run_tests.sh](../../tools/scripts/testing/run_tests.sh)** - Запуск тестів

---

**Версія**: 1.0.0  
**Дата**: 2024-12-19  
**Статус**: Активний 