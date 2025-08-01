"""
Система метрик для тестування
"""

import time
import psutil
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import pytest


class TestMetrics:
    """Клас для збору метрик тестування"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_before = None
        self.memory_after = None
        self.cpu_before = None
        self.cpu_after = None
        self.test_results = []
        self.coverage_data = {}
        self.performance_data = {}
        self.security_data = {}
    
    def start_test_session(self):
        """Початок сесії тестування"""
        self.start_time = time.time()
        self.memory_before = psutil.Process().memory_info().rss
        self.cpu_before = psutil.cpu_percent()
        
        print(f"🚀 Початок тестування: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def end_test_session(self):
        """Завершення сесії тестування"""
        self.end_time = time.time()
        self.memory_after = psutil.Process().memory_info().rss
        self.cpu_after = psutil.cpu_percent()
        
        execution_time = self.end_time - self.start_time
        memory_used = self.memory_after - self.memory_before
        
        print(f"✅ Завершення тестування: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Час виконання: {execution_time:.2f} секунд")
        print(f"💾 Використано пам'яті: {memory_used / 1024 / 1024:.2f} MB")
        print(f"🖥️  CPU використання: {self.cpu_after:.1f}%")
    
    def record_test_result(self, test_name: str, status: str, duration: float, error: str = None):
        """Запис результату тесту"""
        result = {
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
    
    def record_coverage(self, module: str, coverage_percentage: float, lines_covered: int, total_lines: int):
        """Запис даних покриття"""
        self.coverage_data[module] = {
            "coverage_percentage": coverage_percentage,
            "lines_covered": lines_covered,
            "total_lines": total_lines,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Запис метрики продуктивності"""
        if metric_name not in self.performance_data:
            self.performance_data[metric_name] = []
        
        self.performance_data[metric_name].append({
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_security_issue(self, issue_type: str, severity: str, description: str, location: str = ""):
        """Запис проблеми безпеки"""
        if issue_type not in self.security_data:
            self.security_data[issue_type] = []
        
        self.security_data[issue_type].append({
            "severity": severity,
            "description": description,
            "location": location,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """Генерація звіту з метрик"""
        if not self.start_time or not self.end_time:
            raise ValueError("Тестова сесія не була запущена")
        
        execution_time = self.end_time - self.start_time
        memory_used = self.memory_after - self.memory_before if self.memory_after else 0
        
        # Підрахунок статистики тестів
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        failed_tests = len([r for r in self.test_results if r["status"] == "failed"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "skipped"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Середній час виконання тесту
        avg_test_duration = sum(r["duration"] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Середнє покриття коду
        avg_coverage = sum(c["coverage_percentage"] for c in self.coverage_data.values()) / len(self.coverage_data) if self.coverage_data else 0
        
        report = {
            "session_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "execution_time_seconds": execution_time,
                "memory_used_mb": memory_used / 1024 / 1024,
                "cpu_usage_percent": self.cpu_after
            },
            "test_statistics": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate_percent": success_rate,
                "average_test_duration_seconds": avg_test_duration
            },
            "coverage_summary": {
                "average_coverage_percent": avg_coverage,
                "modules_covered": len(self.coverage_data),
                "detailed_coverage": self.coverage_data
            },
            "performance_summary": {
                "metrics_count": len(self.performance_data),
                "detailed_metrics": self.performance_data
            },
            "security_summary": {
                "issues_count": sum(len(issues) for issues in self.security_data.values()),
                "detailed_issues": self.security_data
            },
            "recommendations": self._generate_recommendations(
                success_rate, avg_coverage, execution_time, memory_used
            )
        }
        
        return report
    
    def _generate_recommendations(self, success_rate: float, coverage: float, execution_time: float, memory_used: int) -> List[str]:
        """Генерація рекомендацій на основі метрик"""
        recommendations = []
        
        if success_rate < 95:
            recommendations.append("🔴 Потрібно покращити успішність тестів (поточний рівень: {:.1f}%)".format(success_rate))
        
        if coverage < 90:
            recommendations.append("🟡 Потрібно збільшити покриття коду (поточний рівень: {:.1f}%)".format(coverage))
        
        if execution_time > 300:  # 5 хвилин
            recommendations.append("🟡 Тести виконуються довго ({} сек). Розгляньте паралелізацію".format(execution_time))
        
        if memory_used > 500 * 1024 * 1024:  # 500MB
            recommendations.append("🟡 Високе використання пам'яті ({} MB). Перевірте на витоки пам'яті".format(memory_used / 1024 / 1024))
        
        if not recommendations:
            recommendations.append("✅ Всі метрики в нормі!")
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """Збереження звіту в файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test-results/metrics_report_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Звіт збережено: {filename}")
        return filename


# Pytest hooks для автоматичного збору метрик
_metrics = TestMetrics()

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Початок сесії тестування"""
    _metrics.start_test_session()

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Завершення сесії тестування"""
    _metrics.end_test_session()
    
    # Генеруємо та зберігаємо звіт
    try:
        report_file = _metrics.save_report()
        print(f"📈 Метрики збережено в: {report_file}")
    except Exception as e:
        print(f"⚠️  Помилка збереження метрик: {e}")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Збір метрик для кожного тесту"""
    start_time = time.time()
    
    # Виконуємо тест
    outcome = yield
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Отримуємо результат
    report = outcome.get_result()
    
    # Записуємо метрики
    status = report.outcome
    error = str(report.longrepr) if report.failed else None
    
    _metrics.record_test_result(
        test_name=item.name,
        status=status,
        duration=duration,
        error=error
    )


# Функції для ручного використання
def start_metrics_collection():
    """Початок збору метрик"""
    _metrics.start_test_session()

def end_metrics_collection():
    """Завершення збору метрик"""
    _metrics.end_test_session()

def record_coverage(module: str, coverage_percentage: float, lines_covered: int, total_lines: int):
    """Запис покриття коду"""
    _metrics.record_coverage(module, coverage_percentage, lines_covered, total_lines)

def record_performance(metric_name: str, value: float, unit: str = ""):
    """Запис метрики продуктивності"""
    _metrics.record_performance_metric(metric_name, value, unit)

def record_security_issue(issue_type: str, severity: str, description: str, location: str = ""):
    """Запис проблеми безпеки"""
    _metrics.record_security_issue(issue_type, severity, description, location)

def get_metrics_report() -> Dict[str, Any]:
    """Отримання звіту з метрик"""
    return _metrics.generate_report()

def save_metrics_report(filename: str = None) -> str:
    """Збереження звіту з метрик"""
    return _metrics.save_report(filename)


# Приклад використання
if __name__ == "__main__":
    # Демонстрація роботи метрик
    metrics = TestMetrics()
    
    # Симулюємо тестову сесію
    metrics.start_test_session()
    
    # Записуємо результати тестів
    metrics.record_test_result("test_auth", "passed", 0.5)
    metrics.record_test_result("test_analytics", "passed", 1.2)
    metrics.record_test_result("test_database", "failed", 0.8, "Connection timeout")
    
    # Записуємо покриття
    metrics.record_coverage("auth", 85.5, 171, 200)
    metrics.record_coverage("analytics", 92.3, 184, 200)
    
    # Записуємо метрики продуктивності
    metrics.record_performance("response_time", 150, "ms")
    metrics.record_performance("throughput", 1000, "rps")
    
    # Записуємо проблеми безпеки
    metrics.record_security_issue("sql_injection", "high", "Potential SQL injection vulnerability", "auth/login")
    
    # Завершуємо сесію
    metrics.end_test_session()
    
    # Генеруємо та зберігаємо звіт
    report_file = metrics.save_report()
    
    print("📊 Демонстрація метрик завершена!")
    print(f"📄 Звіт збережено в: {report_file}") 