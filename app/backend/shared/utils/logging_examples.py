# Приклади використання розширеного логування

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
