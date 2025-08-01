# Інструкції по системі логування для AI

## Огляд

Цей документ містить інструкції для AI щодо роботи з розширеною системою логування в проекті. Система логування була розширена для максимально ефективного відстеження та фіксації багів.

## Архітектура логування

### Основні компоненти

1. **StructuredLogger** (`shared/config/logging.py`)
   - Розширений логер з структурованими логами
   - JSON форматування з контекстною інформацією
   - Автоматичне додавання timestamp, service_name, environment

2. **LoggingMiddleware** (`shared/utils/logging_middleware.py`)
   - Автоматичне логування HTTP запитів
   - Контекстне відстеження (request_id, user_id, session_id)
   - Логування подій безпеки та операцій з БД

3. **Декоратори** (`shared/utils/logging_decorators.py`)
   - Автоматичне логування функцій, продуктивності, API викликів
   - Логування подій безпеки та винятків
   - Підтримка асинхронних функцій

4. **LogAnalyzer** (`shared/utils/log_analyzer.py`)
   - Аналіз логів та моніторинг в реальному часі
   - Пошук повільних операцій та частих помилок
   - Експорт зведень в JSON

5. **TestLogger** (`shared/config/logging.py`)
   - Логування тестів з контекстом
   - Автоматичне відстеження результатів тестів

6. **ELK Stack** (`docker/elk/`)
   - Elasticsearch для зберігання логів
   - Logstash для обробки логів
   - Kibana для візуалізації
   - Filebeat для збору логів

7. **AlertingSystem** (`shared/utils/alerting_system.py`)
   - Розумні алерти з автоматичними сповіщеннями
   - Email, Slack, Telegram сповіщення
   - Налаштовувані правила алертів

8. **LogCleanupService** (`shared/utils/log_cleanup_service.py`)
   - Автоматичне очищення старих логів
   - Архівування з стисненням
   - Резервне копіювання

