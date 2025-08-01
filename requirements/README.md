# Централізована система управління залежностями

## 📋 **Огляд**

Ця папка містить централізовану систему управління залежностями для проекту Upwork AI Assistant. Система розділена на логічні компоненти для спрощення підтримки та усунення дублікатів.

## 🏗️ **Структура**

```
requirements/
├── base.txt                    # Базові залежності для всіх сервісів
├── api-gateway.txt            # Специфічні для API Gateway
├── ai-service.txt             # Специфічні для AI Service
├── auth-service.txt           # Специфічні для Auth Service
├── analytics-service.txt      # Специфічні для Analytics Service
├── notification-service.txt   # Специфічні для Notification Service
├── upwork-service.txt         # Специфічні для Upwork Service
├── dev.txt                    # Development залежності
├── test.txt                   # Test залежності
├── prod.txt                   # Production залежності
└── README.md                  # Ця документація
```

## 📦 **Файли залежностей**

### **base.txt**
Спільні залежності для всіх мікросервісів:
- FastAPI та Uvicorn
- HTTP клієнти (requests, httpx)
- Налаштування (python-dotenv, pydantic)
- Логування (loguru)
- База даних (SQLAlchemy, PostgreSQL, Redis)
- Безпека (PyJWT)
- Тестування (pytest)

### **service-specific.txt**
Унікальні залежності для кожного сервісу:

- **api-gateway.txt**: Немає додаткових залежностей
- **ai-service.txt**: OpenAI, Anthropic
- **auth-service.txt**: bcrypt, cryptography, pyotp
- **analytics-service.txt**: pandas, numpy, matplotlib, plotly
- **notification-service.txt**: aiosmtplib, email-validator, python-telegram-bot
- **upwork-service.txt**: Немає додаткових залежностей

### **Environment-specific файли**

- **dev.txt**: Development інструменти (black, flake8, mypy, pre-commit)
- **test.txt**: Додаткові тестові залежності (pytest-cov, factory-boy, locust)
- **prod.txt**: Production залежності (prometheus-client, structlog, healthcheck)

## 🚀 **Використання**

### **Встановлення залежностей**

```bash
# Встановлення всіх залежностей
./tools/scripts/dependencies/install.sh

# Встановлення для конкретного сервісу
./tools/scripts/dependencies/install.sh auth-service

# Встановлення для конкретного середовища
./tools/scripts/dependencies/install.sh all dev
./tools/scripts/dependencies/install.sh all test
./tools/scripts/dependencies/install.sh all prod
```

### **Аудит залежностей**

```bash
# Аудит всіх залежностей
./tools/scripts/dependencies/audit.sh

# Аудит конкретного сервісу
./tools/scripts/dependencies/audit.sh auth-service
```

### **Ручне встановлення**

```bash
# Базові залежності
pip install -r requirements/base.txt

# Специфічні залежності сервісу
pip install -r requirements/auth-service.txt

# Environment-specific залежності
pip install -r requirements/dev.txt
```

## 🔧 **Docker інтеграція**

### **Оновлений Dockerfile**

```dockerfile
# Копіюємо централізовані файли залежностей
COPY ../../requirements/base.txt requirements/
COPY ../../requirements/service-name.txt requirements/

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/service-name.txt
```

### **Переваги нової системи**

1. **Усунення дублікатів** - кожна залежність визначена один раз
2. **Спрощення підтримки** - централізоване управління версіями
3. **Покращення безпеки** - автоматичний аудит вразливостей
4. **Швидше встановлення** - менше дублікатів для завантаження
5. **Кращий контроль** - чітке розділення за призначенням

## 📊 **Статистика**

### **До централізації:**
- 6 окремих requirements.txt файлів
- 8 дублікатів залежностей
- 96 рядків дублювання
- Складність оновлення версій

### **Після централізації:**
- 1 базовий файл + 6 специфічних
- 0 дублікатів
- 100% унікальність
- Просте оновлення версій

## 🛠️ **Скрипти автоматизації**

### **install.sh**
- Встановлення залежностей для сервісів
- Підтримка різних середовищ
- Валідація аргументів
- Кольоровий вивід

### **audit.sh**
- Перевірка безпеки залежностей
- Виявлення дублікатів
- Перевірка застарілих версій
- Інтеграція з pip-audit

## 🔄 **Оновлення залежностей**

### **Додавання нової залежності**

1. **Базова залежність** (для всіх сервісів):
   ```bash
   echo "new-package==1.0.0" >> requirements/base.txt
   ```

2. **Специфічна залежність** (для конкретного сервісу):
   ```bash
   echo "service-specific-package==1.0.0" >> requirements/service-name.txt
   ```

3. **Environment-specific залежність**:
   ```bash
   echo "dev-tool==1.0.0" >> requirements/dev.txt
   ```

### **Оновлення версії**

1. Знайдіть файл з залежністю
2. Оновіть версію
3. Запустіть аудит: `./tools/scripts/dependencies/audit.sh`
4. Протестуйте зміни

## 🚨 **Важливі нотатки**

1. **Завжди використовуйте точні версії** (== замість >=)
2. **Тестуйте зміни** перед комітом
3. **Запускайте аудит** регулярно
4. **Документуйте зміни** в changelog
5. **Не додавайте залежності без потреби**

## 📈 **Майбутні покращення**

- [ ] Автоматичне оновлення версій
- [ ] Інтеграція з CI/CD
- [ ] Dependency scanning в реальному часі
- [ ] License compliance checking
- [ ] Performance impact analysis

---

**Версія**: v1.0.0  
**Дата**: 2024-12-19  
**Статус**: Активна 

## 🏛️ Політика централізації залежностей

- **Всі Python залежності** мають бути визначені тільки в папці `requirements/`.
- **Заборонено** requirements.txt в сервісах! (тільки централізовані файли)
- **Dockerfile** кожного сервісу має використовувати тільки централізовані файли (див. приклади нижче).
- **Оновлення залежностей** — тільки через редагування відповідного requirements/*.txt та запуск скриптів.
- **Аудит безпеки** — регулярно запускати `./tools/scripts/dependencies/audit.sh`.
- **Чекліст для ревʼю:**
  - [ ] Всі залежності централізовано
  - [ ] Dockerfile не містить requirements.txt
  - [ ] Всі зміни задокументовані
  - [ ] README не дублюються

## 📚 Додаткові інструкції
- [Основні інструкції для AI](../docs/instruction_ai/AI_CORE_INSTRUCTIONS.md)
- [Управління файлами](../docs/instruction_ai/FILE_MANAGEMENT.md)
- [Робочий процес](../docs/instruction_ai/WORKFLOW_PROCESS.md)
- [Чекліст відповідності](../docs/instruction_ai/COMPLIANCE_CHECKLIST.md) 