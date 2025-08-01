# 🌐 End-to-End Tests

> **Тестування повних сценаріїв користувача з реальним браузером**

---

## 📋 **Огляд**

E2E тести симулюють реальну поведінку користувача:
- Авторизація та реєстрація
- Пошук роботи на Upwork
- Створення пропозицій
- Робота з analytics dashboard
- Mobile адаптивність

---

## 🏗️ **Архітектура**

```
tests/e2e/
├── auth_flow/                     # Авторизація та реєстрація
│   ├── test_login_flow.py        # Процес входу
│   ├── test_register_flow.py     # Процес реєстрації
│   ├── test_password_reset.py    # Скидання паролю
│   └── test_oauth_flow.py        # OAuth авторизація
├── job_search/                    # Пошук роботи
│   ├── test_job_search.py        # Пошук вакансій
│   ├── test_job_filtering.py     # Фільтрація результатів
│   ├── test_job_details.py       # Деталі вакансії
│   └── test_job_save.py          # Збереження вакансій
├── proposal_creation/             # Створення пропозицій
│   ├── test_proposal_form.py     # Форма пропозиції
│   ├── test_proposal_submit.py   # Відправка пропозиції
│   ├── test_proposal_edit.py     # Редагування пропозиції
│   └── test_proposal_tracking.py # Відстеження статусу
├── analytics_dashboard/           # Analytics dashboard
│   ├── test_dashboard_load.py    # Завантаження dashboard
│   ├── test_charts_interaction.py # Взаємодія з графіками
│   ├── test_data_export.py       # Експорт даних
│   └── test_filters.py           # Фільтри dashboard
├── admin_panel/                   # Admin функціональність
│   ├── test_user_management.py   # Управління користувачами
│   ├── test_system_settings.py   # Налаштування системи
│   └── test_logs_viewing.py      # Перегляд логів
└── mobile_responsive/             # Mobile адаптивність
    ├── test_mobile_navigation.py # Mobile навігація
    ├── test_mobile_forms.py      # Mobile форми
    └── test_mobile_charts.py     # Mobile графіки
```

---

## 🚀 **Запуск тестів**

```bash
# Всі E2E тести
./tools/scripts/testing/run_tests.sh e2e

# Конкретні E2E тести
pytest tests/e2e/auth_flow/ -v
pytest tests/e2e/job_search/ -v
pytest tests/e2e/proposal_creation/ -v

# З різними браузерами
pytest tests/e2e/ --browser=chrome
pytest tests/e2e/ --browser=firefox
pytest tests/e2e/ --browser=safari
```

---

## 📊 **Покриття**

### **Планується покриття:**
- **Auth Flow**: 95%
- **Job Search**: 90%
- **Proposal Creation**: 85%
- **Analytics Dashboard**: 80%
- **Admin Panel**: 75%
- **Mobile Responsive**: 90%

---

## 🔧 **Налаштування**

### **Playwright конфігурація:**
```python
# tests/e2e/conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
```

### **Тестове середовище:**
```python
# tests/e2e/config.py
TEST_CONFIG = {
    "base_url": "http://localhost:3000",
    "api_url": "http://localhost:8000",
    "test_user": {
        "email": "test@example.com",
        "password": "test_password"
    },
    "timeout": 30000
}
```

---

## 📋 **Чекліст**

### **Перед створенням E2E тесту:**
- [ ] Визначити користувацький сценарій
- [ ] Створити тестові дані
- [ ] Налаштувати тестове середовище
- [ ] Визначити очікувані результати
- [ ] Планувати cleanup після тесту

### **Під час написання тесту:**
- [ ] Симулювати реальну поведінку користувача
- [ ] Використовувати описові селектори
- [ ] Додати очікування для асинхронних операцій
- [ ] Обробляти помилки та таймаути
- [ ] Документувати кроки тесту

### **Після написання тесту:**
- [ ] Запустити тест в різних браузерах
- [ ] Перевірити швидкість виконання
- [ ] Додати скріншоти при помилках
- [ ] Документувати тест
- [ ] Додати до CI/CD pipeline

---

## 🎯 **Приклади тестів**

### **Login Flow:**
```python
def test_login_flow(page):
    """Тест процесу входу користувача"""
    # Відкриваємо сторінку входу
    page.goto(f"{TEST_CONFIG['base_url']}/login")
    
    # Заповнюємо форму
    page.fill('[data-testid="email-input"]', TEST_CONFIG['test_user']['email'])
    page.fill('[data-testid="password-input"]', TEST_CONFIG['test_user']['password'])
    
    # Натискаємо кнопку входу
    page.click('[data-testid="login-button"]')
    
    # Очікуємо перенаправлення на dashboard
    page.wait_for_url(f"{TEST_CONFIG['base_url']}/dashboard")
    
    # Перевіряємо що користувач авторизований
    assert page.locator('[data-testid="user-menu"]').is_visible()
```

### **Job Search:**
```python
def test_job_search_flow(page):
    """Тест пошуку роботи"""
    # Авторизуємося
    login_user(page)
    
    # Переходимо до пошуку роботи
    page.goto(f"{TEST_CONFIG['base_url']}/jobs")
    
    # Вводимо пошуковий запит
    page.fill('[data-testid="search-input"]', "React developer")
    page.click('[data-testid="search-button"]')
    
    # Очікуємо результатів
    page.wait_for_selector('[data-testid="job-card"]')
    
    # Перевіряємо що є результати
    job_cards = page.locator('[data-testid="job-card"]')
    assert job_cards.count() > 0
```

---

## 🚨 **Важливі правила**

### **✅ Дозволено:**
- Використання реального браузера
- Симуляція користувацької поведінки
- Тестування UI/UX елементів
- Перевірка responsive дизайну
- Тестування accessibility

### **❌ Заборонено:**
- Реальні API виклики до production
- Зміна production даних
- Повільні тести (> 30 секунд)
- Залежність від стану інших тестів
- Тестування в production середовищі

---

## 📱 **Mobile тестування**

### **Responsive тести:**
```python
def test_mobile_navigation(page):
    """Тест mobile навігації"""
    # Встановлюємо mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    
    # Перевіряємо mobile меню
    page.click('[data-testid="mobile-menu-button"]')
    assert page.locator('[data-testid="mobile-menu"]').is_visible()
```

---

**Статус**: 🚧 В розробці  
**Пріоритет**: Високий  
**Останнє оновлення**: 2024-12-19 