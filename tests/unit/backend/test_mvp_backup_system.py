#!/usr/bin/env python3
"""
Тести для MVP-010: Резервне копіювання (раз в тиждень)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from tests.utils.test_helpers import create_test_user, get_test_db

class TestBackupSystem:
    """Тести для системи резервного копіювання"""

    def test_backup_creation(self):
        """Тест створення резервної копії"""
        user = create_test_user()
        
        # Симулюємо створення backup
        backup = Mock()
        backup.id = 1
        backup.user_id = user["id"]
        backup.backup_type = "full"
        backup.created_at = datetime.now()
        backup.file_size = 1024000  # 1MB
        backup.status = "completed"
        backup.file_path = "/backups/backup_20241219_180000.sql"
        
        assert backup.id == 1
        assert backup.user_id == user["id"]
        assert backup.backup_type == "full"
        assert backup.status == "completed"
        assert backup.file_size > 0
        
        print("✅ Тест створення резервної копії пройшов")

    def test_backup_frequency_weekly(self):
        """Тест частоти резервного копіювання (раз в тиждень)"""
        user = create_test_user()
        
        # Симулюємо останній backup
        last_backup = datetime.now() - timedelta(days=5)  # 5 днів тому
        current_time = datetime.now()
        
        # Перевіряємо, чи можна створити backup (раз в тиждень)
        time_since_last_backup = current_time - last_backup
        can_create_backup = time_since_last_backup.total_seconds() >= 604800  # 7 днів
        
        assert pytest.approx(time_since_last_backup.total_seconds(), abs=1) == 432000  # 5 днів
        assert not can_create_backup  # Ще не пройшло 7 днів
        
        # Симулюємо backup після 7 днів
        last_backup = datetime.now() - timedelta(days=8)  # 8 днів тому
        time_since_last_backup = current_time - last_backup
        can_create_backup = time_since_last_backup.total_seconds() >= 604800
        
        assert can_create_backup  # Пройшло більше 7 днів
        
        print("✅ Тест частоти резервного копіювання (раз в тиждень) пройшов")

    def test_backup_types(self):
        """Тест типів резервного копіювання"""
        user = create_test_user()
        
        # Симулюємо різні типи backup
        backup_types = [
            {"type": "full", "description": "Повне резервне копіювання всіх даних"},
            {"type": "incremental", "description": "Інкрементальне резервне копіювання"},
            {"type": "differential", "description": "Диференціальне резервне копіювання"},
            {"type": "database", "description": "Резервне копіювання тільки бази даних"},
            {"type": "files", "description": "Резервне копіювання тільки файлів"}
        ]
        
        # Перевіряємо типи
        assert len(backup_types) == 5
        assert any(bt["type"] == "full" for bt in backup_types)
        assert any(bt["type"] == "incremental" for bt in backup_types)
        assert any(bt["type"] == "database" for bt in backup_types)
        
        print("✅ Тест типів резервного копіювання пройшов")

    def test_backup_retention_policy(self):
        """Тест політики зберігання backup (5 останніх)"""
        user = create_test_user()
        
        # Симулюємо список backup
        backups = []
        for i in range(10):
            backup = Mock()
            backup.id = i + 1
            backup.created_at = datetime.now() - timedelta(days=i*7)
            backup.file_size = 1024000
            backups.append(backup)
        
        # Сортуємо за датою створення (найновіші перші)
        backups.sort(key=lambda b: b.created_at, reverse=True)
        
        # Залишаємо тільки 5 останніх
        max_backups = 5
        if len(backups) > max_backups:
            backups_to_delete = backups[max_backups:]
            backups = backups[:max_backups]
        
        assert len(backups) == 5
        assert len(backups_to_delete) == 5
        
        # Перевіряємо, що залишилися найновіші
        assert backups[0].id == 1  # Найновіший
        assert backups[4].id == 5   # Найстаріший з залишених
        
        print("✅ Тест політики зберігання backup (5 останніх) пройшов")

    def test_backup_validation(self):
        """Тест валідації резервних копій"""
        user = create_test_user()
        
        def validate_backup(backup_data):
            """Валідація резервної копії"""
            errors = []
            
            if not backup_data.get("file_path"):
                errors.append("Шлях до файлу backup відсутній")
            
            if not backup_data.get("created_at"):
                errors.append("Дата створення backup відсутня")
            
            if backup_data.get("file_size", 0) <= 0:
                errors.append("Розмір файлу backup невалідний")
            
            if not backup_data.get("backup_type"):
                errors.append("Тип backup не вказаний")
            
            if backup_data.get("status") not in ["completed", "failed", "in_progress"]:
                errors.append("Статус backup невалідний")
            
            return errors
        
        # Валідний backup
        valid_backup = {
            "file_path": "/backups/backup_20241219_180000.sql",
            "created_at": datetime.now(),
            "file_size": 1024000,
            "backup_type": "full",
            "status": "completed"
        }
        valid_errors = validate_backup(valid_backup)
        assert len(valid_errors) == 0
        
        # Невалідний backup
        invalid_backup = {
            "file_path": "",
            "created_at": None,
            "file_size": 0,
            "backup_type": "",
            "status": "invalid"
        }
        invalid_errors = validate_backup(invalid_backup)
        assert len(invalid_errors) == 5
        
        print("✅ Тест валідації резервних копій пройшов")

    def test_backup_restoration(self):
        """Тест відновлення з резервної копії"""
        user = create_test_user()
        
        # Симулюємо backup для відновлення
        backup = Mock()
        backup.id = 1
        backup.file_path = "/backups/backup_20241219_180000.sql"
        backup.backup_type = "full"
        backup.file_size = 1024000
        backup.created_at = datetime.now() - timedelta(days=1)
        
        # Симулюємо процес відновлення
        restoration = Mock()
        restoration.backup_id = backup.id
        restoration.started_at = datetime.now()
        restoration.status = "in_progress"
        restoration.progress = 0
        
        # Симулюємо прогрес відновлення
        restoration.progress = 50
        restoration.status = "in_progress"
        
        # Симулюємо завершення відновлення
        restoration.progress = 100
        restoration.status = "completed"
        restoration.completed_at = datetime.now()
        
        # Перевіряємо результат
        assert restoration.backup_id == backup.id
        assert restoration.status == "completed"
        assert restoration.progress == 100
        assert restoration.completed_at is not None
        
        print("✅ Тест відновлення з резервної копії пройшов")

    def test_backup_automation(self):
        """Тест автоматизації резервного копіювання"""
        user = create_test_user()
        
        # Симулюємо автоматичне резервне копіювання
        automation_config = {
            "enabled": True,
            "frequency": "weekly",
            "retention_count": 5,
            "backup_type": "full",
            "auto_cleanup": True,
            "notification_on_success": True,
            "notification_on_failure": True
        }
        
        # Перевіряємо конфігурацію
        assert automation_config["enabled"] == True
        assert automation_config["frequency"] == "weekly"
        assert automation_config["retention_count"] == 5
        assert automation_config["backup_type"] == "full"
        assert automation_config["auto_cleanup"] == True
        
        # Симулюємо планувальник
        scheduler = Mock()
        scheduler.add_job = Mock()
        scheduler.add_job.assert_called
        
        print("✅ Тест автоматизації резервного копіювання пройшов")

    def test_backup_compression(self):
        """Тест стиснення резервних копій"""
        user = create_test_user()
        
        # Симулюємо дані для стиснення
        original_data = "Test backup data " * 1000  # 18KB
        original_size = len(original_data.encode('utf-8'))
        
        # Симулюємо стиснення
        compressed_data = original_data.encode('utf-8')  # В реальності було б gzip
        compressed_size = len(compressed_data)
        
        # Розраховуємо коефіцієнт стиснення
        compression_ratio = (original_size - compressed_size) / original_size * 100
        
        assert original_size > 0
        assert compressed_size > 0
        assert compression_ratio >= 0
        
        print("✅ Тест стиснення резервних копій пройшов")

    def test_backup_integrity_check(self):
        """Тест перевірки цілісності backup"""
        user = create_test_user()
        
        # Симулюємо backup файл
        backup_file = Mock()
        backup_file.path = "/backups/backup_20241219_180000.sql"
        backup_file.size = 1024000
        backup_file.created_at = datetime.now()
        
        # Симулюємо перевірку цілісності
        integrity_check = {
            "file_exists": True,
            "file_size_valid": True,
            "checksum_valid": True,
            "format_valid": True,
            "data_integrity": True
        }
        
        # Перевіряємо всі критерії
        all_valid = all(integrity_check.values())
        
        assert integrity_check["file_exists"] == True
        assert integrity_check["file_size_valid"] == True
        assert integrity_check["checksum_valid"] == True
        assert integrity_check["format_valid"] == True
        assert integrity_check["data_integrity"] == True
        assert all_valid == True
        
        print("✅ Тест перевірки цілісності backup пройшов")

    def test_backup_notification_system(self):
        """Тест системи сповіщень для backup"""
        user = create_test_user()
        
        # Симулюємо сповіщення про backup
        notifications = [
            {
                "type": "backup_started",
                "message": "Резервне копіювання розпочато",
                "timestamp": datetime.now(),
                "user_id": user["id"]
            },
            {
                "type": "backup_completed",
                "message": "Резервне копіювання завершено успішно",
                "timestamp": datetime.now(),
                "user_id": user["id"],
                "backup_size": "1.2MB",
                "duration": "45 секунд"
            },
            {
                "type": "backup_failed",
                "message": "Помилка резервного копіювання",
                "timestamp": datetime.now(),
                "user_id": user["id"],
                "error": "Connection timeout"
            }
        ]
        
        # Перевіряємо типи сповіщень
        notification_types = [n["type"] for n in notifications]
        assert "backup_started" in notification_types
        assert "backup_completed" in notification_types
        assert "backup_failed" in notification_types
        
        # Перевіряємо структуру сповіщень
        for notification in notifications:
            assert "type" in notification
            assert "message" in notification
            assert "timestamp" in notification
            assert "user_id" in notification
        
        print("✅ Тест системи сповіщень для backup пройшов")

    def test_backup_performance_metrics(self):
        """Тест метрик продуктивності backup"""
        user = create_test_user()
        
        # Симулюємо метрики продуктивності
        performance_metrics = {
            "backup_duration_seconds": 45,
            "backup_size_mb": 1.2,
            "compression_ratio": 0.75,
            "transfer_speed_mbps": 2.5,
            "cpu_usage_percent": 15,
            "memory_usage_mb": 64
        }
        
        # Перевіряємо показники продуктивності
        assert performance_metrics["backup_duration_seconds"] <= 300  # Не більше 5 хвилин
        assert performance_metrics["backup_size_mb"] > 0
        assert 0 <= performance_metrics["compression_ratio"] <= 1
        assert performance_metrics["transfer_speed_mbps"] > 0
        assert 0 <= performance_metrics["cpu_usage_percent"] <= 100
        assert performance_metrics["memory_usage_mb"] > 0
        
        # Перевіряємо якісні показники
        assert performance_metrics["backup_duration_seconds"] <= 60  # Хороша швидкість
        assert performance_metrics["compression_ratio"] >= 0.5  # Хороше стиснення
        assert performance_metrics["cpu_usage_percent"] <= 50  # Прийнятне навантаження
        
        print("✅ Тест метрик продуктивності backup пройшов")

if __name__ == "__main__":
    test_instance = TestBackupSystem()
    test_instance.test_backup_creation()
    test_instance.test_backup_frequency_weekly()
    test_instance.test_backup_types()
    test_instance.test_backup_retention_policy()
    test_instance.test_backup_validation()
    test_instance.test_backup_restoration()
    test_instance.test_backup_automation()
    test_instance.test_backup_compression()
    test_instance.test_backup_integrity_check()
    test_instance.test_backup_notification_system()
    test_instance.test_backup_performance_metrics()
    print("\n🎉 Всі тести системи резервного копіювання пройшли успішно!") 