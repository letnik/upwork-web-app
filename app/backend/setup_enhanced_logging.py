#!/usr/bin/env python3
"""
Скрипт для налаштування розширеного логування
"""

import os
import sys
from pathlib import Path

# Додаємо шлях до shared модуля
sys.path.insert(0, str(Path(__file__).parent))

def create_logs_directory():
    """Створення директорії для логів"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Створено директорію для логів: {logs_dir.absolute()}")

def create_logging_documentation():
    """Створення документації по логуванню"""
    docs_dir = Path("shared/docs")
    docs_dir.mkdir(exist_ok=True)
    
    documentation = '''# Розширена система логування

## Огляд

Система логування була значно розширена для забезпечення кращого відстеження та фіксації багів.

### Основні компоненти

1. **StructuredLogger** - розширений логер з структурованими логами
2. **LoggingMiddleware** - автоматичне логування HTTP запитів
3. **DatabaseLoggingMiddleware** - логування операцій з БД
4. **SecurityLoggingMiddleware** - логування подій безпеки
5. **Декоратори** - автоматичне логування функцій
6. **LogAnalyzer** - аналіз та моніторинг логів

### Типи логів

- **Основні логи** - загальна інформація про роботу сервісу
- **Помилки** - детальна інформація про помилки з traceback
- **Безпека** - події безпеки (логіни, неавторизований доступ)
- **Продуктивність** - метрики продуктивності операцій
- **API** - всі HTTP запити з деталями
- **База даних** - операції з БД з тривалістю

### Контекстна інформація

Кожен лог містить:
- Timestamp
- Service name
- Environment
- Module/function
- Request ID (для HTTP запитів)
- User ID (якщо доступний)
- Session ID (якщо доступний)
- Додатковий контекст

### Файли логів

- `service.log` - основні логи
- `service_error.log` - помилки
- `service_security.log` - події безпеки
- `service_performance.log` - метрики продуктивності
- `service_api.log` - API виклики
- `service_database.log` - операції з БД

### Ротація логів

- Основні логи: 50MB, 90 днів
- Помилки: 20MB, 180 днів
- Безпека: 10MB, 365 днів
- Продуктивність: 20MB, 90 днів
- API: 30MB, 60 днів
- База даних: 20MB, 90 днів

### Використання

#### Базове логування
```python
from shared.config.logging import get_logger

logger = get_logger("my-module")
logger.info("Повідомлення", extra={"context": "data"})
```

#### Логування продуктивності
```python
from shared.config.logging import PerformanceLogger

with PerformanceLogger(logger, "operation_name"):
    # Операція
    pass
```

#### Декоратори
```python
from shared.utils.logging_decorators import log_performance

@log_performance("database_query")
def my_function():
    pass
```

#### Middleware
```python
from shared.utils.logging_middleware import LoggingMiddleware

app.add_middleware(LoggingMiddleware)
```

### Аналіз логів

```python
from shared.utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")
summary = analyzer.get_comprehensive_summary(hours=24)
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)
frequent_errors = analyzer.find_frequent_errors(min_count=5)
```

### Моніторинг в реальному часі

```python
from shared.utils.log_analyzer import LogMonitor

monitor = LogMonitor("logs")
new_errors = monitor.check_new_errors()
slow_ops = monitor.check_slow_operations()
security_events = monitor.check_security_events()
```

### Налаштування

Змінні середовища:
- `LOG_LEVEL` - рівень логування (DEBUG, INFO, WARNING, ERROR)
- `ENVIRONMENT` - середовище (development, production)
- `SERVICE_NAME` - назва сервісу

### Переваги

1. **Детальне відстеження** - кожна операція логується з контекстом
2. **Швидка діагностика** - структуровані логи легко аналізувати
3. **Моніторинг продуктивності** - автоматичне відстеження повільних операцій
4. **Безпека** - детальне логування подій безпеки
5. **Аналітика** - інструменти для аналізу логів
6. **Масштабованість** - ротація та стиснення логів
7. **Асинхронність** - логування не блокує основний потік

### Рекомендації

1. Використовуйте контекстну інформацію для кращого відстеження
2. Логуйте всі важливі операції з метриками продуктивності
3. Регулярно аналізуйте логи для виявлення проблем
4. Налаштуйте алерти для критичних помилок
5. Використовуйте декоратори для автоматичного логування
6. Моніторте повільні операції та частих помилок
'''
    
    with open(docs_dir / "LOGGING_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print(f"✅ Створено документацію: {docs_dir / 'LOGGING_GUIDE.md'}")

def create_logging_examples():
    """Створення прикладів використання логування"""
    examples = '''# Приклади використання розширеного логування

from shared.config.logging import get_logger, PerformanceLogger
from shared.utils.logging_decorators import (
    log_function_call, log_performance, log_database_operation,
    log_api_call, log_security_event, log_exceptions
)

# Отримання логера
logger = get_logger("my-module")

# Базове логування
logger.info("Інформаційне повідомлення")
logger.warning("Попередження")
logger.error("Помилка", extra={"context": "additional_info"})

# Логування продуктивності
with PerformanceLogger(logger, "database_query"):
    # Виконуємо операцію
    result = database.execute_query("SELECT * FROM users")
    # Автоматично логується тривалість

# Логування з контекстом
logger.info("Користувач створений", extra={
    "user_id": "123",
    "email": "user@example.com",
    "operation": "user_creation"
})

# Логування помилок з деталями
try:
    risky_operation()
except Exception as e:
    logger.error("Помилка виконання операції", extra={
        "operation": "risky_operation",
        "error_type": type(e).__name__,
        "error_details": str(e)
    })

# Використання декораторів
@log_function_call()
def my_function(param1, param2):
    return param1 + param2

@log_performance("database_operation")
def database_operation():
    # Операція з БД
    pass

@log_database_operation("users", "SELECT")
def get_user(user_id):
    # Отримання користувача
    pass

@log_api_call("/api/users", "GET")
def get_users():
    # API виклик
    pass

@log_security_event("login_attempt")
def login(email, password):
    # Логін
    pass

@log_exceptions()
def risky_function():
    # Функція з можливими помилками
    pass

# Middleware для автоматичного логування запитів
from shared.utils.logging_middleware import LoggingMiddleware

app.add_middleware(LoggingMiddleware)

# Інтеграція в існуючий код
from shared.utils.enhanced_logging_integration import EnhancedLoggingIntegration

logging_integration = EnhancedLoggingIntegration("my-service")

# В обробнику запиту
request_id = logging_integration.setup_request_logging(request)
try:
    # Обробка запиту
    pass
finally:
    logging_integration.cleanup_request_logging()

# Логування подій безпеки
logging_integration.log_login_attempt("user@example.com", True, "192.168.1.1", "Mozilla/5.0...")
logging_integration.log_unauthorized_access("/admin", "GET", "192.168.1.1", "Mozilla/5.0...", "No token")

# Аналіз логів
from shared.utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")
summary = analyzer.get_comprehensive_summary(hours=24)
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)
frequent_errors = analyzer.find_frequent_errors(min_count=5)

print(f"Total errors: {summary['errors']['total_errors']}")
print(f"Slow operations: {len(slow_ops)}")
print(f"Frequent errors: {len(frequent_errors)}")
'''
    
    with open("shared/utils/logging_examples.py", 'w', encoding='utf-8') as f:
        f.write(examples)
    
    print("✅ Створено приклади використання: shared/utils/logging_examples.py")

def create_logging_config_template():
    """Створення шаблону конфігурації логування"""
    config_dir = Path("shared/config")
    config_dir.mkdir(exist_ok=True)
    
    template = '''# Конфігурація логування для сервісу
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "format": "%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service.log",
            "maxBytes": 52428800,  # 50MB
            "backupCount": 10
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/service_error.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 20
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "filename": "logs/service_security.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 30
        },
        "performance_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_performance.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 10
        },
        "api_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_api.log",
            "maxBytes": 31457280,  # 30MB
            "backupCount": 5
        },
        "database_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/service_database.log",
            "maxBytes": 20971520,  # 20MB
            "backupCount": 10
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file", "error_file"]
        },
        "security": {
            "level": "WARNING",
            "handlers": ["security_file"],
            "propagate": False
        },
        "performance": {
            "level": "INFO",
            "handlers": ["performance_file"],
            "propagate": False
        },
        "api": {
            "level": "INFO",
            "handlers": ["api_file"],
            "propagate": False
        },
        "database": {
            "level": "INFO",
            "handlers": ["database_file"],
            "propagate": False
        }
    }
}
'''
    
    with open(config_dir / "logging_config_template.py", 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ Створено шаблон конфігурації: {config_dir / 'logging_config_template.py'}")

def create_logging_summary():
    """Створення зведення про розширене логування"""
    summary = '''# Зведення розширеного логування

## Що було додано

### 1. Розширена конфігурація логування
- **Файл**: `shared/config/logging.py`
- **Функціональність**: Структуровані логи з контекстом, різні типи логів, ротація файлів

### 2. Middleware для автоматичного логування
- **Файл**: `shared/utils/logging_middleware.py`
- **Функціональність**: Автоматичне логування HTTP запитів, подій безпеки, операцій з БД

### 3. Декоратори для логування
- **Файл**: `shared/utils/logging_decorators.py`
- **Функціональність**: Автоматичне логування функцій, продуктивності, API викликів

### 4. Аналізатор логів
- **Файл**: `shared/utils/log_analyzer.py`
- **Функціональність**: Аналіз логів, моніторинг в реальному часі, зведення

### 5. Інтеграція
- **Файл**: `shared/utils/enhanced_logging_integration.py`
- **Функціональність**: Інтеграція розширеного логування в існуючі сервіси

## Типи логів

1. **Основні логи** (`service.log`) - загальна інформація
2. **Помилки** (`service_error.log`) - детальні помилки з traceback
3. **Безпека** (`service_security.log`) - події безпеки
4. **Продуктивність** (`service_performance.log`) - метрики продуктивності
5. **API** (`service_api.log`) - HTTP запити
6. **База даних** (`service_database.log`) - операції з БД

## Контекстна інформація

Кожен лог містить:
- Timestamp
- Service name
- Environment
- Module/function
- Request ID (для HTTP запитів)
- User ID (якщо доступний)
- Session ID (якщо доступний)
- Додатковий контекст

## Ротація логів

- Основні логи: 50MB, 90 днів
- Помилки: 20MB, 180 днів
- Безпека: 10MB, 365 днів
- Продуктивність: 20MB, 90 днів
- API: 30MB, 60 днів
- База даних: 20MB, 90 днів

## Використання

### Базове логування
```python
from shared.config.logging import get_logger

logger = get_logger("my-module")
logger.info("Повідомлення", extra={"context": "data"})
```

### Логування продуктивності
```python
from shared.config.logging import PerformanceLogger

with PerformanceLogger(logger, "operation_name"):
    # Операція
    pass
```

### Декоратори
```python
from shared.utils.logging_decorators import log_performance

@log_performance("database_query")
def my_function():
    pass
```

### Middleware
```python
from shared.utils.logging_middleware import LoggingMiddleware

app.add_middleware(LoggingMiddleware)
```

## Аналіз логів

```python
from shared.utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer("logs")
summary = analyzer.get_comprehensive_summary(hours=24)
slow_ops = analyzer.find_slow_operations(threshold_ms=1000.0)
frequent_errors = analyzer.find_frequent_errors(min_count=5)
```

## Переваги

1. **Детальне відстеження** - кожна операція логується з контекстом
2. **Швидка діагностика** - структуровані логи легко аналізувати
3. **Моніторинг продуктивності** - автоматичне відстеження повільних операцій
4. **Безпека** - детальне логування подій безпеки
5. **Аналітика** - інструменти для аналізу логів
6. **Масштабованість** - ротація та стиснення логів
7. **Асинхронність** - логування не блокує основний потік

## Наступні кроки

1. Інтегрувати middleware в кожен сервіс
2. Додати декоратори до важливих функцій
3. Налаштувати алерти для критичних помилок
4. Регулярно аналізувати логи
5. Моніторити повільні операції
'''
    
    with open("LOGGING_SUMMARY.md", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("✅ Створено зведення: LOGGING_SUMMARY.md")

def main():
    """Основна функція"""
    print("🚀 Налаштування розширеного логування...")
    
    # Створюємо директорію для логів
    create_logs_directory()
    
    # Створюємо документацію
    create_logging_documentation()
    
    # Створюємо приклади
    create_logging_examples()
    
    # Створюємо шаблон конфігурації
    create_logging_config_template()
    
    # Створюємо зведення
    create_logging_summary()
    
    print("\n✅ Розширена система логування налаштована!")
    print("\n📁 Створені файли:")
    print("  - logs/ (директорія для логів)")
    print("  - shared/docs/LOGGING_GUIDE.md (документація)")
    print("  - shared/utils/logging_examples.py (приклади)")
    print("  - shared/config/logging_config_template.py (шаблон конфігурації)")
    print("  - LOGGING_SUMMARY.md (зведення)")
    print("\n📋 Наступні кроки:")
    print("  1. Інтегрувати middleware в кожен сервіс")
    print("  2. Додати декоратори до важливих функцій")
    print("  3. Налаштувати алерти для критичних помилок")
    print("  4. Регулярно аналізувати логи")
    print("  5. Моніторити повільні операції")

if __name__ == "__main__":
    main() 