9. **PerformanceMetricsCollector** (`shared/utils/performance_metrics.py`)
   - Розширені метрики продуктивності
   - Системні метрики (CPU, пам'ять, диск)
   - Кастомні метрики

10. **SecureLogger** (`shared/utils/secure_logging.py`)
    - Безпечне логування з шифруванням
    - Маскування чутливих даних
    - Аудит доступу до логів

11. **CI/CD Integration** (`.github/workflows/log-analysis.yml`)
    - Автоматичний аналіз логів в pipeline
    - Перевірка безпеки та продуктивності
    - Коментування результатів в PR

### Типи логів

- **Основні логи** (`service.log`) - загальна інформація
- **Помилки** (`service_error.log`) - детальні помилки з traceback
- **Безпека** (`service_security.log`) - події безпеки
- **Продуктивність** (`service_performance.log`) - метрики продуктивності
- **API** (`service_api.log`) - HTTP запити
- **База даних** (`service_database.log`) - операції з БД
- **Тести** (`service_test.log`) - результати тестів (тільки в тестовому режимі)

## Інтеграція логування та тестів

### Єдина система логування

**Логи та тести ведуться в одному місці** через єдину систему логування:

```
logs/
├── service.log              # Основні логи сервісу
├── service_error.log        # Помилки сервісу
├── service_security.log     # Події безпеки
├── service_performance.log  # Продуктивність
├── service_api.log          # API запити
├── service_database.log     # Операції БД
├── archive/                 # Архівовані логи
├── backup/                  # Резервні копії
└── test/                    # Тестові логи
    ├── test-service.log     # Основні тестові логи
    ├── test-service_error.log # Помилки тестів
    ├── test-service_test.log  # Результати тестів
    └── ...
```

### Автоматичне визначення тестового режиму

Система автоматично визначає тестовий режим через:
- Наявність `pytest` в `sys.modules`
- Змінну середовища `PYTEST_CURRENT_TEST`
- Параметр `test_mode=True`

## Інструкції для AI

### 1. При створенні нового сервісу

**Обов'язково додати:**
```python
from shared.config.logging import setup_logging, get_logger
from shared.utils.logging_middleware import LoggingMiddleware
from shared.utils.enhanced_logging_integration import EnhancedLoggingIntegration

# Налаштування логування
setup_logging(service_name="new-service")

# Отримання логера
logger = get_logger("new-service")

# Додавання middleware
app.add_middleware(LoggingMiddleware)

# Ініціалізація розширеного логування
integration = EnhancedLoggingIntegration("new-service")
integration.setup_enhanced_logging()
```

### 2. При логуванні операцій

**Використовувати контекстну інформацію:**
```python
# ✅ Правильно
logger.info("Користувач створений", extra={
    "user_id": user.id,
    "email": user.email,
    "operation": "user_creation"
})

# ❌ Неправильно
logger.info("Користувач створений")
```

### 3. При створенні тестів

**Використовувати TestLogger:**
```python
def test_user_creation(test_logger):
    test_logger.info("Початок тесту створення користувача")
    
    # Тестова логіка
    user = create_user("test@example.com")
    
    test_logger.info("Користувач створений", extra={
        "user_id": user.id,
        "email": user.email
    })
    
    assert user.email == "test@example.com"
    test_logger.info("Тест пройшов успішно")
```

### 4. При створенні конфігурації тестів

**В conftest.py додати:**
```python
import pytest
from shared.config.logging import setup_logging

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Налаштування логування для тестів"""
    setup_logging(service_name="test-service", test_mode=True)

@pytest.fixture(autouse=True)
def test_logger(request):
    """Логер для кожного тесту"""
    from shared.config.logging import get_logger
    logger = get_logger("test")
    
    # Логування початку тесту
    logger.test(request.node.name, "STARTED")
    
    yield logger
    
    # Логування завершення тесту
    logger.test(request.node.name, "COMPLETED")
```

### 5. При роботі з чутливими даними

**Використовувати SecureLogger:**
```python
from shared.utils.secure_logging import get_secure_logger

secure_logger = get_secure_logger()

# Автоматичне маскування чутливих даних
secure_logger.info("User login", extra={
    "email": "user@example.com",
    "password": "secret123",  # Автоматично замаскується
    "token": "jwt-token-here"  # Автоматично зашифрується
})
```

### 6. При додаванні метрик продуктивності

**Використовувати PerformanceMetricsCollector:**
```python
from shared.utils.performance_metrics import performance_collector

# Додавання кастомної метрики
def get_active_users_count():
    return len(get_active_users())

performance_collector.add_custom_metric("active_users", get_active_users_count)
```

### 7. При налаштуванні алертів

**Додати нові правила алертів:**
```python
from shared.utils.alerting_system import alerting_system, AlertRule, AlertType, AlertSeverity

# Створення нового правила алерту
new_rule = AlertRule(
    name="Custom Alert",
    alert_type=AlertType.ERROR_THRESHOLD,
    severity=AlertSeverity.HIGH,
    condition=lambda logs: len([l for l in logs if l.get('level') == 'ERROR']) > 5,
    threshold=5,
    time_window_minutes=10,
    cooldown_minutes=30,
    notification_channels=["email", "slack"],
    description="Більше 5 помилок за 10 хвилин"
)

alerting_system.add_rule(new_rule)
```

### 8. При аналізі логів

**Використовувати LogAnalyzer:**
```python
from shared.utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")

# Комплексне зведення
summary = analyzer.get_comprehensive_summary(hours=24)

# Пошук повільних операцій
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)

# Пошук частих помилок
frequent_errors = analyzer.find_frequent_errors(min_count=5)
```

## Контекстна інформація

Кожен лог автоматично містить:

- **Timestamp** - точний час події
- **Service name** - назва сервісу
- **Environment** - середовище (development/production/test)
- **Module/function** - модуль та функція
- **Request ID** - унікальний ID запиту (для HTTP)
- **User ID** - ID користувача (якщо доступний)
- **Session ID** - ID сесії (якщо доступний)
- **Test context** - контекст тесту (в тестовому режимі)
- **test_name** - назва тесту
- **test_file** - файл тесту

## Продуктивність

Система логування забезпечує:

- **Асинхронне логування** - не блокує основний потік
- **Ротація логів** - автоматичне очищення старих файлів
- **Стиснення** - економія місця на диску
- **Фільтрація** - розділення логів по типах
- **Тестів (тривалість виконання)** - моніторинг продуктивності тестів

## Безпека

### Маскування чутливих даних

Автоматично маскуються:
- Email адреси
- IP адреси
- Кредитні карти
- Телефонні номери
- Паролі та токени
- UUID
- Соціальні номери

### Шифрування

- Чутливі дані шифруються перед збереженням
- Використовується Fernet шифрування
- Ключ шифрування налаштовується через змінну середовища

### Аудит доступу

- Всі спроби доступу до логів логуються
- Відстеження підозрілої активності
- Історія доступу зберігається

## Інтеграція в існуючий код

### Покращення існуючого логування

```python
# Було
logger.error(f"Помилка реєстрації користувача: {e}")

# Стало
logger.error("Помилка реєстрації користувача", extra={
    "error": str(e),
    "operation": "user_registration",
    "email": user_data.email
})
```

### Додавання middleware до сервісу

```python
from fastapi import FastAPI
from shared.utils.logging_middleware import LoggingMiddleware

app = FastAPI()
app.add_middleware(LoggingMiddleware)
```

### Інтеграція з тестами

```python
# conftest.py автоматично налаштовує логування для тестів
# Всі тести отримують test_logger fixture

def test_my_feature(test_logger):
    test_logger.info("Тест починається")
    # ... тест ...
    test_logger.info("Тест завершено")
```

## Моніторинг та аналіз

### Використання LogAnalyzer

```python
from shared.utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")

# Комплексне зведення
summary = analyzer.get_comprehensive_summary(hours=24)

# Пошук повільних операцій
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)

# Пошук частих помилок
frequent_errors = analyzer.find_frequent_errors(min_count=5)

# Експорт зведення
analyzer.export_summary_to_json("summary.json", hours=24)
```

### Моніторинг в реальному часі

```python
from shared.utils.log_analyzer import LogMonitor

monitor = LogMonitor("logs")

# Перевірка нових помилок
new_errors = monitor.check_new_errors()

# Перевірка повільних операцій
slow_ops = monitor.check_slow_operations(threshold_ms=1000.0)

# Перевірка подій безпеки
security_events = monitor.check_security_events()
```

### Аналіз тестових логів

```python
# Знайти всі тести що провалились
grep "FAILED" logs/test/test-service_test.log

# Знайти повільні тести
grep "duration_ms" logs/test/test-service_test.log | grep -E "[0-9]{4,}"

# Знайти помилки в тестах
grep "ERROR" logs/test/test-service_error.log
```

### Результати тестів

Система автоматично логує:
- Початок кожного тесту
- Результат тесту (PASSED/FAILED/SKIPPED)
- Тривалість виконання
- Помилки та винятки

### Провалених тестів

Автоматично відстежуються:
- Кількість провалених тестів
- Причини провалу
- Тривалість провалених тестів
- Патерни помилок

## Налаштування

### Змінні середовища

```bash
# Рівень логування
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Середовище
ENVIRONMENT=development  # development, production, test

# Назва сервісу
SERVICE_NAME=my-service

# Шифрування логів
LOG_ENCRYPTION_KEY=your-secret-key

# Алерти
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
ALERT_RECIPIENTS=admin@example.com,dev@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### Ротація логів

Логи автоматично ротуються з наступними налаштуваннями:

- **Основні логи**: 50MB, 90 днів
- **Помилки**: 20MB, 180 днів
- **Безпека**: 10MB, 365 днів
- **Продуктивність**: 20MB, 90 днів
- **API**: 30MB, 60 днів
- **База даних**: 20MB, 90 днів
- **Тести**: 10MB, 30 днів

## Найкращі практики для AI

### 1. При створенні нових сервісів

**Завжди додавати:**
- Імпорт та налаштування логування
- Middleware для HTTP запитів
- Ініціалізацію розширеного логування
- Тестове логування

### 2. При логуванні операцій

**Використовувати контекстну інформацію:**
```python
logger.info("Операція виконана", extra={
    "operation": "operation_name",
    "user_id": user.id,
    "duration_ms": duration,
    "result": "success"
})
```

### 3. При роботі з помилками

**Логувати деталі помилки:**
```python
try:
    operation()
except Exception as e:
    logger.error("Помилка операції", extra={
        "operation": "operation_name",
        "error_type": type(e).__name__,
        "error_details": str(e),
        "user_id": current_user.id if current_user else None
    })
    raise
```

### 4. При створенні тестів

**Використовувати TestLogger:**
```python
def test_feature(test_logger):
    test_logger.info("Початок тесту")
    # ... тест ...
    test_logger.info("Тест завершено")
```

### 5. При аналізі логів

**Використовувати LogAnalyzer:**
```python
analyzer = LogAnalyzer("logs")
summary = analyzer.get_comprehensive_summary(hours=24)
```

### 6. При роботі з чутливими даними

**Використовувати SecureLogger:**
```python
secure_logger = get_secure_logger()
secure_logger.info("Sensitive operation", extra={"password": "secret"})
```

### 7. При додаванні метрик

**Використовувати PerformanceMetricsCollector:**
```python
performance_collector.add_custom_metric("metric_name", metric_function)
```

### 8. При налаштуванні алертів

**Додавати нові правила:**
```python
alerting_system.add_rule(AlertRule(...))
```

### 9. При створенні документації

**Включати приклади логування:**
```python
# Приклад логування операції
logger.info("Операція виконана", extra={
    "operation": "example",
    "user_id": "123"
})
```

### 10. При аналізі проблем

**Використовувати LogAnalyzer для діагностики:**
```python
# Знайти повільні операції
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)

