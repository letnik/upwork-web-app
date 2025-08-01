"""
Сервіс автоматичного очищення та архівування логів
"""

import os
import shutil
import gzip
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
import schedule
import time
import threading
from dataclasses import dataclass

from shared.config.logging import get_logger


@dataclass
class CleanupConfig:
    """Конфігурація очищення логів"""
    retention_days: int = 90
    archive_enabled: bool = True
    archive_path: str = "logs/archive"
    compression_enabled: bool = True
    cleanup_interval_hours: int = 24
    max_archive_size_gb: int = 10
    backup_enabled: bool = True
    backup_path: str = "logs/backup"


class LogCleanupService:
    """Сервіс очищення та архівування логів"""
    
    def __init__(self, config: CleanupConfig = None):
        self.config = config or CleanupConfig()
        self.logger = get_logger("log-cleanup-service")
        self.running = False
        self.cleanup_thread = None
        
        # Створюємо директорії
        self._create_directories()
    
    def _create_directories(self):
        """Створення необхідних директорій"""
        directories = [
            self.config.archive_path,
            self.config.backup_path
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def start_scheduled_cleanup(self):
        """Запуск планового очищення"""
        if self.running:
            self.logger.warning("Сервіс очищення вже запущений")
            return
        
        self.running = True
        
        # Налаштування розкладу
        schedule.every(self.config.cleanup_interval_hours).hours.do(self.cleanup_old_logs)
        schedule.every().day.at("02:00").do(self.archive_logs)
        schedule.every().week.do(self.cleanup_old_archives)
        
        # Запуск в окремому потоці
        self.cleanup_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("Сервіс очищення логів запущений")
    
    def stop_scheduled_cleanup(self):
        """Зупинка планового очищення"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join()
        self.logger.info("Сервіс очищення логів зупинений")
    
    def _run_scheduler(self):
        """Запуск планувальника"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Перевірка кожну хвилину
    
    def cleanup_old_logs(self) -> Dict[str, int]:
        """Очищення старих логів"""
        self.logger.info("Початок очищення старих логів")
        
        cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
        cleanup_stats = {
            "deleted_files": 0,
            "archived_files": 0,
            "total_size_freed": 0
        }
        
        try:
            # Очищення основних логів
            main_logs_path = Path("logs")
            if main_logs_path.exists():
                stats = self._cleanup_directory(main_logs_path, cutoff_date)
                cleanup_stats["deleted_files"] += stats["deleted_files"]
                cleanup_stats["archived_files"] += stats["archived_files"]
                cleanup_stats["total_size_freed"] += stats["size_freed"]
            
            # Очищення тестових логів
            test_logs_path = Path("logs/test")
            if test_logs_path.exists():
                stats = self._cleanup_directory(test_logs_path, cutoff_date)
                cleanup_stats["deleted_files"] += stats["deleted_files"]
                cleanup_stats["archived_files"] += stats["archived_files"]
                cleanup_stats["total_size_freed"] += stats["size_freed"]
            
            self.logger.info("Очищення завершено", extra=cleanup_stats)
            
        except Exception as e:
            self.logger.error("Помилка очищення логів", extra={"error": str(e)})
        
        return cleanup_stats
    
    def _cleanup_directory(self, directory: Path, cutoff_date: datetime) -> Dict[str, int]:
        """Очищення директорії"""
        stats = {
            "deleted_files": 0,
            "archived_files": 0,
            "size_freed": 0
        }
        
        for log_file in directory.glob("*.log*"):
            try:
                file_stat = log_file.stat()
                file_date = datetime.fromtimestamp(file_stat.st_mtime)
                
                if file_date < cutoff_date:
                    file_size = file_stat.st_size
                    
                    if self.config.archive_enabled:
                        # Архівування файлу
                        if self._archive_file(log_file):
                            stats["archived_files"] += 1
                            stats["size_freed"] += file_size
                    else:
                        # Видалення файлу
                        log_file.unlink()
                        stats["deleted_files"] += 1
                        stats["size_freed"] += file_size
                    
                    self.logger.info(f"Оброблено файл: {log_file.name}", extra={
                        "file_size": file_size,
                        "file_date": file_date.isoformat(),
                        "archived": self.config.archive_enabled
                    })
            
            except Exception as e:
                self.logger.error(f"Помилка обробки файлу {log_file.name}", extra={"error": str(e)})
        
        return stats
    
    def _archive_file(self, file_path: Path) -> bool:
        """Архівування файлу"""
        try:
            # Створюємо ім'я архіву
            archive_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log.gz"
            archive_path = Path(self.config.archive_path) / archive_name
            
            # Стиснення файлу
            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Видалення оригінального файлу
            file_path.unlink()
            
            # Створення метаданих архіву
            self._create_archive_metadata(archive_path, file_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка архівування {file_path.name}", extra={"error": str(e)})
            return False
    
    def _create_archive_metadata(self, archive_path: Path, original_file: Path):
        """Створення метаданих архіву"""
        metadata = {
            "original_file": str(original_file),
            "archived_at": datetime.now().isoformat(),
            "archive_size": archive_path.stat().st_size,
            "compression_ratio": self._calculate_compression_ratio(original_file, archive_path)
        }
        
        metadata_path = archive_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _calculate_compression_ratio(self, original_file: Path, archive_file: Path) -> float:
        """Розрахунок коефіцієнта стиснення"""
        try:
            original_size = original_file.stat().st_size
            archive_size = archive_file.stat().st_size
            return archive_size / original_size if original_size > 0 else 1.0
        except:
            return 1.0
    
    def archive_logs(self) -> Dict[str, int]:
        """Архівування поточних логів"""
        self.logger.info("Початок архівування логів")
        
        archive_stats = {
            "archived_files": 0,
            "total_size": 0,
            "compressed_size": 0
        }
        
        try:
            # Архівування основних логів
            main_logs_path = Path("logs")
            if main_logs_path.exists():
                stats = self._archive_directory(main_logs_path)
                archive_stats["archived_files"] += stats["archived_files"]
                archive_stats["total_size"] += stats["total_size"]
                archive_stats["compressed_size"] += stats["compressed_size"]
            
            # Архівування тестових логів
            test_logs_path = Path("logs/test")
            if test_logs_path.exists():
                stats = self._archive_directory(test_logs_path)
                archive_stats["archived_files"] += stats["archived_files"]
                archive_stats["total_size"] += stats["total_size"]
                archive_stats["compressed_size"] += stats["compressed_size"]
            
            self.logger.info("Архівування завершено", extra=archive_stats)
            
        except Exception as e:
            self.logger.error("Помилка архівування", extra={"error": str(e)})
        
        return archive_stats
    
    def _archive_directory(self, directory: Path) -> Dict[str, int]:
        """Архівування директорії"""
        stats = {
            "archived_files": 0,
            "total_size": 0,
            "compressed_size": 0
        }
        
        for log_file in directory.glob("*.log"):
            try:
                file_size = log_file.stat().st_size
                
                # Архівування файлу
                if self._archive_file(log_file):
                    stats["archived_files"] += 1
                    stats["total_size"] += file_size
                    
                    # Розрахунок стиснутого розміру
                    archive_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log.gz"
                    archive_path = Path(self.config.archive_path) / archive_name
                    if archive_path.exists():
                        stats["compressed_size"] += archive_path.stat().st_size
                
            except Exception as e:
                self.logger.error(f"Помилка архівування {log_file.name}", extra={"error": str(e)})
        
        return stats
    
    def cleanup_old_archives(self) -> Dict[str, int]:
        """Очищення старих архівів"""
        self.logger.info("Початок очищення старих архівів")
        
        cleanup_stats = {
            "deleted_archives": 0,
            "size_freed": 0
        }
        
        try:
            archive_path = Path(self.config.archive_path)
            if not archive_path.exists():
                return cleanup_stats
            
            # Отримуємо всі архіви
            archives = list(archive_path.glob("*.log.gz"))
            
            # Сортуємо за датою створення
            archives.sort(key=lambda x: x.stat().st_mtime)
            
            # Розраховуємо загальний розмір
            total_size = sum(archive.stat().st_size for archive in archives)
            max_size_bytes = self.config.max_archive_size_gb * 1024 * 1024 * 1024
            
            # Видаляємо старі архіви, якщо перевищено ліміт
            for archive in archives:
                if total_size <= max_size_bytes:
                    break
                
                try:
                    file_size = archive.stat().st_size
                    archive.unlink()
                    
                    # Видаляємо метадані
                    metadata_file = archive.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    cleanup_stats["deleted_archives"] += 1
                    cleanup_stats["size_freed"] += file_size
                    total_size -= file_size
                    
                    self.logger.info(f"Видалено архів: {archive.name}")
                    
                except Exception as e:
                    self.logger.error(f"Помилка видалення архіву {archive.name}", extra={"error": str(e)})
            
            self.logger.info("Очищення архівів завершено", extra=cleanup_stats)
            
        except Exception as e:
            self.logger.error("Помилка очищення архівів", extra={"error": str(e)})
        
        return cleanup_stats
    
    def backup_logs(self) -> Dict[str, int]:
        """Резервне копіювання логів"""
        if not self.config.backup_enabled:
            return {"backup_files": 0, "backup_size": 0}
        
        self.logger.info("Початок резервного копіювання логів")
        
        backup_stats = {
            "backup_files": 0,
            "backup_size": 0
        }
        
        try:
            backup_path = Path(self.config.backup_path)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Створюємо timestamp для backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = backup_path / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            # Копіюємо основні логи
            main_logs_path = Path("logs")
            if main_logs_path.exists():
                for log_file in main_logs_path.glob("*.log"):
                    try:
                        backup_file = backup_dir / log_file.name
                        shutil.copy2(log_file, backup_file)
                        backup_stats["backup_files"] += 1
                        backup_stats["backup_size"] += log_file.stat().st_size
                    except Exception as e:
                        self.logger.error(f"Помилка backup {log_file.name}", extra={"error": str(e)})
            
            # Копіюємо тестові логи
            test_logs_path = Path("logs/test")
            if test_logs_path.exists():
                test_backup_dir = backup_dir / "test"
                test_backup_dir.mkdir(exist_ok=True)
                
                for log_file in test_logs_path.glob("*.log"):
                    try:
                        backup_file = test_backup_dir / log_file.name
                        shutil.copy2(log_file, backup_file)
                        backup_stats["backup_files"] += 1
                        backup_stats["backup_size"] += log_file.stat().st_size
                    except Exception as e:
                        self.logger.error(f"Помилка backup {log_file.name}", extra={"error": str(e)})
            
            # Створюємо метадані backup
            backup_metadata = {
                "backup_timestamp": timestamp,
                "backup_files": backup_stats["backup_files"],
                "backup_size": backup_stats["backup_size"],
                "created_at": datetime.now().isoformat()
            }
            
            metadata_file = backup_dir / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(backup_metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Резервне копіювання завершено", extra=backup_stats)
            
        except Exception as e:
            self.logger.error("Помилка резервного копіювання", extra={"error": str(e)})
        
        return backup_stats
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Отримання статистики очищення"""
        try:
            stats = {
                "logs_directory_size": 0,
                "archive_directory_size": 0,
                "backup_directory_size": 0,
                "total_log_files": 0,
                "total_archive_files": 0,
                "total_backup_files": 0
            }
            
            # Розмір директорії логів
            logs_path = Path("logs")
            if logs_path.exists():
                stats["logs_directory_size"] = self._get_directory_size(logs_path)
                stats["total_log_files"] = len(list(logs_path.rglob("*.log")))
            
            # Розмір директорії архівів
            archive_path = Path(self.config.archive_path)
            if archive_path.exists():
                stats["archive_directory_size"] = self._get_directory_size(archive_path)
                stats["total_archive_files"] = len(list(archive_path.glob("*.log.gz")))
            
            # Розмір директорії backup
            backup_path = Path(self.config.backup_path)
            if backup_path.exists():
                stats["backup_directory_size"] = self._get_directory_size(backup_path)
                stats["total_backup_files"] = len(list(backup_path.rglob("*.log")))
            
            return stats
            
        except Exception as e:
            self.logger.error("Помилка отримання статистики", extra={"error": str(e)})
            return {}
    
    def _get_directory_size(self, directory: Path) -> int:
        """Розрахунок розміру директорії"""
        total_size = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size


# Глобальний екземпляр сервісу очищення
log_cleanup_service = LogCleanupService() 