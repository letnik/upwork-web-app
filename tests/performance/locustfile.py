"""
Performance тести для Upwork AI Assistant
Використовує Locust для load testing
"""

from locust import HttpUser, task, between
import json
import random


class UpworkAIUser(HttpUser):
    """Користувач для тестування Upwork AI Assistant"""
    
    wait_time = between(1, 3)  # Затримка між запитами 1-3 секунди
    
    def on_start(self):
        """Ініціалізація користувача"""
        self.base_url = "http://localhost:8000"
        self.test_user_id = f"test_user_{random.randint(1000, 9999)}"
    
    @task(3)
    def test_health_check(self):
        """Тестування health check endpoint"""
        self.client.get("/health")
    
    @task(2)
    def test_analytics_dashboard(self):
        """Тестування analytics dashboard"""
        self.client.get(f"/upwork/analytics/overview")
    
    @task(2)
    def test_jobs_search(self):
        """Тестування пошуку вакансій"""
        queries = ["python", "react", "javascript", "docker", "kubernetes"]
        query = random.choice(queries)
        self.client.get(f"/upwork/jobs/search?query={query}")
    
    @task(1)
    def test_job_details(self):
        """Тестування отримання деталей вакансії"""
        job_ids = ["~0123456789012345", "~0123456789012346", "~0123456789012347"]
        job_id = random.choice(job_ids)
        self.client.get(f"/upwork/jobs/{job_id}")
    
    @task(1)
    def test_proposals(self):
        """Тестування отримання пропозицій"""
        self.client.get(f"/upwork/proposals?user_id={self.test_user_id}")
    
    @task(1)
    def test_earnings(self):
        """Тестування отримання заробітку"""
        self.client.get(f"/upwork/earnings?user_id={self.test_user_id}")
    
    @task(1)
    def test_ai_proposal_generation(self):
        """Тестування генерації пропозиції через AI"""
        job_data = {
            "title": "Python Developer Needed",
            "description": "We need a Python developer for our project",
            "budget": {"min": 1000, "max": 5000},
            "skills": ["python", "django", "postgresql"]
        }
        self.client.post(
            "/ai/generate-proposal",
            json=job_data,
            headers={"Content-Type": "application/json"}
        )


class AuthUser(HttpUser):
    """Користувач для тестування Auth Service"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Ініціалізація користувача"""
        self.auth_url = "http://localhost:8001"
    
    @task(2)
    def test_auth_health(self):
        """Тестування health check Auth Service"""
        self.client.get("/health")
    
    @task(1)
    def test_user_registration(self):
        """Тестування реєстрації користувача"""
        user_data = {
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "password": "testpassword123",
            "name": f"Test User {random.randint(1000, 9999)}"
        }
        self.client.post(
            "/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
    
    @task(1)
    def test_user_login(self):
        """Тестування входу користувача"""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        self.client.post(
            "/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )


class AnalyticsUser(HttpUser):
    """Користувач для тестування Analytics Service"""
    
    wait_time = between(1, 2)
    
    def on_start(self):
        """Ініціалізація користувача"""
        self.analytics_url = "http://localhost:8004"
        self.test_user_id = f"test_user_{random.randint(1000, 9999)}"
    
    @task(3)
    def test_analytics_health(self):
        """Тестування health check Analytics Service"""
        self.client.get("/health")
    
    @task(2)
    def test_dashboard_data(self):
        """Тестування отримання даних дашборду"""
        self.client.get(f"/analytics/dashboard?user_id={self.test_user_id}")
    
    @task(1)
    def test_earnings_analytics(self):
        """Тестування аналітики заробітку"""
        self.client.get(f"/analytics/earnings?user_id={self.test_user_id}")
    
    @task(1)
    def test_proposals_analytics(self):
        """Тестування аналітики пропозицій"""
        self.client.get(f"/analytics/proposals?user_id={self.test_user_id}")
    
    @task(1)
    def test_jobs_analytics(self):
        """Тестування аналітики проектів"""
        self.client.get(f"/analytics/jobs?user_id={self.test_user_id}")


# Конфігурація для різних сценаріїв тестування
class Config:
    """Конфігурація для performance тестів"""
    
    # Базові налаштування
    HOST = "http://localhost:8000"
    
    # Сценарії навантаження
    SCENARIOS = {
        "light": {
            "users": 10,
            "spawn_rate": 2,
            "run_time": "30s"
        },
        "medium": {
            "users": 50,
            "spawn_rate": 5,
            "run_time": "60s"
        },
        "heavy": {
            "users": 100,
            "spawn_rate": 10,
            "run_time": "120s"
        }
    }
    
    # Порогові значення
    THRESHOLDS = {
        "response_time_p95": 2000,  # 95% запитів мають відповідати за 2 секунди
        "response_time_p99": 5000,  # 99% запитів мають відповідати за 5 секунд
        "error_rate": 0.01,  # Менше 1% помилок
        "requests_per_second": 10  # Мінімум 10 запитів на секунду
    } 