# Знайти части помилки
frequent_errors = analyzer.find_frequent_errors(min_count=5)
```

## Висновок

Система логування забезпечує:

- **Детальне відстеження** всіх операцій з контекстом
- **Швидку діагностику** проблем через структуровані логи
- **Автоматичне логування** через middleware та декоратори
- **Ефективний аналіз** логів через спеціальні інструменти
- **Масштабованість** через ротацію та стиснення
- **Єдину систему** для логування та тестування
- **Автоматичне визначення** тестового режиму
- **Централізовану конфігурацію** для всіх компонентів
- **ELK Stack** для централізованого аналізу
- **Розумні алерти** з автоматичними сповіщеннями
- **Автоматичне очищення** та архівування логів
- **Розширені метрики** продуктивності
- **Безпечне логування** з шифруванням
- **CI/CD інтеграцію** для автоматичного аналізу

**Логи та тести ведуться в одному місці** - це забезпечує консистентність та полегшує діагностику проблем як в розробці, так і в тестуванні.

Система готова до використання та подальшого розвитку з розширеними можливостями Phase 1-6.

## Ключові рекомендації для AI

### 1. **Моніторинг логерів**
**Регулярно перевіряти використання логерів:**
```python
# ✅ Правильно - використовувати нашу систему
from shared.config.logging import get_logger
logger = get_logger("module-name")

