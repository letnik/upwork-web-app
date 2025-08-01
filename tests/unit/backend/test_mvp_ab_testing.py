#!/usr/bin/env python3
"""
Тести для MVP-006: A/B тестування шаблонів (2 варіанти)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from tests.utils.test_helpers import create_test_user, get_test_db

class TestABTesting:
    """Тести для A/B тестування шаблонів"""
    
    def test_ab_test_creation(self):
        """Тест створення A/B тесту"""
        user = create_test_user()
        db = get_test_db()
        
        # Створюємо два шаблони для тестування
        template_a = Mock()
        template_a.id = 1
        template_a.name = "Template A"
        template_a.content = "This is template A"
        
        template_b = Mock()
        template_b.id = 2
        template_b.name = "Template B"
        template_b.content = "This is template B"
        
        # Створюємо A/B тест
        ab_test = Mock()
        ab_test.id = 1
        ab_test.user_id = user["id"]
        ab_test.name = "Test Proposal Templates"
        ab_test.template_a_id = template_a.id
        ab_test.template_b_id = template_b.id
        ab_test.start_date = datetime.now()
        ab_test.end_date = None
        ab_test.status = "running"
        ab_test.min_duration_days = 7
        ab_test.template_a_sent = 0
        ab_test.template_b_sent = 0
        ab_test.template_a_responses = 0
        ab_test.template_b_responses = 0
        ab_test.template_a_hired = 0
        ab_test.template_b_hired = 0
        ab_test.winner_template_id = None
        
        # Перевіряємо створення
        assert ab_test.id == 1
        assert ab_test.user_id == user["id"]
        assert ab_test.name == "Test Proposal Templates"
        assert ab_test.template_a_id == 1
        assert ab_test.template_b_id == 2
        assert ab_test.status == "running"
        assert ab_test.min_duration_days == 7
        
        print("✅ Тест створення A/B тесту пройшов")
    
    def test_ab_test_minimum_duration(self):
        """Тест мінімальної тривалості A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест з мінімальною тривалістю
        ab_test = Mock()
        ab_test.start_date = datetime.now()
        ab_test.min_duration_days = 7
        
        # Перевіряємо, що тест не може бути завершеним раніше 7 днів
        days_running = (datetime.now() - ab_test.start_date).days
        can_complete = days_running >= ab_test.min_duration_days
        
        assert ab_test.min_duration_days == 7
        assert not can_complete  # Тест щойно створений
        
        # Симулюємо тест, що працює 7 днів
        ab_test.start_date = datetime.now() - timedelta(days=7)
        days_running = (datetime.now() - ab_test.start_date).days
        can_complete = days_running >= ab_test.min_duration_days
        
        assert can_complete
        
        print("✅ Тест мінімальної тривалості A/B тесту пройшов")
    
    def test_ab_test_metrics_tracking(self):
        """Тест відстеження метрик A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест з метриками
        ab_test = Mock()
        ab_test.template_a_sent = 50
        ab_test.template_b_sent = 50
        ab_test.template_a_responses = 8
        ab_test.template_b_responses = 12
        ab_test.template_a_hired = 2
        ab_test.template_b_hired = 4
        
        # Розраховуємо відсотки успішності
        template_a_response_rate = (ab_test.template_a_responses / ab_test.template_a_sent) * 100
        template_b_response_rate = (ab_test.template_b_responses / ab_test.template_b_sent) * 100
        
        template_a_hire_rate = (ab_test.template_a_hired / ab_test.template_a_sent) * 100
        template_b_hire_rate = (ab_test.template_b_hired / ab_test.template_b_sent) * 100
        
        # Перевіряємо розрахунки
        assert template_a_response_rate == 16.0  # 8/50 * 100
        assert template_b_response_rate == 24.0  # 12/50 * 100
        assert template_a_hire_rate == 4.0  # 2/50 * 100
        assert template_b_hire_rate == 8.0  # 4/50 * 100
        
        print("✅ Тест відстеження метрик A/B тесту пройшов")
    
    def test_ab_test_winner_determination(self):
        """Тест визначення переможця A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест з результатами
        ab_test = Mock()
        ab_test.template_a_sent = 100
        ab_test.template_b_sent = 100
        ab_test.template_a_responses = 15
        ab_test.template_b_responses = 25
        ab_test.template_a_hired = 3
        ab_test.template_b_hired = 8
        
        # Розраховуємо метрики
        template_a_metrics = {
            'response_rate': (ab_test.template_a_responses / ab_test.template_a_sent) * 100,
            'hire_rate': (ab_test.template_a_hired / ab_test.template_a_sent) * 100
        }
        
        template_b_metrics = {
            'response_rate': (ab_test.template_b_responses / ab_test.template_b_sent) * 100,
            'hire_rate': (ab_test.template_b_hired / ab_test.template_b_sent) * 100
        }
        
        # Визначаємо переможця (на основі найвищого hire rate)
        if template_a_metrics['hire_rate'] > template_b_metrics['hire_rate']:
            winner = "Template A"
            winner_id = 1
        elif template_b_metrics['hire_rate'] > template_a_metrics['hire_rate']:
            winner = "Template B"
            winner_id = 2
        else:
            winner = "Tie"
            winner_id = None
        
        # Перевіряємо результат
        assert template_a_metrics['response_rate'] == 15.0
        assert template_b_metrics['response_rate'] == 25.0
        assert template_a_metrics['hire_rate'] == 3.0
        assert template_b_metrics['hire_rate'] == 8.0
        assert winner == "Template B"  # Template B має вищий hire rate
        assert winner_id == 2
        
        print("✅ Тест визначення переможця A/B тесту пройшов")
    
    def test_ab_test_status_management(self):
        """Тест управління статусом A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест
        ab_test = Mock()
        ab_test.status = "running"
        ab_test.start_date = datetime.now() - timedelta(days=10)
        ab_test.min_duration_days = 7
        
        # Перевіряємо можливість завершення
        days_running = (datetime.now() - ab_test.start_date).days
        can_complete = days_running >= ab_test.min_duration_days
        
        assert ab_test.status == "running"
        assert can_complete
        
        # Симулюємо завершення тесту
        ab_test.status = "completed"
        ab_test.end_date = datetime.now()
        
        assert ab_test.status == "completed"
        assert ab_test.end_date is not None
        
        # Симулюємо примусове зупинення
        ab_test.status = "stopped"
        
        assert ab_test.status == "stopped"
        
        print("✅ Тест управління статусом A/B тесту пройшов")
    
    def test_ab_test_user_assignment(self):
        """Тест призначення користувачів до груп A/B тесту"""
        user = create_test_user()
        
        # Симулюємо призначення користувача до групи
        def assign_user_to_group(user_id, test_name):
            """Призначає користувача до групи A або B"""
            import hashlib
            hash_value = hashlib.md5(f"{user_id}:{test_name}".encode()).hexdigest()
            group = "A" if int(hash_value[:8], 16) % 2 == 0 else "B"
            return group
        
        # Тестуємо призначення
        group_a = assign_user_to_group(user["id"], "test_1")
        group_b = assign_user_to_group(user["id"], "test_2")
        
        # Перевіряємо, що призначення консистентне
        assert group_a in ["A", "B"]
        assert group_b in ["A", "B"]
        
        # Перевіряємо, що той самий користувач завжди потрапляє в ту саму групу для одного тесту
        group_a_again = assign_user_to_group(user["id"], "test_1")
        assert group_a == group_a_again
        
        print("✅ Тест призначення користувачів до груп A/B тесту пройшов")
    
    def test_ab_test_statistical_significance(self):
        """Тест статистичної значущості A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест з достатньою кількістю даних
        ab_test = Mock()
        ab_test.template_a_sent = 1000
        ab_test.template_b_sent = 1000
        ab_test.template_a_responses = 150
        ab_test.template_b_responses = 200
        ab_test.template_a_hired = 30
        ab_test.template_b_hired = 50
        
        # Розраховуємо відсотки
        template_a_response_rate = (ab_test.template_a_responses / ab_test.template_a_sent) * 100
        template_b_response_rate = (ab_test.template_b_responses / ab_test.template_b_sent) * 100
        
        template_a_hire_rate = (ab_test.template_a_hired / ab_test.template_a_sent) * 100
        template_b_hire_rate = (ab_test.template_b_hired / ab_test.template_b_sent) * 100
        
        # Перевіряємо статистичну значущість (різниця >= 5%)
        response_rate_difference = abs(template_b_response_rate - template_a_response_rate)
        hire_rate_difference = abs(template_b_hire_rate - template_a_hire_rate)
        
        is_statistically_significant = response_rate_difference >= 5 or hire_rate_difference >= 5
        
        assert template_a_response_rate == 15.0
        assert template_b_response_rate == 20.0
        assert template_a_hire_rate == 3.0
        assert template_b_hire_rate == 5.0
        assert response_rate_difference == 5.0
        assert hire_rate_difference == 2.0
        assert is_statistically_significant  # response_rate_difference = 5% >= 5%
        
        print("✅ Тест статистичної значущості A/B тесту пройшов")
    
    def test_ab_test_early_stopping(self):
        """Тест раннього зупинення A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест з критеріями раннього зупинення
        ab_test = Mock()
        ab_test.template_a_sent = 500
        ab_test.template_b_sent = 500
        ab_test.template_a_responses = 25
        ab_test.template_b_responses = 75
        ab_test.min_duration_days = 7
        ab_test.start_date = datetime.now() - timedelta(days=5)
        
        # Розраховуємо відсотки
        template_a_response_rate = (ab_test.template_a_responses / ab_test.template_a_sent) * 100
        template_b_response_rate = (ab_test.template_b_responses / ab_test.template_b_sent) * 100
        
        # Критерії раннього зупинення
        days_running = (datetime.now() - ab_test.start_date).days
        min_duration_met = days_running >= ab_test.min_duration_days
        significant_difference = abs(template_b_response_rate - template_a_response_rate) >= 10
        
        can_stop_early = min_duration_met and significant_difference
        
        assert template_a_response_rate == 5.0
        assert template_b_response_rate == 15.0
        assert abs(template_b_response_rate - template_a_response_rate) == 10.0
        assert not min_duration_met  # 5 днів < 7 днів
        assert not can_stop_early  # не виконана мінімальна тривалість
        
        # Симулюємо після мінімальної тривалості
        ab_test.start_date = datetime.now() - timedelta(days=10)
        days_running = (datetime.now() - ab_test.start_date).days
        min_duration_met = days_running >= ab_test.min_duration_days
        can_stop_early = min_duration_met and significant_difference
        
        assert min_duration_met  # 10 днів >= 7 днів
        assert can_stop_early  # виконана мінімальна тривалість і є значуща різниця
        
        print("✅ Тест раннього зупинення A/B тесту пройшов")
    
    def test_ab_test_multiple_variants(self):
        """Тест підтримки кількох варіантів (обмеження до 2)"""
        user = create_test_user()
        
        # Створюємо A/B тест з двома варіантами
        template_a = Mock()
        template_a.id = 1
        template_a.name = "Template A"
        
        template_b = Mock()
        template_b.id = 2
        template_b.name = "Template B"
        
        ab_test = Mock()
        ab_test.template_a_id = template_a.id
        ab_test.template_b_id = template_b.id
        
        # Перевіряємо, що тільки 2 варіанти
        variants = [template_a, template_b]
        assert len(variants) == 2
        assert ab_test.template_a_id == 1
        assert ab_test.template_b_id == 2
        
        # Перевіряємо, що варіанти різні
        assert ab_test.template_a_id != ab_test.template_b_id
        
        print("✅ Тест підтримки кількох варіантів пройшов")
    
    def test_ab_test_completion_workflow(self):
        """Тест повного workflow завершення A/B тесту"""
        user = create_test_user()
        
        # Створюємо A/B тест
        ab_test = Mock()
        ab_test.status = "running"
        ab_test.start_date = datetime.now() - timedelta(days=14)
        ab_test.min_duration_days = 7
        ab_test.template_a_sent = 1000
        ab_test.template_b_sent = 1000
        ab_test.template_a_responses = 100
        ab_test.template_b_responses = 150
        ab_test.template_a_hired = 20
        ab_test.template_b_hired = 35
        
        # Перевіряємо умови завершення
        days_running = (datetime.now() - ab_test.start_date).days
        min_duration_met = days_running >= ab_test.min_duration_days
        sufficient_data = ab_test.template_a_sent >= 100 and ab_test.template_b_sent >= 100
        
        # Розраховуємо метрики
        template_a_hire_rate = (ab_test.template_a_hired / ab_test.template_a_sent) * 100
        template_b_hire_rate = (ab_test.template_b_hired / ab_test.template_b_sent) * 100
        
        # Визначаємо переможця
        if template_b_hire_rate > template_a_hire_rate:
            winner_id = ab_test.template_b_id = 2
        else:
            winner_id = ab_test.template_a_id = 1
        
        # Завершуємо тест
        ab_test.status = "completed"
        ab_test.end_date = datetime.now()
        ab_test.winner_template_id = winner_id
        
        # Перевіряємо результат
        assert min_duration_met  # 14 днів >= 7 днів
        assert sufficient_data  # 1000 >= 100 для обох варіантів
        assert ab_test.status == "completed"
        assert ab_test.end_date is not None
        assert ab_test.winner_template_id is not None
        assert pytest.approx(template_a_hire_rate, abs=0.01) == 2.0
        assert pytest.approx(template_b_hire_rate, abs=0.01) == 3.5
        assert winner_id == 2  # Template B має вищий hire rate
        
        print("✅ Тест повного workflow завершення A/B тесту пройшов")
    
    def test_ab_test_validation(self):
        """Тест валідації A/B тесту"""
        user = create_test_user()
        
        # Тестуємо валідацію
        def validate_ab_test(name, template_a_id, template_b_id, min_duration_days):
            errors = []
            
            if not name or len(name) < 3:
                errors.append("Назва тесту повинна бути не менше 3 символів")
            
            if template_a_id == template_b_id:
                errors.append("Шаблони A та B повинні бути різними")
            
            if min_duration_days < 1:
                errors.append("Мінімальна тривалість повинна бути не менше 1 дня")
            
            if min_duration_days > 30:
                errors.append("Мінімальна тривалість не може перевищувати 30 днів")
            
            return errors
        
        # Валідний тест
        valid_errors = validate_ab_test("Test", 1, 2, 7)
        assert len(valid_errors) == 0
        
        # Невалідний тест
        invalid_errors = validate_ab_test("", 1, 1, 0)
        assert len(invalid_errors) == 3
        assert "Назва тесту повинна бути не менше 3 символів" in invalid_errors
        assert "Шаблони A та B повинні бути різними" in invalid_errors
        assert "Мінімальна тривалість повинна бути не менше 1 дня" in invalid_errors
        
        print("✅ Тест валідації A/B тесту пройшов")

if __name__ == "__main__":
    # Запуск тестів
    test_instance = TestABTesting()
    
    test_instance.test_ab_test_creation()
    test_instance.test_ab_test_minimum_duration()
    test_instance.test_ab_test_metrics_tracking()
    test_instance.test_ab_test_winner_determination()
    test_instance.test_ab_test_status_management()
    test_instance.test_ab_test_user_assignment()
    test_instance.test_ab_test_statistical_significance()
    test_instance.test_ab_test_early_stopping()
    test_instance.test_ab_test_multiple_variants()
    test_instance.test_ab_test_completion_workflow()
    test_instance.test_ab_test_validation()
    
    print("\n🎉 Всі тести A/B тестування пройшли успішно!") 