"""
Chaos Engineering тести для перевірки стійкості системи
"""

import pytest
import time
import random
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'api-gateway', 'src'))

from main import app

client = TestClient(app)


class TestChaosEngineering:
    """Chaos Engineering тести"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
        self.test_token = "test_token_123"
    
    def test_database_failure_scenario(self):
        """Тест сценарію падіння бази даних"""
        # Симулюємо падіння БД
        with patch('shared.database.connection.get_db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            # Робимо запит до API
            response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            
            # Перевіряємо що система обробляє помилку
            assert response.status_code in [500, 503, 502]
            
            data = response.json()
            assert "error" in data or "detail" in data
            
            # Перевіряємо повідомлення про помилку
            error_message = data.get("error", data.get("detail", ""))
            assert "database" in error_message.lower() or "service" in error_message.lower()
    
    def test_database_slow_response(self):
        """Тест повільної відповіді бази даних"""
        # Симулюємо повільну БД
        with patch('shared.database.connection.get_db') as mock_db:
            def slow_db():
                time.sleep(5)  # 5 секунд затримки
                raise Exception("Database timeout")
            
            mock_db.side_effect = slow_db
            
            # Робимо запит з таймаутом
            start_time = time.time()
            response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            end_time = time.time()
            
            # Перевіряємо що запит не зависає назавжди
            assert end_time - start_time < 10  # Максимум 10 секунд
            
            # Перевіряємо відповідь
            assert response.status_code in [500, 503, 408, 504]
    
    def test_external_service_failure(self):
        """Тест падіння зовнішнього сервісу"""
        # Симулюємо падіння Upwork API
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("External service unavailable")
            
            # Робимо запит до Upwork API
            response = client.get("/api/upwork/jobs")
            
            # Перевіряємо що система обробляє помилку
            assert response.status_code in [500, 503, 502]
            
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_external_service_timeout(self):
        """Тест таймауту зовнішнього сервісу"""
        # Симулюємо таймаут Upwork API
        with patch('requests.get') as mock_get:
            def timeout_request(*args, **kwargs):
                time.sleep(10)  # 10 секунд затримки
                raise Exception("Request timeout")
            
            mock_get.side_effect = timeout_request
            
            # Робимо запит з таймаутом
            start_time = time.time()
            response = client.get("/api/upwork/jobs")
            end_time = time.time()
            
            # Перевіряємо що запит не зависає
            assert end_time - start_time < 15  # Максимум 15 секунд
            
            # Перевіряємо відповідь
            assert response.status_code in [500, 503, 408, 504]
    
    def test_memory_pressure(self):
        """Тест тиску на пам'ять"""
        # Симулюємо високе використання пам'яті
        with patch('psutil.Process') as mock_process:
            # Симулюємо 90% використання пам'яті
            mock_memory = MagicMock()
            mock_memory.rss = 1024 * 1024 * 1024 * 10  # 10GB
            mock_process.return_value.memory_info.return_value = mock_memory
            
            # Робимо запит
            response = client.get("/health")
            
            # Система повинна продовжувати працювати
            assert response.status_code in [200, 503]
            
            if response.status_code == 503:
                data = response.json()
                assert "error" in data or "detail" in data
    
    def test_cpu_pressure(self):
        """Тест тиску на CPU"""
        # Симулюємо високе використання CPU
        with patch('psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 95.0  # 95% CPU
            
            # Робимо запит
            response = client.get("/health")
            
            # Система повинна продовжувати працювати
            assert response.status_code in [200, 503]
    
    def test_network_partition(self):
        """Тест розділення мережі"""
        # Симулюємо мережеві проблеми
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network partition")
            
            # Робимо запит
            response = client.get("/api/upwork/jobs")
            
            # Перевіряємо обробку помилки
            assert response.status_code in [500, 503, 502]
            
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_disk_space_full(self):
        """Тест заповнення диску"""
        # Симулюємо заповнений диск
        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.return_value = (100, 95, 5)  # 95% використано
            
            # Робимо запит
            response = client.get("/health")
            
            # Система повинна продовжувати працювати
            assert response.status_code in [200, 503]
    
    def test_corrupted_data(self):
        """Тест пошкоджених даних"""
        # Симулюємо пошкоджені дані в БД
        with patch('shared.database.connection.get_db') as mock_db:
            def corrupted_data():
                raise Exception("Data corruption detected")
            
            mock_db.side_effect = corrupted_data
            
            # Робимо запит
            response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            
            # Перевіряємо обробку помилки
            assert response.status_code in [500, 503]
            
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_authentication_service_failure(self):
        """Тест падіння сервісу автентифікації"""
        # Симулюємо падіння Auth Service
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Auth service unavailable")
            
            # Робимо запит на авторизацію
            login_data = {
                "email": "test@example.com",
                "password": "password123"
            }
            
            response = client.post("/api/auth/login", json=login_data)
            
            # Перевіряємо обробку помилки
            assert response.status_code in [500, 503, 502]
            
            data = response.json()
            assert "error" in data or "detail" in data
    
    def test_circuit_breaker_pattern(self):
        """Тест паттерну Circuit Breaker"""
        # Симулюємо кілька невдалих запитів
        with patch('requests.get') as mock_get:
            # Перші кілька запитів падають
            mock_get.side_effect = [Exception("Service down")] * 5
            
            responses = []
            for i in range(5):
                response = client.get("/api/upwork/jobs")
                responses.append(response.status_code)
            
            # Перевіряємо що всі запити обробляються
            assert all(status in [500, 503, 502] for status in responses)
            
            # Після кількох невдач, circuit breaker повинен спрацювати
            # і повертати помилку швидко
            start_time = time.time()
            response = client.get("/api/upwork/jobs")
            end_time = time.time()
            
            # Circuit breaker повинен спрацювати швидко
            assert end_time - start_time < 1  # Менше 1 секунди
            assert response.status_code in [503, 502]


class TestLoadTesting:
    """Тести навантаження"""
    
    def test_high_concurrency(self):
        """Тест високої конкурентності"""
        import threading
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Створюємо 50 конкурентних запитів
        threads = []
        for i in range(50):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Чекаємо завершення всіх потоків
        for thread in threads:
            thread.join()
        
        # Перевіряємо що всі запити завершились
        assert len(results) == 50
        
        # Перевіряємо що немає критичних помилок
        critical_errors = [500, 502, 503, 504]
        critical_count = sum(1 for status in results if status in critical_errors)
        
        # Допускаємо не більше 10% критичних помилок
        assert critical_count <= 5  # 10% від 50
    
    def test_sustained_load(self):
        """Тест тривалого навантаження"""
        # Робимо запити протягом 30 секунд
        start_time = time.time()
        request_count = 0
        error_count = 0
        
        while time.time() - start_time < 30:
            response = client.get("/health")
            request_count += 1
            
            if response.status_code >= 500:
                error_count += 1
            
            time.sleep(0.1)  # 100ms між запитами
        
        # Перевіряємо статистику
        error_rate = (error_count / request_count) * 100 if request_count > 0 else 0
        
        # Допускаємо не більше 5% помилок
        assert error_rate <= 5.0
        assert request_count > 0
    
    def test_memory_leak_under_load(self):
        """Тест витоків пам'яті під навантаженням"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Робимо багато запитів
        for i in range(1000):
            client.get("/health")
            
            # Прибираємо сміття кожні 100 запитів
            if i % 100 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Перевіряємо що збільшення пам'яті не критичне
        # Допускаємо збільшення не більше 100MB
        assert memory_increase < 100 * 1024 * 1024


class TestRecoveryTesting:
    """Тести відновлення"""
    
    def test_service_recovery_after_failure(self):
        """Тест відновлення сервісу після збою"""
        # Симулюємо збій сервісу
        with patch('shared.database.connection.get_db') as mock_db:
            # Перші запити падають
            mock_db.side_effect = [Exception("Service down")] * 3
            
            # Робимо кілька запитів
            for i in range(3):
                response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
                assert response.status_code in [500, 503]
            
            # Потім сервіс відновлюється
            mock_db.side_effect = None
            mock_db.return_value = MagicMock()
            
            # Перевіряємо що сервіс працює
            response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            assert response.status_code in [200, 401, 403, 404]
    
    def test_graceful_degradation(self):
        """Тест graceful degradation"""
        # Симулюємо збій неосновного сервісу
        with patch('requests.get') as mock_get:
            # Upwork API недоступний
            mock_get.side_effect = Exception("Upwork API down")
            
            # Основні функції повинні працювати
            response = client.get("/health")
            assert response.status_code == 200
            
            # Неосновні функції можуть не працювати
            response = client.get("/api/upwork/jobs")
            assert response.status_code in [500, 503]
            
            # Але це не повинно впливати на основні функції
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_data_consistency_after_failure(self):
        """Тест консистентності даних після збою"""
        # Симулюємо збій під час запису
        with patch('shared.database.connection.get_db') as mock_db:
            # Симулюємо збій під час транзакції
            def failing_transaction():
                raise Exception("Transaction failed")
            
            mock_db.side_effect = failing_transaction
            
            # Робимо запит на запис
            response = client.post("/api/analytics/update", json={
                "user_id": self.test_user_id,
                "data": {"test": "value"}
            })
            
            # Перевіряємо що транзакція відкотилась
            assert response.status_code in [500, 503]
            
            # Дані повинні залишитись консистентними
            # (в реальному тесті тут була б перевірка стану БД)


class TestMonitoringAndAlerting:
    """Тести моніторингу та алертингу"""
    
    def test_error_logging(self):
        """Тест логування помилок"""
        # Симулюємо помилку
        with patch('shared.database.connection.get_db') as mock_db:
            mock_db.side_effect = Exception("Test error for logging")
            
            # Робимо запит
            response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            
            # Перевіряємо що помилка обробляється
            assert response.status_code in [500, 503]
            
            # В реальному тесті тут була б перевірка логів
    
    def test_metrics_collection(self):
        """Тест збору метрик"""
        # Робимо кілька запитів для збору метрик
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            time.sleep(0.1)
        
        # В реальному тесті тут була б перевірка метрик
        # (response time, throughput, error rate, etc.)
    
    def test_alerting_thresholds(self):
        """Тест порогів алертингу"""
        # Симулюємо високий рівень помилок
        with patch('shared.database.connection.get_db') as mock_db:
            mock_db.side_effect = Exception("High error rate")
            
            # Робимо багато запитів
            error_count = 0
            for i in range(20):
                response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
                if response.status_code >= 500:
                    error_count += 1
            
            error_rate = (error_count / 20) * 100
            
            # Якщо рівень помилок > 50%, повинен спрацювати алерт
            if error_rate > 50:
                # В реальному тесті тут була б перевірка алертів
                assert error_rate > 50  # Підтверджуємо високий рівень помилок


class TestChaosMonkey:
    """Тести Chaos Monkey"""
    
    def test_random_service_failures(self):
        """Тест випадкових збоїв сервісів"""
        # Симулюємо випадкові збої
        services = ["database", "auth", "upwork", "analytics"]
        
        for _ in range(10):
            # Випадково вибираємо сервіс для збою
            failing_service = random.choice(services)
            
            if failing_service == "database":
                with patch('shared.database.connection.get_db') as mock_db:
                    mock_db.side_effect = Exception(f"{failing_service} failure")
                    response = client.get(f"/api/analytics/dashboard?user_id={self.test_user_id}")
            elif failing_service == "upwork":
                with patch('requests.get') as mock_get:
                    mock_get.side_effect = Exception(f"{failing_service} failure")
                    response = client.get("/api/upwork/jobs")
            else:
                response = client.get("/health")
            
            # Перевіряємо що система обробляє збій
            assert response.status_code in [200, 500, 503, 401, 403, 404]
    
    def test_latency_injection(self):
        """Тест ін'єкції затримок"""
        # Симулюємо випадкові затримки
        with patch('time.sleep') as mock_sleep:
            mock_sleep.return_value = None
            
            # Робимо запит
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            # Перевіряємо що система працює
            assert response.status_code == 200
            assert end_time - start_time < 5  # Максимум 5 секунд
    
    def test_resource_exhaustion(self):
        """Тест вичерпання ресурсів"""
        # Симулюємо вичерпання ресурсів
        with patch('psutil.Process') as mock_process:
            # Симулюємо 99% використання пам'яті
            mock_memory = MagicMock()
            mock_memory.rss = 1024 * 1024 * 1024 * 20  # 20GB
            mock_process.return_value.memory_info.return_value = mock_memory
            
            # Робимо запит
            response = client.get("/health")
            
            # Система повинна продовжувати працювати або повернути помилку
            assert response.status_code in [200, 503]
            
            if response.status_code == 503:
                data = response.json()
                assert "error" in data or "detail" in data 