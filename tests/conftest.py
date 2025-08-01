"""Глобальна конфігурація для всіх тестів"""

import sys
import os
import pytest

# Додати шляхи до всіх сервісів
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'shared'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'api-gateway', 'src'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'ai-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'auth-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'analytics-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'notification-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', 'app', 'backend', 'services', 'upwork-service', 'src'),
])

# Імпортувати спільні утиліти
try:
    from utils.test_helpers import (
        create_mock_user, 
        create_mock_job, 
        create_mock_proposal,
        create_mock_analytics_data,
        create_mock_notification
    )
except ImportError:
    # Fallback якщо utils не знайдено
    def create_mock_user(user_id="test_user_123"):
        return {"id": user_id, "email": f"{user_id}@example.com", "password": "password123"}
    
    def create_mock_job(job_id="job_123"):
        return {"id": job_id, "title": "Python Developer", "budget": {"min": 1000, "max": 5000}}
    
    def create_mock_proposal(proposal_id="proposal_123"):
        return {"id": proposal_id, "job_id": "job_123", "user_id": "test_user_123"}
    
    def create_mock_analytics_data():
        return {"earnings": {"total": 15000.0}, "proposals": {"sent": 50}}
    
    def create_mock_notification(notification_id="notif_123"):
        return {"id": notification_id, "type": "job_alert", "message": "New job available"}

@pytest.fixture(scope="session")
def mock_user_data():
    """Глобальні mock дані користувача"""
    return create_mock_user()

@pytest.fixture(scope="session")
def mock_job_data():
    """Глобальні mock дані вакансії"""
    return create_mock_job()

@pytest.fixture(scope="session")
def mock_proposal_data():
    """Глобальні mock дані пропозиції"""
    return create_mock_proposal()

@pytest.fixture(scope="session")
def mock_analytics_data():
    """Глобальні mock дані аналітики"""
    return create_mock_analytics_data()

@pytest.fixture(scope="session")
def mock_notification_data():
    """Глобальні mock дані повідомлення"""
    return create_mock_notification() 