# ❌ Неправильно - використовувати стандартний logging
import logging
logger = logging.getLogger(__name__)
```

**Команди для перевірки:**
```bash
# Знайти файли що використовують стандартний logging
grep -r "import logging" app/backend/
grep -r "logging.getLogger" app/backend/

# Знайти файли що використовують нашу систему
grep -r "from shared.config.logging import" app/backend/
grep -r "get_logger" app/backend/

# Перевірка рівня логування
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\." {} \; | awk '{sum+=$1} END {print "Загальна кількість викликів logger: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\.info" {} \; | awk '{sum+=$1} END {print "INFO викликів: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\.error" {} \; | awk '{sum+=$1} END {print "ERROR викликів: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -l "extra=" {} \; | wc -l

# Перевірка структури логових файлів
ls -la logs/
ls -la logs/test/
wc -l logs/test/test-service_main.log logs/test/test-service_error.log logs/test/test-service_test.log

# Перевірка результатів тестів
grep -c "PASSED\|FAILED" logs/test/test-service_test.log
grep -c "PASSED" logs/test/test-service_test.log
grep -c "FAILED" logs/test/test-service_test.log

# Перегляд зразків логів
head -5 logs/test/test-service_main.log
head -5 logs/test/test-service_error.log
```

### 2. **Оновлення документації**
**При додаванні нових компонентів логування:**
- Оновити `docs/planning/details/guides/development/logging_system_guide.md`
- Оновити `docs/instruction_ai/LOGGING_SYSTEM_INSTRUCTIONS.md`
- Створити звіт в `docs/newspaper/report/`
- Додати приклади використання
- Оновити список компонентів та можливостей

### 3. **Тестування з TestLogger**
**Використовувати TestLogger в усіх тестах:**
```python
def test_feature(test_logger):
    """Тест з автоматичним логуванням"""
    test_logger.info("Початок тесту")
    
    # Тестова логіка
    result = some_operation()
    
    test_logger.info("Операція виконана", extra={
        "result": result,
        "expected": expected_value
    })
    
    assert result == expected_value
    test_logger.info("Тест пройшов успішно")

