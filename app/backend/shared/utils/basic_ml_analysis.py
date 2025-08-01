"""
Базова система машинного навчання для аналізу логів (Phase 3)
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import pickle

from shared.config.logging import get_logger


@dataclass
class BasicAnomaly:
    """Базова аномалія"""
    timestamp: datetime
    anomaly_score: float
    log_message: str
    severity: str
    confidence: float


class BasicMLAnalyzer:
    """Базовий ML аналізатор логів"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("basic-ml-analyzer")
        
        # Базова модель
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Дані для тренування
        self.training_data = []
        self.anomalies_detected = 0
        
        self.logger.info("Базовий ML аналізатор ініціалізовано", extra={
            "service_name": service_name
        })
    
    def add_training_data(self, log_entries: List[Dict[str, Any]]):
        """Додавання даних для тренування"""
        for entry in log_entries:
            features = self._extract_basic_features(entry)
            if features:
                self.training_data.append(features)
        
        self.logger.info(f"Додано {len(log_entries)} записів для тренування")
    
    def train_model(self):
        """Тренування базової моделі"""
        if len(self.training_data) < 100:
            self.logger.warning("Недостатньо даних для тренування")
            return False
        
        try:
            # Підготовка даних
            features_array = np.array(self.training_data)
            
            # Масштабування
            features_scaled = self.scaler.fit_transform(features_array)
            
            # Тренування моделі
            self.isolation_forest.fit(features_scaled)
            
            self.logger.info("Базова ML модель навчена", extra={
                "training_samples": len(self.training_data)
            })
            
            return True
            
        except Exception as e:
            self.logger.error("Помилка тренування моделі", extra={"error": str(e)})
            return False
    
    def detect_anomalies(self, log_entries: List[Dict[str, Any]]) -> List[BasicAnomaly]:
        """Виявлення аномалій"""
        anomalies = []
        
        try:
            for entry in log_entries:
                features = self._extract_basic_features(entry)
                if not features:
                    continue
                
                # Прогноз
                features_scaled = self.scaler.transform([features])
                score = self.isolation_forest.decision_function(features_scaled)[0]
                
                # Виявлення аномалії
                if score < -0.5:  # Поріг аномалії
                    anomaly = BasicAnomaly(
                        timestamp=entry.get('timestamp', datetime.utcnow()),
                        anomaly_score=abs(score),
                        log_message=entry.get('message', ''),
                        severity=self._determine_severity(score),
                        confidence=min(abs(score), 1.0)
                    )
                    anomalies.append(anomaly)
                    self.anomalies_detected += 1
            
            self.logger.info(f"Виявлено {len(anomalies)} аномалій")
            
        except Exception as e:
            self.logger.error("Помилка виявлення аномалій", extra={"error": str(e)})
        
        return anomalies
    
    def _extract_basic_features(self, entry: Dict[str, Any]) -> Optional[List[float]]:
        """Витягнення базових ознак"""
        try:
            features = []
            
            # Часові ознаки
            timestamp = entry.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            features.extend([
                timestamp.hour,
                timestamp.weekday(),
                timestamp.minute
            ])
            
            # Рівень логування
            level = entry.get('level', 'INFO')
            level_encoding = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
            features.append(level_encoding.get(level, 1))
            
            # Довжина повідомлення
            message = entry.get('message', '')
            features.append(len(message))
            
            # Кількість слів
            features.append(len(message.split()))
            
            # Наявність ключових слів
            keywords = ['error', 'exception', 'failed', 'timeout']
            keyword_count = sum(1 for keyword in keywords if keyword.lower() in message.lower())
            features.append(keyword_count)
            
            return features
            
        except Exception as e:
            self.logger.error("Помилка витягнення ознак", extra={"error": str(e)})
            return None
    
    def _determine_severity(self, score: float) -> str:
        """Визначення серйозності"""
        abs_score = abs(score)
        
        if abs_score > 0.8:
            return 'critical'
        elif abs_score > 0.6:
            return 'high'
        elif abs_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики"""
        return {
            'service_name': self.service_name,
            'training_samples': len(self.training_data),
            'anomalies_detected': self.anomalies_detected,
            'model_trained': hasattr(self.isolation_forest, 'estimators_')
        }


# Глобальний екземпляр
basic_ml_analyzer = None


def initialize_basic_ml_analysis(service_name: str):
    """Ініціалізація базового ML аналізу"""
    global basic_ml_analyzer
    
    basic_ml_analyzer = BasicMLAnalyzer(service_name)
    
    logger = get_logger("basic-ml-analysis-init")
    logger.info("Базовий ML аналіз ініціалізовано", extra={
        "service_name": service_name
    })


def get_basic_ml_analyzer() -> BasicMLAnalyzer:
    """Отримання базового ML аналізатора"""
    return basic_ml_analyzer 