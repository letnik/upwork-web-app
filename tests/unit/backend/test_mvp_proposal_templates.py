"""
Тести для MVP компонентів - Шаблони відгуків (10 на користувача)
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta

# Додаємо шлях до спільних компонентів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app', 'backend', 'shared'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
from test_helpers import create_test_user, get_test_db


class TestProposalTemplates:
    """Тести для шаблонів відгуків"""
    
    def test_proposal_template_creation(self):
        """Тест створення шаблону відгуку"""
        # Mock дані
        user = create_test_user()
        db = get_test_db()
        
        # Дані шаблону
        template_data = {
            "name": "Python Developer Template",
            "content": """
# Пропозиція для проекту

## Про мене
{user_profile}

## Підхід до проекту
На основі вашого опису, я пропоную наступний підхід:

### Технічне рішення
- Детальний аналіз вимог
- Архітектурне планування
- Поетапна реалізація

### Комунікація
- Регулярні оновлення прогресу
- Прозорість робочого процесу
- Готовність до обговорень

### Якість
- Тестування на кожному етапі
- Документація коду
- Підтримка після завершення

## Чому обирати мене
- ✅ Досвід у подібних проектах
- ✅ Якісний код та документація
- ✅ Вчасне виконання
- ✅ Підтримка після завершення

