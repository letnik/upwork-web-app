# 🚀 CI/CD Pipeline Documentation

> **Автоматичне тестування та розгортання проекту**

---

## 📋 **Огляд**

CI/CD pipeline автоматично виконує всі тести при кожному push/PR та забезпечує якість коду.

---

## 🔄 **Тригери запуску**

### **Автоматичний запуск:**
- **Push** в `main` або `develop` гілки
- **Pull Request** в `main` або `develop` гілки

### **Ручний запуск:**
- Через GitHub Actions UI
- Через GitHub CLI

---

## 🧪 **Jobs (Завдання)**

### **1. Backend Tests** 🐍
**Призначення**: Тестування Python/FastAPI коду
**Сервіси**: PostgreSQL, Redis
**Кроки**:
- Встановлення Python 3.11
- Встановлення залежностей
- Запуск pytest з покриттям
- Завантаження результатів в Codecov

### **2. Frontend Tests** ⚛️
**Призначення**: Тестування React/TypeScript коду
**Кроки**:
- Встановлення Node.js 18
- Встановлення npm залежностей
- Запуск Jest тестів з покриттям
- Завантаження результатів в Codecov

### **3. Security Tests** 🔒
**Призначення**: Сканування безпеки коду
**Інструменти**: Bandit, Safety
**Кроки**:
- Сканування Python коду на вразливості
- Перевірка залежностей на безпеку
- Генерація звітів

### **4. Docker Tests** 🐳
**Призначення**: Тестування Docker образів
**Кроки**:
- Збірка всіх Docker образів
- Тестування контейнерів
- Перевірка health endpoints

### **5. Integration Tests** 🔗
**Призначення**: Тестування взаємодії сервісів
**Залежності**: Backend Tests, Frontend Tests
**Кроки**:
- Запуск всіх сервісів через docker-compose
- Виконання integration тестів
- Очищення ресурсів

### **6. Performance Tests** ⚡
**Призначення**: Тестування продуктивності
**Залежності**: Backend Tests
**Інструменти**: Locust
**Кроки**:
- Запуск backend сервісів
- Load тестування
- Аналіз результатів

### **7. E2E Tests** 🔄
**Призначення**: End-to-end тестування
**Залежності**: Backend Tests, Frontend Tests
**Інструменти**: Playwright
**Кроки**:
- Запуск всіх сервісів
- Виконання браузерних тестів
- Генерація звітів

### **8. Test Report** 📊
**Призначення**: Збірка результатів
**Залежності**: Всі тести
**Кроки**:
- Генерація звіту
- Відправка сповіщень при помилках

---

## 📊 **Метрики та звіти**

### **Покриття коду:**
- **Backend**: ~98.4% (61/62 тестів)
- **Frontend**: ~96% (22 тести)
- **Security**: 100% (security headers)

### **Типи звітів:**
- **Coverage reports** (XML, HTML)
- **Security reports** (JSON)
- **E2E reports** (HTML)
- **Performance reports** (CSV)

---

## ⚙️ **Налаштування**

### **Environment Variables:**
```yaml
# .github/workflows/test.yml
env:
  POSTGRES_PASSWORD: postgres
  POSTGRES_DB: test_db
  REDIS_URL: redis://localhost:6379
```

### **Secrets (потрібно налаштувати):**
- `CODECOV_TOKEN` - для завантаження покриття
- `DOCKER_USERNAME` - для Docker registry
- `DOCKER_PASSWORD` - для Docker registry

---

## 🚨 **Сповіщення**

### **При успіху:**
- Звіт в GitHub Actions
- Завантаження артефактів
- Оновлення метрик

### **При помилці:**
- Детальний звіт про помилки
- Список невдалих тестів
- Рекомендації для виправлення

---

## 🔧 **Локальне тестування**

### **Backend:**
```bash
cd app/backend
pytest tests/ -v --cov=. --cov-report=html
```

### **Frontend:**
```bash
cd app/frontend
npm test -- --coverage --watchAll=false
```

### **Docker:**
```bash
cd app/backend
docker-compose up -d
curl http://localhost:8000/health
```

---

## 📈 **Моніторинг**

### **GitHub Actions:**
- Статус кожного job
- Час виконання
- Використання ресурсів

### **Codecov:**
- Покриття коду в часі
- Тренди покриття
- Детальні звіти

### **Security:**
- Сканування вразливостей
- Оновлення залежностей
- Compliance звіти

---

## 🎯 **Плани розвитку**

### **Пріоритет 1:**
- [ ] Додати автоматичне розгортання
- [ ] Інтеграція з Slack/Discord
- [ ] Кешування залежностей

### **Пріоритет 2:**
- [ ] Додати staging environment
- [ ] Автоматичне створення release
- [ ] Rollback механізми

### **Пріоритет 3:**
- [ ] Додати canary deployments
- [ ] A/B тестування
- [ ] Blue-green deployments

---

## 📚 **Корисні посилання**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.io/)
- [Playwright CI/CD](https://playwright.dev/docs/ci)
- [Locust Documentation](https://docs.locust.io/)

---

**Останнє оновлення**: 2025-01-30  
**Версія**: v1.0.0  
**Статус**: Активна розробка 