# Використовувати спеціалізовані логери
def test_performance(performance_logger):
    """Тест продуктивності"""
    with PerformanceLogger(performance_logger, "test_operation"):
        # Тестова операція
        pass

def test_security(security_logger):
    """Тест безпеки"""
    security_logger.security("test_event", {
        "ip_address": "192.168.1.1"
    })
```

### 4. **Регулярний аналіз логів**
**Використовувати LogAnalyzer для регулярного аналізу:**
```python
from shared.utils.log_analyzer import LogAnalyzer

# Щоденний аналіз
analyzer = LogAnalyzer("logs")
daily_summary = analyzer.get_comprehensive_summary(hours=24)

# Пошук проблем
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)
frequent_errors = analyzer.find_frequent_errors(min_count=5)
security_events = analyzer.get_security_summary(hours=24)

# Експорт зведення
analyzer.export_summary_to_json("daily_summary.json", hours=24)
```

**Автоматизація аналізу:**
```python
# Скрипт для щоденного аналізу
def daily_log_analysis():
    analyzer = LogAnalyzer("logs")
    
    # Отримання зведення
    summary = analyzer.get_comprehensive_summary(hours=24)
    
    # Перевірка критичних показників
    if summary['errors']['total'] > 100:
        send_alert("Високий рівень помилок")
    
    if summary['performance']['avg_response_time'] > 2000:
        send_alert("Повільна робота системи")
    
    # Збереження зведення
    analyzer.export_summary_to_json(f"summary_{datetime.now().strftime('%Y%m%d')}.json")