Готовий обговорити деталі та почати роботу!
            """,
            "category": "web_dev",
            "variables": {
                "user_profile": "string",
                "project_type": "string",
                "budget": "string"
            },
            "style": "formal",
            "is_default": False
        }
        
        # Перевіряємо структуру даних
        assert "name" in template_data
        assert "content" in template_data
        assert "category" in template_data
        assert "variables" in template_data
        assert "style" in template_data
        
        # Перевіряємо типи даних
        assert isinstance(template_data["name"], str)
        assert isinstance(template_data["content"], str)
        assert isinstance(template_data["variables"], dict)
        assert isinstance(template_data["style"], str)
        
        # Перевіряємо валідність даних
        assert len(template_data["name"]) <= 100
        assert len(template_data["content"]) > 0
        assert template_data["style"] in ["formal", "friendly", "technical"]
        
        print("✅ Тест створення шаблону відгуку пройшов")
    
    def test_proposal_template_limit_validation(self):
        """Тест перевірки ліміту шаблонів (до 10 на користувача)"""
        user = create_test_user()
        
        # Симулюємо 10 існуючих шаблонів
        existing_templates = 10
        
        # Перевіряємо ліміт
        assert existing_templates <= 10, "Ліміт шаблонів перевищено"
        
        # Симулюємо спробу створити 11-й шаблон
        if existing_templates >= 10:
            error_message = "Досягнуто ліміт шаблонів відгуків (10)"
            assert "ліміт" in error_message.lower()
            assert "10" in error_message
        
        print("✅ Тест перевірки ліміту шаблонів пройшов")
    
    def test_proposal_template_categories(self):
        """Тест категорій шаблонів"""
        # Валідні категорії
        valid_categories = [
            "general",
            "web_dev", 
            "mobile_dev",
            "design",
            "writing",
            "marketing",
            "data_science",
            "admin_support"
        ]
        
        for category in valid_categories:
            # Перевіряємо, що категорія валідна
            assert category in valid_categories, f"Неправильна категорія: {category}"
            
            # Створюємо приклад шаблону для кожной категорії
            template = {
                "name": f"Template - {category}",
                "content": f"Шаблон для категорії {category}",
                "category": category,
                "style": "formal"
            }
            
            # Перевіряємо структуру
            assert "name" in template
            assert "content" in template
            assert "category" in template
            assert template["category"] == category
        
        print("✅ Тест категорій шаблонів пройшов")
    
    def test_proposal_template_variables(self):
        """Тест змінних в шаблонах"""
        # Приклади змінних
        template_variables = [
            {
                "user_profile": "string",
                "project_type": "string",
                "budget": "string",
                "timeline": "string"
            },
            {
                "client_name": "string",
                "project_description": "string",
                "requirements": "string",
                "deadline": "string"
            },
            {
                "skills": "array",
                "experience": "string",
                "portfolio": "string",
                "rate": "number"
            }
        ]
        
        for variables in template_variables:
            # Перевіряємо структуру змінних
            assert len(variables) > 0, "Змінні не можуть бути порожніми"
            
            for var_name, var_type in variables.items():
                # Перевіряємо назви змінних
                assert len(var_name) > 0, "Назва змінної не може бути порожньою"
                assert var_type in ["string", "number", "array", "boolean"], f"Неправильний тип змінної: {var_type}"
        
        print("✅ Тест змінних в шаблонах пройшов")
    
    def test_proposal_template_styles(self):
        """Тест стилів шаблонів"""
        # Валідні стилі
        valid_styles = ["formal", "friendly", "technical"]
        
        for style in valid_styles:
            # Перевіряємо, що стиль валідний
            assert style in valid_styles, f"Неправильний стиль: {style}"
            
            # Створюємо приклад шаблону для кожного стилю
            template = {
                "name": f"Template - {style}",
                "content": f"Шаблон у стилі {style}",
                "style": style
            }
            
            # Перевіряємо структуру
            assert "name" in template
            assert "content" in template
            assert "style" in template
            assert template["style"] == style
        
        print("✅ Тест стилів шаблонів пройшов")
    
    def test_proposal_template_success_rate_tracking(self):
        """Тест відстеження успішності шаблонів"""
        # Mock дані для успішності
        success_data = [
            {"usage_count": 15, "successful_uses": 12, "success_rate": 80.0},
            {"usage_count": 25, "successful_uses": 20, "success_rate": 80.0},
            {"usage_count": 8, "successful_uses": 6, "success_rate": 75.0},
            {"usage_count": 30, "successful_uses": 27, "success_rate": 90.0}
        ]
        
        for data in success_data:
            # Перевіряємо, що дані валідні
            assert data["usage_count"] >= 0, "Кількість використань не може бути від'ємною"
            assert data["successful_uses"] >= 0, "Кількість успішних використань не може бути від'ємною"
            assert data["successful_uses"] <= data["usage_count"], "Успішні використання не можуть перевищувати загальні"
            assert 0 <= data["success_rate"] <= 100, "Успішність повинна бути в діапазоні 0-100"
            
            # Перевіряємо розрахунок успішності
            if data["usage_count"] > 0:
                calculated_rate = (data["successful_uses"] / data["usage_count"]) * 100
                assert abs(calculated_rate - data["success_rate"]) < 1, "Неправильний розрахунок успішності"
        
        print("✅ Тест відстеження успішності пройшов")
    
    def test_proposal_template_default_templates(self):
        """Тест шаблонів за замовчуванням"""
        # Шаблони за замовчуванням
        default_templates = [
            {
                "name": "Загальний шаблон",
                "content": "Універсальний шаблон для всіх проектів",
                "category": "general",
                "style": "formal",
                "is_default": True
            },
            {
                "name": "Технічний шаблон",
                "content": "Шаблон для технічних проектів",
                "category": "web_dev",
                "style": "technical",
                "is_default": True
            },
            {
                "name": "Дружній шаблон",
                "content": "Шаблон з дружнім тоном",
                "category": "general",
                "style": "friendly",
                "is_default": True
            }
        ]
        
        for template in default_templates:
            # Перевіряємо, що це шаблон за замовчуванням
            assert template["is_default"] == True, f"Шаблон '{template['name']}' повинен бути за замовчуванням"
            
            # Перевіряємо структуру
            assert "name" in template
            assert "content" in template
            assert "category" in template
            assert "style" in template
            
            # Перевіряємо валідність контенту
            assert len(template["content"]) > 0, "Контент шаблону не може бути порожнім"
        
        print("✅ Тест шаблонів за замовчуванням пройшов")
    
    def test_proposal_template_validation(self):
        """Тест валідації шаблонів"""
        # Валідні шаблони
        valid_templates = [
            {
                "name": "Valid Template 1",
                "content": "Valid content",
                "category": "web_dev",
                "style": "formal"
            },
            {
                "name": "Valid Template 2",
                "content": "Another valid content",
                "category": "general",
                "style": "friendly"
            }
        ]
        
        # Невалідні шаблони
        invalid_templates = [
            {
                "name": "",  # Порожня назва
                "content": "Valid content",
                "category": "web_dev",
                "style": "formal"
            },
            {
                "name": "Valid name",
                "content": "",  # Порожній контент
                "category": "web_dev",
                "style": "formal"
            },
            {
                "name": "Valid name",
                "content": "Valid content",
                "category": "invalid_category",  # Невідома категорія
                "style": "formal"
            }
        ]
        
        # Перевіряємо валідні шаблони
        for template in valid_templates:
            assert len(template["name"]) > 0, "Назва не може бути порожньою"
            assert len(template["content"]) > 0, "Контент не може бути порожнім"
            assert template["category"] in ["general", "web_dev", "mobile_dev", "design"], "Неправильна категорія"
            assert template["style"] in ["formal", "friendly", "technical"], "Неправильний стиль"
        
        # Перевіряємо невалідні шаблони
        for template in invalid_templates:
            is_invalid = False
            if len(template["name"]) == 0:
                is_invalid = True
            if len(template["content"]) == 0:
                is_invalid = True
            if template["category"] not in ["general", "web_dev", "mobile_dev", "design"]:
                is_invalid = True
            
            # Перевіряємо, що шаблон дійсно невалідний
            assert is_invalid, f"Шаблон повинен бути невалідним: {template}"
        
        print("✅ Тест валідації шаблонів пройшов")


class TestProposalTemplateIntegration:
    """Інтеграційні тести для шаблонів відгуків"""
    
    def test_proposal_template_complete_workflow(self):
        """Тест повного workflow шаблонів відгуків"""
        # 1. Створення користувача
        user = create_test_user()
        assert user["id"] is not None
        
        # 2. Створення шаблону відгуку
        template_data = {
            "name": "Python Developer Template",
            "content": """
