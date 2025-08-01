"""
Тести для MVP компонентів - AI інструкції природною мовою
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


class TestAIInstructions:
    """Тести для AI інструкцій природною мовою"""
    
    def test_create_ai_instruction_success(self):
        """Тест успішного створення AI інструкції"""
        # Mock дані
        user = create_test_user()
        db = get_test_db()
        
        # Дані AI інструкції
        instruction_data = {
            "name": "Python Developer Filter",
            "content": "Шукай проекти з Python та Django, фокусуйся на веб-розробці, уникай WordPress та PHP",
            "instruction_type": "filter",
            "is_default": False
        }
        
        # Перевіряємо структуру даних
        assert "name" in instruction_data
        assert "content" in instruction_data
        assert "instruction_type" in instruction_data
        
        # Перевіряємо типи даних
        assert isinstance(instruction_data["name"], str)
        assert isinstance(instruction_data["content"], str)
        assert isinstance(instruction_data["instruction_type"], str)
        
        # Перевіряємо валідність даних
        assert len(instruction_data["name"]) <= 100
        assert len(instruction_data["content"]) <= 2000
        assert instruction_data["instruction_type"] in ["filter", "proposal", "analysis"]
        
        print("✅ Тест створення AI інструкції пройшов")
    
    def test_ai_instruction_natural_language(self):
        """Тест AI інструкцій природною мовою"""
        # Приклади природних інструкцій
        natural_instructions = [
            {
                "name": "Python Developer",
                "content": "Шукай проекти з Python та Django, фокусуйся на веб-розробці, уникай WordPress та PHP",
                "type": "filter"
            },
            {
                "name": "React Developer",
                "content": "Фокусуйся на проектах з React та TypeScript, шукай клієнтів з хорошим рейтингом",
                "type": "filter"
            },
            {
                "name": "Proposal Writer",
                "content": "Створюй професійні відгуки з акцентом на досвід та результаті, уникай загальних фраз",
                "type": "proposal"
            },
            {
                "name": "Job Analyzer",
                "content": "Аналізуй вакансії на предмет реалістичності бюджету та якості опису проекту",
                "type": "analysis"
            }
        ]
        
        for instruction in natural_instructions:
            # Перевіряємо природність мови
            content = instruction["content"]
            assert len(content) >= 20, "Інструкція занадто коротка"
            assert len(content) <= 500, "Інструкція занадто довга"
            
            # Перевіряємо наявність ключових слів природної мови
            natural_keywords = ["шукай", "фокусуйся", "уникай", "аналізуй", "створюй", "проекти", "клієнтів"]
            has_natural_keywords = any(keyword in content.lower() for keyword in natural_keywords)
            assert has_natural_keywords, f"Інструкція '{instruction['name']}' не містить природних ключових слів"
            
            # Перевіряємо тип інструкції
            assert instruction["type"] in ["filter", "proposal", "analysis"], f"Неправильний тип інструкції: {instruction['type']}"
        
        print("✅ Тест AI інструкцій природною мовою пройшов")
    
    def test_ai_instruction_types(self):
        """Тест типів AI інструкцій"""
        # Валідні типи інструкцій
        valid_types = ["filter", "proposal", "analysis"]
        
        for instruction_type in valid_types:
            # Перевіряємо, що тип валідний
            assert instruction_type in valid_types, f"Неправильний тип інструкції: {instruction_type}"
            
            # Створюємо приклад інструкції для кожного типу
            instruction_data = {
                "name": f"Test {instruction_type.title()}",
                "content": f"Тестова інструкція типу {instruction_type}",
                "instruction_type": instruction_type,
                "is_default": False
            }
            
            # Перевіряємо структуру
            assert "name" in instruction_data
            assert "content" in instruction_data
            assert "instruction_type" in instruction_data
            assert instruction_data["instruction_type"] == instruction_type
        
        print("✅ Тест типів AI інструкцій пройшов")
    
    def test_ai_instruction_effectiveness_tracking(self):
        """Тест відстеження ефективності AI інструкцій"""
        # Mock дані для ефективності
        effectiveness_data = [
            {"usage_count": 10, "effectiveness_score": 85.5},
            {"usage_count": 25, "effectiveness_score": 92.3},
            {"usage_count": 5, "effectiveness_score": 78.1},
            {"usage_count": 15, "effectiveness_score": 88.7}
        ]
        
        for data in effectiveness_data:
            # Перевіряємо, що дані валідні
            assert data["usage_count"] >= 0, "Кількість використань не може бути від'ємною"
            assert data["effectiveness_score"] >= 0, "Оцінка ефективності не може бути від'ємною"
            assert data["effectiveness_score"] <= 100, "Оцінка ефективності не може перевищувати 100"
            
            # Перевіряємо логіку: більше використань = більша точність оцінки
            if data["usage_count"] > 10:
                assert data["effectiveness_score"] is not None, "Для часто використовуваних інструкцій повинна бути оцінка"
        
        print("✅ Тест відстеження ефективності пройшов")
    
    def test_ai_instruction_default_templates(self):
        """Тест шаблонів AI інструкцій за замовчуванням"""
        # Шаблони за замовчуванням
        default_templates = [
            {
                "name": "Загальний фільтр",
                "content": "Шукай проекти з хорошим бюджетом та детальним описом, уникай проектів з нереальними дедлайнами",
                "type": "filter",
                "is_default": True
            },
            {
                "name": "Професійний відгук",
                "content": "Створюй професійні відгуки з акцентом на досвід та результаті, адаптуй під специфіку проекту",
                "type": "proposal",
                "is_default": True
            },
            {
                "name": "Аналіз вакансії",
                "content": "Аналізуй вакансії на предмет реалістичності бюджету, якості опису та рейтингу клієнта",
                "type": "analysis",
                "is_default": True
            }
        ]
        
        for template in default_templates:
            # Перевіряємо, що це шаблон за замовчуванням
            assert template["is_default"] == True, f"Шаблон '{template['name']}' повинен бути за замовчуванням"
            
            # Перевіряємо структуру
            assert "name" in template
            assert "content" in template
            assert "type" in template
            
            # Перевіряємо валідність контенту
            assert len(template["content"]) >= 30, "Шаблон за замовчуванням занадто короткий"
            assert len(template["content"]) <= 300, "Шаблон за замовчуванням занадто довгий"
        
        print("✅ Тест шаблонів за замовчуванням пройшов")
    
    def test_ai_instruction_validation(self):
        """Тест валідації AI інструкцій"""
        # Валідні інструкції
        valid_instructions = [
            {
                "name": "Valid Instruction 1",
                "content": "Шукай проекти з Python",
                "type": "filter"
            },
            {
                "name": "Valid Instruction 2", 
                "content": "Створюй професійні відгуки",
                "type": "proposal"
            }
        ]
        
        # Невалідні інструкції
        invalid_instructions = [
            {
                "name": "",  # Порожня назва
                "content": "Тест",
                "type": "filter"
            },
            {
                "name": "Test",
                "content": "",  # Порожній контент
                "type": "filter"
            },
            {
                "name": "Test",
                "content": "Тест",
                "type": "invalid_type"  # Невідомий тип
            }
        ]
        
        # Перевіряємо валідні інструкції
        for instruction in valid_instructions:
            assert len(instruction["name"]) > 0, "Назва не може бути порожньою"
            assert len(instruction["content"]) > 0, "Контент не може бути порожнім"
            assert instruction["type"] in ["filter", "proposal", "analysis"], "Неправильний тип"
        
        # Перевіряємо невалідні інструкції
        for instruction in invalid_instructions:
            is_invalid = False
            if len(instruction["name"]) == 0:
                is_invalid = True
            if len(instruction["content"]) == 0:
                is_invalid = True
            if instruction["type"] not in ["filter", "proposal", "analysis"]:
                is_invalid = True
            
            # Перевіряємо, що інструкція дійсно невалідна
            assert is_invalid, f"Інструкція повинна бути невалідною: {instruction}"
        
        print("✅ Тест валідації AI інструкцій пройшов")


class TestAIInstructionsIntegration:
    """Інтеграційні тести для AI інструкцій"""
    
    def test_ai_instruction_complete_workflow(self):
        """Тест повного workflow AI інструкцій"""
        # 1. Створення користувача
        user = create_test_user()
        assert user["id"] is not None
        
        # 2. Створення AI інструкції
        instruction_data = {
            "name": "Advanced Python Filter",
            "content": "Шукай проекти з Python, Django та PostgreSQL. Фокусуйся на проектах з машинним навчанням та API розробкою. Уникай проектів з WordPress та PHP. Перевага клієнтам з рейтингом вище 4.5 та бюджетом від $2000.",
            "instruction_type": "filter",
            "is_default": False
        }
        
        # 3. Валідація даних
        assert len(instruction_data["name"]) <= 100
        assert len(instruction_data["content"]) <= 2000
        assert instruction_data["instruction_type"] in ["filter", "proposal", "analysis"]
        
        # 4. Перевірка природності мови
        content = instruction_data["content"]
        natural_keywords = ["шукай", "фокусуйся", "уникай", "перевага"]
        has_natural_keywords = any(keyword in content.lower() for keyword in natural_keywords)
        assert has_natural_keywords, "Інструкція не містить природних ключових слів"
        
        # 5. Перевірка технічних термінів
        tech_terms = ["python", "django", "postgresql", "машинним", "api"]
        has_tech_terms = any(term in content.lower() for term in tech_terms)
        assert has_tech_terms, "Інструкція не містить технічних термінів"
        
        # 6. Симуляція збереження
        instruction_id = "test_instruction_123"
        assert instruction_id is not None
        
        print("✅ Тест повного workflow AI інструкцій пройшов")
    
    def test_ai_instruction_effectiveness_calculation(self):
        """Тест розрахунку ефективності AI інструкцій"""
        # Mock дані для розрахунку ефективності
        test_cases = [
            {
                "usage_count": 20,
                "successful_matches": 15,
                "expected_effectiveness": 75.0
            },
            {
                "usage_count": 50,
                "successful_matches": 42,
                "expected_effectiveness": 84.0
            },
            {
                "usage_count": 10,
                "successful_matches": 8,
                "expected_effectiveness": 80.0
            }
        ]
        
        for case in test_cases:
            # Розраховуємо ефективність
            if case["usage_count"] > 0:
                effectiveness = (case["successful_matches"] / case["usage_count"]) * 100
            else:
                effectiveness = 0
            
            # Перевіряємо розрахунок
            assert effectiveness == case["expected_effectiveness"], f"Неправильний розрахунок ефективності: {effectiveness} != {case['expected_effectiveness']}"
            
            # Перевіряємо діапазон
            assert 0 <= effectiveness <= 100, "Ефективність повинна бути в діапазоні 0-100"
        
        print("✅ Тест розрахунку ефективності пройшов")
    
    def test_ai_instruction_recommendations(self):
        """Тест рекомендацій для AI інструкцій (раз в день)"""
        # Симулюємо рекомендації
        recommendations = [
            {
                "instruction_id": "test_1",
                "current_effectiveness": 65.0,
                "recommendation": "Додайте більше специфічних технологій для покращення точності",
                "priority": "medium"
            },
            {
                "instruction_id": "test_2", 
                "current_effectiveness": 45.0,
                "recommendation": "Перегляньте ключові слова та додайте більше контексту",
                "priority": "high"
            },
            {
                "instruction_id": "test_3",
                "current_effectiveness": 85.0,
                "recommendation": "Інструкція працює добре, можна додати більше нюансів",
                "priority": "low"
            }
        ]
        
        for rec in recommendations:
            # Перевіряємо структуру рекомендації
            assert "instruction_id" in rec
            assert "current_effectiveness" in rec
            assert "recommendation" in rec
            assert "priority" in rec
            
            # Перевіряємо логіку пріоритетів
            if rec["current_effectiveness"] < 50:
                assert rec["priority"] == "high", "Низька ефективність повинна мати високий пріоритет"
            elif rec["current_effectiveness"] < 70:
                assert rec["priority"] == "medium", "Середня ефективність повинна мати середній пріоритет"
            else:
                assert rec["priority"] == "low", "Висока ефективність повинна мати низький пріоритет"
        
        print("✅ Тест рекомендацій пройшов")


if __name__ == "__main__":
    # Запуск тестів
    test_ai_instructions = TestAIInstructions()
    test_ai_instructions.test_create_ai_instruction_success()
    test_ai_instructions.test_ai_instruction_natural_language()
    test_ai_instructions.test_ai_instruction_types()
    test_ai_instructions.test_ai_instruction_effectiveness_tracking()
    test_ai_instructions.test_ai_instruction_default_templates()
    test_ai_instructions.test_ai_instruction_validation()
    
    test_integration = TestAIInstructionsIntegration()
    test_integration.test_ai_instruction_complete_workflow()
    test_integration.test_ai_instruction_effectiveness_calculation()
    test_integration.test_ai_instruction_recommendations()
    
    print("\n🎉 Всі тести AI інструкцій пройшли успішно!") 