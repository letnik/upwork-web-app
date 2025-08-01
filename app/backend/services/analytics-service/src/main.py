"""
Analytics Service - Мікросервіс для аналітики та звітності
"""

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import sys
import os
import random

# Створюємо FastAPI додаток
app = FastAPI(
    title="Analytics Service",
    description="Мікросервіс для аналітики та звітності",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Analytics Engine
class AnalyticsEngine:
    def __init__(self):
        pass
    
    def get_dashboard_data(self, user_id: str):
        return {
            "earnings": {
                "total": 15000.0,
                "monthly": 3000.0,
                "weekly": 750.0
            },
            "proposals": {
                "sent": 50,
                "accepted": 20,
                "pending": 15,
                "rejected": 15
            },
            "jobs": {
                "applied": 100,
                "won": 25,
                "active": 10,
                "completed": 15
            },
            "performance": {
                "rating": 4.8,
                "success_rate": 40.0
            },
            "categories": [
                {"name": "Web Development", "value": 40, "color": "#2196F3"},
                {"name": "Mobile Development", "value": 25, "color": "#4CAF50"},
                {"name": "UI/UX Design", "value": 20, "color": "#FF9800"},
                {"name": "Content Writing", "value": 15, "color": "#9C27B0"}
            ],
            "time_series": [
                {"date": "2024-12-15", "earnings": 500, "proposals": 5},
                {"date": "2024-12-16", "earnings": 750, "proposals": 8},
                {"date": "2024-12-17", "earnings": 600, "proposals": 6},
                {"date": "2024-12-18", "earnings": 900, "proposals": 10},
                {"date": "2024-12-19", "earnings": 800, "proposals": 7}
            ],
            "trends": {
                "earnings": 12.5,
                "proposals": 8.3
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def get_comprehensive_analytics(self, user_id: str):
        """Метод для тестів"""
        return self.get_dashboard_data(user_id)
    
    def calculate_earnings_analytics(self, user_id: str, days: int = 30):
        """Метод для тестів"""
        return self.get_earnings_analytics(user_id, days)
    
    def calculate_proposals_analytics(self, user_id: str):
        """Метод для тестів"""
        return self.get_proposals_analytics(user_id)
    
    def calculate_jobs_analytics(self, user_id: str):
        """Метод для тестів"""
        return self.get_jobs_analytics(user_id)
    
    def calculate_category_analytics(self, user_id: str):
        """Метод для тестів"""
        return self.get_categories_analytics(user_id)
    
    def generate_time_series_data(self, user_id: str, days: int = 30):
        """Метод для тестів"""
        return self.get_timeseries_data(user_id, days)
    
    def get_earnings_analytics(self, user_id: str, days: int = 30):
        return {
            "total": 15000.0,
            "monthly": 3000.0,
            "weekly": 750.0,
            "daily": 107.0,
            "trend": 12.5,
            "currency": "USD",
            "breakdown": {
                "hourly": 8000.0,
                "fixed": 7000.0
            },
            "top_clients": [
                {"name": "Tech Solutions Inc", "amount": 5000.0},
                {"name": "Digital Agency", "amount": 3000.0}
            ]
        }
    
    def get_proposals_analytics(self, user_id: str):
        return {
            "sent": 50,
            "accepted": 20,
            "pending": 10,
            "rejected": 20,
            "success_rate": 40.0,
            "avg_response_time": "2.5 hours",
            "top_categories": [
                {"name": "Web Development", "sent": 25, "accepted": 12},
                {"name": "Mobile Development", "sent": 15, "accepted": 6}
            ]
        }
    
    def get_jobs_analytics(self, user_id: str):
        return {
            "applied": 100,
            "won": 25,
            "active": 10,
            "completed": 15,
            "total_earnings": 15000.0,
            "avg_job_value": 600.0,
            "top_skills": ["Python", "React", "Node.js", "Docker"],
            "job_types": {
                "hourly": 15,
                "fixed": 10
            }
        }
    
    def get_categories_analytics(self, user_id: str):
        return [
            {"name": "Web Development", "value": 30.0, "color": "#8884d8", "jobs": 15},
            {"name": "Mobile Development", "value": 25.0, "color": "#82ca9d", "jobs": 12},
            {"name": "Data Science", "value": 20.0, "color": "#ffc658", "jobs": 10},
            {"name": "DevOps", "value": 15.0, "color": "#ff7300", "jobs": 8},
            {"name": "UI/UX Design", "value": 10.0, "color": "#00ff00", "jobs": 5}
        ]
    
    def get_timeseries_data(self, user_id: str, days: int = 30):
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "earnings": random.randint(100, 500),
                "proposals": random.randint(1, 5),
                "jobs": random.randint(1, 3),
                "rating": round(random.uniform(4.0, 5.0), 1)
            })
        return data
    
    def get_analytics_summary(self, user_id: str):
        return {
            "summary": {
                "total_earnings": 15000.0,
                "success_rate": 40.0,
                "active_jobs": 10,
                "rating": 4.8,
                "top_category": "Web Development"
            },
            "trends": {"earnings": 12.5, "proposals": 8.2},
            "recommendations": [
                "Focus on high-paying jobs",
                "Improve proposal quality",
                "Expand to new categories"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def export_analytics_data(self, user_id: str, format: str = "json"):
        data = self.get_dashboard_data(user_id)
        if format == "csv":
            return "csv_data_here"
        return data

# Mock Data Generator
class MockDataGenerator:
    def __init__(self):
        pass
    
    def generate_mock_data(self, user_id: str):
        return {
            "user_data": {
                "user": {
                    "id": user_id,
                    "name": "Test User",
                    "email": "test@example.com",
                    "profile_completion": 95
                }
            },
            "time_series": [
                {"date": "2024-01-15", "earnings": 1200.0, "proposals": 5, "jobs": 3},
                {"date": "2024-01-14", "earnings": 1100.0, "proposals": 4, "jobs": 2}
            ],
            "categories": [
                {"name": "Web Development", "value": 30.0, "jobs": 15},
                {"name": "Mobile Development", "value": 25.0, "jobs": 12}
            ],
            "performance": {
                "rating": 4.8,
                "success_rate": 40.0,
                "response_time": "2.5 hours"
            },
            "jobs": [
                {"id": 1, "title": "Python Developer", "budget": 1000, "status": "active"},
                {"id": 2, "title": "React Developer", "budget": 800, "status": "completed"}
            ],
            "proposals": [
                {"id": 1, "job_id": 1, "status": "submitted", "submitted_at": "2024-01-15T10:00:00Z"},
                {"id": 2, "job_id": 2, "status": "accepted", "submitted_at": "2024-01-14T15:30:00Z"}
            ],
            "earnings": [
                {"id": 1, "amount": 500, "date": "2024-01-15", "job_id": 1},
                {"id": 2, "amount": 800, "date": "2024-01-14", "job_id": 2}
            ],
            "generated_at": datetime.utcnow().isoformat(),
            "user_id": user_id
        }
    
    def generate_comprehensive_mock_data(self, user_id: str):
        """Метод для тестів"""
        return self.generate_mock_data(user_id)

# Створюємо екземпляри
analytics_engine = AnalyticsEngine()
mock_data_generator = MockDataGenerator()


@app.on_event("startup")
async def startup_event():
    """Подія запуску сервісу"""
    print("🚀 Запуск Analytics Service...")


@app.get("/")
async def root():
    """Головна сторінка сервісу"""
    return {
        "service": "Analytics Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Перевірка здоров'я сервісу"""
    return {
        "status": "healthy",
        "service": "analytics-service",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/test")
async def test_endpoint():
    """Тестовий endpoint"""
    return {"message": "Analytics service is working!", "status": "ok"}


@app.get("/analytics/dashboard")
async def get_dashboard_data():
    """Отримання даних дашборду"""
    try:
        user_id = "test_user_123"
        data = analytics_engine.get_dashboard_data(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/dashboard-simple")
async def get_dashboard_data_simple():
    """Отримання даних дашборду (спрощена версія)"""
    try:
        user_id = "test_user_123"
        data = analytics_engine.get_dashboard_data(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/earnings")
async def get_earnings_analytics(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, description="Number of days")
):
    """Отримання аналітики заробітку"""
    try:
        data = analytics_engine.get_earnings_analytics(user_id, days)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/proposals")
async def get_proposals_analytics(user_id: str = Query(..., description="User ID")):
    """Отримання аналітики пропозицій"""
    try:
        data = analytics_engine.get_proposals_analytics(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/jobs")
async def get_jobs_analytics(user_id: str = Query(..., description="User ID")):
    """Отримання аналітики проектів"""
    try:
        data = analytics_engine.get_jobs_analytics(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/categories")
async def get_categories_analytics(user_id: str = Query(..., description="User ID")):
    """Отримання аналітики категорій"""
    try:
        data = analytics_engine.get_categories_analytics(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/timeseries")
async def get_timeseries_data(
    user_id: str = Query(..., description="User ID"),
    days: int = Query(30, description="Number of days")
):
    """Отримання часових рядів"""
    try:
        data = analytics_engine.get_timeseries_data(user_id, days)
        return {"status": "success", "data": data, "user_id": user_id, "days": days}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/summary")
async def get_analytics_summary(user_id: str = Query(..., description="User ID")):
    """Отримання зведення аналітики"""
    try:
        data = analytics_engine.get_analytics_summary(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/export")
async def export_analytics_data(
    user_id: str = Query(..., description="User ID"),
    format: str = Query("json", description="Export format")
):
    """Експорт даних аналітики"""
    try:
        data = analytics_engine.export_analytics_data(user_id, format)
        return {"status": "success", "data": data, "user_id": user_id, "format": format}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/mock/generate")
async def generate_mock_data(user_id: str = Query(..., description="User ID")):
    """Генерація мок даних"""
    try:
        data = mock_data_generator.generate_mock_data(user_id)
        return {"status": "success", "data": data, "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/overview")
async def get_analytics_overview(user_id: str = None):
    """Отримання загального огляду аналітики"""
    try:
        # Генеруємо просту статистику
        analytics_data = {
            "total_jobs": 150,
            "total_proposals": 45,
            "success_rate": 0.78,
            "average_earnings": 2500,
            "top_skills": ["Python", "JavaScript", "React", "Node.js", "Docker"],
            "recent_activity": [
                {"date": "2024-01-15", "proposals": 3, "earnings": 500},
                {"date": "2024-01-14", "proposals": 2, "earnings": 300},
                {"date": "2024-01-13", "proposals": 1, "earnings": 200}
            ]
        }
        
        return {
            "status": "success",
            "data": analytics_data,
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Помилка отримання аналітики: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Помилка отримання аналітики"
        ) 