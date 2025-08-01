"""
Кореляційний аналіз для виявлення причин проблем
"""

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio

from shared.config.logging import get_logger


@dataclass
class CorrelationResult:
    """Результат кореляційного аналізу"""
    metric1: str
    metric2: str
    correlation_type: str
    correlation_value: float
    p_value: float
    significance: str
    sample_size: int
    timestamp: datetime


@dataclass
class AnomalyCorrelation:
    """Кореляція аномалій"""
    anomaly_metric: str
    correlated_metrics: List[str]
    correlation_strength: float
    time_lag: Optional[int] = None
    confidence: float = 0.0


class CorrelationAnalyzer:
    """Аналізатор кореляцій"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("correlation-analyzer")
        self.correlation_history: List[CorrelationResult] = []
        self.anomaly_correlations: List[AnomalyCorrelation] = []
        
        # Налаштування аналізу
        self.min_correlation_threshold = 0.7
        self.max_p_value = 0.05
        self.min_sample_size = 10
        
        self.logger.info("Кореляційний аналізатор ініціалізовано", extra={
            "service_name": service_name,
            "min_correlation_threshold": self.min_correlation_threshold,
            "max_p_value": self.max_p_value
        })
    
    def analyze_correlations(self, metrics_data: Dict[str, List[float]], 
                           timestamps: List[datetime]) -> List[CorrelationResult]:
        """Аналіз кореляцій між метриками"""
        correlations = []
        
        # Конвертація в DataFrame
        df = pd.DataFrame(metrics_data)
        df['timestamp'] = timestamps
        
        # Отримання числових колонок
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_columns) < 2:
            self.logger.warning("Недостатньо числових метрик для аналізу")
            return correlations
        
        # Аналіз попарних кореляцій
        for i, metric1 in enumerate(numeric_columns):
            for metric2 in numeric_columns[i+1:]:
                try:
                    # Видалення NaN значень
                    clean_data = df[[metric1, metric2]].dropna()
                    
                    if len(clean_data) < self.min_sample_size:
                        continue
                    
                    # Різні типи кореляцій
                    correlation_types = [
                        ('pearson', pearsonr),
                        ('spearman', spearmanr),
                        ('kendall', kendalltau)
                    ]
                    
                    for corr_type, corr_func in correlation_types:
                        corr_value, p_value = corr_func(clean_data[metric1], clean_data[metric2])
                        
                        # Перевірка значимості
                        significance = self._determine_significance(corr_value, p_value)
                        
                        if significance != "none":
                            correlation = CorrelationResult(
                                metric1=metric1,
                                metric2=metric2,
                                correlation_type=corr_type,
                                correlation_value=corr_value,
                                p_value=p_value,
                                significance=significance,
                                sample_size=len(clean_data),
                                timestamp=datetime.utcnow()
                            )
                            
                            correlations.append(correlation)
                            self.correlation_history.append(correlation)
                
                except Exception as e:
                    self.logger.error(f"Помилка аналізу кореляції {metric1}-{metric2}", 
                                    extra={"error": str(e)})
        
        self.logger.info(f"Знайдено {len(correlations)} значущих кореляцій")
        return correlations
    
    def _determine_significance(self, correlation_value: float, p_value: float) -> str:
        """Визначення значимості кореляції"""
        if abs(correlation_value) < self.min_correlation_threshold:
            return "none"
        
        if p_value > self.max_p_value:
            return "none"
        
        if abs(correlation_value) >= 0.9:
            return "very_strong"
        elif abs(correlation_value) >= 0.8:
            return "strong"
        elif abs(correlation_value) >= 0.7:
            return "moderate"
        else:
            return "weak"
    
    def find_anomaly_correlations(self, anomaly_metric: str, 
                                 metrics_data: Dict[str, List[float]], 
                                 timestamps: List[datetime]) -> List[AnomalyCorrelation]:
        """Пошук кореляцій з аномаліями"""
        correlations = []
        
        # Аналіз кореляцій з часовими затримками
        for lag in range(-5, 6):  # Затримки від -5 до +5 періодів
            lagged_correlations = self._analyze_lagged_correlations(
                anomaly_metric, metrics_data, timestamps, lag
            )
            correlations.extend(lagged_correlations)
        
        # Групування та агрегація результатів
        grouped_correlations = self._group_correlations(correlations)
        
        # Створення об'єктів AnomalyCorrelation
        anomaly_correlations = []
        for metric, corr_data in grouped_correlations.items():
            if corr_data['max_correlation'] >= self.min_correlation_threshold:
                anomaly_corr = AnomalyCorrelation(
                    anomaly_metric=anomaly_metric,
                    correlated_metrics=[metric],
                    correlation_strength=corr_data['max_correlation'],
                    time_lag=corr_data['best_lag'],
                    confidence=corr_data['confidence']
                )
                anomaly_correlations.append(anomaly_corr)
        
        self.anomaly_correlations.extend(anomaly_correlations)
        
        self.logger.info(f"Знайдено {len(anomaly_correlations)} кореляцій з аномалією {anomaly_metric}")
        return anomaly_correlations
    
    def _analyze_lagged_correlations(self, anomaly_metric: str, 
                                   metrics_data: Dict[str, List[float]], 
                                   timestamps: List[datetime], 
                                   lag: int) -> List[Dict[str, Any]]:
        """Аналіз кореляцій з часовою затримкою"""
        correlations = []
        
        if anomaly_metric not in metrics_data:
            return correlations
        
        anomaly_data = metrics_data[anomaly_metric]
        
        for metric, data in metrics_data.items():
            if metric == anomaly_metric:
                continue
            
            try:
                # Створення лагованих даних
                if lag > 0:
                    # Позитивна затримка: аномалія слідує за метрикою
                    lagged_anomaly = anomaly_data[lag:]
                    lagged_metric = data[:-lag] if len(data) > lag else []
                elif lag < 0:
                    # Негативна затримка: метрика слідує за аномалією
                    lagged_anomaly = anomaly_data[:lag]
                    lagged_metric = data[-lag:] if len(data) > abs(lag) else []
                else:
                    # Без затримки
                    lagged_anomaly = anomaly_data
                    lagged_metric = data
                
                # Перевірка довжини даних
                min_length = min(len(lagged_anomaly), len(lagged_metric))
                if min_length < self.min_sample_size:
                    continue
                
                lagged_anomaly = lagged_anomaly[:min_length]
                lagged_metric = lagged_metric[:min_length]
                
                # Обчислення кореляції
                corr_value, p_value = pearsonr(lagged_anomaly, lagged_metric)
                
                if abs(corr_value) >= self.min_correlation_threshold and p_value <= self.max_p_value:
                    correlations.append({
                        'metric': metric,
                        'correlation': corr_value,
                        'p_value': p_value,
                        'lag': lag,
                        'sample_size': min_length
                    })
            
            except Exception as e:
                self.logger.error(f"Помилка аналізу лагованої кореляції", 
                                extra={"error": str(e), "metric": metric, "lag": lag})
        
        return correlations
    
    def _group_correlations(self, correlations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Групування кореляцій по метриках"""
        grouped = defaultdict(lambda: {
            'correlations': [],
            'max_correlation': 0,
            'best_lag': 0,
            'confidence': 0
        })
        
        for corr in correlations:
            metric = corr['metric']
            grouped[metric]['correlations'].append(corr)
            
            if abs(corr['correlation']) > abs(grouped[metric]['max_correlation']):
                grouped[metric]['max_correlation'] = corr['correlation']
                grouped[metric]['best_lag'] = corr['lag']
        
        # Обчислення довіри
        for metric, data in grouped.items():
            if data['correlations']:
                # Середнє значення p-value як міра довіри
                avg_p_value = np.mean([c['p_value'] for c in data['correlations']])
                data['confidence'] = 1 - avg_p_value
        
        return dict(grouped)
    
    def get_correlation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Отримання зведення кореляцій"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_correlations = [
            c for c in self.correlation_history 
            if c.timestamp > cutoff_time
        ]
        
        summary = {
            'period_hours': hours,
            'total_correlations': len(recent_correlations),
            'strong_correlations': len([c for c in recent_correlations if c.significance == 'strong']),
            'moderate_correlations': len([c for c in recent_correlations if c.significance == 'moderate']),
            'weak_correlations': len([c for c in recent_correlations if c.significance == 'weak']),
            'top_correlations': [],
            'anomaly_correlations': len(self.anomaly_correlations)
        }
        
        # Топ кореляції
        if recent_correlations:
            sorted_correlations = sorted(
                recent_correlations, 
                key=lambda x: abs(x.correlation_value), 
                reverse=True
            )
            summary['top_correlations'] = [
                {
                    'metric1': c.metric1,
                    'metric2': c.metric2,
                    'correlation': c.correlation_value,
                    'type': c.correlation_type,
                    'significance': c.significance
                }
                for c in sorted_correlations[:10]
            ]
        
        return summary
    
    def export_correlation_report(self, filename: str = None) -> str:
        """Експорт звіту про кореляції"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"correlation_report_{self.service_name}_{timestamp}.json"
        
        report = {
            'service_name': self.service_name,
            'generated_at': datetime.utcnow().isoformat(),
            'summary': self.get_correlation_summary(),
            'recent_correlations': [
                asdict(c) for c in self.correlation_history[-100:]  # Останні 100
            ],
            'anomaly_correlations': [
                asdict(c) for c in self.anomaly_correlations
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Звіт про кореляції експортовано: {filename}")
        return filename


class PerformanceCorrelationAnalyzer(CorrelationAnalyzer):
    """Спеціалізований аналізатор кореляцій продуктивності"""
    
    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.performance_metrics = [
            'cpu_usage', 'memory_usage', 'response_time', 
            'throughput', 'error_rate', 'queue_size'
        ]
    
    def analyze_performance_correlations(self, performance_data: Dict[str, List[float]], 
                                       timestamps: List[datetime]) -> List[CorrelationResult]:
        """Аналіз кореляцій продуктивності"""
        # Фільтрація тільки метрик продуктивності
        filtered_data = {
            k: v for k, v in performance_data.items() 
            if k in self.performance_metrics
        }
        
        return self.analyze_correlations(filtered_data, timestamps)
    
    def find_bottlenecks(self, performance_data: Dict[str, List[float]], 
                        timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Пошук вузьких місць продуктивності"""
        bottlenecks = []
        
        # Аналіз кореляцій з response_time
        if 'response_time' in performance_data:
            correlations = self.find_anomaly_correlations(
                'response_time', performance_data, timestamps
            )
            
            for corr in correlations:
                if corr.correlation_strength > 0.8:  # Сильна кореляція
                    bottleneck = {
                        'type': 'performance_bottleneck',
                        'primary_metric': 'response_time',
                        'correlated_metric': corr.correlated_metrics[0],
                        'correlation_strength': corr.correlation_strength,
                        'time_lag': corr.time_lag,
                        'confidence': corr.confidence,
                        'recommendation': self._get_bottleneck_recommendation(
                            corr.correlated_metrics[0]
                        )
                    }
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def _get_bottleneck_recommendation(self, metric: str) -> str:
        """Отримання рекомендації для вузького місця"""
        recommendations = {
            'cpu_usage': 'Розгляньте можливість масштабування CPU або оптимізації коду',
            'memory_usage': 'Перевірте витоки пам\'яті або збільшіть доступну пам\'ять',
            'queue_size': 'Оптимізуйте обробку черги або збільшіть кількість воркерів',
            'error_rate': 'Перевірте логи на наявність помилок та їх причини',
            'throughput': 'Оптимізуйте мережеві налаштування або збільшіть пропускну здатність'
        }
        
        return recommendations.get(metric, 'Перевірте налаштування та оптимізуйте систему')