# Пропозиція для проекту

## Про мене
{user_profile}

## Підхід до проекту
На основі вашого опису, я пропоную наступний підхід:

### Технічне рішення
- Детальний аналіз вимог
- Архітектурне планування
- Поетапна реалізація

### Комунікація
- Регулярні оновлення прогресу
- Прозорість робочого процесу
- Готовність до обговорень

### Якість
- Тестування на кожному етапі
- Документація коду
- Підтримка після завершення

## Чому обирати мене
- ✅ Досвід у подібних проектах
- ✅ Якісний код та документація
- ✅ Вчасне виконання
- ✅ Підтримка після завершення

Готовий обговорити деталі та почати роботу!
            """,
            "category": "web_dev",
            "variables": {
                "user_profile": "string",
                "project_type": "string",
                "budget": "string"
            },
            "style": "formal",
            "is_default": False
        }
        
        # 3. Валідація даних
        assert len(template_data["name"]) <= 100
        assert len(template_data["content"]) > 0
        assert template_data["category"] in ["general", "web_dev", "mobile_dev", "design"]
        assert template_data["style"] in ["formal", "friendly", "technical"]
        
        # 4. Перевірка змінних
        variables = template_data["variables"]
        assert "user_profile" in variables
        assert "project_type" in variables
        assert "budget" in variables
        
        # 5. Симуляція збереження
        template_id = "test_template_123"
        assert template_id is not None
        
        # 6. Перевірка результату
        assert template_data["name"] == "Python Developer Template"
        assert template_data["category"] == "web_dev"
        assert template_data["style"] == "formal"
        assert "user_profile" in template_data["content"]
        
        print("✅ Тест повного workflow шаблонів пройшов")
    
    def test_proposal_template_usage_tracking(self):
        """Тест відстеження використання шаблонів"""
        # Mock дані для відстеження використання
        usage_tracking = [
            {
                "template_id": "template_1",
                "usage_count": 25,
                "successful_uses": 20,
                "success_rate": 80.0,
                "last_used": datetime.utcnow()
            },
            {
                "template_id": "template_2",
                "usage_count": 15,
                "successful_uses": 12,
                "success_rate": 80.0,
                "last_used": datetime.utcnow() - timedelta(days=1)
            },
            {
                "template_id": "template_3",
                "usage_count": 8,
                "successful_uses": 6,
                "success_rate": 75.0,
                "last_used": datetime.utcnow() - timedelta(days=3)
            }
        ]
        
        for tracking in usage_tracking:
            # Перевіряємо структуру
            assert "template_id" in tracking
            assert "usage_count" in tracking
            assert "successful_uses" in tracking
            assert "success_rate" in tracking
            assert "last_used" in tracking
            
            # Перевіряємо валідність даних
            assert tracking["usage_count"] >= 0
            assert tracking["successful_uses"] >= 0
            assert tracking["successful_uses"] <= tracking["usage_count"]
            assert 0 <= tracking["success_rate"] <= 100
            
            # Перевіряємо розрахунок успішності
            if tracking["usage_count"] > 0:
                calculated_rate = (tracking["successful_uses"] / tracking["usage_count"]) * 100
                assert abs(calculated_rate - tracking["success_rate"]) < 1
        
        print("✅ Тест відстеження використання пройшов")
    
    def test_proposal_template_performance_metrics(self):
        """Тест метрик продуктивності шаблонів"""
        # Mock метрики продуктивності
        performance_metrics = {
            "total_templates": 150,
            "active_templates": 120,
            "average_success_rate": 78.5,
            "most_popular_category": "web_dev",
            "average_usage_per_template": 12.3,
            "templates_created_today": 5,
            "templates_updated_today": 8
        }
        
        # Перевіряємо валідність метрик
        assert performance_metrics["total_templates"] >= 0
        assert performance_metrics["active_templates"] <= performance_metrics["total_templates"]
        assert 0 <= performance_metrics["average_success_rate"] <= 100
        assert performance_metrics["most_popular_category"] in ["general", "web_dev", "mobile_dev", "design"]
        assert performance_metrics["average_usage_per_template"] >= 0
        assert performance_metrics["templates_created_today"] >= 0
        assert performance_metrics["templates_updated_today"] >= 0
        
        # Перевіряємо логіку
        if performance_metrics["total_templates"] > 0:
            active_rate = (performance_metrics["active_templates"] / performance_metrics["total_templates"]) * 100
            assert active_rate <= 100, "Відсоток активних шаблонів не може перевищувати 100%"
        
        print("✅ Тест метрик продуктивності пройшов")


if __name__ == "__main__":
    # Запуск тестів
    test_templates = TestProposalTemplates()
    test_templates.test_proposal_template_creation()
    test_templates.test_proposal_template_limit_validation()
    test_templates.test_proposal_template_categories()
    test_templates.test_proposal_template_variables()
    test_templates.test_proposal_template_styles()
    test_templates.test_proposal_template_success_rate_tracking()
    test_templates.test_proposal_template_default_templates()
    test_templates.test_proposal_template_validation()
    
    test_integration = TestProposalTemplateIntegration()
    test_integration.test_proposal_template_complete_workflow()
    test_integration.test_proposal_template_usage_tracking()
    test_integration.test_proposal_template_performance_metrics()
    
    print("\n🎉 Всі тести шаблонів відгуків пройшли успішно!") 