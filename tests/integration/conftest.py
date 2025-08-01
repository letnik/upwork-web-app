"""Конфігурація для Integration тестів"""

import sys
import os
import pytest

# Додати шляхи до всіх сервісів
sys.path.extend([
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'api-gateway', 'src'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'ai-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'auth-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'analytics-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'notification-service', 'src'),
    os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'services', 'upwork-service', 'src'),
])

@pytest.fixture
def mock_user_data():
    """Mock дані користувача"""
    return {
        "id": "test_user_123",
        "email": "test@example.com",
        "password": "password123"
    }

@pytest.fixture
def mock_job_data():
    """Mock дані вакансії"""
    return {
        "id": "job_123",
        "title": "Python Developer",
        "description": "We need a Python developer",
        "budget": {"min": 1000, "max": 5000}
    }

@pytest.fixture
def mock_proposal_data():
    """Mock дані пропозиції"""
    return {
        "id": "proposal_123",
        "job_id": "job_123",
        "user_id": "test_user_123",
        "cover_letter": "I am interested in this position",
        "bid_amount": 3000,
        "status": "pending"
    } 