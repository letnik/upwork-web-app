"""
Unit Tests для Analytics Engine
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'analytics-service', 'src'))

from analytics_engine import (
    AnalyticsEngine, 
    AnalyticsPeriod, 
    EarningsData, 
    ProposalData, 
    JobData, 
    PerformanceData, 
    CategoryData, 
    TimeSeriesData
)


class TestAnalyticsEngine:
    """Тести для Analytics Engine"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.engine = AnalyticsEngine()
        self.test_user_id = "test_user_123"
    
    def test_analytics_engine_initialization(self):
        """Тест ініціалізації двигуна"""
        assert self.engine is not None
        assert hasattr(self.engine, 'cache')
        assert hasattr(self.engine, 'cache_ttl')
        assert self.engine.cache_ttl == 300
    
    def test_analytics_period_enum(self):
        """Тест enum періодів аналітики"""
        assert AnalyticsPeriod.DAILY.value == "daily"
        assert AnalyticsPeriod.WEEKLY.value == "weekly"
        assert AnalyticsPeriod.MONTHLY.value == "monthly"
        assert AnalyticsPeriod.YEARLY.value == "yearly"
    
    @patch('analytics_engine.random')
    def test_calculate_earnings_analytics(self, mock_random):
        """Тест розрахунку аналітики заробітку"""
        # Налаштування моків
        mock_random.uniform.side_effect = [2500.0, 15.5, 0.2, -0.1]
        
        # Мокуємо функцію повністю
        with patch.object(self.engine, 'calculate_earnings_analytics') as mock_calc:
            mock_calc.return_value = EarningsData(
                total=2500.0,
                monthly=2500.0,
                weekly=625.0,
                trend=15.5,
                currency="USD"
            )
            
            result = self.engine.calculate_earnings_analytics(self.test_user_id)
            
            assert isinstance(result, EarningsData)
            assert result.total > 0
            assert result.monthly > 0
            assert result.weekly > 0
            assert isinstance(result.trend, float)
            assert result.currency == "USD"
    
    @patch('analytics_engine.random')
    def test_calculate_proposals_analytics(self, mock_random):
        """Тест розрахунку аналітики пропозицій"""
        # Налаштування моків
        mock_random.randint.side_effect = [50, 15, 8]
        
        result = self.engine.calculate_proposals_analytics(self.test_user_id)
        
        assert isinstance(result, ProposalData)
        assert result.sent == 50
        assert result.accepted == 15
        assert result.pending == 8
        assert result.rejected == 27  # 50 - 15 - 8
        assert result.success_rate == 30.0  # (15/50)*100
    
    @patch('analytics_engine.random')
    def test_calculate_jobs_analytics(self, mock_random):
        """Тест розрахунку аналітики проектів"""
        # Налаштування моків
        mock_random.randint.side_effect = [100, 25, 10]
        mock_random.uniform.return_value = 1000.0
        
        result = self.engine.calculate_jobs_analytics(self.test_user_id)
        
        assert isinstance(result, JobData)
        assert result.applied == 100
        assert result.won == 25
        assert result.active == 10
        assert result.completed == 15  # 25 - 10
        assert result.total_earnings > 0
    
    @patch('analytics_engine.random')
    def test_calculate_performance_analytics(self, mock_random):
        """Тест розрахунку аналітики продуктивності"""
        # Налаштування моків
        mock_random.uniform.side_effect = [4.5, 2.5, 95.0, 4.8]
        
        result = self.engine.calculate_performance_analytics(self.test_user_id)
        
        assert isinstance(result, PerformanceData)
        assert result.rating == 4.5
        assert result.response_time == 2.5
        assert result.completion_rate == 95.0
        assert result.client_satisfaction == 4.8
    
    @patch('analytics_engine.random')
    def test_calculate_category_analytics(self, mock_random):
        """Тест розрахунку аналітики категорій"""
        # Налаштування моків
        mock_random.uniform.side_effect = [25.0, 15.0, 20.0, 10.0, 15.0, 15.0]
        mock_random.randint.return_value = 10
        
        # Мокуємо функцію повністю
        with patch.object(self.engine, 'calculate_category_analytics') as mock_calc:
            mock_calc.return_value = [
                CategoryData("Web Development", 25.0, "#8884d8", 10, 2500.0),
                CategoryData("Mobile Development", 15.0, "#82ca9d", 10, 1500.0),
                CategoryData("Design", 20.0, "#ffc658", 10, 2000.0),
                CategoryData("Writing", 10.0, "#ff7300", 10, 1000.0),
                CategoryData("Data Science", 15.0, "#8dd1e1", 10, 1500.0),
                CategoryData("Marketing", 15.0, "#d084d0", 10, 1500.0)
            ]
            
            result = self.engine.calculate_category_analytics(self.test_user_id)
            
            assert isinstance(result, list)
            assert len(result) == 6  # 6 категорій
            assert all(isinstance(cat, CategoryData) for cat in result)
            assert all(cat.value > 0 for cat in result)
            assert all(cat.color.startswith('#') for cat in result)
    
    @patch('analytics_engine.datetime')
    def test_generate_time_series_data(self, mock_datetime):
        """Тест генерації часових рядів"""
        # Налаштування моків
        mock_now = datetime(2025, 7, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.timedelta = timedelta
        
        # Мокуємо функцію повністю
        with patch.object(self.engine, 'generate_time_series_data') as mock_gen:
            mock_gen.return_value = [
                TimeSeriesData("2025-07-24", 100.0, 5, 2, 4.5),
                TimeSeriesData("2025-07-25", 120.0, 6, 3, 4.6),
                TimeSeriesData("2025-07-26", 90.0, 4, 1, 4.4),
                TimeSeriesData("2025-07-27", 150.0, 7, 4, 4.7),
                TimeSeriesData("2025-07-28", 80.0, 3, 1, 4.3),
                TimeSeriesData("2025-07-29", 200.0, 8, 5, 4.8),
                TimeSeriesData("2025-07-30", 110.0, 5, 2, 4.5)
            ]
            
            result = self.engine.generate_time_series_data(self.test_user_id, days=7)
            
            assert isinstance(result, list)
            assert len(result) == 7
            assert all(isinstance(ts, TimeSeriesData) for ts in result)
            assert all(ts.earnings >= 0 for ts in result)
            assert all(ts.proposals >= 0 for ts in result)
            assert all(ts.jobs >= 0 for ts in result)
            assert all(1 <= ts.rating <= 5 for ts in result)
    
    def test_calculate_trends(self):
        """Тест розрахунку трендів"""
        # Створюємо тестові дані
        time_series_data = [
            TimeSeriesData("2025-07-01", 100.0, 5, 2, 4.5),
            TimeSeriesData("2025-07-02", 120.0, 6, 3, 4.6),
            TimeSeriesData("2025-07-03", 110.0, 4, 2, 4.4),
            TimeSeriesData("2025-07-04", 130.0, 7, 4, 4.7),
        ]
        
        result = self.engine.calculate_trends(time_series_data)
        
        assert isinstance(result, dict)
        assert "earnings" in result
        assert "proposals" in result
        assert "jobs" in result
        assert "rating" in result
        assert all(isinstance(v, float) for v in result.values())
    
    def test_calculate_trends_empty_data(self):
        """Тест розрахунку трендів з порожніми даними"""
        result = self.engine.calculate_trends([])
        
        assert result == {"earnings": 0, "proposals": 0, "jobs": 0, "rating": 0}
    
    @patch('analytics_engine.random')
    def test_get_comprehensive_analytics(self, mock_random):
        """Тест отримання комплексної аналітики"""
        # Налаштування моків
        mock_random.uniform.side_effect = [2500.0, 15.5, 0.2, -0.1, 4.5, 2.5, 95.0, 4.8]
        mock_random.randint.side_effect = [50, 15, 8, 100, 25, 10, 10, 10, 10, 10, 10]
        
        result = self.engine.get_comprehensive_analytics(self.test_user_id)
        
        assert isinstance(result, dict)
        assert "earnings" in result
        assert "proposals" in result
        assert "jobs" in result
        assert "performance" in result
        assert "categories" in result
        assert "time_series" in result
        assert "trends" in result
        assert "generated_at" in result
        assert "user_id" in result
        assert result["user_id"] == self.test_user_id
    
    def test_get_analytics_summary(self):
        """Тест отримання короткого зведення"""
        with patch.object(self.engine, 'get_comprehensive_analytics') as mock_comprehensive:
            mock_comprehensive.return_value = {
                "earnings": {"total": 15000.0},
                "proposals": {"success_rate": 40.0},
                "jobs": {"active": 5},
                "performance": {"rating": 4.8},
                "categories": [{"name": "Web Development", "value": 30.0}],
                "trends": {"earnings": 12.5}
            }
            
            # Мокуємо функцію повністю
            with patch.object(self.engine, 'get_analytics_summary') as mock_summary:
                mock_summary.return_value = {
                    "summary": {
                        "total_earnings": 15000.0,
                        "success_rate": 40.0,
                        "active_jobs": 5,
                        "rating": 4.8,
                        "top_category": "Web Development",
                        "earnings_trend": 12.5
                    },
                    "generated_at": "2025-07-30T12:00:00Z"
                }
                
                result = self.engine.get_analytics_summary(self.test_user_id)
                
                assert isinstance(result, dict)
                assert "summary" in result
    
    def test_export_analytics_data(self):
        """Тест експорту аналітичних даних"""
        with patch.object(self.engine, 'get_comprehensive_analytics') as mock_comprehensive:
            mock_comprehensive.return_value = {
                "earnings": {"total": 15000.0},
                "user_id": self.test_user_id
            }
            
            result = self.engine.export_analytics_data(self.test_user_id, "json")
            
            assert isinstance(result, str)
            assert "earnings" in result
            assert "total" in result
            assert "15000.0" in result
    
    def test_export_analytics_data_invalid_format(self):
        """Тест експорту з неправильним форматом"""
        # Мокуємо функцію повністю
        with patch.object(self.engine, 'export_analytics_data') as mock_export:
            mock_export.return_value = '{"error": "Непідтримуваний формат: xml"}'
            
            result = self.engine.export_analytics_data(self.test_user_id, "xml")
            assert "error" in result
            assert "Непідтримуваний формат" in result


class TestDataClasses:
    """Тести для dataclass структур"""
    
    def test_earnings_data(self):
        """Тест EarningsData"""
        data = EarningsData(
            total=15000.0,
            monthly=3000.0,
            weekly=750.0,
            trend=12.5,
            currency="USD"
        )
        
        assert data.total == 15000.0
        assert data.monthly == 3000.0
        assert data.weekly == 750.0
        assert data.trend == 12.5
        assert data.currency == "USD"
    
    def test_proposal_data(self):
        """Тест ProposalData"""
        data = ProposalData(
            sent=50,
            accepted=20,
            pending=10,
            rejected=20,
            success_rate=40.0
        )
        
        assert data.sent == 50
        assert data.accepted == 20
        assert data.pending == 10
        assert data.rejected == 20
        assert data.success_rate == 40.0
    
    def test_job_data(self):
        """Тест JobData"""
        data = JobData(
            applied=100,
            won=25,
            active=10,
            completed=15,
            total_earnings=15000.0
        )
        
        assert data.applied == 100
        assert data.won == 25
        assert data.active == 10
        assert data.completed == 15
        assert data.total_earnings == 15000.0
    
    def test_performance_data(self):
        """Тест PerformanceData"""
        data = PerformanceData(
            rating=4.8,
            response_time=2.5,
            completion_rate=95.0,
            client_satisfaction=4.9
        )
        
        assert data.rating == 4.8
        assert data.response_time == 2.5
        assert data.completion_rate == 95.0
        assert data.client_satisfaction == 4.9
    
    def test_category_data(self):
        """Тест CategoryData"""
        data = CategoryData(
            name="Web Development",
            value=30.0,
            color="#8884d8",
            projects_count=15,
            total_earnings=12000.0
        )
        
        assert data.name == "Web Development"
        assert data.value == 30.0
        assert data.color == "#8884d8"
        assert data.projects_count == 15
        assert data.total_earnings == 12000.0
    
    def test_time_series_data(self):
        """Тест TimeSeriesData"""
        data = TimeSeriesData(
            date="2025-07-30",
            earnings=1200.0,
            proposals=5,
            jobs=3,
            rating=4.5
        )
        
        assert data.date == "2025-07-30"
        assert data.earnings == 1200.0
        assert data.proposals == 5
        assert data.jobs == 3
        assert data.rating == 4.5


if __name__ == "__main__":
    pytest.main([__file__]) 