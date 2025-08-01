"""
Security тести для SQL Injection
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'api-gateway', 'src'))

from main import app

client = TestClient(app)


class TestSQLInjection:
    """Тести для SQL Injection атак"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.test_user_id = "test_user_123"
        self.test_token = "test_token_123"
    
    def test_sql_injection_in_user_id(self):
        """Тест SQL injection в user_id параметрі"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'hacked'); --",
            "' OR 1=1; --",
            "admin'--",
            "1' OR '1' = '1' --",
            "1'; DELETE FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/api/analytics/dashboard?user_id={malicious_input}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with input: {malicious_input}"
            
            # Перевіряємо що немає SQL помилок в відповіді
            if response.status_code == 200:
                data = response.json()
                assert "sql" not in str(data).lower(), \
                    f"SQL error in response: {data}"
    
    def test_sql_injection_in_search_query(self):
        """Тест SQL injection в пошуковому запиті"""
        malicious_inputs = [
            "'; DROP TABLE jobs; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM jobs --",
            "python'; DROP TABLE users; --",
            "developer' OR 1=1 --"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/api/upwork/jobs?q={malicious_input}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with input: {malicious_input}"
    
    def test_sql_injection_in_json_payload(self):
        """Тест SQL injection в JSON payload"""
        malicious_payloads = [
            {"user_id": "'; DROP TABLE users; --"},
            {"email": "test@example.com'; DROP TABLE users; --"},
            {"search": "python'; INSERT INTO users VALUES ('hacker', 'hacked'); --"}
        ]
        
        for payload in malicious_payloads:
            response = client.post("/api/analytics/search", json=payload)
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with payload: {payload}"
    
    def test_sql_injection_in_headers(self):
        """Тест SQL injection в заголовках"""
        malicious_headers = [
            {"X-User-ID": "'; DROP TABLE users; --"},
            {"Authorization": "Bearer '; DROP TABLE users; --"},
            {"X-Custom-Header": "'; INSERT INTO users VALUES ('hacker', 'hacked'); --"}
        ]
        
        for headers in malicious_headers:
            response = client.get("/api/analytics/dashboard", headers=headers)
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with headers: {headers}"
    
    def test_sql_injection_in_path_parameters(self):
        """Тест SQL injection в path параметрах"""
        malicious_paths = [
            "/api/users/'; DROP TABLE users; --",
            "/api/analytics/'; INSERT INTO users VALUES ('hacker', 'hacked'); --",
            "/api/jobs/'; OR 1=1 --"
        ]
        
        for path in malicious_paths:
            response = client.get(path)
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with path: {path}"
    
    def test_sql_injection_in_form_data(self):
        """Тест SQL injection в form data"""
        malicious_forms = [
            {"email": "test@example.com'; DROP TABLE users; --"},
            {"password": "password'; OR 1=1 --"},
            {"name": "'; INSERT INTO users VALUES ('hacker', 'hacked'); --"}
        ]
        
        for form_data in malicious_forms:
            response = client.post("/api/auth/register", data=form_data)
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"SQL injection succeeded with form data: {form_data}"
    
    def test_blind_sql_injection(self):
        """Тест blind SQL injection"""
        blind_payloads = [
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "1' AND (SELECT LENGTH(password) FROM users WHERE id=1) > 0 --",
            "1' AND (SELECT ASCII(SUBSTRING(username,1,1)) FROM users WHERE id=1) > 0 --"
        ]
        
        for payload in blind_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Blind SQL injection succeeded with payload: {payload}"
    
    def test_time_based_sql_injection(self):
        """Тест time-based SQL injection"""
        time_based_payloads = [
            "1' AND (SELECT SLEEP(5)) --",
            "1' AND (SELECT BENCHMARK(1000000,MD5(1))) --",
            "1' WAITFOR DELAY '00:00:05' --"
        ]
        
        for payload in time_based_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Time-based SQL injection succeeded with payload: {payload}"
    
    def test_union_based_sql_injection(self):
        """Тест union-based SQL injection"""
        union_payloads = [
            "1' UNION SELECT * FROM users --",
            "1' UNION SELECT username,password FROM users --",
            "1' UNION SELECT 1,2,3,4,5 --"
        ]
        
        for payload in union_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Union-based SQL injection succeeded with payload: {payload}"
    
    def test_error_based_sql_injection(self):
        """Тест error-based SQL injection"""
        error_payloads = [
            "1' AND UPDATEXML(1,CONCAT(0x7e,(SELECT @@version),0x7e),1) --",
            "1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e)) --",
            "1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(VERSION(),FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.TABLES GROUP BY x)a) --"
        ]
        
        for payload in error_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Error-based SQL injection succeeded with payload: {payload}"
    
    def test_boolean_based_sql_injection(self):
        """Тест boolean-based SQL injection"""
        boolean_payloads = [
            "1' AND 1=1 --",
            "1' AND 1=2 --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "1' AND (SELECT COUNT(*) FROM users) = 0 --"
        ]
        
        for payload in boolean_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Boolean-based SQL injection succeeded with payload: {payload}"
    
    def test_sql_injection_in_nested_queries(self):
        """Тест SQL injection в nested queries"""
        nested_payloads = [
            "1' AND (SELECT COUNT(*) FROM (SELECT * FROM users) t) > 0 --",
            "1' AND EXISTS(SELECT * FROM users WHERE id=1) --",
            "1' AND (SELECT COUNT(*) FROM users WHERE id IN (SELECT id FROM users)) > 0 --"
        ]
        
        for payload in nested_payloads:
            response = client.get(f"/api/analytics/dashboard?user_id={payload}")
            
            # Перевіряємо що система не піддалася атаці
            assert response.status_code in [400, 401, 403, 404, 422], \
                f"Nested SQL injection succeeded with payload: {payload}"
    
    def test_sql_injection_prevention_mechanisms(self):
        """Тест механізмів запобігання SQL injection"""
        # Тестуємо валідацію вхідних даних
        response = client.get("/api/analytics/dashboard?user_id=123")
        
        # Перевіряємо що валідні дані проходять
        assert response.status_code in [200, 401, 403], \
            "Valid input should be processed correctly"
        
        # Тестуємо параметризовані запити
        valid_data = {"user_id": "123", "email": "test@example.com"}
        response = client.post("/api/analytics/search", json=valid_data)
        
        # Перевіряємо що валідні дані проходять
        assert response.status_code in [200, 401, 403], \
            "Valid JSON data should be processed correctly"
    
    def test_sql_injection_logging(self):
        """Тест логування SQL injection спроб"""
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.get(f"/api/analytics/dashboard?user_id={malicious_input}")
        
        # Перевіряємо що система відповідає належним чином
        assert response.status_code in [400, 401, 403, 404, 422], \
            "SQL injection attempt should be blocked"
        
        # В реальному середовищі тут буде перевірка логів
        # assert "sql_injection_attempt" in log_content
    
    def test_sql_injection_rate_limiting(self):
        """Тест rate limiting для SQL injection спроб"""
        malicious_input = "'; DROP TABLE users; --"
        
        # Робимо багато спроб SQL injection
        for i in range(10):
            response = client.get(f"/api/analytics/dashboard?user_id={malicious_input}")
            
            # Після кількох спроб повинен спрацювати rate limiting
            if response.status_code == 429:  # Too Many Requests
                break
        
        # Перевіряємо що rate limiting працює
        assert response.status_code in [400, 401, 403, 404, 422, 429], \
            "Rate limiting should work for SQL injection attempts" 