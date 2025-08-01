"""
Приклади Test-Driven Development (TDD) workflow
"""

import pytest
from typing import List, Dict, Any
from datetime import datetime, timedelta


# ============================================================================
# ПРИКЛАД 1: Створення функції аналітики заробітку
# ============================================================================

class TestEarningsAnalytics:
    """TDD приклад для функції аналітики заробітку"""
    
    def test_calculate_monthly_earnings(self):
        """Тест 1: Розрахунок місячного заробітку"""
        # Arrange
        earnings_data = [
            {"date": "2024-01-15", "amount": 1000},
            {"date": "2024-01-20", "amount": 1500},
            {"date": "2024-01-25", "amount": 800}
        ]
        
        # Act
        result = calculate_monthly_earnings(earnings_data, "2024-01")
        
        # Assert
        assert result["total"] == 3300
        assert result["count"] == 3
        assert result["average"] == 1100
        assert result["month"] == "2024-01"
    
    def test_calculate_monthly_earnings_empty_data(self):
        """Тест 2: Розрахунок з порожніми даними"""
        # Arrange
        earnings_data = []
        
        # Act
        result = calculate_monthly_earnings(earnings_data, "2024-01")
        
        # Assert
        assert result["total"] == 0
        assert result["count"] == 0
        assert result["average"] == 0
        assert result["month"] == "2024-01"
    
    def test_calculate_monthly_earnings_different_month(self):
        """Тест 3: Розрахунок для іншого місяця"""
        # Arrange
        earnings_data = [
            {"date": "2024-01-15", "amount": 1000},
            {"date": "2024-02-20", "amount": 1500},
            {"date": "2024-02-25", "amount": 800}
        ]
        
        # Act
        result = calculate_monthly_earnings(earnings_data, "2024-02")
        
        # Assert
        assert result["total"] == 2300
        assert result["count"] == 2
        assert result["average"] == 1150
        assert result["month"] == "2024-02"


# Реалізація після написання тестів
def calculate_monthly_earnings(earnings_data: List[Dict[str, Any]], month: str) -> Dict[str, Any]:
    """Розрахунок місячного заробітку"""
    monthly_earnings = [
        earning for earning in earnings_data 
        if earning["date"].startswith(month)
    ]
    
    if not monthly_earnings:
        return {
            "total": 0,
            "count": 0,
            "average": 0,
            "month": month
        }
    
    total = sum(earning["amount"] for earning in monthly_earnings)
    count = len(monthly_earnings)
    average = total / count
    
    return {
        "total": total,
        "count": count,
        "average": average,
        "month": month
    }


# ============================================================================
# ПРИКЛАД 2: Створення функції валідації email
# ============================================================================

class TestEmailValidation:
    """TDD приклад для валідації email"""
    
    def test_valid_email_format(self):
        """Тест 1: Валідний формат email"""
        # Arrange
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com"
        ]
        
        # Act & Assert
        for email in valid_emails:
            assert is_valid_email(email), f"Email {email} повинен бути валідним"
    
    def test_invalid_email_format(self):
        """Тест 2: Невалідний формат email"""
        # Arrange
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "user@example..com"
        ]
        
        # Act & Assert
        for email in invalid_emails:
            assert not is_valid_email(email), f"Email {email} повинен бути невалідним"
    
    def test_email_with_special_characters(self):
        """Тест 3: Email зі спеціальними символами"""
        # Arrange
        special_emails = [
            "user.name+tag@example.com",
            "user-name@example.com",
            "user_name@example.com"
        ]
        
        # Act & Assert
        for email in special_emails:
            assert is_valid_email(email), f"Email {email} повинен бути валідним"
    
    def test_empty_or_none_email(self):
        """Тест 4: Порожній або None email"""
        # Arrange
        empty_emails = ["", None]
        
        # Act & Assert
        for email in empty_emails:
            assert not is_valid_email(email), f"Email {email} повинен бути невалідним"


# Реалізація після написання тестів
def is_valid_email(email: str) -> bool:
    """Валідація email адреси"""
    if not email:
        return False
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ============================================================================
# ПРИКЛАД 3: Створення функції кешування
# ============================================================================

