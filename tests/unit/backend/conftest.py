"""
Конфігурація pytest для unit тестів
"""

import pytest
import os
import sys
from pathlib import Path

# Додаємо шляхи до модулів
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "app" / "backend"))

from shared.config.logging import setup_logging, get_logger, TestLogger, set_test_context, clear_test_context


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Налаштування логування для тестів"""
    # Налаштовуємо логування в тестовому режимі
    setup_logging(
        service_name="test-service",
        log_level="DEBUG",
        test_mode=True
    )
    
    # Створюємо папку для тестових логів
    os.makedirs("logs/test", exist_ok=True)
    
    logger = get_logger("test-setup")
    logger.info("Тестове середовище налаштовано")
    
    yield
    
    # Очищення після тестів
    logger.info("Тестове середовище завершено")


@pytest.fixture(autouse=True)
def test_logger(request):
    """Логер для кожного тесту"""
    test_name = request.node.name
    test_file = request.node.fspath.strpath
    
    # Встановлюємо контекст тесту
    set_test_context(test_name, test_file)
    
    logger = get_logger(f"test.{test_name}")
    
    # Логуємо початок тесту
    logger.test(test_name, "STARTED", extra={"test_file": test_file})
    
    yield logger
    
    # Логуємо завершення тесту
    logger.test(test_name, "COMPLETED", extra={"test_file": test_file})
    
    # Очищуємо контекст
    clear_test_context()


@pytest.fixture
def performance_logger():
    """Логер для тестування продуктивності"""
    return get_logger("test.performance")


@pytest.fixture
def security_logger():
    """Логер для тестування безпеки"""
    return get_logger("test.security")


@pytest.fixture
def api_logger():
    """Логер для тестування API"""
    return get_logger("test.api")


@pytest.fixture
def database_logger():
    """Логер для тестування бази даних"""
    return get_logger("test.database")


def pytest_configure(config):
    """Конфігурація pytest"""
    # Додаємо маркери
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Модифікація зібраних тестів"""
    for item in items:
        # Додаємо маркер slow для тестів з "slow" в назві
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Додаємо маркер integration для тестів з "integration" в назві
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Додаємо маркер security для тестів з "security" в назві
        if "security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        
        # Додаємо маркер performance для тестів з "performance" в назві
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)


def pytest_runtest_setup(item):
    """Налаштування перед виконанням тесту"""
    logger = get_logger("pytest")
    logger.info(f"Початок тесту: {item.name}", extra={
        "test_file": str(item.fspath),
        "test_nodeid": item.nodeid
    })


def pytest_runtest_teardown(item, nextitem):
    """Очищення після виконання тесту"""
    logger = get_logger("pytest")
    logger.info(f"Завершення тесту: {item.name}", extra={
        "test_file": str(item.fspath),
        "test_nodeid": item.nodeid
    })


def pytest_runtest_logreport(report):
    """Логування результатів тестів"""
    logger = get_logger("pytest")
    
    if report.when == "call":
        if report.passed:
            logger.test(report.nodeid, "PASSED", extra={
                "duration": report.duration,
                "test_file": str(report.fspath)
            })
        elif report.failed:
            logger.test(report.nodeid, "FAILED", extra={
                "duration": report.duration,
                "test_file": str(report.fspath),
                "error": str(report.longrepr) if report.longrepr else None
            })
        elif report.skipped:
            logger.test(report.nodeid, "SKIPPED", extra={
                "duration": report.duration,
                "test_file": str(report.fspath),
                "reason": str(report.longrepr) if report.longrepr else None
            })


def pytest_sessionstart(session):
    """Початок тестової сесії"""
    logger = get_logger("pytest")
    logger.info("Початок тестової сесії", extra={
        "session_id": getattr(session, 'testscollected', 0)
    })


def pytest_sessionfinish(session, exitstatus):
    """Завершення тестової сесії"""
    logger = get_logger("pytest")
    
    # Підрахунок результатів тестів
    passed = 0
    failed = 0
    skipped = 0
    
    for item in session.items:
        if hasattr(item, 'rep_call'):
            if item.rep_call.passed:
                passed += 1
            elif item.rep_call.failed:
                failed += 1
            elif item.rep_call.skipped:
                skipped += 1
    
    logger.info("Завершення тестової сесії", extra={
        "exit_status": exitstatus,
        "total_tests": len(session.items),
        "passed": passed,
        "failed": failed,
        "skipped": skipped
    }) 