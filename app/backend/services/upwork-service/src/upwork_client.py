"""
Upwork API Client для роботи з Upwork API
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared'))

try:
    from shared.config.logging import get_logger
    from shared.utils.encryption import decrypt_data
except ImportError:
    # Fallback для тестування
    import logging
    def get_logger(name):
        return logging.getLogger(name)
    
    def decrypt_data(data):
        return data  # Простий fallback

logger = get_logger("upwork-client")


class UpworkAPIClient:
    """Клієнт для роботи з Upwork API"""
    
    def __init__(self, access_token: str, base_url: str = "https://api.upwork.com/api/v3"):
        self.access_token = access_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Upwork-AI-Assistant/1.0'
        })
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit = 100  # requests per hour
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Виконання запиту з обробкою помилок та rate limiting"""
        try:
            # Rate limiting
            if self.request_count >= self.rate_limit:
                logger.warning("Rate limit досягнуто")
                raise Exception("Rate limit exceeded")
            
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            
            self.request_count += 1
            self.last_request_time = datetime.utcnow()
            
            if response.status_code == 401:
                logger.error("Unauthorized - можливо токен закінчився")
                raise Exception("Token expired or invalid")
            
            if response.status_code == 429:
                logger.warning("Rate limit exceeded")
                raise Exception("Rate limit exceeded")
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Помилка запиту до Upwork API: {e}")
            raise
    
    def get_user_profile(self) -> Dict:
        """Отримання профілю користувача"""
        logger.info("Отримання профілю користувача")
        return self._make_request('GET', '/freelancers/me')
    
    def search_jobs(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """Пошук вакансій"""
        logger.info(f"Пошук вакансій: {query}")
        
        params = {'q': query}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/jobs/search', params=params)
    
    def get_job_details(self, job_id: str) -> Dict:
        """Деталі вакансії"""
        logger.info(f"Отримання деталей вакансії: {job_id}")
        return self._make_request('GET', f'/jobs/{job_id}')
    
    def submit_proposal(self, job_id: str, proposal_data: Dict) -> Dict:
        """Відправка відгуку"""
        logger.info(f"Відправка відгуку на вакансію: {job_id}")
        return self._make_request('POST', f'/jobs/{job_id}/proposals', json=proposal_data)
    
    def get_messages(self, thread_id: Optional[str] = None) -> Dict:
        """Отримання повідомлень"""
        logger.info("Отримання повідомлень")
        
        params = {}
        if thread_id:
            params['thread_id'] = thread_id
        
        return self._make_request('GET', '/messages', params=params)
    
    def send_message(self, thread_id: str, message: str) -> Dict:
        """Відправка повідомлення"""
        logger.info(f"Відправка повідомлення в thread: {thread_id}")
        
        data = {
            'thread_id': thread_id,
            'message': message
        }
        
        return self._make_request('POST', '/messages', json=data)
    
    def get_client_info(self, client_id: str) -> Dict:
        """Інформація про клієнта"""
        logger.info(f"Отримання інформації про клієнта: {client_id}")
        return self._make_request('GET', f'/clients/{client_id}')
    
    def get_freelancer_profile(self, freelancer_id: str) -> Dict:
        """Профіль фрілансера"""
        logger.info(f"Отримання профілю фрілансера: {freelancer_id}")
        return self._make_request('GET', f'/freelancers/{freelancer_id}')
    
    def get_categories(self) -> Dict:
        """Список категорій"""
        logger.info("Отримання списку категорій")
        return self._make_request('GET', '/categories')
    
    def get_skills(self) -> Dict:
        """Список навичок"""
        logger.info("Отримання списку навичок")
        return self._make_request('GET', '/skills')
    
    def get_workdiary(self, freelancer_id: str, date: Optional[str] = None) -> Dict:
        """Отримання work diary"""
        logger.info(f"Отримання work diary для фрілансера: {freelancer_id}")
        
        params = {}
        if date:
            params['date'] = date
        
        return self._make_request('GET', f'/workdiaries/{freelancer_id}', params=params)
    
    def get_contracts(self) -> Dict:
        """Отримання контрактів"""
        logger.info("Отримання контрактів")
        return self._make_request('GET', '/contracts')
    
    def get_earnings(self, freelancer_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict:
        """Отримання заробітку"""
        logger.info(f"Отримання заробітку для фрілансера: {freelancer_id}")
        
        params = {}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        return self._make_request('GET', f'/earnings/{freelancer_id}', params=params)


class UpworkAPIManager:
    """Менеджер для роботи з Upwork API через OAuth токени"""
    
    def __init__(self, db_session, user_id: str):
        self.db = db_session
        self.user_id = user_id
        self.client = None
    
    def _get_valid_access_token(self) -> str:
        """Отримання дійсного access token"""
        from app.backend.services.auth_service.src.models import OAuthConnection
        
        connection = self.db.query(OAuthConnection).filter(
            OAuthConnection.user_id == self.user_id,
            OAuthConnection.provider == "upwork",
            OAuthConnection.is_active == True
        ).first()
        
        if not connection:
            raise Exception("Upwork не підключено")
        
        # Перевіряємо чи не закінчився термін дії
        if connection.expires_at <= datetime.utcnow():
            # Оновлюємо токен
            from app.backend.services.auth_service.src.oauth import refresh_upwork_token
            refresh_upwork_token()
            
            # Отримуємо оновлений токен
            connection = self.db.query(OAuthConnection).filter(
                OAuthConnection.user_id == self.user_id,
                OAuthConnection.provider == "upwork",
                OAuthConnection.is_active == True
            ).first()
        
        return decrypt_data(connection.access_token)
    
    def get_client(self) -> UpworkAPIClient:
        """Отримання API клієнта"""
        if not self.client:
            access_token = self._get_valid_access_token()
            self.client = UpworkAPIClient(access_token)
        
        return self.client
    
    def search_jobs(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """Пошук вакансій"""
        client = self.get_client()
        return client.search_jobs(query, filters)
    
    def get_job_details(self, job_id: str) -> Dict:
        """Деталі вакансії"""
        client = self.get_client()
        return client.get_job_details(job_id)
    
    def submit_proposal(self, job_id: str, proposal_data: Dict) -> Dict:
        """Відправка відгуку"""
        client = self.get_client()
        return client.submit_proposal(job_id, proposal_data)
    
    def get_user_profile(self) -> Dict:
        """Профіль користувача"""
        client = self.get_client()
        return client.get_user_profile()
    
    def get_messages(self, thread_id: Optional[str] = None) -> Dict:
        """Повідомлення"""
        client = self.get_client()
        return client.get_messages(thread_id)
    
    def send_message(self, thread_id: str, message: str) -> Dict:
        """Відправка повідомлення"""
        client = self.get_client()
        return client.send_message(thread_id, message)


# Тестові дані для розробки
class MockUpworkAPIClient:
    """Mock клієнт для тестування без реального API"""
    
    def __init__(self, access_token: str = "test_token"):
        self.access_token = access_token
        logger.info("Використовується MockUpworkAPIClient")
    
    def get_user_profile(self) -> Dict:
        """Mock профіль користувача - відповідає реальному Upwork API"""
        return {
            "id": "~0123456789012345",
            "name": "John Doe",
            "title": "Full Stack Developer",
            "description": "Experienced full stack developer with 5+ years of experience in web development, specializing in Python, React, and cloud technologies.",
            "skills": [
                {"skill": "python", "level": "expert"},
                {"skill": "react", "level": "expert"},
                {"skill": "node.js", "level": "intermediate"},
                {"skill": "postgresql", "level": "intermediate"},
                {"skill": "aws", "level": "intermediate"},
                {"skill": "docker", "level": "intermediate"},
                {"skill": "typescript", "level": "intermediate"},
                {"skill": "fastapi", "level": "expert"}
            ],
            "hourly_rate": 35.0,
            "total_earnings": 45000.0,
            "success_rate": 98.0,
            "member_since": "2020-01-15T00:00:00Z",
            "location": "Ukraine",
            "timezone": "UTC+2",
            "availability": "full-time",
            "profile_photo": "https://example.com/photo.jpg",
            "portfolio_items": [
                {
                    "id": "portfolio_1",
                    "title": "E-commerce Platform",
                    "description": "Full stack e-commerce platform built with React and Python",
                    "url": "https://example.com/project1"
                },
                {
                    "id": "portfolio_2", 
                    "title": "API Gateway",
                    "description": "Microservices API gateway with authentication and rate limiting",
                    "url": "https://example.com/project2"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Developer",
                    "issuer": "Amazon Web Services",
                    "date": "2023-06-15"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "Technical University",
                    "year": 2019
                }
            ],
            "languages": [
                {"language": "English", "level": "Native"},
                {"language": "Ukrainian", "level": "Native"},
                {"language": "Russian", "level": "Fluent"}
            ],
            "verification_status": "verified",
            "profile_completion": 95,
            "response_time": "2 hours",
            "total_jobs": 25,
            "total_hours": 1200,
            "feedback_score": 4.9,
            "reviews_count": 18
        }
    
    def search_jobs(self, query: str, filters: Optional[Dict] = None) -> Dict:
        """Mock пошук вакансій - відповідає реальному Upwork API"""
        return {
            "jobs": [
                {
                    "id": "~0123456789012345",
                    "title": "Python Developer Needed for Web Application",
                    "description": "We need an experienced Python developer to help us build a modern web application using FastAPI and PostgreSQL. The project involves creating REST APIs, database design, and integration with third-party services.",
                    "budget": {
                        "min": 1000,
                        "max": 5000,
                        "type": "fixed"
                    },
                    "client": {
                        "id": "~0123456789012346",
                        "name": "Tech Solutions Inc",
                        "rating": 4.8,
                        "reviews_count": 15,
                        "total_spent": 50000,
                        "location": "United States"
                    },
                    "skills": ["python", "fastapi", "postgresql", "rest api", "docker"],
                    "posted_time": "2024-01-15T10:30:00Z",
                    "category": "Web Development",
                    "subcategory": "Web Programming",
                    "experience_level": "intermediate",
                    "project_length": "3-6 months",
                    "hours_per_week": "10-30 hrs/week",
                    "job_type": "hourly",
                    "url": "https://www.upwork.com/jobs/~0123456789012345",
                    "proposals_count": 8,
                    "client_hires": 5,
                    "payment_verified": True,
                    "preferred_qualifications": ["Experience with AWS", "Knowledge of React"],
                    "attachments": [],
                    "enterprise_job": False,
                    "job_status": "open"
                },
                {
                    "id": "~0123456789012347",
                    "title": "React Frontend Developer for Mobile App",
                    "description": "Looking for a skilled React developer to help us build a mobile application using React Native. The app will include user authentication, real-time messaging, and payment integration.",
                    "budget": {
                        "min": 2000,
                        "max": 8000,
                        "type": "fixed"
                    },
                    "client": {
                        "id": "~0123456789012348",
                        "name": "Startup Innovations",
                        "rating": 4.5,
                        "reviews_count": 8,
                        "total_spent": 25000,
                        "location": "Canada"
                    },
                    "skills": ["react", "react native", "typescript", "mobile development", "firebase"],
                    "posted_time": "2024-01-14T15:30:00Z",
                    "category": "Mobile Development",
                    "subcategory": "Mobile App Development",
                    "experience_level": "expert",
                    "project_length": "1-3 months",
                    "hours_per_week": "20-40 hrs/week",
                    "job_type": "hourly",
                    "url": "https://www.upwork.com/jobs/~0123456789012347",
                    "proposals_count": 12,
                    "client_hires": 3,
                    "payment_verified": True,
                    "preferred_qualifications": ["Experience with Redux", "Knowledge of iOS/Android"],
                    "attachments": [],
                    "enterprise_job": False,
                    "job_status": "open"
                },
                {
                    "id": "~0123456789012349",
                    "title": "Full Stack Developer for E-commerce Platform",
                    "description": "We need a full stack developer to build a complete e-commerce platform from scratch. The platform should include user management, product catalog, shopping cart, payment processing, and admin dashboard.",
                    "budget": {
                        "min": 5000,
                        "max": 15000,
                        "type": "fixed"
                    },
                    "client": {
                        "id": "~0123456789012350",
                        "name": "E-commerce Solutions",
                        "rating": 4.9,
                        "reviews_count": 25,
                        "total_spent": 100000,
                        "location": "United Kingdom"
                    },
                    "skills": ["python", "django", "react", "postgresql", "stripe", "aws"],
                    "posted_time": "2024-01-13T09:15:00Z",
                    "category": "Web Development",
                    "subcategory": "E-commerce Development",
                    "experience_level": "expert",
                    "project_length": "6+ months",
                    "hours_per_week": "30-40 hrs/week",
                    "job_type": "hourly",
                    "url": "https://www.upwork.com/jobs/~0123456789012349",
                    "proposals_count": 5,
                    "client_hires": 8,
                    "payment_verified": True,
                    "preferred_qualifications": ["Experience with Shopify", "Knowledge of SEO"],
                    "attachments": [],
                    "enterprise_job": False,
                    "job_status": "open"
                }
            ],
            "paging": {
                "total": 1500,
                "offset": 0,
                "count": 20
            }
        }
    
    def get_job_details(self, job_id: str) -> Dict:
        """Mock деталі вакансії - відповідає реальному Upwork API"""
        # Симулюємо різні вакансії на основі ID
        job_templates = {
            "~0123456789012345": {
                "id": "~0123456789012345",
                "title": "Python Developer Needed for Web Application",
                "description": "We need an experienced Python developer to help us build a modern web application using FastAPI and PostgreSQL. The project involves creating REST APIs, database design, and integration with third-party services.\n\nKey Responsibilities:\n- Design and implement REST APIs using FastAPI\n- Design database schema and implement with PostgreSQL\n- Integrate with third-party services (payment, email, etc.)\n- Write unit tests and integration tests\n- Deploy application to cloud infrastructure\n\nRequirements:\n- 3+ years experience with Python\n- Experience with FastAPI or similar frameworks\n- Strong knowledge of PostgreSQL\n- Experience with Docker and cloud deployment\n- Good communication skills\n\nThis is a long-term project with potential for ongoing work.",
                "budget": {
                    "min": 1000,
                    "max": 5000,
                    "type": "fixed"
                },
                "client": {
                    "id": "~0123456789012346",
                    "name": "Tech Solutions Inc",
                    "rating": 4.8,
                    "reviews_count": 15,
                    "total_spent": 50000,
                    "location": "United States",
                    "member_since": "2020-03-15T00:00:00Z",
                    "hire_rate": 85,
                    "avg_hourly_rate": 45,
                    "total_hired": 12
                },
                "skills": ["python", "fastapi", "postgresql", "rest api", "docker", "aws"],
                "posted_time": "2024-01-15T10:30:00Z",
                "category": "Web Development",
                "subcategory": "Web Programming",
                "experience_level": "intermediate",
                "project_length": "3-6 months",
                "hours_per_week": "10-30 hrs/week",
                "job_type": "hourly",
                "url": "https://www.upwork.com/jobs/~0123456789012345",
                "proposals_count": 8,
                "client_hires": 5,
                "payment_verified": True,
                "preferred_qualifications": ["Experience with AWS", "Knowledge of React", "CI/CD experience"],
                "attachments": [],
                "enterprise_job": False,
                "job_status": "open",
                "visibility": "public",
                "timezone": "UTC-5",
                "contractor_tier": "intermediate",
                "client_feedback": "Great communication and quality work",
                "project_type": "ongoing",
                "verification_status": "verified"
            }
        }
        
        # Повертаємо шаблон або створюємо базовий
        if job_id in job_templates:
            return job_templates[job_id]
        else:
            return {
                "id": job_id,
                "title": "Sample Job",
                "description": "This is a sample job description for testing purposes.",
                "budget": {
                    "min": 1000,
                    "max": 3000,
                    "type": "fixed"
                },
                "client": {
                    "id": "~0123456789012346",
                    "name": "Sample Client",
                    "rating": 4.5,
                    "reviews_count": 10,
                    "total_spent": 25000,
                    "location": "United States"
                },
                "skills": ["python", "javascript", "html", "css"],
                "posted_time": "2024-01-15T10:30:00Z",
                "category": "Web Development",
                "subcategory": "Web Programming",
                "experience_level": "intermediate",
                "project_length": "1-3 months",
                "hours_per_week": "10-20 hrs/week",
                "job_type": "hourly",
                "url": f"https://www.upwork.com/jobs/{job_id}",
                "proposals_count": 5,
                "client_hires": 3,
                "payment_verified": True,
                "preferred_qualifications": [],
                "attachments": [],
                "enterprise_job": False,
                "job_status": "open"
            }
    
    def submit_proposal(self, job_id: str, proposal_data: Dict) -> Dict:
        """Mock відправка відгуку"""
        logger.info(f"Mock відправка відгуку на вакансію {job_id}")
        return {
            "success": True,
            "proposal_id": f"proposal_{job_id}_{datetime.utcnow().timestamp()}",
            "message": "Proposal submitted successfully"
        }
    
    def get_messages(self, thread_id: Optional[str] = None) -> Dict:
        """Mock повідомлення"""
        return {
            "messages": [
                {
                    "id": "msg_1",
                    "thread_id": thread_id or "thread_1",
                    "sender": "client_1",
                    "content": "Hi, I'm interested in your proposal",
                    "timestamp": "2024-01-15T12:00:00Z"
                }
            ]
        }
    
    def send_message(self, thread_id: str, message: str) -> Dict:
        """Mock відправка повідомлення"""
        logger.info(f"Mock відправка повідомлення в thread {thread_id}")
        return {
            "success": True,
            "message_id": f"msg_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_client_info(self, client_id: str) -> Dict:
        """Mock інформація про клієнта - відповідає реальному Upwork API"""
        client_templates = {
            "~0123456789012346": {
                "id": "~0123456789012346",
                "name": "Tech Solutions Inc",
                "rating": 4.8,
                "reviews_count": 15,
                "total_spent": 50000,
                "location": "United States",
                "member_since": "2020-03-15T00:00:00Z",
                "hire_rate": 85,
                "avg_hourly_rate": 45,
                "total_hired": 12,
                "description": "Technology company specializing in web and mobile development",
                "company_size": "10-49 employees",
                "industry": "Technology",
                "payment_verified": True,
                "verification_status": "verified",
                "timezone": "UTC-5",
                "preferred_freelancer_location": ["United States", "Ukraine", "India"],
                "preferred_hourly_rate": {"min": 25, "max": 75},
                "total_jobs_posted": 25,
                "active_jobs": 3,
                "avg_project_size": 5000,
                "response_time": "2 hours",
                "communication_style": "professional",
                "project_types": ["web-development", "mobile-development", "api-development"]
            },
            "~0123456789012348": {
                "id": "~0123456789012348",
                "name": "Startup Innovations",
                "rating": 4.5,
                "reviews_count": 8,
                "total_spent": 25000,
                "location": "Canada",
                "member_since": "2021-06-10T00:00:00Z",
                "hire_rate": 75,
                "avg_hourly_rate": 35,
                "total_hired": 5,
                "description": "Innovative startup focused on mobile applications",
                "company_size": "1-9 employees",
                "industry": "Technology",
                "payment_verified": True,
                "verification_status": "verified",
                "timezone": "UTC-6",
                "preferred_freelancer_location": ["Canada", "United States", "Ukraine"],
                "preferred_hourly_rate": {"min": 20, "max": 60},
                "total_jobs_posted": 12,
                "active_jobs": 2,
                "avg_project_size": 4000,
                "response_time": "4 hours",
                "communication_style": "casual",
                "project_types": ["mobile-development", "ui-ux-design"]
            }
        }
        
        if client_id in client_templates:
            return client_templates[client_id]
        else:
            return {
                "id": client_id,
                "name": "Sample Client",
                "rating": 4.5,
                "reviews_count": 10,
                "total_spent": 25000,
                "location": "United States",
                "member_since": "2020-01-01T00:00:00Z",
                "hire_rate": 80,
                "avg_hourly_rate": 40,
                "total_hired": 8
            }
    
    def get_freelancer_profile(self, freelancer_id: str) -> Dict:
        """Mock профіль фрілансера - відповідає реальному Upwork API"""
        freelancer_templates = {
            "~0123456789012345": {
                "id": "~0123456789012345",
                "name": "John Doe",
                "title": "Full Stack Developer",
                "description": "Experienced full stack developer with 5+ years of experience",
                "skills": [
                    {"skill": "python", "level": "expert"},
                    {"skill": "react", "level": "expert"},
                    {"skill": "node.js", "level": "intermediate"}
                ],
                "hourly_rate": 35.0,
                "total_earnings": 45000.0,
                "success_rate": 98.0,
                "member_since": "2020-01-15T00:00:00Z",
                "location": "Ukraine",
                "timezone": "UTC+2",
                "availability": "full-time",
                "verification_status": "verified",
                "profile_completion": 95,
                "response_time": "2 hours",
                "total_jobs": 25,
                "total_hours": 1200,
                "feedback_score": 4.9,
                "reviews_count": 18,
                "portfolio_items": [
                    {
                        "id": "portfolio_1",
                        "title": "E-commerce Platform",
                        "description": "Full stack e-commerce platform",
                        "url": "https://example.com/project1"
                    }
                ],
                "certifications": [
                    {
                        "name": "AWS Certified Developer",
                        "issuer": "Amazon Web Services",
                        "date": "2023-06-15"
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Computer Science",
                        "institution": "Technical University",
                        "year": 2019
                    }
                ],
                "languages": [
                    {"language": "English", "level": "Native"},
                    {"language": "Ukrainian", "level": "Native"}
                ]
            }
        }
        
        if freelancer_id in freelancer_templates:
            return freelancer_templates[freelancer_id]
        else:
            return {
                "id": freelancer_id,
                "name": "Sample Freelancer",
                "title": "Developer",
                "description": "Sample freelancer profile",
                "skills": [{"skill": "python", "level": "intermediate"}],
                "hourly_rate": 25.0,
                "total_earnings": 15000.0,
                "success_rate": 95.0,
                "member_since": "2021-01-01T00:00:00Z",
                "location": "United States",
                "timezone": "UTC-5",
                "availability": "part-time",
                "verification_status": "verified",
                "profile_completion": 85,
                "response_time": "4 hours",
                "total_jobs": 10,
                "total_hours": 500,
                "feedback_score": 4.7,
                "reviews_count": 8
            }
    
    def get_categories(self) -> Dict:
        """Mock категорії вакансій - відповідає реальному Upwork API"""
        return {
            "categories": [
                {
                    "id": "web-development",
                    "name": "Web Development",
                    "subcategories": [
                        {"id": "web-programming", "name": "Web Programming"},
                        {"id": "e-commerce-development", "name": "E-commerce Development"},
                        {"id": "web-design", "name": "Web Design"}
                    ]
                },
                {
                    "id": "mobile-development",
                    "name": "Mobile Development",
                    "subcategories": [
                        {"id": "mobile-app-development", "name": "Mobile App Development"},
                        {"id": "ios-development", "name": "iOS Development"},
                        {"id": "android-development", "name": "Android Development"}
                    ]
                },
                {
                    "id": "data-science",
                    "name": "Data Science",
                    "subcategories": [
                        {"id": "machine-learning", "name": "Machine Learning"},
                        {"id": "data-analysis", "name": "Data Analysis"},
                        {"id": "artificial-intelligence", "name": "Artificial Intelligence"}
                    ]
                },
                {
                    "id": "design-creative",
                    "name": "Design & Creative",
                    "subcategories": [
                        {"id": "ui-ux-design", "name": "UI/UX Design"},
                        {"id": "graphic-design", "name": "Graphic Design"},
                        {"id": "logo-design", "name": "Logo Design"}
                    ]
                },
                {
                    "id": "writing",
                    "name": "Writing",
                    "subcategories": [
                        {"id": "content-writing", "name": "Content Writing"},
                        {"id": "copywriting", "name": "Copywriting"},
                        {"id": "technical-writing", "name": "Technical Writing"}
                    ]
                }
            ]
        }
    
    def get_skills(self) -> Dict:
        """Mock навички - відповідає реальному Upwork API"""
        return {
            "skills": [
                {"id": "python", "name": "Python", "category": "Programming"},
                {"id": "javascript", "name": "JavaScript", "category": "Programming"},
                {"id": "react", "name": "React", "category": "Programming"},
                {"id": "node-js", "name": "Node.js", "category": "Programming"},
                {"id": "postgresql", "name": "PostgreSQL", "category": "Databases"},
                {"id": "mongodb", "name": "MongoDB", "category": "Databases"},
                {"id": "aws", "name": "Amazon Web Services", "category": "Cloud Computing"},
                {"id": "docker", "name": "Docker", "category": "DevOps"},
                {"id": "kubernetes", "name": "Kubernetes", "category": "DevOps"},
                {"id": "ui-ux-design", "name": "UI/UX Design", "category": "Design"},
                {"id": "graphic-design", "name": "Graphic Design", "category": "Design"},
                {"id": "content-writing", "name": "Content Writing", "category": "Writing"},
                {"id": "copywriting", "name": "Copywriting", "category": "Writing"},
                {"id": "data-analysis", "name": "Data Analysis", "category": "Data Science"},
                {"id": "machine-learning", "name": "Machine Learning", "category": "Data Science"}
            ]
        }
    
    def get_workdiary(self, freelancer_id: str, date: Optional[str] = None) -> Dict:
        """Mock робочий щоденник - відповідає реальному Upwork API"""
        if not date:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        return {
            "workdiary": {
                "freelancer_id": freelancer_id,
                "date": date,
                "entries": [
                    {
                        "id": "entry_1",
                        "contract_id": "contract_1",
                        "job_title": "Web Development Project",
                        "hours": 8.0,
                        "description": "Developed REST API endpoints and database schema",
                        "start_time": f"{date}T09:00:00Z",
                        "end_time": f"{date}T17:00:00Z",
                        "activity": "development",
                        "status": "approved"
                    },
                    {
                        "id": "entry_2",
                        "contract_id": "contract_2",
                        "job_title": "Mobile App Development",
                        "hours": 4.0,
                        "description": "Implemented user authentication and profile features",
                        "start_time": f"{date}T18:00:00Z",
                        "end_time": f"{date}T22:00:00Z",
                        "activity": "development",
                        "status": "pending"
                    }
                ],
                "total_hours": 12.0,
                "total_approved_hours": 8.0,
                "total_pending_hours": 4.0
            }
        }
    
    def get_contracts(self) -> Dict:
        """Mock контракти - відповідає реальному Upwork API"""
        return {
            "contracts": [
                {
                    "id": "contract_1",
                    "job_id": "~0123456789012345",
                    "job_title": "Python Developer Needed for Web Application",
                    "client_id": "~0123456789012346",
                    "client_name": "Tech Solutions Inc",
                    "freelancer_id": "~0123456789012345",
                    "freelancer_name": "John Doe",
                    "start_date": "2024-01-01T00:00:00Z",
                    "end_date": None,
                    "status": "active",
                    "type": "hourly",
                    "hourly_rate": 35.0,
                    "total_hours": 120.0,
                    "total_amount": 4200.0,
                    "timezone": "UTC-5",
                    "payment_terms": "weekly",
                    "visibility": "public",
                    "description": "Full stack web development project",
                    "skills": ["python", "fastapi", "postgresql", "react"],
                    "milestones": [
                        {
                            "id": "milestone_1",
                            "title": "API Development",
                            "description": "Develop REST API endpoints",
                            "amount": 2000.0,
                            "due_date": "2024-02-01T00:00:00Z",
                            "status": "completed"
                        },
                        {
                            "id": "milestone_2",
                            "title": "Frontend Development",
                            "description": "Develop React frontend",
                            "amount": 2200.0,
                            "due_date": "2024-03-01T00:00:00Z",
                            "status": "in_progress"
                        }
                    ]
                },
                {
                    "id": "contract_2",
                    "job_id": "~0123456789012347",
                    "job_title": "React Frontend Developer for Mobile App",
                    "client_id": "~0123456789012348",
                    "client_name": "Startup Innovations",
                    "freelancer_id": "~0123456789012345",
                    "freelancer_name": "John Doe",
                    "start_date": "2024-01-15T00:00:00Z",
                    "end_date": None,
                    "status": "active",
                    "type": "fixed",
                    "total_amount": 5000.0,
                    "timezone": "UTC-6",
                    "payment_terms": "milestone",
                    "visibility": "public",
                    "description": "Mobile app development with React Native",
                    "skills": ["react", "react native", "typescript", "firebase"],
                    "milestones": [
                        {
                            "id": "milestone_3",
                            "title": "Authentication System",
                            "description": "Implement user authentication",
                            "amount": 1500.0,
                            "due_date": "2024-02-15T00:00:00Z",
                            "status": "completed"
                        },
                        {
                            "id": "milestone_4",
                            "title": "Core Features",
                            "description": "Implement core app features",
                            "amount": 2000.0,
                            "due_date": "2024-03-15T00:00:00Z",
                            "status": "in_progress"
                        },
                        {
                            "id": "milestone_5",
                            "title": "Testing & Deployment",
                            "description": "Testing and app store deployment",
                            "amount": 1500.0,
                            "due_date": "2024-04-15T00:00:00Z",
                            "status": "pending"
                        }
                    ]
                }
            ]
        }
    
    def get_earnings(self, freelancer_id: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict:
        """Mock заробіток - відповідає реальному Upwork API"""
        if not from_date:
            from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        return {
            "earnings": {
                "freelancer_id": freelancer_id,
                "period": {
                    "from_date": from_date,
                    "to_date": to_date
                },
                "summary": {
                    "total_earnings": 4500.0,
                    "total_hours": 120.0,
                    "avg_hourly_rate": 37.5,
                    "total_projects": 3,
                    "active_contracts": 2
                },
                "breakdown": [
                    {
                        "contract_id": "contract_1",
                        "job_title": "Python Developer Needed for Web Application",
                        "client_name": "Tech Solutions Inc",
                        "earnings": 2800.0,
                        "hours": 80.0,
                        "rate": 35.0,
                        "type": "hourly"
                    },
                    {
                        "contract_id": "contract_2",
                        "job_title": "React Frontend Developer for Mobile App",
                        "client_name": "Startup Innovations",
                        "earnings": 1700.0,
                        "hours": 40.0,
                        "rate": 42.5,
                        "type": "hourly"
                    }
                ],
                "currency": "USD",
                "payment_method": "paypal",
                "next_payment_date": "2024-02-01T00:00:00Z"
            }
        } 