class TestCacheSystem:
    """TDD приклад для системи кешування"""
    
    def test_cache_set_and_get(self):
        """Тест 1: Встановлення та отримання з кешу"""
        # Arrange
        cache = Cache()
        key = "test_key"
        value = "test_value"
        
        # Act
        cache.set(key, value)
        result = cache.get(key)
        
        # Assert
        assert result == value
    
    def test_cache_get_nonexistent_key(self):
        """Тест 2: Отримання неіснуючого ключа"""
        # Arrange
        cache = Cache()
        
        # Act
        result = cache.get("nonexistent_key")
        
        # Assert
        assert result is None
    
    def test_cache_expiration(self):
        """Тест 3: Застарівання кешу"""
        # Arrange
        cache = Cache()
        key = "expiring_key"
        value = "expiring_value"
        
        # Act
        cache.set(key, value, ttl=1)  # 1 секунда
        result_before = cache.get(key)
        
        import time
        time.sleep(1.1)  # Чекаємо більше TTL
        
        result_after = cache.get(key)
        
        # Assert
        assert result_before == value
        assert result_after is None
    
    def test_cache_update_existing_key(self):
        """Тест 4: Оновлення існуючого ключа"""
        # Arrange
        cache = Cache()
        key = "update_key"
        value1 = "old_value"
        value2 = "new_value"
        
        # Act
        cache.set(key, value1)
        cache.set(key, value2)
        result = cache.get(key)
        
        # Assert
        assert result == value2
    
    def test_cache_clear(self):
        """Тест 5: Очищення кешу"""
        # Arrange
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Act
        cache.clear()
        result1 = cache.get("key1")
        result2 = cache.get("key2")
        
        # Assert
        assert result1 is None
        assert result2 is None


# Реалізація після написання тестів
class Cache:
    """Простий кеш з TTL"""
    
    def __init__(self):
        self._cache = {}
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Встановлення значення в кеш"""
        expiry = None
        if ttl:
            expiry = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            "value": value,
            "expiry": expiry
        }
    
    def get(self, key: str) -> Any:
        """Отримання значення з кешу"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        
        # Перевіряємо застарівання
        if item["expiry"] and datetime.now() > item["expiry"]:
            del self._cache[key]
            return None
        
        return item["value"]
    
    def clear(self):
        """Очищення кешу"""
        self._cache.clear()


# ============================================================================
# ПРИКЛАД 4: Створення функції сортування пропозицій
# ============================================================================

class TestProposalSorting:
    """TDD приклад для сортування пропозицій"""
    
    def test_sort_proposals_by_budget(self):
        """Тест 1: Сортування пропозицій за бюджетом"""
        # Arrange
        proposals = [
            {"id": 1, "budget": 1000, "title": "Low budget"},
            {"id": 2, "budget": 5000, "title": "High budget"},
            {"id": 3, "budget": 2500, "title": "Medium budget"}
        ]
        
        # Act
        result = sort_proposals(proposals, "budget", "desc")
        
        # Assert
        assert result[0]["id"] == 2
        assert result[1]["id"] == 3
        assert result[2]["id"] == 1
    
    def test_sort_proposals_by_date(self):
        """Тест 2: Сортування пропозицій за датою"""
        # Arrange
        proposals = [
            {"id": 1, "date": "2024-01-15", "title": "Old"},
            {"id": 2, "date": "2024-01-20", "title": "New"},
            {"id": 3, "date": "2024-01-18", "title": "Middle"}
        ]
        
        # Act
        result = sort_proposals(proposals, "date", "asc")
        
        # Assert
        assert result[0]["id"] == 1
        assert result[1]["id"] == 3
        assert result[2]["id"] == 2
    
    def test_sort_proposals_empty_list(self):
        """Тест 3: Сортування порожнього списку"""
        # Arrange
        proposals = []
        
        # Act
        result = sort_proposals(proposals, "budget", "desc")
        
        # Assert
        assert result == []
    
    def test_sort_proposals_invalid_field(self):
        """Тест 4: Сортування за неіснуючим полем"""
        # Arrange
        proposals = [
            {"id": 1, "budget": 1000},
            {"id": 2, "budget": 5000}
        ]
        
        # Act
        result = sort_proposals(proposals, "nonexistent_field", "desc")
        
        # Assert
        assert result == proposals  # Повертаємо оригінальний список
    
    def test_sort_proposals_invalid_order(self):
        """Тест 5: Сортування з невалідним порядком"""
        # Arrange
        proposals = [
            {"id": 1, "budget": 1000},
            {"id": 2, "budget": 5000}
        ]
        
        # Act
        result = sort_proposals(proposals, "budget", "invalid_order")
        
        # Assert
        assert result == proposals  # Повертаємо оригінальний список


