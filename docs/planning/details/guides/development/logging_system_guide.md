# Система логування - Гайд для розробників

## Огляд

Система логування в проекті була розширена для забезпечення максимально ефективного відстеження та фіксації багів. Цей гайд описує, як використовувати систему логування в розробці та тестуванні.

## Архітектура логування

### Основні компоненти

1. **StructuredLogger** - розширений логер з структурованими логами
2. **LoggingMiddleware** - автоматичне логування HTTP запитів
3. **DatabaseLoggingMiddleware** - логування операцій з БД
4. **SecurityLoggingMiddleware** - логування подій безпеки
5. **Декоратори** - автоматичне логування функцій
6. **LogAnalyzer** - аналіз та моніторинг логів
7. **TestLogger** - логування тестів
8. **LoggingConfig** - централізована конфігурація
9. **ELK Stack** - централізований аналіз логів (Elasticsearch, Logstash, Kibana)
10. **AlertingSystem** - розумні алерти з email/Slack/Telegram сповіщеннями
11. **LogCleanupService** - автоматичне очищення та архівування логів
12. **PerformanceMetricsCollector** - розширені метрики продуктивності
13. **SecureLogger** - безпечне логування з шифруванням чутливих даних
14. **LogAuditTrail** - аудит доступу до логів
15. **CI/CD Integration** - автоматичний аналіз логів в pipeline

### Типи логів

- **Основні логи** (`service.log`) - загальна інформація про роботу сервісу
- **Помилки** (`service_error.log`) - детальна інформація про помилки з traceback
- **Безпека** (`service_security.log`) - події безпеки (логіни, неавторизований доступ)
- **Продуктивність** (`service_performance.log`) - метрики продуктивності операцій
- **API** (`service_api.log`) - всі HTTP запити з деталями
- **База даних** (`service_database.log`) - операції з БД з тривалістю
- **Тести** (`service_test.log`) - результати тестів (тільки в тестовому режимі)

## Цілісність архітектури

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
│   ├── service_20241219_120000.log.gz
│   └── ...
├── backup/                  # Резервні копії
│   ├── backup_20241219_120000/
│   └── ...
└── test/                    # Тестові логи
    ├── test-service.log     # Основні тестові логи
    ├── test-service_error.log # Помилки тестів
    ├── test-service_test.log  # Результати тестів
    └── ...
```

### Централізована конфігурація

Всі налаштування логування централізовані в `shared/config/logging_config.py`:

```python
@dataclass
class LoggingConfig:
    service_name: str
    log_level: str = "INFO"
    environment: str = "development"
    rotation_config: Dict[str, Dict[str, Any]] = None
    console_format: str = None
    file_format: str = None
    logs_directory: str = "logs"
    test_logs_directory: str = "logs/test"
```

### Автоматичне визначення тестового режиму

Система автоматично визначає тестовий режим через:
- Наявність `pytest` в `sys.modules`
- Змінну середовища `PYTEST_CURRENT_TEST`
- Параметр `test_mode=True`
- Перевірку назви сервісу на наявність "test"

## Логічні дири та їх вирішення

### 1. Дублювання конфігурації

**Проблема:** Конфігурація логування була розкидана по різних файлах
**Вирішення:** Створено централізований `LoggingConfig` клас

### 2. Непослідовне використання логерів

**Проблема:** Деякі файли використовували стандартний `logging` замість нашої системи
**Вирішення:** Виправлено всі файли для використання `get_logger()`

### 3. Відсутність контексту в тестах

**Проблема:** Тести не логувалися з контекстом
**Вирішення:** Додано `TestLogger` та автоматичне логування тестів

### 4. Неоптимальна ротація логів

**Проблема:** Всі логи мали однакові налаштування ротації
**Вирішення:** Створено окремі налаштування для різних типів логів

### 5. Відсутність фільтрації

**Проблема:** Всі логи записувалися в один файл
**Вирішення:** Додано фільтри для різних типів логів

### 6. Відсутність централізованого аналізу

**Проблема:** Складно аналізувати логи з різних сервісів
**Вирішення:** Інтегровано ELK Stack для централізованого аналізу

### 7. Відсутність автоматичних алертів

**Проблема:** Проблеми виявлялися тільки після ручного аналізу
**Вирішення:** Створено систему розумних алертів з автоматичними сповіщеннями

### 8. Відсутність безпеки логування

**Проблема:** Чутливі дані могли потрапити в логи
**Вирішення:** Додано шифрування та маскування чутливих даних

## Нові компоненти Phase 2

### ELK Stack

**Файли:**
- `docker/elk/docker-compose.yml` - конфігурація ELK Stack
- `docker/elk/logstash/pipeline/logstash.conf` - обробка логів
- `docker/elk/filebeat/filebeat.yml` - збір логів

**Запуск:**
```bash
cd docker/elk
docker-compose up -d
```

**Доступ:**
- Kibana: http://localhost:5601
- Elasticsearch: http://localhost:9200
- Logstash: http://localhost:9600

### Система алертів

**Файл:** `app/backend/shared/utils/alerting_system.py`

**Типи алертів:**
- High Error Rate (>10% помилок)
- Slow Response Time (>2с відповідь)
- Security Events (≥5 подій безпеки)
- Performance Degradation (≥50% деградація)

**Налаштування сповіщень:**
```bash
# Email
export SMTP_SERVER=smtp.gmail.com
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-password
export ALERT_RECIPIENTS=admin@example.com,dev@example.com

