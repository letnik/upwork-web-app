"""
Local Analytics Engine для обробки аналітичних даних
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random
import math

from shared.config.logging import get_logger


class AnalyticsPeriod(Enum):
    """Періоди аналітики"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class EarningsData:
    """Дані про заробіток"""
    total: float
    monthly: float
    weekly: float
    trend: float
    currency: str = "USD"


@dataclass
class ProposalData:
    """Дані про пропозиції"""
    sent: int
    accepted: int
    pending: int
    rejected: int
    success_rate: float


@dataclass
class JobData:
    """Дані про проекти"""
    applied: int
    won: int
    active: int
    completed: int
    total_earnings: float


@dataclass
class PerformanceData:
    """Дані про продуктивність"""
    rating: float
    response_time: float
    completion_rate: float
    client_satisfaction: float


@dataclass
class CategoryData:
    """Дані по категоріях"""
    name: str
    value: float
    color: str
    projects_count: int
    total_earnings: float


@dataclass
class TimeSeriesData:
    """Часові ряди"""
    date: str
    earnings: float
    proposals: int
    jobs: int
    rating: float


class AnalyticsEngine:
    """Двигун аналітики для обробки даних"""
    
    def __init__(self):
        self.logger = get_logger("analytics-engine")
        self.cache = {}
        self.cache_ttl = 300  # 5 хвилин
        
    def calculate_earnings_analytics(self, user_id: str, period: AnalyticsPeriod = AnalyticsPeriod.MONTHLY) -> EarningsData:
        """Розрахунок аналітики заробітку"""
        try:
            self.logger.info("Розрахунок аналітики заробітку", extra={
                "user_id": user_id,
                "period": period.value,
                "operation": "calculate_earnings_analytics"
            })
            
            # Імітація реальних даних
            base_earnings = random.uniform(1000, 5000)
            trend = random.uniform(-20, 30)
            
            monthly = base_earnings * (1 + random.uniform(0.1, 0.3))
            weekly = monthly / 4 * (1 + random.uniform(-0.2, 0.2))
            
            earnings_data = EarningsData(
                total=base_earnings * 12,
                monthly=monthly,
                weekly=weekly,
                trend=trend
            )
            
            self.logger.info("Аналітика заробітку розрахована", extra={
                "user_id": user_id,
                "total_earnings": earnings_data.total,
                "monthly_earnings": earnings_data.monthly,
                "trend": earnings_data.trend
            })
            
            return earnings_data
            
        except Exception as e:
            self.logger.error("Помилка розрахунку аналітики заробітку", extra={
                "user_id": user_id,
                "period": period.value,
                "error": str(e)
            })
            raise
    
    def calculate_proposals_analytics(self, user_id: str) -> ProposalData:
        """Розрахунок аналітики пропозицій"""
        try:
            sent = random.randint(20, 100)
            accepted = random.randint(5, sent // 3)
            pending = random.randint(0, sent // 4)
            rejected = sent - accepted - pending
            
            success_rate = (accepted / sent * 100) if sent > 0 else 0
            
            return ProposalData(
                sent=sent,
                accepted=accepted,
                pending=pending,
                rejected=rejected,
                success_rate=round(success_rate, 1)
            )
        except Exception as e:
            self.logger.error(f"Помилка розрахунку пропозицій: {e}")
            return ProposalData(sent=0, accepted=0, pending=0, rejected=0, success_rate=0)
    
    def calculate_jobs_analytics(self, user_id: str) -> JobData:
        """Розрахунок аналітики проектів"""
        try:
            applied = random.randint(30, 150)
            won = random.randint(5, applied // 4)
            active = random.randint(1, won // 2)
            completed = won - active
            
            total_earnings = completed * random.uniform(500, 2000)
            
            return JobData(
                applied=applied,
                won=won,
                active=active,
                completed=completed,
                total_earnings=round(total_earnings, 2)
            )
        except Exception as e:
            self.logger.error(f"Помилка розрахунку проектів: {e}")
            return JobData(applied=0, won=0, active=0, completed=0, total_earnings=0)
    
    def calculate_performance_analytics(self, user_id: str) -> PerformanceData:
        """Розрахунок аналітики продуктивності"""
        try:
            rating = random.uniform(4.0, 5.0)
            response_time = random.uniform(1.0, 5.0)
            completion_rate = random.uniform(85, 100)
            client_satisfaction = random.uniform(4.0, 5.0)
            
            return PerformanceData(
                rating=round(rating, 1),
                response_time=round(response_time, 1),
                completion_rate=round(completion_rate, 1),
                client_satisfaction=round(client_satisfaction, 1)
            )
        except Exception as e:
            self.logger.error(f"Помилка розрахунку продуктивності: {e}")
            return PerformanceData(rating=0, response_time=0, completion_rate=0, client_satisfaction=0)
    
    def calculate_category_analytics(self, user_id: str) -> List[CategoryData]:
        """Розрахунок аналітики по категоріях"""
        try:
            categories = [
                ("Web Development", "#8884d8"),
                ("Mobile Development", "#82ca9d"),
                ("Design", "#ffc658"),
                ("Writing", "#ff7300"),
                ("Data Science", "#8dd1e1"),
                ("Marketing", "#d084d0")
            ]
            
            result = []
            total_value = 100
            
            for i, (name, color) in enumerate(categories):
                if i == len(categories) - 1:
                    value = total_value
                else:
                    value = random.uniform(5, 40)
                    total_value -= value
                
                projects_count = random.randint(1, 20)
                total_earnings = projects_count * random.uniform(200, 1500)
                
                result.append(CategoryData(
                    name=name,
                    value=round(value, 1),
                    color=color,
                    projects_count=projects_count,
                    total_earnings=round(total_earnings, 2)
                ))
            
            return result
        except Exception as e:
            self.logger.error(f"Помилка розрахунку категорій: {e}")
            return []
    
    def generate_time_series_data(self, user_id: str, days: int = 30) -> List[TimeSeriesData]:
        """Генерація часових рядів"""
        try:
            data = []
            base_date = datetime.now() - timedelta(days=days)
            
            for i in range(days):
                date = base_date + timedelta(days=i)
                
                # Базові значення з трендом
                base_earnings = 100 + i * 2 + random.uniform(-20, 20)
                base_proposals = 2 + (i % 7) + random.randint(-1, 2)
                base_jobs = 1 + (i % 14) + random.randint(-1, 1)
                base_rating = 4.5 + random.uniform(-0.3, 0.3)
                
                data.append(TimeSeriesData(
                    date=date.strftime("%Y-%m-%d"),
                    earnings=round(max(0, base_earnings), 2),
                    proposals=max(0, base_proposals),
                    jobs=max(0, base_jobs),
                    rating=round(max(1, min(5, base_rating)), 1)
                ))
            
            return data
        except Exception as e:
            self.logger.error(f"Помилка генерації часових рядів: {e}")
            return []
    
    def calculate_trends(self, time_series_data: List[TimeSeriesData]) -> Dict[str, float]:
        """Розрахунок трендів"""
        try:
            if len(time_series_data) < 2:
                return {"earnings": 0, "proposals": 0, "jobs": 0, "rating": 0}
            
            # Розділяємо дані на першу та другу половину
            mid_point = len(time_series_data) // 2
            first_half = time_series_data[:mid_point]
            second_half = time_series_data[mid_point:]
            
            def calculate_average(data_list: List[TimeSeriesData], field: str) -> float:
                values = [getattr(item, field) for item in data_list]
                return sum(values) / len(values) if values else 0
            
            trends = {}
            for field in ["earnings", "proposals", "jobs", "rating"]:
                first_avg = calculate_average(first_half, field)
                second_avg = calculate_average(second_half, field)
                
                if first_avg > 0:
                    trend = ((second_avg - first_avg) / first_avg) * 100
                else:
                    trend = 0
                
                trends[field] = round(trend, 1)
            
            return trends
        except Exception as e:
            self.logger.error(f"Помилка розрахунку трендів: {e}")
            return {"earnings": 0, "proposals": 0, "jobs": 0, "rating": 0}
    
    def get_comprehensive_analytics(self, user_id: str) -> Dict[str, Any]:
        """Отримання комплексної аналітики"""
        try:
            # Розрахунок всіх метрик
            earnings = self.calculate_earnings_analytics(user_id)
            proposals = self.calculate_proposals_analytics(user_id)
            jobs = self.calculate_jobs_analytics(user_id)
            performance = self.calculate_performance_analytics(user_id)
            categories = self.calculate_category_analytics(user_id)
            time_series = self.generate_time_series_data(user_id)
            trends = self.calculate_trends(time_series)
            
            return {
                "earnings": asdict(earnings),
                "proposals": asdict(proposals),
                "jobs": asdict(jobs),
                "performance": asdict(performance),
                "categories": [asdict(cat) for cat in categories],
                "time_series": [asdict(ts) for ts in time_series],
                "trends": trends,
                "generated_at": datetime.now().isoformat(),
                "user_id": user_id
            }
        except Exception as e:
            self.logger.error(f"Помилка отримання комплексної аналітики: {e}")
            return {
                "error": "Помилка генерації аналітики",
                "user_id": user_id
            }
    
    def get_analytics_summary(self, user_id: str) -> Dict[str, Any]:
        """Отримання короткого зведення аналітики"""
        try:
            analytics = self.get_comprehensive_analytics(user_id)
            
            if "error" in analytics:
                return analytics
            
            return {
                "summary": {
                    "total_earnings": analytics["earnings"]["total"],
                    "success_rate": analytics["proposals"]["success_rate"],
                    "active_jobs": analytics["jobs"]["active"],
                    "rating": analytics["performance"]["rating"],
                    "top_category": max(analytics["categories"], key=lambda x: x["value"])["name"] if analytics["categories"] else "N/A"
                },
                "trends": analytics["trends"],
                "last_updated": analytics["generated_at"]
            }
        except Exception as e:
            self.logger.error(f"Помилка отримання зведення: {e}")
            return {"error": "Помилка генерації зведення"}
    
    def export_analytics_data(self, user_id: str, format: str = "json") -> str:
        """Експорт аналітичних даних"""
        try:
            analytics = self.get_comprehensive_analytics(user_id)
            
            if format.lower() == "json":
                return json.dumps(analytics, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Непідтримуваний формат: {format}")
        except Exception as e:
            self.logger.error(f"Помилка експорту даних: {e}")
            return json.dumps({"error": "Помилка експорту"}, indent=2)


# Глобальний екземпляр двигуна
analytics_engine = AnalyticsEngine() 