# Реалізація після написання тестів
def sort_proposals(proposals: List[Dict[str, Any]], field: str, order: str) -> List[Dict[str, Any]]:
    """Сортування пропозицій за вказаним полем"""
    if not proposals:
        return []
    
    # Перевіряємо чи існує поле в першому елементі
    if field not in proposals[0]:
        return proposals
    
    # Визначаємо порядок сортування
    reverse = order.lower() == "desc"
    
    # Сортуємо
    try:
        return sorted(proposals, key=lambda x: x[field], reverse=reverse)
    except (TypeError, KeyError):
        return proposals


# ============================================================================
# ПРИКЛАД 5: Створення функції аналізу продуктивності
# ============================================================================

class TestPerformanceAnalysis:
    """TDD приклад для аналізу продуктивності"""
    
    def test_calculate_success_rate(self):
        """Тест 1: Розрахунок успішності"""
        # Arrange
        performance_data = {
            "total_jobs": 100,
            "completed_jobs": 85,
            "cancelled_jobs": 10,
            "failed_jobs": 5
        }
        
        # Act
        result = calculate_success_rate(performance_data)
        
        # Assert
        assert result["success_rate"] == 85.0
        assert result["completion_rate"] == 85.0
        assert result["cancellation_rate"] == 10.0
        assert result["failure_rate"] == 5.0
    
    def test_calculate_success_rate_zero_jobs(self):
        """Тест 2: Розрахунок з нульовими роботами"""
        # Arrange
        performance_data = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "cancelled_jobs": 0,
            "failed_jobs": 0
        }
        
        # Act
        result = calculate_success_rate(performance_data)
        
        # Assert
        assert result["success_rate"] == 0.0
        assert result["completion_rate"] == 0.0
        assert result["cancellation_rate"] == 0.0
        assert result["failure_rate"] == 0.0
    
    def test_calculate_success_rate_perfect_performance(self):
        """Тест 3: Ідеальна продуктивність"""
        # Arrange
        performance_data = {
            "total_jobs": 50,
            "completed_jobs": 50,
            "cancelled_jobs": 0,
            "failed_jobs": 0
        }
        
        # Act
        result = calculate_success_rate(performance_data)
        
        # Assert
        assert result["success_rate"] == 100.0
        assert result["completion_rate"] == 100.0
        assert result["cancellation_rate"] == 0.0
        assert result["failure_rate"] == 0.0


# Реалізація після написання тестів
def calculate_success_rate(performance_data: Dict[str, int]) -> Dict[str, float]:
    """Розрахунок показників успішності"""
    total_jobs = performance_data.get("total_jobs", 0)
    
    if total_jobs == 0:
        return {
            "success_rate": 0.0,
            "completion_rate": 0.0,
            "cancellation_rate": 0.0,
            "failure_rate": 0.0
        }
    
    completed_jobs = performance_data.get("completed_jobs", 0)
    cancelled_jobs = performance_data.get("cancelled_jobs", 0)
    failed_jobs = performance_data.get("failed_jobs", 0)
    
    success_rate = (completed_jobs / total_jobs) * 100
    completion_rate = (completed_jobs / total_jobs) * 100
    cancellation_rate = (cancelled_jobs / total_jobs) * 100
    failure_rate = (failed_jobs / total_jobs) * 100
    
    return {
        "success_rate": success_rate,
        "completion_rate": completion_rate,
        "cancellation_rate": cancellation_rate,
        "failure_rate": failure_rate
    }


# ============================================================================
# ДЕМОНСТРАЦІЯ TDD WORKFLOW
# ============================================================================

def demonstrate_tdd_workflow():
    """Демонстрація TDD workflow"""
    print("🚀 Демонстрація TDD Workflow")
    print("=" * 50)
    
    # Крок 1: Написання тесту
    print("1️⃣ Написання тесту (Red)")
    print("   - Визначаємо очікувану поведінку")
    print("   - Тест падає (Red)")
    
    # Крок 2: Мінімальна реалізація
    print("\n2️⃣ Мінімальна реалізація (Green)")
    print("   - Найпростіша реалізація для проходження тесту")
    print("   - Тест проходить (Green)")
    
    # Крок 3: Рефакторинг
    print("\n3️⃣ Рефакторинг (Refactor)")
    print("   - Покращення коду без зміни поведінки")
    print("   - Тести все ще проходять")
    
    print("\n✅ TDD цикл завершено!")


if __name__ == "__main__":
    demonstrate_tdd_workflow() 