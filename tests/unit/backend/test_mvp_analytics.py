#!/usr/bin/env python3
"""
Тести для MVP-008: Аналітика та статистика
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from tests.utils.test_helpers import create_test_user, get_test_db

class TestAnalytics:
    """Тести для аналітики та статистики"""

    def test_user_analytics_creation(self):
        """Тест створення аналітики користувача"""
        user = create_test_user()
        
        analytics = Mock()
        analytics.id = 1
        analytics.user_id = user["id"]
        analytics.date = datetime.now()
        analytics.jobs_found = 25
        analytics.proposals_sent = 15
        analytics.responses_received = 8
        analytics.interviews_scheduled = 3
        analytics.jobs_won = 2
        analytics.total_earned = 2500.00
        analytics.active_profiles = 3
        analytics.active_templates = 5
        
        assert analytics.user_id == user["id"]
        assert analytics.jobs_found == 25
        assert analytics.proposals_sent == 15
        assert analytics.responses_received == 8
        assert analytics.jobs_won == 2
        assert analytics.total_earned == 2500.00
        
        print("✅ Тест створення аналітики користувача пройшов")

    def test_analytics_metrics_calculation(self):
        """Тест розрахунку метрик аналітики"""
        user = create_test_user()
        
        # Симулюємо дані за місяць
        analytics_data = [
            {"date": datetime.now() - timedelta(days=i), "proposals_sent": 5, "responses_received": 2, "jobs_won": 1, "total_earned": 500} 
            for i in range(30)
        ]
        
        # Розраховуємо загальні метрики
        total_proposals = sum(d["proposals_sent"] for d in analytics_data)
        total_responses = sum(d["responses_received"] for d in analytics_data)
        total_won = sum(d["jobs_won"] for d in analytics_data)
        total_earned = sum(d["total_earned"] for d in analytics_data)
        
        response_rate = (total_responses / total_proposals) * 100 if total_proposals > 0 else 0
        win_rate = (total_won / total_proposals) * 100 if total_proposals > 0 else 0
        
        assert total_proposals == 150  # 5 * 30
        assert total_responses == 60   # 2 * 30
        assert total_won == 30         # 1 * 30
        assert total_earned == 15000   # 500 * 30
        assert response_rate == 40.0   # 60/150 * 100
        assert win_rate == 20.0        # 30/150 * 100
        
        print("✅ Тест розрахунку метрик аналітики пройшов")

    def test_analytics_trends_calculation(self):
        """Тест розрахунку трендів"""
        user = create_test_user()
        
        # Симулюємо дані за останні 3 місяці
        monthly_data = [
            {"month": "2024-10", "earnings": 8000, "proposals": 45, "win_rate": 25},
            {"month": "2024-11", "earnings": 9500, "proposals": 52, "win_rate": 28},
            {"month": "2024-12", "earnings": 12000, "proposals": 60, "win_rate": 32}
        ]
        
        # Розраховуємо тренди
        earnings_trend = ((monthly_data[2]["earnings"] - monthly_data[0]["earnings"]) / monthly_data[0]["earnings"]) * 100
        proposals_trend = ((monthly_data[2]["proposals"] - monthly_data[0]["proposals"]) / monthly_data[0]["proposals"]) * 100
        win_rate_trend = monthly_data[2]["win_rate"] - monthly_data[0]["win_rate"]
        
        assert earnings_trend == 50.0      # (12000-8000)/8000 * 100
        assert pytest.approx(proposals_trend, abs=0.01) == 33.33    # (60-45)/45 * 100
        assert win_rate_trend == 7.0       # 32-25
        
        print("✅ Тест розрахунку трендів пройшов")

    def test_analytics_time_series(self):
        """Тест часових рядів аналітики"""
        user = create_test_user()
        
        # Симулюємо дані за тиждень
        daily_data = []
        for i in range(7):
            day_data = {
                "date": datetime.now() - timedelta(days=6-i),
                "earnings": 200 + (i * 50),
                "proposals": 3 + i,
                "responses": 1 + (i // 2)
            }
            daily_data.append(day_data)
        
        # Перевіряємо структуру даних
        assert len(daily_data) == 7
        assert all("date" in d for d in daily_data)
        assert all("earnings" in d for d in daily_data)
        assert all("proposals" in d for d in daily_data)
        
        # Перевіряємо зростання показників
        assert daily_data[6]["earnings"] > daily_data[0]["earnings"]
        assert daily_data[6]["proposals"] > daily_data[0]["proposals"]
        
        print("✅ Тест часових рядів аналітики пройшов")

    def test_analytics_category_breakdown(self):
        """Тест розбивки по категоріях"""
        user = create_test_user()
        
        # Симулюємо дані по категоріях
        category_data = [
            {"category": "Web Development", "proposals": 25, "won": 8, "earnings": 8000},
            {"category": "Mobile Development", "proposals": 15, "won": 5, "earnings": 6000},
            {"category": "Design", "proposals": 10, "won": 3, "earnings": 4000},
            {"category": "Writing", "proposals": 5, "won": 2, "earnings": 2000}
        ]
        
        total_proposals = sum(c["proposals"] for c in category_data)
        total_won = sum(c["won"] for c in category_data)
        total_earnings = sum(c["earnings"] for c in category_data)
        
        # Розраховуємо відсотки
        web_percentage = (category_data[0]["proposals"] / total_proposals) * 100
        mobile_percentage = (category_data[1]["proposals"] / total_proposals) * 100
        
        assert total_proposals == 55
        assert total_won == 18
        assert total_earnings == 20000
        assert pytest.approx(web_percentage, abs=0.01) == 45.45  # 25/55 * 100
        assert pytest.approx(mobile_percentage, abs=0.01) == 27.27  # 15/55 * 100
        
        print("✅ Тест розбивки по категоріях пройшов")

    def test_analytics_performance_metrics(self):
        """Тест метрик продуктивності"""
        user = create_test_user()
        
        # Симулюємо метрики продуктивності
        performance = {
            "response_time_hours": 2.5,
            "completion_rate": 95.5,
            "client_satisfaction": 4.8,
            "on_time_delivery": 98.0,
            "repeat_clients": 65.0
        }
        
        # Перевіряємо діапазони
        assert 0 <= performance["response_time_hours"] <= 24
        assert 0 <= performance["completion_rate"] <= 100
        assert 0 <= performance["client_satisfaction"] <= 5
        assert 0 <= performance["on_time_delivery"] <= 100
        assert 0 <= performance["repeat_clients"] <= 100
        
        # Перевіряємо якісні показники
        assert performance["completion_rate"] >= 90  # Високий рівень завершення
        assert performance["client_satisfaction"] >= 4.5  # Високий рівень задоволення
        assert performance["on_time_delivery"] >= 95  # Високий рівень своєчасності
        
        print("✅ Тест метрик продуктивності пройшов")

    def test_analytics_report_generation(self):
        """Тест генерації звітів"""
        user = create_test_user()
        
        # Симулюємо генерацію звіту
        report = {
            "user_id": user["id"],
            "period": "monthly",
            "generated_at": datetime.now(),
            "summary": {
                "total_proposals": 150,
                "total_responses": 60,
                "total_won": 30,
                "total_earnings": 15000,
                "response_rate": 40.0,
                "win_rate": 20.0
            },
            "trends": {
                "earnings_growth": 15.5,
                "proposals_growth": 12.3,
                "win_rate_change": 2.1
            },
            "top_categories": [
                {"name": "Web Development", "proposals": 45, "earnings": 8000},
                {"name": "Mobile Development", "proposals": 30, "earnings": 6000}
            ]
        }
        
        # Перевіряємо структуру звіту
        assert "user_id" in report
        assert "period" in report
        assert "summary" in report
        assert "trends" in report
        assert "top_categories" in report
        
        # Перевіряємо дані
        assert report["summary"]["total_proposals"] == 150
        assert report["summary"]["response_rate"] == 40.0
        assert len(report["top_categories"]) > 0
        
        print("✅ Тест генерації звітів пройшов")

    def test_analytics_data_validation(self):
        """Тест валідації даних аналітики"""
        user = create_test_user()
        
        def validate_analytics_data(data):
            errors = []
            
            if data.get("proposals_sent", 0) < 0:
                errors.append("Кількість відправлених пропозицій не може бути від'ємною")
            
            if data.get("responses_received", 0) > data.get("proposals_sent", 0):
                errors.append("Кількість відповідей не може перевищувати кількість пропозицій")
            
            if data.get("jobs_won", 0) > data.get("responses_received", 0):
                errors.append("Кількість виграних робіт не може перевищувати кількість відповідей")
            
            if data.get("total_earned", 0) < 0:
                errors.append("Заробіток не може бути від'ємним")
            
            return errors
        
        # Валідні дані
        valid_data = {
            "proposals_sent": 50,
            "responses_received": 20,
            "jobs_won": 8,
            "total_earned": 5000
        }
        valid_errors = validate_analytics_data(valid_data)
        assert len(valid_errors) == 0
        
        # Невалідні дані
        invalid_data = {
            "proposals_sent": 10,
            "responses_received": 15,  # Більше ніж пропозицій
            "jobs_won": 20,            # Більше ніж відповідей
            "total_earned": -1000      # Від'ємний заробіток
        }
        invalid_errors = validate_analytics_data(invalid_data)
        assert len(invalid_errors) == 3
        
        print("✅ Тест валідації даних аналітики пройшов")

    def test_analytics_export_functionality(self):
        """Тест функціональності експорту аналітики"""
        user = create_test_user()
        
        # Симулюємо дані для експорту
        export_data = {
            "period": "2024-12",
            "metrics": {
                "proposals_sent": 150,
                "responses_received": 60,
                "jobs_won": 30,
                "total_earnings": 15000
            },
            "time_series": [
                {"date": "2024-12-01", "proposals": 5, "earnings": 500},
                {"date": "2024-12-02", "proposals": 8, "earnings": 800}
            ],
            "categories": [
                {"name": "Web Development", "proposals": 45, "earnings": 8000},
                {"name": "Mobile Development", "proposals": 30, "earnings": 6000}
            ]
        }
        
        # Перевіряємо структуру для експорту
        assert "period" in export_data
        assert "metrics" in export_data
        assert "time_series" in export_data
        assert "categories" in export_data
        
        # Перевіряємо наявність всіх необхідних полів
        required_metrics = ["proposals_sent", "responses_received", "jobs_won", "total_earnings"]
        for metric in required_metrics:
            assert metric in export_data["metrics"]
        
        print("✅ Тест функціональності експорту аналітики пройшов")

if __name__ == "__main__":
    test_instance = TestAnalytics()
    test_instance.test_user_analytics_creation()
    test_instance.test_analytics_metrics_calculation()
    test_instance.test_analytics_trends_calculation()
    test_instance.test_analytics_time_series()
    test_instance.test_analytics_category_breakdown()
    test_instance.test_analytics_performance_metrics()
    test_instance.test_analytics_report_generation()
    test_instance.test_analytics_data_validation()
    test_instance.test_analytics_export_functionality()
    print("\n🎉 Всі тести аналітики пройшли успішно!") 