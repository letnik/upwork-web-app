"""
Машинне навчання для аналізу логів та виявлення аномалій
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import pickle
import asyncio
import threading
from collections import defaultdict, deque
import re
import hashlib

from shared.config.logging import get_logger


@dataclass
class LogAnomaly:
    """Аномалія в логах"""
    timestamp: datetime
    anomaly_type: str
    severity: str
    confidence: float
    log_entry: str
    features: Dict[str, Any]
    cluster_id: Optional[int] = None
    similar_anomalies: List[str] = None


@dataclass
class MLModel:
    """Модель машинного навчання"""
    name: str
    model_type: str
    model: Any
    scaler: StandardScaler
    features: List[str]
    accuracy: float
    last_trained: datetime
    training_samples: int
    version: str


class MLLogAnalyzer:
    """Аналізатор логів з машинним навчанням"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("ml-log-analyzer")
        
        # Налаштування ML
        self.min_training_samples = 1000
        self.retrain_interval = 168  # години (1 тиждень)
        self.anomaly_threshold = 0.8
        self.max_features = 100
        
        # Дані для тренування
        self.training_data = deque(maxlen=50000)
        self.anomalies_history = deque(maxlen=10000)
        
        # Моделі ML
        self.models: Dict[str, MLModel] = {}
        self.active_models = {}
        
        # Статистика
        self.stats = {
            'total_logs_analyzed': 0,
            'anomalies_detected': 0,
            'false_positives': 0,
            'model_accuracy': 0.0,
            'last_analysis': None
        }
        
        self._initialize_models()
        
        self.logger.info("ML аналізатор логів ініціалізовано", extra={
            "service_name": service_name,
            "models": list(self.models.keys())
        })
    
    def _initialize_models(self):
        """Ініціалізація моделей ML"""
        
        # Isolation Forest для виявлення аномалій
        isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        self.models['anomaly_detection'] = MLModel(
            name='anomaly_detection',
            model_type='isolation_forest',
            model=isolation_forest,
            scaler=StandardScaler(),
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0,
            version='1.0'
        )
        
        # Random Forest для класифікації типів логів
        random_forest = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.models['log_classification'] = MLModel(
            name='log_classification',
            model_type='random_forest',
            model=random_forest,
            scaler=StandardScaler(),
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0,
            version='1.0'
        )
        
        # DBSCAN для кластеризації логів
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        
        self.models['log_clustering'] = MLModel(
            name='log_clustering',
            model_type='dbscan',
            model=dbscan,
            scaler=StandardScaler(),
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0,
            version='1.0'
        )
        
        # TF-IDF для аналізу тексту логів
        tfidf = TfidfVectorizer(
            max_features=self.max_features,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.models['text_analysis'] = MLModel(
            name='text_analysis',
            model_type='tfidf',
            model=tfidf,
            scaler=None,  # TF-IDF не потребує масштабування
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0,
            version='1.0'
        )
        
        # Встановлення активних моделей
        self.active_models = {
            'anomaly_detection': 'anomaly_detection',
            'log_classification': 'log_classification',
            'log_clustering': 'log_clustering',
            'text_analysis': 'text_analysis'
        }
    
    def add_training_data(self, log_entries: List[Dict[str, Any]]):
        """Додавання даних для тренування"""
        for entry in log_entries:
            self.training_data.append(entry)
        
        # Автоматичне перетренування
        if len(self.training_data) >= self.min_training_samples:
            time_since_training = datetime.utcnow() - self.models['anomaly_detection'].last_trained
            if time_since_training.total_seconds() > self.retrain_interval * 3600:
                asyncio.create_task(self._retrain_models())
    
    async def analyze_logs(self, log_entries: List[Dict[str, Any]]) -> List[LogAnomaly]:
        """Аналіз логів з використанням ML"""
        anomalies = []
        
        try:
            # Підготовка даних
            features = self._extract_features(log_entries)
            
            if not features:
                return anomalies
            
            # Виявлення аномалій
            anomaly_model = self.models[self.active_models['anomaly_detection']]
            features_scaled = anomaly_model.scaler.transform(features)
            anomaly_scores = anomaly_model.model.decision_function(features_scaled)
            
            # Класифікація логів
            classification_model = self.models[self.active_models['log_classification']]
            if classification_model.training_samples > 0:
                log_types = classification_model.model.predict(features_scaled)
            else:
                log_types = ['unknown'] * len(log_entries)
            
            # Кластеризація логів
            clustering_model = self.models[self.active_models['log_clustering']]
            if clustering_model.training_samples > 0:
                clusters = clustering_model.model.fit_predict(features_scaled)
            else:
                clusters = [-1] * len(log_entries)
            
            # Аналіз тексту
            text_features = self._extract_text_features([entry.get('message', '') for entry in log_entries])
            
            # Створення результатів
            for i, (entry, score, log_type, cluster, text_feature) in enumerate(
                zip(log_entries, anomaly_scores, log_types, clusters, text_features)
            ):
                if score < -self.anomaly_threshold:  # Аномалія
                    anomaly = LogAnomaly(
                        timestamp=entry.get('timestamp', datetime.utcnow()),
                        anomaly_type=self._classify_anomaly_type(entry, score, log_type),
                        severity=self._determine_severity(score),
                        confidence=abs(score),
                        log_entry=entry.get('message', ''),
                        features={
                            'anomaly_score': score,
                            'log_type': log_type,
                            'cluster_id': cluster,
                            'text_features': text_feature
                        },
                        cluster_id=cluster,
                        similar_anomalies=self._find_similar_anomalies(entry, cluster)
                    )
                    
                    anomalies.append(anomaly)
                    self.anomalies_history.append(anomaly)
            
            # Оновлення статистики
            self.stats['total_logs_analyzed'] += len(log_entries)
            self.stats['anomalies_detected'] += len(anomalies)
            self.stats['last_analysis'] = datetime.utcnow().isoformat()
            
            self.logger.info(f"Проаналізовано {len(log_entries)} логів, знайдено {len(anomalies)} аномалій")
            
        except Exception as e:
            self.logger.error("Помилка аналізу логів", extra={"error": str(e)})
        
        return anomalies
    
    def _extract_features(self, log_entries: List[Dict[str, Any]]) -> List[List[float]]:
        """Витягнення ознак з логів"""
        features = []
        
        for entry in log_entries:
            feature_vector = []
            
            # Часові ознаки
            timestamp = entry.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            feature_vector.extend([
                timestamp.hour,
                timestamp.weekday(),
                timestamp.isocalendar()[1],
                timestamp.minute
            ])
            
            # Рівень логування
            level = entry.get('level', 'INFO')
            level_encoding = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
            feature_vector.append(level_encoding.get(level, 1))
            
            # Довжина повідомлення
            message = entry.get('message', '')
            feature_vector.append(len(message))
            
            # Кількість слів
            feature_vector.append(len(message.split()))
            
            # Наявність ключових слів
            keywords = ['error', 'exception', 'failed', 'timeout', 'connection', 'database']
            keyword_count = sum(1 for keyword in keywords if keyword.lower() in message.lower())
            feature_vector.append(keyword_count)
            
            # Хеш повідомлення (для унікальності)
            message_hash = hash(message) % 10000
            feature_vector.append(message_hash)
            
            # Додаткові метрики
            extra = entry.get('extra', {})
            feature_vector.extend([
                extra.get('duration_ms', 0) / 1000,  # Нормалізація до секунд
                extra.get('response_time_ms', 0) / 1000,
                extra.get('cpu_usage', 0),
                extra.get('memory_usage', 0),
                extra.get('error_rate', 0)
            ])
            
            features.append(feature_vector)
        
        return features
    
    def _extract_text_features(self, messages: List[str]) -> List[Dict[str, float]]:
        """Витягнення текстових ознак"""
        text_features = []
        
        try:
            text_model = self.models[self.active_models['text_analysis']]
            
            if text_model.training_samples > 0:
                # Використання навченої TF-IDF моделі
                tfidf_matrix = text_model.model.transform(messages)
                feature_names = text_model.model.get_feature_names_out()
                
                for i in range(len(messages)):
                    features = {}
                    for j, feature_name in enumerate(feature_names):
                        if tfidf_matrix[i, j] > 0:
                            features[feature_name] = float(tfidf_matrix[i, j])
                    text_features.append(features)
            else:
                # Прості текстові ознаки
                for message in messages:
                    features = {
                        'length': len(message),
                        'word_count': len(message.split()),
                        'uppercase_ratio': sum(1 for c in message if c.isupper()) / len(message) if message else 0,
                        'digit_ratio': sum(1 for c in message if c.isdigit()) / len(message) if message else 0,
                        'special_char_ratio': sum(1 for c in message if not c.isalnum() and not c.isspace()) / len(message) if message else 0
                    }
                    text_features.append(features)
        
        except Exception as e:
            self.logger.error("Помилка витягнення текстових ознак", extra={"error": str(e)})
            text_features = [{} for _ in messages]
        
        return text_features
    
    def _classify_anomaly_type(self, entry: Dict[str, Any], score: float, log_type: str) -> str:
        """Класифікація типу аномалії"""
        message = entry.get('message', '').lower()
        level = entry.get('level', 'INFO')
        
        if 'error' in message or 'exception' in message:
            return 'error_anomaly'
        elif 'timeout' in message or 'connection' in message:
            return 'connection_anomaly'
        elif 'database' in message or 'sql' in message:
            return 'database_anomaly'
        elif 'security' in message or 'auth' in message:
            return 'security_anomaly'
        elif 'performance' in message or 'slow' in message:
            return 'performance_anomaly'
        elif level in ['ERROR', 'CRITICAL']:
            return 'critical_anomaly'
        else:
            return 'general_anomaly'
    
    def _determine_severity(self, score: float) -> str:
        """Визначення серйозності аномалії"""
        abs_score = abs(score)
        
        if abs_score > 0.9:
            return 'critical'
        elif abs_score > 0.7:
            return 'high'
        elif abs_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _find_similar_anomalies(self, entry: Dict[str, Any], cluster_id: int) -> List[str]:
        """Пошук подібних аномалій"""
        similar = []
        
        if cluster_id != -1:  # Не ізольована точка
            for anomaly in self.anomalies_history:
                if anomaly.cluster_id == cluster_id and anomaly.log_entry != entry.get('message', ''):
                    similar.append(anomaly.log_entry)
                    if len(similar) >= 5:  # Максимум 5 подібних
                        break
        
        return similar
    
    async def _retrain_models(self):
        """Перетренування моделей ML"""
        self.logger.info("Початок перетренування ML моделей")
        
        try:
            if len(self.training_data) < self.min_training_samples:
                self.logger.warning("Недостатньо даних для тренування")
                return
            
            # Підготовка даних
            training_entries = list(self.training_data)
            features = self._extract_features(training_entries)
            
            if len(features) < self.min_training_samples:
                return
            
            # Тренування моделі виявлення аномалій
            await self._train_anomaly_detection(features)
            
            # Тренування моделі класифікації
            await self._train_log_classification(training_entries, features)
            
            # Тренування моделі кластеризації
            await self._train_log_clustering(features)
            
            # Тренування моделі аналізу тексту
            await self._train_text_analysis(training_entries)
            
            self.logger.info("ML моделі успішно перетреновано")
            
        except Exception as e:
            self.logger.error("Помилка перетренування ML моделей", extra={"error": str(e)})
    
    async def _train_anomaly_detection(self, features: List[List[float]]):
        """Тренування моделі виявлення аномалій"""
        try:
            model_info = self.models['anomaly_detection']
            
            # Масштабування ознак
            model_info.scaler.fit(features)
            features_scaled = model_info.scaler.transform(features)
            
            # Тренування моделі
            model_info.model.fit(features_scaled)
            
            # Оновлення інформації
            model_info.features = self._get_feature_names()
            model_info.last_trained = datetime.utcnow()
            model_info.training_samples = len(features)
            model_info.version = f"{model_info.version.split('.')[0]}.{int(model_info.version.split('.')[1]) + 1}"
            
            self.logger.info("Модель виявлення аномалій перетреновано", extra={
                "training_samples": len(features),
                "version": model_info.version
            })
            
        except Exception as e:
            self.logger.error("Помилка тренування моделі виявлення аномалій", extra={"error": str(e)})
    
    async def _train_log_classification(self, entries: List[Dict[str, Any]], features: List[List[float]]):
        """Тренування моделі класифікації логів"""
        try:
            model_info = self.models['log_classification']
            
            # Підготовка міток
            labels = []
            for entry in entries:
                level = entry.get('level', 'INFO')
                message = entry.get('message', '').lower()
                
                if 'error' in message or level == 'ERROR':
                    labels.append('error')
                elif 'warning' in message or level == 'WARNING':
                    labels.append('warning')
                elif 'security' in message or 'auth' in message:
                    labels.append('security')
                elif 'performance' in message or 'slow' in message:
                    labels.append('performance')
                else:
                    labels.append('info')
            
            # Кодування міток
            label_encoder = LabelEncoder()
            encoded_labels = label_encoder.fit_transform(labels)
            
            # Масштабування ознак
            model_info.scaler.fit(features)
            features_scaled = model_info.scaler.transform(features)
            
            # Тренування моделі
            model_info.model.fit(features_scaled, encoded_labels)
            
            # Оцінка точності
            predictions = model_info.model.predict(features_scaled)
            accuracy = (predictions == encoded_labels).mean()
            
            # Оновлення інформації
            model_info.accuracy = accuracy
            model_info.features = self._get_feature_names()
            model_info.last_trained = datetime.utcnow()
            model_info.training_samples = len(features)
            
            self.logger.info("Модель класифікації логів перетреновано", extra={
                "accuracy": accuracy,
                "training_samples": len(features)
            })
            
        except Exception as e:
            self.logger.error("Помилка тренування моделі класифікації", extra={"error": str(e)})
    
    async def _train_log_clustering(self, features: List[List[float]]):
        """Тренування моделі кластеризації логів"""
        try:
            model_info = self.models['log_clustering']
            
            # Масштабування ознак
            model_info.scaler.fit(features)
            features_scaled = model_info.scaler.transform(features)
            
            # Тренування моделі
            clusters = model_info.model.fit_predict(features_scaled)
            
            # Оновлення інформації
            model_info.features = self._get_feature_names()
            model_info.last_trained = datetime.utcnow()
            model_info.training_samples = len(features)
            
            self.logger.info("Модель кластеризації логів перетреновано", extra={
                "clusters_found": len(set(clusters)) - (1 if -1 in clusters else 0),
                "training_samples": len(features)
            })
            
        except Exception as e:
            self.logger.error("Помилка тренування моделі кластеризації", extra={"error": str(e)})
    
    async def _train_text_analysis(self, entries: List[Dict[str, Any]]):
        """Тренування моделі аналізу тексту"""
        try:
            model_info = self.models['text_analysis']
            
            # Підготовка текстів
            messages = [entry.get('message', '') for entry in entries]
            
            # Тренування TF-IDF
            tfidf_matrix = model_info.model.fit_transform(messages)
            
            # Оновлення інформації
            model_info.features = list(model_info.model.get_feature_names_out())
            model_info.last_trained = datetime.utcnow()
            model_info.training_samples = len(messages)
            
            self.logger.info("Модель аналізу тексту перетреновано", extra={
                "features_count": len(model_info.features),
                "training_samples": len(messages)
            })
            
        except Exception as e:
            self.logger.error("Помилка тренування моделі аналізу тексту", extra={"error": str(e)})
    
    def _get_feature_names(self) -> List[str]:
        """Отримання назв ознак"""
        return [
            'hour', 'weekday', 'week_of_year', 'minute',
            'log_level', 'message_length', 'word_count',
            'keyword_count', 'message_hash',
            'duration_sec', 'response_time_sec',
            'cpu_usage', 'memory_usage', 'error_rate'
        ]
    
    def get_ml_stats(self) -> Dict[str, Any]:
        """Отримання статистики ML"""
        stats = {
            'total_logs_analyzed': self.stats['total_logs_analyzed'],
            'anomalies_detected': self.stats['anomalies_detected'],
            'anomaly_rate': (self.stats['anomalies_detected'] / self.stats['total_logs_analyzed'] 
                           if self.stats['total_logs_analyzed'] > 0 else 0),
            'models_info': {}
        }
        
        for name, model_info in self.models.items():
            stats['models_info'][name] = {
                'accuracy': model_info.accuracy,
                'training_samples': model_info.training_samples,
                'last_trained': model_info.last_trained.isoformat(),
                'version': model_info.version
            }
        
        return stats
    
    def save_models(self, directory: str = "ml_models"):
        """Збереження моделей"""
        import os
        
        os.makedirs(directory, exist_ok=True)
        
        for name, model_info in self.models.items():
            model_path = os.path.join(directory, f"{name}_model.pkl")
            scaler_path = os.path.join(directory, f"{name}_scaler.pkl")
            
            # Збереження моделі
            with open(model_path, 'wb') as f:
                pickle.dump(model_info.model, f)
            
            # Збереження scaler
            if model_info.scaler:
                with open(scaler_path, 'wb') as f:
                    pickle.dump(model_info.scaler, f)
            
            # Збереження метаданих
            metadata = {
                'name': model_info.name,
                'model_type': model_info.model_type,
                'features': model_info.features,
                'accuracy': model_info.accuracy,
                'last_trained': model_info.last_trained.isoformat(),
                'training_samples': model_info.training_samples,
                'version': model_info.version
            }
            
            metadata_path = os.path.join(directory, f"{name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        self.logger.info(f"ML моделі збережено в {directory}")
    
    def load_models(self, directory: str = "ml_models"):
        """Завантаження моделей"""
        import os
        
        for name in self.models.keys():
            model_path = os.path.join(directory, f"{name}_model.pkl")
            scaler_path = os.path.join(directory, f"{name}_scaler.pkl")
            metadata_path = os.path.join(directory, f"{name}_metadata.json")
            
            if os.path.exists(model_path):
                try:
                    # Завантаження моделі
                    with open(model_path, 'rb') as f:
                        self.models[name].model = pickle.load(f)
                    
                    # Завантаження scaler
                    if os.path.exists(scaler_path):
                        with open(scaler_path, 'rb') as f:
                            self.models[name].scaler = pickle.load(f)
                    
                    # Завантаження метаданих
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            self.models[name].features = metadata.get('features', [])
                            self.models[name].accuracy = metadata.get('accuracy', 0.0)
                            self.models[name].last_trained = datetime.fromisoformat(metadata.get('last_trained'))
                            self.models[name].training_samples = metadata.get('training_samples', 0)
                            self.models[name].version = metadata.get('version', '1.0')
                    
                    self.logger.info(f"Модель {name} завантажено")
                    
                except Exception as e:
                    self.logger.error(f"Помилка завантаження моделі {name}", extra={"error": str(e)})


# Глобальний екземпляр ML аналізатора
ml_log_analyzer = None


def initialize_ml_log_analysis(service_name: str):
    """Ініціалізація ML аналізу логів"""
    global ml_log_analyzer
    
    ml_log_analyzer = MLLogAnalyzer(service_name)
    
    logger = get_logger("ml-log-analysis-init")
    logger.info("ML аналіз логів ініціалізовано", extra={
        "service_name": service_name
    })


def get_ml_log_analyzer() -> MLLogAnalyzer:
    """Отримання ML аналізатора логів"""
    return ml_log_analyzer 