# Команди для швидкої перевірки логів
```bash
# Аналіз тестових логів
python3 -c "from shared.utils.log_analyzer import LogAnalyzer; analyzer = LogAnalyzer('logs/test'); summary = analyzer.get_comprehensive_summary(hours=8760); print('=== АНАЛІЗ ТЕСТОВИХ ЛОГІВ ==='); print(f'Помилки: {summary[\"errors\"]}'); print(f'Продуктивність: {summary[\"performance\"]}'); print(f'API: {summary[\"api\"]}'); print(f'Безпека: {summary[\"security\"]}'); print(f'База даних: {summary[\"database\"]}')"

# Аналіз основних логів
python3 -c "from shared.utils.log_analyzer import LogAnalyzer; analyzer = LogAnalyzer('logs'); summary = analyzer.get_comprehensive_summary(hours=8760); print('=== АНАЛІЗ ОСНОВНИХ ЛОГІВ ==='); print(f'Помилки: {summary[\"errors\"]}'); print(f'Продуктивність: {summary[\"performance\"]}'); print(f'API: {summary[\"api\"]}'); print(f'Безпека: {summary[\"security\"]}'); print(f'База даних: {summary[\"database\"]}')"

# Пошук частих помилок
python3 -c "from shared.utils.log_analyzer import LogAnalyzer; analyzer = LogAnalyzer('logs/test'); frequent_errors = analyzer.find_frequent_errors(min_count=3); print('=== ЧАСТІ ПОМИЛКИ ==='); print(f'Знайдено {len(frequent_errors)} типів частих помилок:'); print(frequent_errors)"

# Тестування парсингу логів
python3 -c "from shared.utils.log_analyzer import LogAnalyzer; analyzer = LogAnalyzer('logs/test'); print('=== ТЕСТ ПАРСИНГУ ==='); sample_line = '2025-07-31 17:52:15.445 | INFO | shared.config.logging:info:82 | {\"message\": \"Тестове середовище налаштовано\", \"context\": {\"timestamp\": \"2025-07-31T14:52:15.445276\", \"service\": \"upwork-service\", \"environment\": \"development\", \"module\": \"test-setup\"}}'; parsed = analyzer.parse_log_line(sample_line); print(f'Рівень: {parsed.get(\"level\")}'); print(f'Повідомлення: {parsed.get(\"message\")[:50]}...'); print(f'Модуль: {parsed.get(\"module\")}')"

# Тестування моніторингу
python3 -c "from shared.utils.log_analyzer import LogMonitor; monitor = LogMonitor('logs/test'); print('=== ТЕСТ МОНІТОРИНГУ ==='); new_errors = monitor.check_new_errors(); slow_ops = monitor.check_slow_operations(threshold_ms=1000.0); security_events = monitor.check_security_events(); print(f'Нові помилки: {len(new_errors)}'); print(f'Повільні операції: {len(slow_ops)}'); print(f'Події безпеки: {len(security_events)}')"
```

### 5. **Моніторинг показників якості логування**
**Регулярно перевіряти показники якості:**
```bash
# Перевірка рівня логування
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\." {} \; | awk '{sum+=$1} END {print "Загальна кількість викликів logger: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\.info" {} \; | awk '{sum+=$1} END {print "INFO викликів: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -c "logger\.error" {} \; | awk '{sum+=$1} END {print "ERROR викликів: " sum}'
find . -name "*.py" -not -path "*/venv/*" -exec grep -l "extra=" {} \; | wc -l

# Перевірка структури логових файлів
ls -la logs/
ls -la logs/test/
wc -l logs/test/test-service_main.log logs/test/test-service_error.log logs/test/test-service_test.log

# Перевірка результатів тестів
grep -c "PASSED\|FAILED" logs/test/test-service_test.log
grep -c "PASSED" logs/test/test-service_test.log
grep -c "FAILED" logs/test/test-service_test.log

# Перегляд зразків логів
head -5 logs/test/test-service_main.log
head -5 logs/test/test-service_error.log
```

**Мінімальні показники для проекту:**
- **Загальна кількість викликів logger:** > 400
- **INFO викликів:** > 150
- **ERROR викликів:** > 150
- **Файлів з контекстним логуванням (extra=):** > 20
- **Файлів з нашою системою логування:** > 35

