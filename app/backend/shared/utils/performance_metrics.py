"""
Розширені метрики продуктивності для логування
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

from shared.config.logging import get_logger


@dataclass
class PerformanceMetric:
    """Метрика продуктивності"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class SystemMetrics:
    """Системні метрики"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: datetime


class PerformanceMetricsCollector:
    """Збірник метрик продуктивності"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("performance-metrics")
        self.metrics_history: deque = deque(maxlen=10000)  # Останні 10k метрик
        self.system_metrics_history: deque = deque(maxlen=1000)  # Останні 1k системних метрик
        self.custom_metrics: Dict[str, Callable] = {}
        self.collection_interval = 60  # секунди
        self.running = False
        self.collection_thread = None
        
        self.logger.info("Ініціалізовано збірник метрик продуктивності", extra={
            "service_name": service_name,
            "collection_interval": self.collection_interval
        })
    
    def start_collection(self):
        """Запуск збору метрик"""
        if self.running:
            self.logger.warning("Збір метрик вже запущений")
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collect_metrics_loop, daemon=True)
        self.collection_thread.start()
        
        self.logger.info("Збір метрик продуктивності запущений")
    
    def stop_collection(self):
        """Зупинка збору метрик"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
        self.logger.info("Збір метрик продуктивності зупинений")
    
    def _collect_metrics_loop(self):
        """Цикл збору метрик"""
        while self.running:
            try:
                # Збір системних метрик
                system_metrics = self._collect_system_metrics()
                self.system_metrics_history.append(system_metrics)
                
                # Збір кастомних метрик
                custom_metrics = self._collect_custom_metrics()
                for metric in custom_metrics:
                    self.metrics_history.append(metric)
                
                # Логування метрик
                self._log_metrics(system_metrics, custom_metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error("Помилка збору метрик", extra={"error": str(e)})
                time.sleep(10)  # Коротка пауза при помилці
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Збір системних метрик"""
        try:
            # CPU використання
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Використання пам'яті
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Використання диску
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Мережевий I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error("Помилка збору системних метрик", extra={"error": str(e)})
            return SystemMetrics(0, 0, 0, {}, datetime.utcnow())
    
    def _collect_custom_metrics(self) -> List[PerformanceMetric]:
        """Збір кастомних метрик"""
        metrics = []
        
        for metric_name, metric_func in self.custom_metrics.items():
            try:
                value = metric_func()
                metric = PerformanceMetric(
                    name=metric_name,
                    value=value,
                    unit="count",
                    timestamp=datetime.utcnow(),
                    tags={"service": self.service_name, "type": "custom"},
                    metadata={}
                )
                metrics.append(metric)
            except Exception as e:
                self.logger.error(f"Помилка збору метрики {metric_name}", extra={"error": str(e)})
        
        return metrics
    
    def _log_metrics(self, system_metrics: SystemMetrics, custom_metrics: List[PerformanceMetric]):
        """Логування метрик"""
        # Логування системних метрик
        self.logger.performance("System metrics collected", extra={
            "cpu_usage_percent": system_metrics.cpu_usage,
            "memory_usage_percent": system_metrics.memory_usage,
            "disk_usage_percent": system_metrics.disk_usage,
            "network_bytes_sent": system_metrics.network_io.get("bytes_sent", 0),
            "network_bytes_recv": system_metrics.network_io.get("bytes_recv", 0),
            "timestamp": system_metrics.timestamp.isoformat()
        })
        
        # Логування кастомних метрик
        for metric in custom_metrics:
            self.logger.performance(f"Custom metric: {metric.name}", extra={
                "metric_name": metric.name,
                "metric_value": metric.value,
                "metric_unit": metric.unit,
                "metric_tags": metric.tags,
                "timestamp": metric.timestamp.isoformat()
            })
    
    def add_custom_metric(self, name: str, metric_func: Callable[[], float]):
        """Додавання кастомної метрики"""
        self.custom_metrics[name] = metric_func
        self.logger.info(f"Додано кастомну метрику: {name}")
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Отримання зведення метрик"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Фільтруємо метрики за часом
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        recent_system_metrics = [m for m in self.system_metrics_history if m.timestamp > cutoff_time]
        
        summary = {
            "period_hours": hours,
            "metrics_count": len(recent_metrics),
            "system_metrics_count": len(recent_system_metrics),
            "custom_metrics": {},
            "system_metrics": {}
        }
        
        # Агрегація кастомних метрик
        if recent_metrics:
            metric_groups = defaultdict(list)
            for metric in recent_metrics:
                metric_groups[metric.name].append(metric.value)
            
            for name, values in metric_groups.items():
                summary["custom_metrics"][name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
        
        # Агрегація системних метрик
        if recent_system_metrics:
            cpu_values = [m.cpu_usage for m in recent_system_metrics]
            memory_values = [m.memory_usage for m in recent_system_metrics]
            disk_values = [m.disk_usage for m in recent_system_metrics]
            
            summary["system_metrics"] = {
                "cpu_usage": {
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "avg": sum(cpu_values) / len(cpu_values)
                },
                "memory_usage": {
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "avg": sum(memory_values) / len(memory_values)
                },
                "disk_usage": {
                    "min": min(disk_values),
                    "max": max(disk_values),
                    "avg": sum(disk_values) / len(disk_values)
                }
            }
        
        return summary


class DatabaseMetrics:
    """Метрики бази даних"""
    
    def __init__(self, logger):
        self.logger = logger
        self.query_times = deque(maxlen=1000)
        self.connection_pool_stats = {}
    
    def log_query(self, query: str, duration: float, rows_affected: int = None):
        """Логування запиту до БД"""
        self.query_times.append(duration)
        
        self.logger.database("Database query executed", extra={
            "query_type": self._get_query_type(query),
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected,
            "query_hash": hash(query) % 10000  # Хеш для анонімізації
        })
    
    def _get_query_type(self, query: str) -> str:
        """Визначення типу запиту"""
        query_upper = query.strip().upper()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Отримання статистики продуктивності БД"""
        if not self.query_times:
            return {}
        
        times = list(self.query_times)
        return {
            "total_queries": len(times),
            "avg_query_time_ms": sum(times) / len(times) * 1000,
            "max_query_time_ms": max(times) * 1000,
            "min_query_time_ms": min(times) * 1000,
            "slow_queries_count": len([t for t in times if t > 1.0])  # > 1 секунди
        }


class APIMetrics:
    """Метрики API"""
    
    def __init__(self, logger):
        self.logger = logger
        self.request_times = deque(maxlen=1000)
        self.status_codes = defaultdict(int)
        self.endpoint_usage = defaultdict(int)
    
    def log_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Логування API запиту"""
        self.request_times.append(duration)
        self.status_codes[status_code] += 1
        self.endpoint_usage[f"{method} {endpoint}"] += 1
        
        self.logger.api_call(method, endpoint, status_code, duration, extra={
            "response_time_ms": round(duration * 1000, 2),
            "success": 200 <= status_code < 400
        })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Отримання статистики продуктивності API"""
        if not self.request_times:
            return {}
        
        times = list(self.request_times)
        return {
            "total_requests": len(times),
            "avg_response_time_ms": sum(times) / len(times) * 1000,
            "max_response_time_ms": max(times) * 1000,
            "min_response_time_ms": min(times) * 1000,
            "status_codes": dict(self.status_codes),
            "top_endpoints": dict(sorted(self.endpoint_usage.items(), key=lambda x: x[1], reverse=True)[:10])
        }


class SecurityMetrics:
    """Метрики безпеки"""
    
    def __init__(self, logger):
        self.logger = logger
        self.security_events = deque(maxlen=1000)
        self.failed_logins = 0
        self.unauthorized_access = 0
        self.suspicious_ips = set()
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Логування події безпеки"""
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        self.security_events.append(event)
        
        # Оновлення лічильників
        if event_type == "failed_login":
            self.failed_logins += 1
        elif event_type == "unauthorized_access":
            self.unauthorized_access += 1
        
        if "ip_address" in details:
            self.suspicious_ips.add(details["ip_address"])
        
        self.logger.security(f"Security event: {event_type}", extra=details)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Отримання статистики безпеки"""
        return {
            "total_security_events": len(self.security_events),
            "failed_logins": self.failed_logins,
            "unauthorized_access": self.unauthorized_access,
            "suspicious_ips_count": len(self.suspicious_ips),
            "recent_events": list(self.security_events)[-10:]  # Останні 10 подій
        }


# Глобальні екземпляри метрик
performance_collector = None
database_metrics = None
api_metrics = None
security_metrics = None


def initialize_metrics(service_name: str):
    """Ініціалізація метрик"""
    global performance_collector, database_metrics, api_metrics, security_metrics
    
    logger = get_logger("metrics")
    
    # Ініціалізація збірника метрик
    performance_collector = PerformanceMetricsCollector(service_name)
    performance_collector.start_collection()
    
    # Ініціалізація спеціалізованих метрик
    database_metrics = DatabaseMetrics(logger)
    api_metrics = APIMetrics(logger)
    security_metrics = SecurityMetrics(logger)
    
    logger.info("Метрики продуктивності ініціалізовані", extra={
        "service_name": service_name,
        "components": ["performance_collector", "database_metrics", "api_metrics", "security_metrics"]
    })


def get_metrics_summary() -> Dict[str, Any]:
    """Отримання зведення всіх метрик"""
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "performance": {},
        "database": {},
        "api": {},
        "security": {}
    }
    
    if performance_collector:
        summary["performance"] = performance_collector.get_metrics_summary()
    
    if database_metrics:
        summary["database"] = database_metrics.get_performance_stats()
    
    if api_metrics:
        summary["api"] = api_metrics.get_performance_stats()
    
    if security_metrics:
        summary["security"] = security_metrics.get_security_stats()
    
    return summary 