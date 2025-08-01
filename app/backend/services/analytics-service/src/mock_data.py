"""
Мок дані для тестування аналітики
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import asdict

from shared.config.logging import get_logger


class MockDataGenerator:
    """Генератор мок даних для аналітики"""
    
    def __init__(self):
        self.logger = get_logger("mock-data-generator")
        
    def generate_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Генерація аналітичних даних користувача"""
        try:
            self.logger.info("Генерація мок даних для користувача", extra={
                "user_id": user_id,
                "days": days,
                "operation": "generate_user_analytics"
            })
            
            # Генерація даних про заробіток
            earnings_data = {
                "total_earnings": round(random.uniform(5000, 50000), 2),
                "monthly_earnings": round(random.uniform(1000, 8000), 2),
                "weekly_earnings": round(random.uniform(200, 2000), 2),
                "trend": round(random.uniform(-15, 25), 1),
                "currency": "USD"
            }
            
            # Генерація даних про пропозиції
            proposals_data = {
                "sent": random.randint(50, 200),
                "accepted": random.randint(10, 50),
                "pending": random.randint(5, 20),
                "rejected": random.randint(20, 80),
                "success_rate": round(random.uniform(0.1, 0.4), 2)
            }
            
            # Генерація даних про проекти
            jobs_data = {
                "applied": random.randint(30, 100),
                "won": random.randint(5, 25),
                "active": random.randint(1, 8),
                "completed": random.randint(10, 40),
                "total_earnings": round(random.uniform(3000, 30000), 2)
            }
            
            # Генерація даних про продуктивність
            performance_data = {
                "rating": round(random.uniform(4.0, 5.0), 1),
                "response_time": round(random.uniform(1, 24), 1),
                "completion_rate": round(random.uniform(0.8, 1.0), 2),
                "client_satisfaction": round(random.uniform(4.0, 5.0), 1)
            }
            
            # Генерація часових рядів
            time_series_data = self._generate_time_series_data(days)
            
            # Генерація даних по категоріях
            categories_data = self._generate_categories_data()
            
            analytics_data = {
                "user_id": user_id,
                "earnings": earnings_data,
                "proposals": proposals_data,
                "jobs": jobs_data,
                "performance": performance_data,
                "time_series": time_series_data,
                "categories": categories_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info("Мок дані згенеровані успішно", extra={
                "user_id": user_id,
                "total_earnings": earnings_data["total_earnings"],
                "proposals_sent": proposals_data["sent"],
                "jobs_won": jobs_data["won"]
            })
            
            return analytics_data
            
        except Exception as e:
            self.logger.error("Помилка генерації мок даних", extra={
                "user_id": user_id,
                "error": str(e)
            })
            raise
    
    def _generate_time_series_data(self, days: int) -> List[Dict[str, Any]]:
        """Генерація часових рядів"""
        time_series = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            time_series.append({
                "date": date.strftime("%Y-%m-%d"),
                "earnings": round(random.uniform(100, 2000), 2),
                "proposals": random.randint(1, 10),
                "jobs": random.randint(0, 5)
            })
        return time_series
    
    def _generate_categories_data(self) -> List[Dict[str, Any]]:
        """Генерація даних по категоріях"""
        categories = [
            "Web Development",
            "Mobile Development", 
            "Design & Creative",
            "Writing & Translation",
            "Digital Marketing",
            "Data Science & Analytics"
        ]
        
        categories_data = []
        for category in categories:
            value = round(random.uniform(1000, 10000), 2)
            categories_data.append({
                "name": category,
                "value": value,
                "percentage": round(random.uniform(5, 30), 1)
            })
        return categories_data 