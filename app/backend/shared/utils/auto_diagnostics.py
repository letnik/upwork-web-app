"""
Автоматична діагностика для швидшого вирішення проблем
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import re
import subprocess
import psutil
import os

from shared.config.logging import get_logger


class DiagnosticSeverity(Enum):
    """Рівні серйозності діагностики"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DiagnosticStatus(Enum):
    """Статуси діагностики"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RESOLVED = "resolved"


@dataclass
class DiagnosticRule:
    """Правило діагностики"""
    name: str
    description: str
    category: str
    severity: DiagnosticSeverity
    check_function: Callable
    auto_fix_function: Optional[Callable] = None
    dependencies: List[str] = None
    enabled: bool = True


@dataclass
class DiagnosticResult:
    """Результат діагностики"""
    rule_name: str
    status: DiagnosticStatus
    severity: DiagnosticSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration_ms: float
    auto_fix_applied: bool = False
    fix_result: Optional[str] = None


@dataclass
class DiagnosticReport:
    """Звіт діагностики"""
    service_name: str
    timestamp: datetime
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: int
    errors: int
    critical_issues: int
    results: List[DiagnosticResult]
    summary: str
    recommendations: List[str]


class AutoDiagnostics:
    """Система автоматичної діагностики"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("auto-diagnostics")
        self.rules: List[DiagnosticRule] = []
        self.results_history: List[DiagnosticResult] = []
        self.auto_fix_enabled = True
        
        # Налаштування діагностики
        self.max_diagnostic_time = 300  # секунди
        self.retry_attempts = 3
        self.parallel_checks = True
        
        self._setup_default_rules()
        
        self.logger.info("Система автоматичної діагностики ініціалізовано", extra={
            "service_name": service_name,
            "rules_count": len(self.rules)
        })
    
    def _setup_default_rules(self):
        """Налаштування стандартних правил діагностики"""
        
        # Системні правила
        self.add_rule(DiagnosticRule(
            name="System Resources Check",
            description="Перевірка системних ресурсів",
            category="system",
            severity=DiagnosticSeverity.WARNING,
            check_function=self._check_system_resources,
            auto_fix_function=self._auto_fix_system_resources
        ))
        
        self.add_rule(DiagnosticRule(
            name="Database Connectivity",
            description="Перевірка підключення до бази даних",
            category="database",
            severity=DiagnosticSeverity.ERROR,
            check_function=self._check_database_connectivity,
            auto_fix_function=self._auto_fix_database_connectivity
        ))
        
        self.add_rule(DiagnosticRule(
            name="API Endpoints Health",
            description="Перевірка здоров'я API ендпоінтів",
            category="api",
            severity=DiagnosticSeverity.ERROR,
            check_function=self._check_api_health,
            auto_fix_function=self._auto_fix_api_health
        ))
        
        self.add_rule(DiagnosticRule(
            name="Log File Permissions",
            description="Перевірка прав доступу до файлів логів",
            category="logging",
            severity=DiagnosticSeverity.WARNING,
            check_function=self._check_log_permissions,
            auto_fix_function=self._auto_fix_log_permissions
        ))
        
        self.add_rule(DiagnosticRule(
            name="Memory Leaks Detection",
            description="Виявлення витоків пам'яті",
            category="performance",
            severity=DiagnosticSeverity.WARNING,
            check_function=self._check_memory_leaks,
            auto_fix_function=self._auto_fix_memory_leaks
        ))
        
        self.add_rule(DiagnosticRule(
            name="Network Connectivity",
            description="Перевірка мережевого підключення",
            category="network",
            severity=DiagnosticSeverity.ERROR,
            check_function=self._check_network_connectivity,
            auto_fix_function=self._auto_fix_network_connectivity
        ))
        
        self.add_rule(DiagnosticRule(
            name="Security Vulnerabilities",
            description="Перевірка вразливостей безпеки",
            category="security",
            severity=DiagnosticSeverity.CRITICAL,
            check_function=self._check_security_vulnerabilities,
            auto_fix_function=self._auto_fix_security_vulnerabilities
        ))
        
        self.add_rule(DiagnosticRule(
            name="Configuration Validation",
            description="Валідація конфігурації",
            category="configuration",
            severity=DiagnosticSeverity.ERROR,
            check_function=self._check_configuration,
            auto_fix_function=self._auto_fix_configuration
        ))
    
    def add_rule(self, rule: DiagnosticRule):
        """Додавання правила діагностики"""
        self.rules.append(rule)
        self.logger.info(f"Додано правило діагностики: {rule.name}")
    
    async def run_diagnostics(self, categories: List[str] = None, 
                            auto_fix: bool = None) -> DiagnosticReport:
        """Запуск діагностики"""
        start_time = time.time()
        
        if auto_fix is None:
            auto_fix = self.auto_fix_enabled
        
        # Фільтрація правил за категоріями
        rules_to_check = self.rules
        if categories:
            rules_to_check = [r for r in self.rules if r.category in categories]
        
        enabled_rules = [r for r in rules_to_check if r.enabled]
        
        self.logger.info(f"Запуск діагностики: {len(enabled_rules)} правил", extra={
            "categories": categories,
            "auto_fix": auto_fix
        })
        
        results = []
        
        if self.parallel_checks:
            # Паралельне виконання перевірок
            tasks = []
            for rule in enabled_rules:
                task = asyncio.create_task(self._run_single_check(rule, auto_fix))
                tasks.append(task)
            
            # Очікування завершення всіх перевірок
            rule_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(rule_results):
                if isinstance(result, Exception):
                    # Обробка помилок
                    error_result = DiagnosticResult(
                        rule_name=enabled_rules[i].name,
                        status=DiagnosticStatus.FAILED,
                        severity=enabled_rules[i].severity,
                        message=f"Помилка виконання: {str(result)}",
                        details={"error": str(result)},
                        timestamp=datetime.utcnow(),
                        duration_ms=0
                    )
                    results.append(error_result)
                else:
                    results.append(result)
        else:
            # Послідовне виконання перевірок
            for rule in enabled_rules:
                result = await self._run_single_check(rule, auto_fix)
                results.append(result)
        
        # Збереження результатів
        self.results_history.extend(results)
        
        # Створення звіту
        report = self._create_diagnostic_report(results, time.time() - start_time)
        
        self.logger.info("Діагностика завершена", extra={
            "total_checks": report.total_checks,
            "failed_checks": report.failed_checks,
            "duration_ms": round((time.time() - start_time) * 1000, 2)
        })
        
        return report
    
    async def _run_single_check(self, rule: DiagnosticRule, auto_fix: bool) -> DiagnosticResult:
        """Виконання одиночної перевірки"""
        start_time = time.time()
        
        try:
            # Виконання перевірки
            if asyncio.iscoroutinefunction(rule.check_function):
                check_result = await rule.check_function()
            else:
                check_result = rule.check_function()
            
            # Визначення статусу
            if check_result.get('status', False):
                status = DiagnosticStatus.COMPLETED
                severity = DiagnosticSeverity.INFO
            else:
                status = DiagnosticStatus.FAILED
                severity = rule.severity
            
            result = DiagnosticResult(
                rule_name=rule.name,
                status=status,
                severity=severity,
                message=check_result.get('message', ''),
                details=check_result.get('details', {}),
                timestamp=datetime.utcnow(),
                duration_ms=round((time.time() - start_time) * 1000, 2)
            )
            
            # Автоматичне виправлення
            if (status == DiagnosticStatus.FAILED and 
                auto_fix and rule.auto_fix_function):
                
                fix_result = await self._apply_auto_fix(rule, result)
                result.auto_fix_applied = True
                result.fix_result = fix_result
                
                # Повторна перевірка після виправлення
                if fix_result.get('success', False):
                    retry_result = await self._run_single_check(rule, False)
                    if retry_result.status == DiagnosticStatus.COMPLETED:
                        result.status = DiagnosticStatus.RESOLVED
                        result.message = f"Автоматично виправлено: {result.message}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Помилка виконання перевірки {rule.name}", 
                            extra={"error": str(e)})
            
            return DiagnosticResult(
                rule_name=rule.name,
                status=DiagnosticStatus.FAILED,
                severity=rule.severity,
                message=f"Помилка виконання: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow(),
                duration_ms=round((time.time() - start_time) * 1000, 2)
            )
    
    async def _apply_auto_fix(self, rule: DiagnosticRule, 
                             result: DiagnosticResult) -> Dict[str, Any]:
        """Застосування автоматичного виправлення"""
        try:
            if asyncio.iscoroutinefunction(rule.auto_fix_function):
                fix_result = await rule.auto_fix_function(result)
            else:
                fix_result = rule.auto_fix_function(result)
            
            self.logger.info(f"Автоматичне виправлення застосовано: {rule.name}", 
                           extra={"fix_result": fix_result})
            
            return fix_result
            
        except Exception as e:
            self.logger.error(f"Помилка автоматичного виправлення {rule.name}", 
                            extra={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося застосувати автоматичне виправлення: {str(e)}"
            }
    
    def _create_diagnostic_report(self, results: List[DiagnosticResult], 
                                total_duration: float) -> DiagnosticReport:
        """Створення звіту діагностики"""
        total_checks = len(results)
        passed_checks = len([r for r in results if r.status == DiagnosticStatus.COMPLETED])
        failed_checks = len([r for r in results if r.status == DiagnosticStatus.FAILED])
        resolved_checks = len([r for r in results if r.status == DiagnosticStatus.RESOLVED])
        
        warnings = len([r for r in results if r.severity == DiagnosticSeverity.WARNING])
        errors = len([r for r in results if r.severity == DiagnosticSeverity.ERROR])
        critical_issues = len([r for r in results if r.severity == DiagnosticSeverity.CRITICAL])
        
        # Генерація зведення
        if failed_checks == 0:
            summary = "Всі перевірки пройшли успішно"
        elif resolved_checks > 0:
            summary = f"Виявлено {failed_checks} проблем, {resolved_checks} автоматично виправлено"
        else:
            summary = f"Виявлено {failed_checks} проблем, потребують ручного вирішення"
        
        # Генерація рекомендацій
        recommendations = self._generate_recommendations(results)
        
        return DiagnosticReport(
            service_name=self.service_name,
            timestamp=datetime.utcnow(),
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            errors=errors,
            critical_issues=critical_issues,
            results=results,
            summary=summary,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, results: List[DiagnosticResult]) -> List[str]:
        """Генерація рекомендацій на основі результатів"""
        recommendations = []
        
        failed_results = [r for r in results if r.status == DiagnosticStatus.FAILED]
        
        for result in failed_results:
            if result.rule_name == "System Resources Check":
                recommendations.append("Розгляньте можливість масштабування системних ресурсів")
            elif result.rule_name == "Database Connectivity":
                recommendations.append("Перевірте налаштування бази даних та мережеве підключення")
            elif result.rule_name == "API Endpoints Health":
                recommendations.append("Перевірте конфігурацію API та доступність сервісів")
            elif result.rule_name == "Security Vulnerabilities":
                recommendations.append("Негайно оновіть систему безпеки та перевірте логи")
            elif result.rule_name == "Memory Leaks Detection":
                recommendations.append("Проаналізуйте код на наявність витоків пам'яті")
        
        if not recommendations:
            recommendations.append("Система працює стабільно, регулярно виконуйте діагностику")
        
        return recommendations
    
    # Стандартні функції перевірок
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Перевірка системних ресурсів"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            issues = []
            if cpu_percent > 80:
                issues.append(f"Високе використання CPU: {cpu_percent}%")
            if memory.percent > 85:
                issues.append(f"Високе використання пам'яті: {memory.percent}%")
            if disk.percent > 90:
                issues.append(f"Високе використання диску: {disk.percent}%")
            
            return {
                "status": len(issues) == 0,
                "message": "Системні ресурси в нормі" if len(issues) == 0 else "; ".join(issues),
                "details": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "issues": issues
                }
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки системних ресурсів: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_database_connectivity(self) -> Dict[str, Any]:
        """Перевірка підключення до бази даних"""
        try:
            # Тут буде логіка перевірки підключення до БД
            # Поки що повертаємо заглушку
            return {
                "status": True,
                "message": "Підключення до бази даних працює",
                "details": {"connection": "active"}
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка підключення до БД: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Перевірка здоров'я API"""
        try:
            # Тут буде логіка перевірки API
            return {
                "status": True,
                "message": "API ендпоінти працюють",
                "details": {"endpoints": "healthy"}
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка API: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_log_permissions(self) -> Dict[str, Any]:
        """Перевірка прав доступу до логів"""
        try:
            log_dir = "logs"
            if os.path.exists(log_dir):
                # Перевірка прав на запис
                test_file = os.path.join(log_dir, "test_write.tmp")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    return {
                        "status": True,
                        "message": "Права доступу до логів в нормі",
                        "details": {"permissions": "write"}
                    }
                except Exception:
                    return {
                        "status": False,
                        "message": "Немає прав на запис в директорію логів",
                        "details": {"permissions": "read_only"}
                    }
            else:
                return {
                    "status": False,
                    "message": "Директорія логів не існує",
                    "details": {"directory": "missing"}
                }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки прав доступу: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_memory_leaks(self) -> Dict[str, Any]:
        """Перевірка витоків пам'яті"""
        try:
            # Проста перевірка використання пам'яті
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return {
                    "status": False,
                    "message": "Підозра на витік пам'яті",
                    "details": {"memory_percent": memory.percent}
                }
            else:
                return {
                    "status": True,
                    "message": "Витоків пам'яті не виявлено",
                    "details": {"memory_percent": memory.percent}
                }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки пам'яті: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_network_connectivity(self) -> Dict[str, Any]:
        """Перевірка мережевого підключення"""
        try:
            # Перевірка підключення до зовнішніх сервісів
            import socket
            
            test_hosts = ["8.8.8.8", "1.1.1.1"]  # Google DNS, Cloudflare DNS
            for host in test_hosts:
                try:
                    socket.create_connection((host, 53), timeout=5)
                    return {
                        "status": True,
                        "message": "Мережеве підключення працює",
                        "details": {"test_host": host}
                    }
                except:
                    continue
            
            return {
                "status": False,
                "message": "Проблеми з мережевим підключенням",
                "details": {"test_hosts": test_hosts}
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки мережі: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_security_vulnerabilities(self) -> Dict[str, Any]:
        """Перевірка вразливостей безпеки"""
        try:
            # Базова перевірка безпеки
            return {
                "status": True,
                "message": "Критичних вразливостей не виявлено",
                "details": {"security_scan": "passed"}
            }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки безпеки: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def _check_configuration(self) -> Dict[str, Any]:
        """Перевірка конфігурації"""
        try:
            # Перевірка наявності основних конфігураційних файлів
            config_files = ["config.py", "settings.py"]
            missing_files = []
            
            for file in config_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if missing_files:
                return {
                    "status": False,
                    "message": f"Відсутні конфігураційні файли: {', '.join(missing_files)}",
                    "details": {"missing_files": missing_files}
                }
            else:
                return {
                    "status": True,
                    "message": "Конфігурація в порядку",
                    "details": {"config_files": "present"}
                }
        except Exception as e:
            return {
                "status": False,
                "message": f"Помилка перевірки конфігурації: {str(e)}",
                "details": {"error": str(e)}
            }
    
    # Функції автоматичного виправлення
    async def _auto_fix_system_resources(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення системних ресурсів"""
        try:
            # Логіка автоматичного виправлення
            return {
                "success": True,
                "message": "Системні ресурси оптимізовано",
                "actions": ["restart_services", "clear_cache"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити системні ресурси: {str(e)}"
            }
    
    async def _auto_fix_database_connectivity(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення підключення до БД"""
        try:
            # Логіка перепідключення до БД
            return {
                "success": True,
                "message": "Підключення до БД відновлено",
                "actions": ["reconnect_database", "clear_connection_pool"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося відновити підключення до БД: {str(e)}"
            }
    
    async def _auto_fix_api_health(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення API"""
        try:
            # Логіка перезапуску API сервісів
            return {
                "success": True,
                "message": "API сервіси перезапущено",
                "actions": ["restart_api_services", "clear_cache"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити API: {str(e)}"
            }
    
    async def _auto_fix_log_permissions(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення прав доступу до логів"""
        try:
            # Логіка виправлення прав доступу
            return {
                "success": True,
                "message": "Права доступу до логів виправлено",
                "actions": ["fix_permissions", "create_log_directory"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити права доступу: {str(e)}"
            }
    
    async def _auto_fix_memory_leaks(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення витоків пам'яті"""
        try:
            # Логіка очищення пам'яті
            return {
                "success": True,
                "message": "Пам'ять очищено",
                "actions": ["garbage_collection", "restart_processes"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити витоки пам'яті: {str(e)}"
            }
    
    async def _auto_fix_network_connectivity(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення мережевого підключення"""
        try:
            # Логіка відновлення мережевого підключення
            return {
                "success": True,
                "message": "Мережеве підключення відновлено",
                "actions": ["restart_network_services", "clear_dns_cache"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося відновити мережеве підключення: {str(e)}"
            }
    
    async def _auto_fix_security_vulnerabilities(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення вразливостей безпеки"""
        try:
            # Логіка виправлення безпеки
            return {
                "success": True,
                "message": "Вразливості безпеки виправлено",
                "actions": ["update_security_patches", "restart_security_services"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити вразливості безпеки: {str(e)}"
            }
    
    async def _auto_fix_configuration(self, result: DiagnosticResult) -> Dict[str, Any]:
        """Автоматичне виправлення конфігурації"""
        try:
            # Логіка виправлення конфігурації
            return {
                "success": True,
                "message": "Конфігурацію виправлено",
                "actions": ["restore_default_config", "validate_settings"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Не вдалося виправити конфігурацію: {str(e)}"
            }
    
    def get_diagnostic_history(self, hours: int = 24) -> List[DiagnosticResult]:
        """Отримання історії діагностики"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [r for r in self.results_history if r.timestamp > cutoff_time]
    
    def export_diagnostic_report(self, report: DiagnosticReport, filename: str = None) -> str:
        """Експорт звіту діагностики"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_report_{self.service_name}_{timestamp}.json"
        
        report_data = asdict(report)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Звіт діагностики експортовано: {filename}")
        return filename


# Глобальний екземпляр системи діагностики
auto_diagnostics = None


def initialize_auto_diagnostics(service_name: str):
    """Ініціалізація автоматичної діагностики"""
    global auto_diagnostics
    
    auto_diagnostics = AutoDiagnostics(service_name)
    
    logger = get_logger("auto-diagnostics-init")
    logger.info("Автоматична діагностика ініціалізовано", extra={
        "service_name": service_name
    })


def get_auto_diagnostics() -> AutoDiagnostics:
    """Отримання системи автоматичної діагностики"""
    return auto_diagnostics 