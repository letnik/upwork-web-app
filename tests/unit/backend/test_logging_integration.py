"""
Тести інтеграції логування
"""

import pytest
import time
from shared.config.logging import (
    get_logger, PerformanceLogger, TestLogger, 
    set_request_context, clear_request_context,
    set_test_context, clear_test_context
)
from shared.utils.logging_decorators import (
    log_function_call, log_performance, log_database_operation,
    log_api_call, log_security_event, log_exceptions
)


class TestLoggingIntegration:
    """Тести інтеграції системи логування"""
    
    def test_basic_logging(self, test_logger):
        """Тест базового логування"""
        test_logger.info("Тест базового логування", extra={
            "test_type": "basic",
            "data": {"key": "value"}
        })
        
        # Перевіряємо що логер працює
        assert test_logger.name == f"test.{self.test_basic_logging.__name__}"
    
    def test_performance_logging(self, performance_logger):
        """Тест логування продуктивності"""
        with PerformanceLogger(performance_logger, "test_operation"):
            time.sleep(0.1)  # Симулюємо операцію
        
        # Перевіряємо що логер продуктивності працює
        assert performance_logger.name == "test.performance"
    
    def test_security_logging(self, security_logger):
        """Тест логування безпеки"""
        security_logger.security("test_security_event", {
            "ip_address": "192.168.1.1",
            "user_agent": "test-agent",
            "event_type": "login_attempt"
        })
        
        assert security_logger.name == "test.security"
    
    def test_api_logging(self, api_logger):
        """Тест логування API"""
        api_logger.api_call(
            method="GET",
            endpoint="/api/test",
            status_code=200,
            duration=0.05,
            extra={"user_id": "123"}
        )
        
        assert api_logger.name == "test.api"
    
    def test_database_logging(self, database_logger):
        """Тест логування бази даних"""
        database_logger.database(
            operation="SELECT",
            table="users",
            duration=0.02,
            rows_affected=10,
            extra={"query": "SELECT * FROM users"}
        )
        
        assert database_logger.name == "test.database"
    
    def test_request_context(self, test_logger):
        """Тест контексту запиту"""
        # Встановлюємо контекст
        set_request_context("req-123", "user-456", "session-789")
        
        test_logger.info("Тест з контекстом запиту")
        
        # Очищуємо контекст
        clear_request_context()
    
    def test_test_context(self, test_logger):
        """Тест контексту тесту"""
        # Встановлюємо контекст тесту
        set_test_context("test_context", "test_file.py")
        
        test_logger.info("Тест з контекстом тесту")
        
        # Очищуємо контекст
        clear_test_context()
    
    def test_error_logging(self, test_logger):
        """Тест логування помилок"""
        try:
            raise ValueError("Тестова помилка")
        except Exception as e:
            test_logger.error("Тест логування помилки", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
    
    def test_decorators(self, test_logger):
        """Тест декораторів логування"""
        
        @log_function_call()
        def test_function():
            return "test_result"
        
        @log_performance("test_operation")
        def test_performance_function():
            time.sleep(0.01)
            return "performance_result"
        
        @log_database_operation("test_table", "SELECT")
        def test_database_function():
            return "database_result"
        
        @log_api_call("/api/test", "GET")
        def test_api_function():
            return "api_result"
        
        @log_security_event("test_event")
        def test_security_function():
            return "security_result"
        
        @log_exceptions()
        def test_exception_function():
            raise ValueError("Test exception")
        
        # Виконуємо функції
        result1 = test_function()
        result2 = test_performance_function()
        result3 = test_database_function()
        result4 = test_api_function()
        result5 = test_security_function()
        
        # Перевіряємо результати
        assert result1 == "test_result"
        assert result2 == "performance_result"
        assert result3 == "database_result"
        assert result4 == "api_result"
        assert result5 == "security_result"
        
        # Тестуємо логування винятків
        with pytest.raises(ValueError):
            test_exception_function()


class TestLoggingDecorators:
    """Тести декораторів логування"""
    
    def test_log_function_call_decorator(self, test_logger):
        """Тест декоратора log_function_call"""
        
        @log_function_call()
        def sample_function(param1, param2):
            return param1 + param2
        
        result = sample_function(1, 2)
        assert result == 3
    
    def test_log_performance_decorator(self, test_logger):
        """Тест декоратора log_performance"""
        
        @log_performance("test_operation")
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        result = slow_function()
        assert result == "done"
    
    def test_log_database_operation_decorator(self, test_logger):
        """Тест декоратора log_database_operation"""
        
        @log_database_operation("users", "SELECT")
        def database_query():
            return ["user1", "user2"]
        
        result = database_query()
        assert result == ["user1", "user2"]
    
    def test_log_api_call_decorator(self, test_logger):
        """Тест декоратора log_api_call"""
        
        @log_api_call("/api/users", "GET")
        def api_request():
            return {"users": []}
        
        result = api_request()
        assert result == {"users": []}
    
    def test_log_security_event_decorator(self, test_logger):
        """Тест декоратора log_security_event"""
        
        @log_security_event("login_attempt")
        def login_function():
            return {"status": "success"}
        
        result = login_function()
        assert result == {"status": "success"}
    
    def test_log_exceptions_decorator(self, test_logger):
        """Тест декоратора log_exceptions"""
        
        @log_exceptions()
        def error_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            error_function()


class TestLoggingContextManagers:
    """Тести контекстних менеджерів логування"""
    
    def test_performance_logger_context(self, performance_logger):
        """Тест контекстного менеджера PerformanceLogger"""
        
        with PerformanceLogger(performance_logger, "test_operation", {"extra": "data"}):
            time.sleep(0.01)
        
        # Перевіряємо що логер працює
        assert performance_logger.name == "test.performance"
    
    def test_test_logger_context(self, test_logger):
        """Тест контекстного менеджера TestLogger"""
        
        with TestLogger(test_logger, "test_context", "test_file.py"):
            time.sleep(0.01)
        
        # Перевіряємо що логер працює
        assert test_logger.name == f"test.{self.test_test_logger_context.__name__}"


@pytest.mark.slow
class TestSlowLoggingOperations:
    """Тести повільних операцій логування"""
    
    def test_slow_performance_logging(self, performance_logger):
        """Тест логування повільної операції"""
        with PerformanceLogger(performance_logger, "slow_operation"):
            time.sleep(0.5)  # Повільна операція
        
        assert performance_logger.name == "test.performance"
    
    def test_bulk_logging(self, test_logger):
        """Тест масового логування"""
        for i in range(100):
            test_logger.info(f"Log message {i}", extra={"index": i})
        
        assert test_logger.name == f"test.{self.test_bulk_logging.__name__}"


@pytest.mark.security
class TestSecurityLogging:
    """Тести логування безпеки"""
    
    def test_login_attempt_logging(self, security_logger):
        """Тест логування спроби входу"""
        security_logger.security("login_attempt", {
            "email": "test@example.com",
            "ip_address": "192.168.1.1",
            "success": False,
            "reason": "invalid_password"
        })
        
        assert security_logger.name == "test.security"
    
    def test_unauthorized_access_logging(self, security_logger):
        """Тест логування неавторизованого доступу"""
        security_logger.security("unauthorized_access", {
            "endpoint": "/admin",
            "ip_address": "192.168.1.1",
            "user_agent": "malicious-bot",
            "reason": "no_token"
        })
        
        assert security_logger.name == "test.security" 