### 6. **Розширення контекстного логування**
**Постійно додавати контекстну інформацію:**
```python
# ✅ Правильно - з контекстом
logger.info("Користувач створений", extra={
    "user_id": user.id,
    "email": user.email,
    "operation": "user_creation",
    "duration_ms": duration,
    "source": "api"
})

# ❌ Неправильно - без контексту
logger.info("Користувач створений")
```

**Області для розширення контексту:**
- API виклики (response_time, status_code, user_id)
- Операції з БД (query_type, table, rows_affected)
- Авторизація (auth_method, user_id, ip_address)
- Помилки (error_type, stack_trace, context)
- Продуктивність (duration_ms, memory_usage, cpu_usage)

### 7. **Налаштування алертів для критичних подій**
**Створювати алерти для важливих подій:**
```python
from shared.utils.alerting_system import alerting_system, AlertRule, AlertType, AlertSeverity

# Алерт на високий рівень помилок
error_alert = AlertRule(
    name="High Error Rate",
    alert_type=AlertType.ERROR_THRESHOLD,
    severity=AlertSeverity.HIGH,
    condition=lambda logs: len([l for l in logs if l.get('level') == 'ERROR']) > 10,
    threshold=10,
    time_window_minutes=5,
    notification_channels=["email", "slack"],
    description="Більше 10 помилок за 5 хвилин"
)

# Алерт на повільні операції
performance_alert = AlertRule(
    name="Slow Operations",
    alert_type=AlertType.PERFORMANCE_THRESHOLD,
    severity=AlertSeverity.MEDIUM,
    condition=lambda logs: any(l.get('duration_ms', 0) > 5000 for l in logs),
    threshold=5000,
    time_window_minutes=10,
    notification_channels=["slack"],
    description="Операції повільніше 5 секунд"
)

# Алерт на події безпеки
security_alert = AlertRule(
    name="Security Events",
    alert_type=AlertType.SECURITY_EVENT,
    severity=AlertSeverity.CRITICAL,
    condition=lambda logs: any('security' in l.get('message', '').lower() for l in logs),
    time_window_minutes=1,
    notification_channels=["email", "slack", "telegram"],
    description="Виявлені події безпеки"
)

alerting_system.add_rule(error_alert)
alerting_system.add_rule(performance_alert)
alerting_system.add_rule(security_alert)
```

**Типи алертів для налаштування:**
- **Помилки:** високий рівень помилок, критичні помилки
- **Продуктивність:** повільні операції, високе навантаження
- **Безпека:** підозріла активність, спроби взлому
- **Система:** недоступність сервісів, проблеми з БД
- **Тести:** провалені тести, повільні тести

### 8. **Перевірка цілісності системи**
**Регулярно перевіряти цілісність логування:**
```python
def check_logging_integrity():
    """Перевірка цілісності системи логування"""
    
    # Перевірка наявності всіх компонентів
    required_files = [
        "shared/config/logging.py",
        "shared/config/logging_config.py",
        "shared/utils/logging_middleware.py",
        "shared/utils/logging_decorators.py",
        "shared/utils/log_analyzer.py",
        "shared/utils/alerting_system.py",
        "shared/utils/log_cleanup_service.py",
        "shared/utils/performance_metrics.py",
        "shared/utils/secure_logging.py",
        "shared/utils/async_logging.py",
        "shared/utils/metrics_cache.py",
        "shared/utils/advanced_alerting.py",
        "shared/utils/correlation_analysis.py",
        "shared/utils/auto_diagnostics.py",
        "shared/utils/load_prediction.py",
        "shared/utils/ml_log_analysis.py",
        "shared/utils/microservice_logging.py",
        "shared/utils/advanced_visualizations.py",
        "shared/utils/basic_ml_analysis.py",
        "shared/utils/basic_microservice_logging.py",
        "shared/utils/basic_visualizations.py"
    ]
    
    # Перевірка використання правильної системи логування
    # Перевірка наявності тестових файлів
    # Перевірка документації
```