class SecurityCorrelationAnalyzer(CorrelationAnalyzer):
    """Спеціалізований аналізатор кореляцій безпеки"""
    
    def __init__(self, service_name: str):
        super().__init__(service_name)
        self.security_metrics = [
            'failed_logins', 'unauthorized_access', 'suspicious_ips',
            'blocked_requests', 'security_events', 'mfa_failures'
        ]
    
    def analyze_security_correlations(self, security_data: Dict[str, List[float]], 
                                    timestamps: List[datetime]) -> List[CorrelationResult]:
        """Аналіз кореляцій безпеки"""
        filtered_data = {
            k: v for k, v in security_data.items() 
            if k in self.security_metrics
        }
        
        return self.analyze_correlations(filtered_data, timestamps)
    
    def detect_attack_patterns(self, security_data: Dict[str, List[float]], 
                             timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Виявлення патернів атак"""
        patterns = []
        
        # Аналіз кореляцій з failed_logins
        if 'failed_logins' in security_data:
            correlations = self.find_anomaly_correlations(
                'failed_logins', security_data, timestamps
            )
            
            for corr in correlations:
                if corr.correlation_strength > 0.7:
                    pattern = {
                        'type': 'attack_pattern',
                        'primary_event': 'failed_logins',
                        'correlated_event': corr.correlated_metrics[0],
                        'correlation_strength': corr.correlation_strength,
                        'time_lag': corr.time_lag,
                        'threat_level': self._assess_threat_level(corr.correlation_strength),
                        'recommendation': self._get_security_recommendation(
                            corr.correlated_metrics[0]
                        )
                    }
                    patterns.append(pattern)
        
        return patterns
    
    def _assess_threat_level(self, correlation_strength: float) -> str:
        """Оцінка рівня загрози"""
        if correlation_strength > 0.9:
            return 'critical'
        elif correlation_strength > 0.8:
            return 'high'
        elif correlation_strength > 0.7:
            return 'medium'
        else:
            return 'low'
    
    def _get_security_recommendation(self, event_type: str) -> str:
        """Отримання рекомендації безпеки"""
        recommendations = {
            'unauthorized_access': 'Перевірте систему авторизації та налаштування доступу',
            'suspicious_ips': 'Блокуйте підозрілі IP адреси та налаштуйте WAF',
            'blocked_requests': 'Перевірте правила блокування та налаштування безпеки',
            'mfa_failures': 'Перевірте налаштування MFA та сповіщення користувачів'
        }
        
        return recommendations.get(event_type, 'Перевірте систему безпеки та логи')


# Глобальні екземпляри аналізаторів
correlation_analyzer = None
performance_correlation_analyzer = None
security_correlation_analyzer = None


def initialize_correlation_analysis(service_name: str):
    """Ініціалізація кореляційного аналізу"""
    global correlation_analyzer, performance_correlation_analyzer, security_correlation_analyzer
    
    correlation_analyzer = CorrelationAnalyzer(service_name)
    performance_correlation_analyzer = PerformanceCorrelationAnalyzer(service_name)
    security_correlation_analyzer = SecurityCorrelationAnalyzer(service_name)
    
    logger = get_logger("correlation-analysis-init")
    logger.info("Кореляційний аналіз ініціалізовано", extra={
        "service_name": service_name,
        "analyzers": ["general", "performance", "security"]
    })


def get_correlation_analyzer() -> CorrelationAnalyzer:
    """Отримання загального аналізатора кореляцій"""
    return correlation_analyzer


def get_performance_correlation_analyzer() -> PerformanceCorrelationAnalyzer:
    """Отримання аналізатора кореляцій продуктивності"""
    return performance_correlation_analyzer


def get_security_correlation_analyzer() -> SecurityCorrelationAnalyzer:
    """Отримання аналізатора кореляцій безпеки"""
    return security_correlation_analyzer 