# Slack
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
export SLACK_CHANNEL=#alerts

# Telegram
export TELEGRAM_BOT_TOKEN=your-bot-token
export TELEGRAM_CHAT_ID=your-chat-id
```

### Автоматичне очищення логів

**Файл:** `app/backend/shared/utils/log_cleanup_service.py`

**Можливості:**
- Автоматичне очищення старих логів (90 днів)
- Архівування з стисненням (gzip)
- Резервне копіювання
- Контроль розміру архівів (максимум 10GB)

### Розширені метрики продуктивності

**Файл:** `app/backend/shared/utils/performance_metrics.py`

**Компоненти:**
- PerformanceMetricsCollector - збір системних метрик
- DatabaseMetrics - метрики бази даних
- APIMetrics - метрики API
- SecurityMetrics - метрики безпеки

**Використання:**
```python
from shared.utils.performance_metrics import initialize_metrics, get_metrics_summary

# Ініціалізація метрик
initialize_metrics("my-service")

# Отримання зведення
summary = get_metrics_summary()
```

### Безпечне логування

**Файл:** `app/backend/shared/utils/secure_logging.py`

**Компоненти:**
- SensitiveDataMasker - маскування чутливих даних
- SecureLogger - безпечний логер з шифруванням
- LogAuditTrail - аудит доступу до логів
- SecureLogAnalyzer - безпечний аналіз логів

**Використання:**
```python
from shared.utils.secure_logging import initialize_secure_logging, get_secure_logger

# Ініціалізація
initialize_secure_logging("my-service", encryption_key="your-key")

# Отримання безпечного логера
secure_logger = get_secure_logger()
secure_logger.info("Sensitive operation", extra={"password": "secret123"})
```

### CI/CD Інтеграція

**Файл:** `.github/workflows/log-analysis.yml`

**Можливості:**
- Автоматичний аналіз логів при push/PR
- Перевірка критичних помилок
- Аналіз продуктивності
- Сканування безпеки
- Автоматичне очищення логів
- Коментування результатів в PR

## Використання в розробці

### 1. Базове логування

```python
from shared.config.logging import get_logger

# Отримання логера для модуля
logger = get_logger("my-module")

# Базові методи логування
logger.debug("Детальна інформація для дебагу")
logger.info("Інформаційне повідомлення")
logger.warning("Попередження")
logger.error("Помилка")
logger.critical("Критична помилка")

# Логування з контекстом
logger.info("Користувач створений", extra={
    "user_id": "123",
    "email": "user@example.com",
    "operation": "user_creation"
})
```

### 2. Логування продуктивності

```python
from shared.config.logging import PerformanceLogger

# Використання контекстного менеджера
with PerformanceLogger(logger, "database_query"):
    # Виконуємо операцію
    result = database.execute_query("SELECT * FROM users")
    # Автоматично логується тривалість

# Або через декоратор
from shared.utils.logging_decorators import log_performance

@log_performance("database_operation")
def database_operation():
    # Операція з БД
    pass
```

### 3. Логування помилок з деталями

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
```

### 4. Декоратори для автоматичного логування

```python
from shared.utils.logging_decorators import (
    log_function_call, log_performance, log_database_operation,
    log_api_call, log_security_event, log_exceptions, log_async_function
)

# Логування викликів функцій
@log_function_call()
def my_function(param1, param2):
    return param1 + param2

# Логування продуктивності
@log_performance("database_query")
def get_user_data(user_id):
    return database.get_user(user_id)

# Логування операцій з БД
@log_database_operation("users", "SELECT")
def get_user(user_id):
    return database.execute("SELECT * FROM users WHERE id = ?", user_id)

# Логування API викликів
@log_api_call("/api/users", "GET")
def get_users():
    return api_client.get_users()

# Логування подій безпеки
@log_security_event("login_attempt")
def login(email, password):
    # Логіка входу
    pass

# Логування винятків
@log_exceptions()
def risky_function():
    # Функція з можливими помилками
    pass

# Логування асинхронних функцій
@log_async_function()
async def async_operation():
    # Асинхронна операція
    pass
```