### 9. **Найкращі практики для AI**
**При роботі з логуванням завжди:**
- Використовувати `get_logger()` замість `logging.getLogger()`
- Додавати контекстну інформацію в `extra`
- Використовувати TestLogger в тестах
- Регулярно аналізувати логи через LogAnalyzer
- Моніторити показники якості логування
- Розширювати контекстне логування
- Налаштовувати алерти для критичних подій
- Оновлювати документацію при змінах
- Перевіряти цілісність системи
- Використовувати декоратори для автоматичного логування
- Логувати важливі операції з метриками продуктивності
- Використовувати SecureLogger для чутливих даних

### 10. **Оцінка достатності логування**
**Регулярно оцінювати рівень логування:**

**Мінімальні показники для проекту:**
- **Загальна кількість викликів logger:** > 400 (поточний: 433 ✅)
- **INFO викликів:** > 150 (поточний: 177 ✅)
- **ERROR викликів:** > 150 (поточний: 184 ✅)
- **Файлів з контекстним логуванням (extra=):** > 20 (поточний: 22 ✅)
- **Файлів з нашою системою логування:** > 35 (поточний: 38 ✅)

**Критичні області для логування:**
- ✅ Авторизація та аутентифікація
- ✅ API виклики та відповіді
- ✅ Операції з базою даних
- ✅ Фінансові операції
- ✅ Помилки та винятки
- ✅ Тестове виконання
- ✅ Продуктивність операцій
- ✅ Події безпеки

### 11. **Логування для тестів - найкращі практики**
**Так, логування для тестів є стандартною практикою:**

**Переваги логування тестів:**
- **Діагностика проблем** - швидке знаходження причин провалу тестів
- **Відстеження продуктивності** - моніторинг часу виконання тестів
- **Аудит змін** - історія змін в поведінці системи
- **Документування** - автоматична документація роботи системи
- **CI/CD інтеграція** - автоматичний аналіз результатів тестів

**Наші показники тестового логування:**
- ✅ **2,282 рядки логів** в тестовому файлі
- ✅ **398 PASSED тестів** з детальним логуванням
- ✅ **18 тестових помилок** з повним контекстом
- ✅ **Автоматичне логування** початку/завершення тестів
- ✅ **Тривалість виконання** кожного тесту
- ✅ **Контекст тесту** (файл, назва, параметри)

**Рекомендації для тестового логування:**
```python
def test_complex_operation(test_logger):
    """Приклад правильного логування тесту"""
    test_logger.info("Початок тесту складного API", extra={
        "test_name": "test_complex_api",
        "expected_result": "success",
        "test_data": {"user_id": "123", "operation": "create"}
    })
    
    try:
        # Виконання тесту
        result = api.create_user(test_data)
        
        test_logger.info("API виклик успішний", extra={
            "response_time_ms": result.response_time,
            "status_code": result.status_code,
            "user_id": result.user_id
        })
        
        assert result.status_code == 200
        test_logger.info("Тест пройшов успішно")
        
    except Exception as e:
        test_logger.error("Тест провалився", extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "test_data": test_data
        })
        raise
```

**Стандартні практики в індустрії:**
- **Google/Netflix** - детальне логування всіх тестів
- **Microsoft** - автоматичне логування CI/CD pipeline
- **Amazon** - логування тестів продуктивності
- **Facebook** - логування A/B тестів
- **Uber** - логування інтеграційних тестів

**Наша система забезпечує:**
- ✅ Автоматичне логування всіх тестів
- ✅ Структуровані логи з JSON контекстом
- ✅ Розділення тестових та продакшн логів
- ✅ Аналіз тестових логів через LogAnalyzer
- ✅ Моніторинг продуктивності тестів
- ✅ Інтеграція з CI/CD pipeline 