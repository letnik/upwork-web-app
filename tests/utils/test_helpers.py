"""Централізовані утиліти для тестів"""

import sys
import os
from typing import Dict, Any, Optional
from unittest.mock import Mock

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'backend', 'shared'))

def create_test_user(user_id="test_user_123", email="test@example.com"):
    """Створити тестового користувача"""
    return {
        "id": user_id,
        "email": email,
        "password": "test_password_123",
        "first_name": "Test",
        "last_name": "User",
        "role": "freelancer",
        "created_at": "2025-07-31T12:00:00Z",
        "is_active": True,
        "email_verified": True
    }

def get_test_db():
    """Отримати тестову базу даних"""
    # Створюємо mock для тестової БД
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.rollback.return_value = None
    return mock_db

def create_mock_user(user_id="test_user_123"):
    """Створити mock користувача"""
    return {
        "id": user_id,
        "email": f"{user_id}@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "freelancer",
        "created_at": "2025-07-31T12:00:00Z"
    }

def create_mock_job(job_id="job_123"):
    """Створити mock вакансію"""
    return {
        "id": job_id,
        "title": "Python Developer",
        "description": "We need a Python developer",
        "budget": {"min": 1000, "max": 5000},
        "skills": ["Python", "Django", "React"],
        "client": "Test Client",
        "posted_at": "2025-07-31T10:00:00Z"
    }

def create_mock_proposal(proposal_id="proposal_123"):
    """Створити mock пропозицію"""
    return {
        "id": proposal_id,
        "job_id": "job_123",
        "user_id": "test_user_123",
        "cover_letter": "I am interested in this position",
        "bid_amount": 3000,
        "status": "pending",
        "submitted_at": "2025-07-31T14:00:00Z"
    }

def create_mock_analytics_data():
    """Створити mock дані аналітики"""
    return {
        "earnings": {"total": 15000.0, "monthly": 5000.0},
        "proposals": {"sent": 50, "accepted": 15, "rejected": 35},
        "jobs": {"active": 5, "completed": 25, "total": 30},
        "clients": {"total": 12, "active": 8}
    }

def create_mock_notification(notification_id="notif_123"):
    """Створити mock повідомлення"""
    return {
        "id": notification_id,
        "type": "job_alert",
        "message": "New job available",
        "timestamp": "2025-07-31T12:00:00Z",
        "read": False,
        "priority": "medium"
    }

def create_mock_auth_response():
    """Створити mock відповідь авторизації"""
    return {
        "status": "success",
        "access_token": "test_token_123",
        "refresh_token": "refresh_token_123",
        "user_id": "test_user_123",
        "expires_in": 3600
    }

def create_mock_api_response(status="success", data=None, error=None):
    """Створити mock API відповідь"""
    response = {"status": status}
    if data:
        response["data"] = data
    if error:
        response["error"] = error
    return response 