### 5. Middleware для HTTP запитів

```python
from shared.utils.logging_middleware import LoggingMiddleware

# Додавання middleware до FastAPI додатку
app.add_middleware(LoggingMiddleware)
```

### 6. Логування подій безпеки

```python
from shared.utils.logging_middleware import SecurityLoggingMiddleware

security_logger = SecurityLoggingMiddleware()

# Логування спроби входу
security_logger.log_login_attempt(
    email="user@example.com",
    success=True,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)

# Логування неавторизованого доступу
security_logger.log_unauthorized_access(
    endpoint="/admin",
    method="GET",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    reason="No token"
)

# Логування перевищення ліміту запитів
security_logger.log_rate_limit_exceeded(
    ip_address="192.168.1.1",
    endpoint="/api/users",
    limit=100,
    window="1 minute"
)
```

### 7. Логування операцій з базою даних

```python
from shared.utils.logging_middleware import DatabaseLoggingMiddleware

db_logger = DatabaseLoggingMiddleware()

# Логування SQL запиту
db_logger.log_query(
    operation="SELECT",
    table="users",
    duration=0.05,  # секунди
    rows_affected=10,
    query="SELECT * FROM users WHERE active = 1",
    extra={"user_id": "123"}
)
```

### 8. Безпечне логування

```python
from shared.utils.secure_logging import initialize_secure_logging, get_secure_logger

# Ініціалізація безпечного логування
initialize_secure_logging("my-service", encryption_key="your-secret-key")

# Отримання безпечного логера
secure_logger = get_secure_logger()

# Автоматичне маскування чутливих даних
secure_logger.info("User login", extra={
    "email": "user@example.com",
    "password": "secret123",  # Автоматично замаскується
    "token": "jwt-token-here"  # Автоматично зашифрується
})
```

### 9. Розширені метрики

```python
from shared.utils.performance_metrics import initialize_metrics, get_metrics_summary

# Ініціалізація метрик
initialize_metrics("my-service")

# Додавання кастомної метрики
from shared.utils.performance_metrics import performance_collector

def get_active_users_count():
    return len(get_active_users())

performance_collector.add_custom_metric("active_users", get_active_users_count)

# Отримання зведення метрик
summary = get_metrics_summary()
print(f"CPU Usage: {summary['performance']['system_metrics']['cpu_usage']['avg']}%")
```

## Використання в тестах

### 1. Автоматичне логування тестів

Система автоматично логує всі тести через `conftest.py`:

```python
# Автоматично створюється для кожного тесту
def test_example(test_logger):
    test_logger.info("Тест виконується")
    # Логується автоматично: STARTED, PASSED/FAILED, COMPLETED
```

### 2. Спеціалізовані логери для тестів

```python
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

def test_api(api_logger):
    """Тест API"""
    api_logger.api_call("GET", "/api/test", 200, 0.05)

def test_database(database_logger):
    """Тест бази даних"""
    database_logger.database("SELECT", "users", 0.02, 10)
```

### 3. Контекстні менеджери для тестів

```python
from shared.config.logging import TestLogger

def test_with_context(test_logger):
    with TestLogger(test_logger, "test_name", "test_file.py"):
        # Тест автоматично логується з контекстом
        pass
```

### 4. Маркери для тестів

```python
@pytest.mark.slow
def test_slow_operation():
    """Повільний тест"""
    pass

@pytest.mark.security
def test_security_feature():
    """Тест безпеки"""
    pass

@pytest.mark.performance
def test_performance():
    """Тест продуктивності"""
    pass

@pytest.mark.integration
def test_integration():
    """Інтеграційний тест"""
    pass
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

### Додавання контексту

```python
# Встановлення контексту запиту
from shared.config.logging import set_request_context, generate_request_id

request_id = generate_request_id()
set_request_context(request_id, user_id="123", session_id="abc")

# Очищення контексту
from shared.config.logging import clear_request_context
clear_request_context()

# Встановлення контексту тесту
from shared.config.logging import set_test_context

set_test_context("test_name", "test_file.py")

