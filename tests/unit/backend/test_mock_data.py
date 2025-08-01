"""
Unit Tests для Mock Data Generator
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'services', 'analytics-service', 'src'))

from mock_data import MockDataGenerator


class TestMockDataGenerator:
    """Тести для Mock Data Generator"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.generator = MockDataGenerator()
        self.test_user_id = "test_user_123"
    
    def test_mock_data_generator_initialization(self):
        """Тест ініціалізації генератора"""
        assert self.generator is not None
        assert hasattr(self.generator, 'logger')
    
    @patch('mock_data.random')
    def test_generate_user_analytics(self, mock_random):
        """Тест генерації аналітичних даних користувача"""
        # Налаштування моків для всіх викликів random
        mock_random.uniform.side_effect = [
            15000.0, 3000.0, 750.0, 12.5,  # earnings
            0.25,  # success_rate
            1000.0,  # jobs total_earnings
            4.8, 2.5, 0.95, 4.9,  # performance
            # time_series (30 днів * 3 значення = 90 викликів)
            *[1200.0 for _ in range(30)],  # earnings для кожного дня
            *[5 for _ in range(30)],  # proposals для кожного дня  
            *[3 for _ in range(30)],  # jobs для кожного дня
            # categories (6 категорій * 2 значення = 12 викликів)
            *[30.0 for _ in range(6)],  # value для кожної категорії
            *[15.0 for _ in range(6)]   # percentage для кожної категорії
        ]
        mock_random.randint.side_effect = [
            100, 25, 10, 30, 15, 5,  # proposals
            30, 15, 5,  # jobs
            # time_series (30 днів * 2 значення = 60 викликів)
            *[5 for _ in range(30)],  # proposals для кожного дня
            *[3 for _ in range(30)]   # jobs для кожного дня
        ]
        mock_random.choice.return_value = "Web Development"
        
        result = self.generator.generate_user_analytics(self.test_user_id)
        
        assert isinstance(result, dict)
        assert result["user_id"] == self.test_user_id
        assert "earnings" in result
        assert "proposals" in result
        assert "jobs" in result
        assert "performance" in result
        assert "time_series" in result
        assert "categories" in result
        assert "generated_at" in result
    
    def test_generate_user_analytics_with_different_days(self):
        """Тест генерації з різною кількістю днів"""
        result = self.generator.generate_user_analytics(self.test_user_id, days=7)
        
        assert isinstance(result, dict)
        assert result["user_id"] == self.test_user_id
        assert "time_series" in result
        assert len(result["time_series"]) == 7
    
    def test_generate_user_analytics_error_handling(self):
        """Тест обробки помилок"""
        # Тестуємо з невалідним user_id
        result = self.generator.generate_user_analytics("")
        
        assert isinstance(result, dict)
        assert result["user_id"] == ""


class TestMockDataErrorHandling:
    """Тести для обробки помилок"""
    
    def setup_method(self):
        """Налаштування перед кожним тестом"""
        self.generator = MockDataGenerator()
        self.test_user_id = "test_user_123"
    
    @patch('mock_data.random')
    def test_generate_user_analytics_error_handling(self, mock_random):
        """Тест обробки помилок при генерації даних"""
        # Симулюємо помилку
        mock_random.uniform.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            self.generator.generate_user_analytics(self.test_user_id)
    
    def test_generate_user_analytics_with_none_user_id(self):
        """Тест з None user_id"""
        result = self.generator.generate_user_analytics(None)
        
        assert isinstance(result, dict)
        assert result["user_id"] is None 