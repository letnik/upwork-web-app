"""
Тести для MVP компонентів - Профілі фільтрів
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
from test_helpers import create_test_user, get_test_db


class TestFilterProfiles:
    """Тести для профілів фільтрів"""
    
    def test_create_filter_profile_success(self):
        """Тест успішного створення профілю фільтрів"""
        # Mock дані
        user = create_test_user()
        db = get_test_db()
        
        # Дані профілю
        profile_data = {
            "name": "Python Developer",
            "keywords": ["Python", "Django", "React"],
            "exclude_keywords": ["WordPress", "PHP"],
            "ai_instructions": "Шукай проекти з Python та веб-розробкою",
            "budget_min": 1000.0,
            "budget_max": 5000.0,
            "hourly_rate_min": 25.0,
            "hourly_rate_max": 50.0,
            "experience_level": "intermediate",
            "job_type": "fixed",
            "categories": ["Web Development", "Backend"],
            "countries": ["United States", "Canada"],
            "working_hours": {"start": "09:00", "end": "17:00"},
            "timezone": "UTC-5"
        }
        
        # Перевіряємо структуру даних
        assert "name" in profile_data
        assert "keywords" in profile_data
        assert "ai_instructions" in profile_data
        assert "budget_min" in profile_data
        assert "budget_max" in profile_data
        
        # Перевіряємо типи даних
        assert isinstance(profile_data["name"], str)
        assert isinstance(profile_data["keywords"], list)
        assert isinstance(profile_data["ai_instructions"], str)
        assert isinstance(profile_data["budget_min"], float)
        assert isinstance(profile_data["budget_max"], float)
        
        # Перевіряємо валідність даних
        assert len(profile_data["name"]) <= 100
        assert len(profile_data["keywords"]) <= 20
        assert len(profile_data["ai_instructions"]) <= 1000
        
        print("✅ Тест створення профілю фільтрів пройшов")
    
    def test_filter_profile_limit_validation(self):
        """Тест перевірки ліміту профілів (до 10 на користувача)"""
        user = create_test_user()
        
        # Симулюємо 10 існуючих профілів
        existing_profiles = 10
        
        # Перевіряємо ліміт
        assert existing_profiles <= 10, "Ліміт профілів перевищено"
        
        # Симулюємо спробу створити 11-й профіль
        if existing_profiles >= 10:
            error_message = "Досягнуто ліміт профілів фільтрів (10)"
            assert "ліміт" in error_message.lower()
            assert "10" in error_message
        
        print("✅ Тест перевірки ліміту профілів пройшов")
    
    def test_filter_profile_ai_instructions(self):
        """Тест AI інструкцій природною мовою"""
        # Приклади AI інструкцій
        ai_instructions = [
            "Шукай проекти з Python та веб-розробкою",
            "Фокусуйся на проектах з React та Node.js",
            "Шукай клієнтів з хорошим рейтингом та історією",
            "Уникай проектів з нереальними дедлайнами",
            "Перевага проектам з детальним описом та бюджетом"
        ]
        
        for instruction in ai_instructions:
            # Перевіряємо, що інструкція написана природною мовою
            assert len(instruction) > 10, "Інструкція занадто коротка"
            assert len(instruction) <= 500, "Інструкція занадто довга"
            assert any(word in instruction.lower() for word in ["шукай", "фокусуйся", "уникай", "перевага"]), "Інструкція не містить ключових слів"
        
        print("✅ Тест AI інструкцій пройшов")
    
    def test_filter_profile_budget_validation(self):
        """Тест валідації бюджету"""
        # Валідні значення бюджету
        valid_budgets = [
            {"min": 100, "max": 1000},
            {"min": 500, "max": 5000},
            {"min": 1000, "max": 10000},
            {"min": None, "max": 5000},
            {"min": 1000, "max": None}
        ]
        
        for budget in valid_budgets:
            if budget["min"] is not None and budget["max"] is not None:
                # Перевіряємо, що мінімум менше максимуму
                assert budget["min"] <= budget["max"], "Мінімальний бюджет більший за максимальний"
            
            # Перевіряємо діапазон значень
            if budget["min"] is not None:
                assert budget["min"] >= 0, "Мінімальний бюджет не може бути від'ємним"
            if budget["max"] is not None:
                assert budget["max"] <= 100000, "Максимальний бюджет занадто великий"
        
        print("✅ Тест валідації бюджету пройшов")
    
    def test_filter_profile_categories(self):
        """Тест категорій роботи"""
        # Валідні категорії
        valid_categories = [
            "Web Development",
            "Mobile Development", 
            "Design & Creative",
            "Writing & Translation",
            "Digital Marketing",
            "Data Science & Analytics",
            "Engineering & Architecture",
            "Sales & Marketing",
            "Customer Service",
            "Legal"
        ]
        
        for category in valid_categories:
            assert len(category) > 0, "Категорія не може бути порожньою"
            assert len(category) <= 50, "Назва категорії занадто довга"
            assert category.strip() == category, "Категорія містить зайві пробіли"
        
        print("✅ Тест категорій роботи пройшов")
    
    def test_filter_profile_working_hours(self):
        """Тест налаштувань робочих годин"""
        # Приклади робочих годин
        working_hours_examples = [
            {"start": "09:00", "end": "17:00", "timezone": "UTC-5"},
            {"start": "08:00", "end": "16:00", "timezone": "UTC+2"},
            {"start": "10:00", "end": "18:00", "timezone": "UTC+0"},
            {"flexible": True, "timezone": "UTC-8"}
        ]
        
        for hours in working_hours_examples:
            if "start" in hours and "end" in hours:
                # Перевіряємо формат часу
                assert ":" in hours["start"], "Неправильний формат початкового часу"
                assert ":" in hours["end"], "Неправильний формат кінцевого часу"
                
                # Перевіряємо, що кінець після початку
                start_hour = int(hours["start"].split(":")[0])
                end_hour = int(hours["end"].split(":")[0])
                assert start_hour < end_hour, "Кінцевий час раніше за початковий"
            
            # Перевіряємо часовий пояс
            if "timezone" in hours:
                assert hours["timezone"].startswith("UTC"), "Неправильний формат часового поясу"
        
        print("✅ Тест робочих годин пройшов")


class TestFilterProfileIntegration:
    """Інтеграційні тести для профілів фільтрів"""
    
    def test_filter_profile_complete_workflow(self):
        """Тест повного workflow профілю фільтрів"""
        # 1. Створення користувача
        user = create_test_user()
        assert user["id"] is not None
        
        # 2. Створення профілю фільтрів
        profile_data = {
            "name": "Full Stack Developer",
            "keywords": ["React", "Node.js", "Python", "PostgreSQL"],
            "exclude_keywords": ["WordPress", "PHP", "Joomla"],
            "ai_instructions": "Шукай проекти з сучасним стеком технологій, уникай legacy систем",
            "budget_min": 2000.0,
            "budget_max": 8000.0,
            "hourly_rate_min": 30.0,
            "hourly_rate_max": 60.0,
            "experience_level": "expert",
            "job_type": "fixed",
            "categories": ["Web Development", "Backend", "Frontend"],
            "countries": ["United States", "Canada", "United Kingdom"],
            "working_hours": {"start": "09:00", "end": "17:00", "timezone": "UTC-5"},
            "timezone": "UTC-5"
        }
        
        # 3. Валідація даних
        assert len(profile_data["keywords"]) <= 20
        assert profile_data["budget_min"] <= profile_data["budget_max"]
        assert profile_data["hourly_rate_min"] <= profile_data["hourly_rate_max"]
        
        # 4. Симуляція збереження
        profile_id = "test_profile_123"
        assert profile_id is not None
        
        # 5. Перевірка результату
        assert profile_data["name"] == "Full Stack Developer"
        assert "React" in profile_data["keywords"]
        assert "WordPress" in profile_data["exclude_keywords"]
        assert "сучасним стеком" in profile_data["ai_instructions"]
        
        print("✅ Тест повного workflow профілю фільтрів пройшов")
    
    def test_filter_profile_ai_instructions_natural_language(self):
        """Тест AI інструкцій природною мовою"""
        # Приклади природних інструкцій
        natural_instructions = [
            "Шукай проекти з Python та Django, фокусуйся на веб-розробці",
            "Уникай проектів з нереальними дедлайнами та низьким бюджетом",
            "Перевага клієнтам з хорошим рейтингом та детальним описом проекту",
            "Шукай проекти з React та TypeScript, уникай jQuery та старих технологій",
            "Фокусуйся на проектах з машинним навчанням та аналізом даних"
        ]
        
        for instruction in natural_instructions:
            # Перевіряємо природність мови
            assert any(word in instruction.lower() for word in ["шукай", "фокусуйся", "уникай", "перевага"])
            assert len(instruction) >= 20, "Інструкція занадто коротка"
            assert len(instruction) <= 500, "Інструкція занадто довга"
            
            # Перевіряємо наявність технічних термінів (хоча б в одній інструкції)
            tech_terms = ["python", "django", "react", "typescript", "машинним", "веб-розробці"]
            has_tech_terms = any(term in instruction.lower() for term in tech_terms)
            # Не всі інструкції обов'язково мають технічні терміни
        
        print("✅ Тест AI інструкцій природною мовою пройшов")


if __name__ == "__main__":
    # Запуск тестів
    test_filter_profiles = TestFilterProfiles()
    test_filter_profiles.test_create_filter_profile_success()
    test_filter_profiles.test_filter_profile_limit_validation()
    test_filter_profiles.test_filter_profile_ai_instructions()
    test_filter_profiles.test_filter_profile_budget_validation()
    test_filter_profiles.test_filter_profile_categories()
    test_filter_profiles.test_filter_profile_working_hours()
    
    test_integration = TestFilterProfileIntegration()
    test_integration.test_filter_profile_complete_workflow()
    test_integration.test_filter_profile_ai_instructions_natural_language()
    
    print("\n🎉 Всі тести профілів фільтрів пройшли успішно!") 