# Очищення контексту тесту
from shared.config.logging import clear_test_context
clear_test_context()
```

## Аналіз логів

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

### Аналіз в Kibana

1. Відкрийте Kibana: http://localhost:5601
2. Створіть індекс-патерн: `logs-*`
3. Створіть Dashboard для моніторингу:
   - Кількість помилок по часу
   - Середній час відповіді
   - Події безпеки
   - Продуктивність сервісів

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

## Найкращі практики

### 1. Використовуйте контекстну інформацію

```python
# ✅ Добре
logger.error("Помилка створення користувача", extra={
    "user_id": user.id,
    "email": user.email,
    "operation": "user_creation"
})

# ❌ Погано
logger.error("Помилка створення користувача")
```

### 2. Логуйте важливі операції

```python
# ✅ Логуйте початок та кінець важливих операцій
logger.info("Початок імпорту даних", extra={"file": filename})
# ... імпорт даних ...
logger.info("Завершено імпорт даних", extra={
    "file": filename,
    "rows_imported": row_count
})
```

### 3. Використовуйте декоратори для повторюваних операцій

```python
# ✅ Використовуйте декоратори
@log_performance("database_query")
def get_user_data(user_id):
    return database.get_user(user_id)

# ❌ Не логуйте вручну кожен раз
def get_user_data(user_id):
    start_time = time.time()
    result = database.get_user(user_id)
    duration = time.time() - start_time
    logger.info(f"Database query took {duration}s")
    return result
```

### 4. Не логуйте чутливу інформацію

```python
# ✅ Безпечно
logger.info("Користувач авторизований", extra={
    "user_id": user.id,
    "ip_address": request.client.host
})

# ❌ Небезпечно
logger.info("Користувач авторизований", extra={
    "password": user.password,
    "token": jwt_token
})
```

### 5. Використовуйте правильні рівні логування

```python
# DEBUG - детальна інформація для дебагу
logger.debug("SQL query executed", extra={"query": sql})

# INFO - загальна інформація про роботу
logger.info("Користувач створений", extra={"user_id": user.id})

# WARNING - попередження, але не критично
logger.warning("Database connection slow", extra={"duration": 2.5})

# ERROR - помилка, але додаток може продовжувати роботу
logger.error("Failed to send email", extra={"user_id": user.id})

# CRITICAL - критична помилка, додаток не може працювати
logger.critical("Database connection lost")
```

### 6. Логування в тестах

```python
# ✅ Логуйте важливі кроки тестів
def test_user_creation(test_logger):
    test_logger.info("Початок тесту створення користувача")
    
    # Створення користувача
    user = create_user("test@example.com")
    test_logger.info("Користувач створений", extra={"user_id": user.id})
    
    # Перевірка
    assert user.email == "test@example.com"
    test_logger.info("Тест пройшов успішно")

# ✅ Використовуйте спеціалізовані логери
def test_performance(performance_logger):
    with PerformanceLogger(performance_logger, "user_creation"):
        user = create_user("test@example.com")
    assert user is not None
```

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

## Відладка логування

### Перевірка налаштувань

```python
from shared.config.logging import setup_logging

# Налаштування логування з конкретними параметрами
setup_logging(
    service_name="my-service",
    log_level="DEBUG",
    test_mode=True  # для тестів
)
```

### Перевірка файлів логів

```bash
# Перегляд основних логів
tail -f logs/my-service.log

# Перегляд помилок
tail -f logs/my-service_error.log

# Перегляд продуктивності
tail -f logs/my-service_performance.log

# Перегляд тестових логів
tail -f logs/test/test-service.log
tail -f logs/test/test-service_test.log
```

### Аналіз тестових логів

```bash
# Знайти всі тести що провалились
grep "FAILED" logs/test/test-service_test.log

# Знайти повільні тести
grep "duration_ms" logs/test/test-service_test.log | grep -E "[0-9]{4,}"

# Знайти помилки в тестах
grep "ERROR" logs/test/test-service_error.log
```

## Перевірка цілісності

### Команди для перевірки

```bash
# Перевірка наявності всіх файлів логування
find . -name "*.py" -exec grep -l "logging" {} \;

# Перевірка використання стандартного logging
grep -r "import logging" app/backend/
grep -r "logging.getLogger" app/backend/

# Перевірка використання нашої системи
grep -r "from shared.config.logging import" app/backend/
grep -r "get_logger" app/backend/
```

### Автоматична перевірка

```python
# Скрипт для перевірки цілісності логування
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
        "shared/utils/secure_logging.py"
    ]
    
    # Перевірка використання правильної системи логування
    # Перевірка наявності тестових файлів
    # Перевірка документації
```

## Підсумок

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

Всі логічні дири вирішені, архітектура оптимізована та забезпечує повну цілісність системи логування з розширеними можливостями Phase 1-6. 