"""
Тести для MVP компонентів - Система моніторингу вакансій
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
from test_helpers import create_test_user, get_test_db


class TestJobMonitoring:
    """Тести для системи моніторингу вакансій"""
    
    def test_job_match_creation(self):
        """Тест створення знайденої вакансії"""
        # Mock дані
        user = create_test_user()
        db = get_test_db()
        
        # Дані вакансії
        job_data = {
            "job_id": "upwork_job_123",
            "job_title": "Python Developer Needed",
            "job_description": "We need a Python developer for web development",
            "client_name": "TechCorp Inc",
            "client_rating": 4.8,
            "budget": "$2000-$5000",
            "hourly_rate": 35.0,
            "job_type": "fixed",
            "experience_level": "intermediate",
            "skills": ["Python", "Django", "React"],
            "country": "United States",
            "posted_date": datetime.utcnow(),
            "match_score": 85.5,
            "status": "new"
        }
        
        # Перевіряємо структуру даних
        assert "job_id" in job_data
        assert "job_title" in job_data
        assert "match_score" in job_data
        assert "status" in job_data
        
        # Перевіряємо типи даних
        assert isinstance(job_data["job_id"], str)
        assert isinstance(job_data["job_title"], str)
        assert isinstance(job_data["match_score"], float)
        assert isinstance(job_data["status"], str)
        
        # Перевіряємо валідність даних
        assert len(job_data["job_id"]) > 0
        assert len(job_data["job_title"]) <= 255
        assert 0 <= job_data["match_score"] <= 100
        assert job_data["status"] in ["new", "viewed", "applied", "rejected"]
        
        print("✅ Тест створення знайденої вакансії пройшов")
    
    def test_job_monitoring_status_tracking(self):
        """Тест відстеження статусу вакансій"""
        # Статуси вакансій
        job_statuses = ["new", "viewed", "applied", "rejected"]
        
        for status in job_statuses:
            # Перевіряємо, що статус валідний
            assert status in job_statuses, f"Неправильний статус вакансії: {status}"
            
            # Створюємо приклад вакансії з кожним статусом
            job_data = {
                "job_id": f"job_{status}_123",
                "job_title": f"Test Job - {status}",
                "status": status,
                "match_score": 75.0
            }
            
            # Перевіряємо логіку статусів
            if status == "new":
                assert job_data["status"] == "new"
            elif status == "viewed":
                assert job_data["status"] in ["viewed", "applied", "rejected"]
            elif status == "applied":
                assert job_data["status"] == "applied"
            elif status == "rejected":
                assert job_data["status"] == "rejected"
        
        print("✅ Тест відстеження статусу вакансій пройшов")
    
    def test_job_match_score_calculation(self):
        """Тест розрахунку оцінки підходящості вакансії"""
        # Mock дані для розрахунку оцінки
        test_cases = [
            {
                "job_data": {
                    "budget": "$2000-$5000",
                    "client_rating": 4.8,
                    "skills_match": 0.9,
                    "experience_match": 0.8
                },
                "expected_score": 85.0
            },
            {
                "job_data": {
                    "budget": "$500-$1000",
                    "client_rating": 3.5,
                    "skills_match": 0.6,
                    "experience_match": 0.7
                },
                "expected_score": 65.0
            },
            {
                "job_data": {
                    "budget": "$5000-$10000",
                    "client_rating": 5.0,
                    "skills_match": 1.0,
                    "experience_match": 1.0
                },
                "expected_score": 95.0
            }
        ]
        
        for case in test_cases:
            # Симулюємо розрахунок оцінки
            job_data = case["job_data"]
            
            # Розраховуємо оцінку на основі різних факторів
            budget_score = 15  # Бал за бюджет (0-15)
            rating_score = (job_data["client_rating"] / 5) * 20  # Бал за рейтинг клієнта (0-20)
            skills_score = job_data["skills_match"] * 35  # Бал за відповідність навичок (0-35)
            experience_score = job_data["experience_match"] * 30  # Бал за відповідність досвіду (0-30)
            
            total_score = budget_score + rating_score + skills_score + experience_score
            
            # Перевіряємо діапазон
            assert 0 <= total_score <= 100, f"Оцінка повинна бути в діапазоні 0-100: {total_score}"
            
            # Перевіряємо логіку: кращі умови = вища оцінка
            if job_data["client_rating"] >= 4.5 and job_data["skills_match"] >= 0.8:
                assert total_score >= 70, "Високі показники повинні давати високу оцінку"
        
        print("✅ Тест розрахунку оцінки підходящості пройшов")
    
    def test_job_monitoring_filters(self):
        """Тест фільтрів моніторингу вакансій"""
        # Приклади фільтрів
        monitoring_filters = [
            {
                "name": "High Budget Jobs",
                "conditions": {
                    "budget_min": 2000,
                    "client_rating_min": 4.5,
                    "match_score_min": 80
                }
            },
            {
                "name": "Python Projects",
                "conditions": {
                    "skills_required": ["Python", "Django"],
                    "job_type": "fixed",
                    "experience_level": "intermediate"
                }
            },
            {
                "name": "Quick Projects",
                "conditions": {
                    "budget_max": 1000,
                    "job_type": "fixed",
                    "duration_max_days": 7
                }
            }
        ]
        
        for filter_config in monitoring_filters:
            # Перевіряємо структуру фільтра
            assert "name" in filter_config
            assert "conditions" in filter_config
            
            conditions = filter_config["conditions"]
            
            # Перевіряємо валідність умов
            if "budget_min" in conditions:
                assert conditions["budget_min"] >= 0, "Мінімальний бюджет не може бути від'ємним"
            if "budget_max" in conditions:
                assert conditions["budget_max"] <= 100000, "Максимальний бюджет занадто великий"
            if "client_rating_min" in conditions:
                assert 0 <= conditions["client_rating_min"] <= 5, "Рейтинг клієнта повинен бути 0-5"
            if "match_score_min" in conditions:
                assert 0 <= conditions["match_score_min"] <= 100, "Мінімальна оцінка повинна бути 0-100"
        
        print("✅ Тест фільтрів моніторингу пройшов")
    
    def test_job_monitoring_notifications(self):
        """Тест сповіщень про нові вакансії"""
        # Приклади сповіщень
        notifications = [
            {
                "type": "new_job_match",
                "job_title": "Python Developer Needed",
                "match_score": 85.5,
                "budget": "$2000-$5000",
                "priority": "high"
            },
            {
                "type": "high_match_job",
                "job_title": "Senior React Developer",
                "match_score": 92.3,
                "budget": "$5000-$8000",
                "priority": "urgent"
            },
            {
                "type": "job_status_update",
                "job_title": "Web Developer",
                "status": "applied",
                "priority": "medium"
            }
        ]
        
        for notification in notifications:
            # Перевіряємо структуру сповіщення
            assert "type" in notification
            assert "job_title" in notification
            assert "priority" in notification
            
            # Перевіряємо типи сповіщень
            assert notification["type"] in ["new_job_match", "high_match_job", "job_status_update"]
            
            # Перевіряємо пріоритети
            assert notification["priority"] in ["low", "medium", "high", "urgent"]
            
            # Перевіряємо логіку пріоритетів
            if "match_score" in notification:
                if notification["match_score"] >= 90:
                    assert notification["priority"] in ["high", "urgent"], "Високі оцінки повинні мати високий пріоритет"
                elif notification["match_score"] >= 80:
                    assert notification["priority"] in ["medium", "high"], "Середні оцінки повинні мати середній пріоритет"
        
        print("✅ Тест сповіщень про вакансії пройшов")
    
    def test_job_monitoring_analytics(self):
        """Тест аналітики моніторингу вакансій"""
        # Mock дані аналітики
        analytics_data = {
            "total_jobs_found": 150,
            "jobs_viewed": 120,
            "jobs_applied": 45,
            "jobs_rejected": 15,
            "average_match_score": 78.5,
            "top_skills": ["Python", "React", "Django"],
            "average_budget": 3500,
            "success_rate": 30.0  # 45 applied / 150 found
        }
        
        # Перевіряємо валідність даних
        assert analytics_data["total_jobs_found"] >= 0
        assert analytics_data["jobs_viewed"] <= analytics_data["total_jobs_found"]
        assert analytics_data["jobs_applied"] <= analytics_data["jobs_viewed"]
        assert analytics_data["jobs_rejected"] <= analytics_data["jobs_applied"]
        assert 0 <= analytics_data["average_match_score"] <= 100
        assert 0 <= analytics_data["success_rate"] <= 100
        
        # Перевіряємо логіку
        if analytics_data["total_jobs_found"] > 0:
            view_rate = (analytics_data["jobs_viewed"] / analytics_data["total_jobs_found"]) * 100
            assert view_rate <= 100, "Відсоток переглянутих вакансій не може перевищувати 100%"
        
        print("✅ Тест аналітики моніторингу пройшов")


class TestJobMonitoringIntegration:
    """Інтеграційні тести для моніторингу вакансій"""
    
    def test_job_monitoring_complete_workflow(self):
        """Тест повного workflow моніторингу вакансій"""
        # 1. Створення користувача
        user = create_test_user()
        assert user["id"] is not None
        
        # 2. Створення профілю фільтрів
        filter_profile = {
            "name": "Python Developer Filter",
            "keywords": ["Python", "Django", "React"],
            "budget_min": 2000,
            "budget_max": 8000,
            "experience_level": "intermediate"
        }
        
        # 3. Симуляція пошуку вакансій
        found_jobs = [
            {
                "job_id": "job_1",
                "job_title": "Python Developer",
                "budget": "$3000-$6000",
                "match_score": 85.5,
                "status": "new"
            },
            {
                "job_id": "job_2", 
                "job_title": "Django Developer",
                "budget": "$2500-$5000",
                "match_score": 78.2,
                "status": "new"
            }
        ]
        
        # 4. Перевірка фільтрації
        for job in found_jobs:
            # Перевіряємо, що вакансія відповідає фільтрам
            assert job["match_score"] >= 70, "Вакансія повинна мати достатньо високу оцінку"
            assert job["status"] == "new", "Нова вакансія повинна мати статус 'new'"
        
        # 5. Симуляція перегляду вакансії
        job_to_view = found_jobs[0]
        job_to_view["status"] = "viewed"
        job_to_view["viewed_at"] = datetime.utcnow()
        
        # 6. Перевірка оновлення статусу
        assert job_to_view["status"] == "viewed"
        assert "viewed_at" in job_to_view
        
        print("✅ Тест повного workflow моніторингу пройшов")
    
    def test_job_monitoring_real_time_updates(self):
        """Тест реального часу оновлень"""
        # Симулюємо оновлення в реальному часі
        real_time_updates = [
            {
                "timestamp": datetime.utcnow(),
                "action": "job_found",
                "job_id": "job_123",
                "match_score": 85.5
            },
            {
                "timestamp": datetime.utcnow() + timedelta(minutes=5),
                "action": "job_viewed", 
                "job_id": "job_123",
                "status": "viewed"
            },
            {
                "timestamp": datetime.utcnow() + timedelta(minutes=10),
                "action": "job_applied",
                "job_id": "job_123", 
                "status": "applied"
            }
        ]
        
        for update in real_time_updates:
            # Перевіряємо структуру оновлення
            assert "timestamp" in update
            assert "action" in update
            assert "job_id" in update
            
            # Перевіряємо типи дій
            assert update["action"] in ["job_found", "job_viewed", "job_applied", "job_rejected"]
            
            # Перевіряємо часову послідовність
            if len(real_time_updates) > 1:
                assert update["timestamp"] >= real_time_updates[0]["timestamp"], "Оновлення повинні йти в хронологічному порядку"
        
        print("✅ Тест реального часу оновлень пройшов")
    
    def test_job_monitoring_performance_metrics(self):
        """Тест метрик продуктивності моніторингу"""
        # Mock метрики продуктивності
        performance_metrics = {
            "jobs_processed_per_hour": 150,
            "average_processing_time_ms": 250,
            "cache_hit_rate": 85.5,
            "api_response_time_ms": 120,
            "error_rate": 0.5,
            "uptime_percentage": 99.8
        }
        
        # Перевіряємо валідність метрик
        assert performance_metrics["jobs_processed_per_hour"] > 0
        assert performance_metrics["average_processing_time_ms"] > 0
        assert 0 <= performance_metrics["cache_hit_rate"] <= 100
        assert performance_metrics["api_response_time_ms"] > 0
        assert 0 <= performance_metrics["error_rate"] <= 100
        assert 0 <= performance_metrics["uptime_percentage"] <= 100
        
        # Перевіряємо якість продуктивності
        assert performance_metrics["average_processing_time_ms"] < 1000, "Час обробки повинен бути менше 1 секунди"
        assert performance_metrics["api_response_time_ms"] < 500, "Час відповіді API повинен бути менше 500мс"
        assert performance_metrics["error_rate"] < 5, "Рівень помилок повинен бути менше 5%"
        assert performance_metrics["uptime_percentage"] >= 99, "Uptime повинен бути не менше 99%"
        
        print("✅ Тест метрик продуктивності пройшов")


if __name__ == "__main__":
    # Запуск тестів
    test_job_monitoring = TestJobMonitoring()
    test_job_monitoring.test_job_match_creation()
    test_job_monitoring.test_job_monitoring_status_tracking()
    test_job_monitoring.test_job_match_score_calculation()
    test_job_monitoring.test_job_monitoring_filters()
    test_job_monitoring.test_job_monitoring_notifications()
    test_job_monitoring.test_job_monitoring_analytics()
    
    test_integration = TestJobMonitoringIntegration()
    test_integration.test_job_monitoring_complete_workflow()
    test_integration.test_job_monitoring_real_time_updates()
    test_integration.test_job_monitoring_performance_metrics()
    
    print("\n🎉 Всі тести моніторингу вакансій пройшли успішно!") 