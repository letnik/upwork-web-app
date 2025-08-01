"""
Прогнозування навантаження для проактивного масштабування
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import asyncio
import threading
from collections import deque

from shared.config.logging import get_logger


@dataclass
class LoadPrediction:
    """Прогноз навантаження"""
    timestamp: datetime
    predicted_load: float
    confidence: float
    model_used: str
    features_used: List[str]
    actual_load: Optional[float] = None
    error: Optional[float] = None


@dataclass
class PredictionModel:
    """Модель прогнозування"""
    name: str
    model: Any
    scaler: StandardScaler
    features: List[str]
    accuracy: float
    last_trained: datetime
    training_samples: int


class LoadPredictor:
    """Система прогнозування навантаження"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("load-predictor")
        
        # Налаштування прогнозування
        self.prediction_horizon = 60  # хвилини
        self.min_training_samples = 100
        self.retrain_interval = 24  # години
        self.feature_window = 24  # години для збору ознак
        
        # Дані для тренування
        self.historical_data = deque(maxlen=10000)
        self.predictions_history = deque(maxlen=1000)
        
        # Моделі прогнозування
        self.models: Dict[str, PredictionModel] = {}
        self.current_model = None
        
        # Статистика
        self.stats = {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'avg_error': 0.0,
            'last_prediction': None
        }
        
        self._initialize_models()
        
        self.logger.info("Система прогнозування навантаження ініціалізовано", extra={
            "service_name": service_name,
            "prediction_horizon": self.prediction_horizon,
            "models": list(self.models.keys())
        })
    
    def _initialize_models(self):
        """Ініціалізація моделей прогнозування"""
        
        # Random Forest модель
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.models['random_forest'] = PredictionModel(
            name='random_forest',
            model=rf_model,
            scaler=StandardScaler(),
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0
        )
        
        # Linear Regression модель
        lr_model = LinearRegression()
        
        self.models['linear_regression'] = PredictionModel(
            name='linear_regression',
            model=lr_model,
            scaler=StandardScaler(),
            features=[],
            accuracy=0.0,
            last_trained=datetime.utcnow(),
            training_samples=0
        )
        
        # Встановлення поточної моделі
        self.current_model = 'random_forest'
    
    def add_historical_data(self, timestamp: datetime, load_metrics: Dict[str, float]):
        """Додавання історичних даних"""
        data_point = {
            'timestamp': timestamp,
            **load_metrics
        }
        
        self.historical_data.append(data_point)
        
        # Автоматичне перетренування моделі
        if len(self.historical_data) >= self.min_training_samples:
            time_since_training = datetime.utcnow() - self.models[self.current_model].last_trained
            if time_since_training.total_seconds() > self.retrain_interval * 3600:
                asyncio.create_task(self._retrain_models())
    
    async def predict_load(self, current_metrics: Dict[str, float], 
                          prediction_minutes: int = None) -> LoadPrediction:
        """Прогнозування навантаження"""
        if prediction_minutes is None:
            prediction_minutes = self.prediction_horizon
        
        try:
            # Підготовка ознак
            features = self._prepare_features(current_metrics)
            
            if not features:
                raise ValueError("Недостатньо даних для прогнозування")
            
            # Отримання поточної моделі
            model_info = self.models[self.current_model]
            
            # Масштабування ознак
            features_scaled = model_info.scaler.transform([features])
            
            # Прогнозування
            predicted_load = model_info.model.predict(features_scaled)[0]
            
            # Оцінка довіри
            confidence = self._calculate_confidence(features, model_info)
            
            # Створення прогнозу
            prediction = LoadPrediction(
                timestamp=datetime.utcnow(),
                predicted_load=predicted_load,
                confidence=confidence,
                model_used=self.current_model,
                features_used=model_info.features
            )
            
            # Збереження прогнозу
            self.predictions_history.append(prediction)
            
            # Оновлення статистики
            self.stats['total_predictions'] += 1
            self.stats['last_prediction'] = prediction.timestamp.isoformat()
            
            self.logger.info("Прогноз навантаження створено", extra={
                "predicted_load": predicted_load,
                "confidence": confidence,
                "model": self.current_model,
                "prediction_minutes": prediction_minutes
            })
            
            return prediction
            
        except Exception as e:
            self.logger.error("Помилка прогнозування навантаження", extra={
                "error": str(e),
                "current_metrics": current_metrics
            })
            raise
    
    def _prepare_features(self, current_metrics: Dict[str, float]) -> List[float]:
        """Підготовка ознак для прогнозування"""
        if len(self.historical_data) < self.min_training_samples:
            return []
        
        # Основні метрики
        features = [
            current_metrics.get('cpu_usage', 0),
            current_metrics.get('memory_usage', 0),
            current_metrics.get('response_time', 0),
            current_metrics.get('throughput', 0),
            current_metrics.get('error_rate', 0),
            current_metrics.get('queue_size', 0)
        ]
        
        # Часові ознаки
        now = datetime.utcnow()
        features.extend([
            now.hour,  # Година дня
            now.weekday(),  # День тижня
            now.isocalendar()[1],  # Тиждень року
        ])
        
        # Середні значення за останні періоди
        recent_data = list(self.historical_data)[-self.feature_window:]
        if recent_data:
            recent_loads = [d.get('cpu_usage', 0) for d in recent_data]
            features.extend([
                np.mean(recent_loads),
                np.std(recent_loads),
                np.max(recent_loads),
                np.min(recent_loads)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        # Трендові ознаки
        if len(self.historical_data) >= 10:
            recent_loads = [d.get('cpu_usage', 0) for d in list(self.historical_data)[-10:]]
            features.append(np.polyfit(range(len(recent_loads)), recent_loads, 1)[0])  # Нахил тренду
        else:
            features.append(0)
        
        return features
    
    def _calculate_confidence(self, features: List[float], model_info: PredictionModel) -> float:
        """Розрахунок довіри до прогнозу"""
        # Базова довіра на основі точності моделі
        base_confidence = model_info.accuracy
        
        # Корекція на основі кількості тренувальних даних
        sample_factor = min(1.0, model_info.training_samples / 1000)
        
        # Корекція на основі варіативності даних
        if len(self.historical_data) >= 10:
            recent_loads = [d.get('cpu_usage', 0) for d in list(self.historical_data)[-10:]]
            variability = np.std(recent_loads) / (np.mean(recent_loads) + 1e-6)
            variability_factor = max(0.5, 1 - variability)
        else:
            variability_factor = 0.5
        
        confidence = base_confidence * sample_factor * variability_factor
        return min(1.0, max(0.0, confidence))
    
    async def _retrain_models(self):
        """Перетренування моделей"""
        self.logger.info("Початок перетренування моделей")
        
        try:
            # Підготовка даних для тренування
            if len(self.historical_data) < self.min_training_samples:
                self.logger.warning("Недостатньо даних для тренування")
                return
            
            # Конвертація в DataFrame
            df = pd.DataFrame(list(self.historical_data))
            
            # Підготовка ознак та цілей
            X, y = self._prepare_training_data(df)
            
            if len(X) < self.min_training_samples:
                self.logger.warning("Недостатньо даних після підготовки")
                return
            
            # Тренування кожної моделі
            for model_name, model_info in self.models.items():
                try:
                    # Розділення на тренувальну та тестову вибірки
                    split_idx = int(len(X) * 0.8)
                    X_train, X_test = X[:split_idx], X[split_idx:]
                    y_train, y_test = y[:split_idx], y[split_idx:]
                    
                    # Масштабування ознак
                    model_info.scaler.fit(X_train)
                    X_train_scaled = model_info.scaler.transform(X_train)
                    X_test_scaled = model_info.scaler.transform(X_test)
                    
                    # Тренування моделі
                    model_info.model.fit(X_train_scaled, y_train)
                    
                    # Оцінка точності
                    y_pred = model_info.model.predict(X_test_scaled)
                    mse = mean_squared_error(y_test, y_pred)
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    # Оновлення інформації про модель
                    model_info.accuracy = 1 - (mse / (np.var(y_test) + 1e-6))
                    model_info.features = self._get_feature_names()
                    model_info.last_trained = datetime.utcnow()
                    model_info.training_samples = len(X_train)
                    
                    self.logger.info(f"Модель {model_name} перетреновано", extra={
                        "accuracy": model_info.accuracy,
                        "mse": mse,
                        "mae": mae,
                        "training_samples": len(X_train)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Помилка тренування моделі {model_name}", 
                                    extra={"error": str(e)})
            
            # Вибір найкращої моделі
            self._select_best_model()
            
        except Exception as e:
            self.logger.error("Помилка перетренування моделей", extra={"error": str(e)})
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[List[List[float]], List[float]]:
        """Підготовка даних для тренування"""
        X, y = [], []
        
        for i in range(len(df) - 1):
            try:
                # Ознаки
                current_row = df.iloc[i]
                features = self._extract_features_from_row(current_row)
                
                # Ціль (навантаження в наступний момент)
                next_row = df.iloc[i + 1]
                target = next_row.get('cpu_usage', 0)
                
                X.append(features)
                y.append(target)
                
            except Exception as e:
                self.logger.warning(f"Помилка підготовки рядка {i}", extra={"error": str(e)})
                continue
        
        return X, y
    
    def _extract_features_from_row(self, row: pd.Series) -> List[float]:
        """Витягнення ознак з рядка даних"""
        features = [
            row.get('cpu_usage', 0),
            row.get('memory_usage', 0),
            row.get('response_time', 0),
            row.get('throughput', 0),
            row.get('error_rate', 0),
            row.get('queue_size', 0)
        ]
        
        # Часові ознаки
        timestamp = pd.to_datetime(row['timestamp'])
        features.extend([
            timestamp.hour,
            timestamp.weekday(),
            timestamp.isocalendar()[1]
        ])
        
        return features
    
    def _get_feature_names(self) -> List[str]:
        """Отримання назв ознак"""
        return [
            'cpu_usage', 'memory_usage', 'response_time', 'throughput', 'error_rate', 'queue_size',
            'hour', 'weekday', 'week_of_year'
        ]
    
    def _select_best_model(self):
        """Вибір найкращої моделі"""
        best_model = None
        best_accuracy = 0
        
        for model_name, model_info in self.models.items():
            if model_info.accuracy > best_accuracy:
                best_accuracy = model_info.accuracy
                best_model = model_name
        
        if best_model and best_model != self.current_model:
            self.current_model = best_model
            self.logger.info(f"Обрано нову найкращу модель: {best_model}", 
                           extra={"accuracy": best_accuracy})
    
    def update_prediction_accuracy(self, prediction: LoadPrediction, actual_load: float):
        """Оновлення точності прогнозу"""
        prediction.actual_load = actual_load
        prediction.error = abs(prediction.predicted_load - actual_load)
        
        # Оновлення статистики
        if prediction.error < 0.1:  # 10% помилка
            self.stats['accurate_predictions'] += 1
        
        # Оновлення середньої помилки
        total_predictions = self.stats['total_predictions']
        current_avg = self.stats['avg_error']
        new_avg = (current_avg * (total_predictions - 1) + prediction.error) / total_predictions
        self.stats['avg_error'] = new_avg
        
        self.logger.info("Точність прогнозу оновлено", extra={
            "predicted": prediction.predicted_load,
            "actual": actual_load,
            "error": prediction.error,
            "avg_error": new_avg
        })
    
    def get_prediction_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Отримання зведення прогнозів"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_predictions = [
            p for p in self.predictions_history 
            if p.timestamp > cutoff_time
        ]
        
        summary = {
            'period_hours': hours,
            'total_predictions': len(recent_predictions),
            'avg_predicted_load': 0,
            'avg_confidence': 0,
            'avg_error': 0,
            'model_usage': {},
            'accuracy_rate': 0
        }
        
        if recent_predictions:
            summary['avg_predicted_load'] = np.mean([p.predicted_load for p in recent_predictions])
            summary['avg_confidence'] = np.mean([p.confidence for p in recent_predictions])
            
            # Помилки для прогнозів з фактичними значеннями
            predictions_with_actual = [p for p in recent_predictions if p.actual_load is not None]
            if predictions_with_actual:
                summary['avg_error'] = np.mean([p.error for p in predictions_with_actual])
                summary['accuracy_rate'] = len([p for p in predictions_with_actual if p.error < 0.1]) / len(predictions_with_actual)
            
            # Використання моделей
            model_counts = {}
            for p in recent_predictions:
                model_counts[p.model_used] = model_counts.get(p.model_used, 0) + 1
            summary['model_usage'] = model_counts
        
        return summary
    
    def get_scaling_recommendations(self, predicted_load: float, 
                                  current_capacity: float) -> List[str]:
        """Отримання рекомендацій по масштабуванню"""
        recommendations = []
        
        # Розрахунок коефіцієнта навантаження
        load_factor = predicted_load / current_capacity if current_capacity > 0 else 0
        
        if load_factor > 1.5:
            recommendations.append("Критичне навантаження: негайно масштабуйте систему")
        elif load_factor > 1.2:
            recommendations.append("Високе навантаження: плануйте масштабування")
        elif load_factor > 0.8:
            recommendations.append("Середнє навантаження: моніторте тренди")
        elif load_factor < 0.3:
            recommendations.append("Низьке навантаження: розгляньте зменшення ресурсів")
        
        # Рекомендації на основі тренду
        if len(self.historical_data) >= 10:
            recent_loads = [d.get('cpu_usage', 0) for d in list(self.historical_data)[-10:]]
            trend = np.polyfit(range(len(recent_loads)), recent_loads, 1)[0]
            
            if trend > 0.1:
                recommendations.append("Зростаючий тренд: плануйте проактивне масштабування")
            elif trend < -0.1:
                recommendations.append("Спадаючий тренд: оптимізуйте використання ресурсів")
        
        return recommendations
    
    def export_prediction_data(self, filename: str = None) -> str:
        """Експорт даних прогнозування"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"load_prediction_data_{self.service_name}_{timestamp}.json"
        
        export_data = {
            'service_name': self.service_name,
            'exported_at': datetime.utcnow().isoformat(),
            'stats': self.stats,
            'current_model': self.current_model,
            'models_info': {
                name: {
                    'accuracy': model.accuracy,
                    'training_samples': model.training_samples,
                    'last_trained': model.last_trained.isoformat()
                }
                for name, model in self.models.items()
            },
            'recent_predictions': [
                asdict(p) for p in list(self.predictions_history)[-100:]
            ],
            'historical_data_sample': [
                {k: v for k, v in d.items() if k != 'timestamp'} 
                for d in list(self.historical_data)[-50:]
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Дані прогнозування експортовано: {filename}")
        return filename


# Глобальний екземпляр прогнозувача
load_predictor = None


def initialize_load_prediction(service_name: str):
    """Ініціалізація прогнозування навантаження"""
    global load_predictor
    
    load_predictor = LoadPredictor(service_name)
    
    logger = get_logger("load-prediction-init")
    logger.info("Прогнозування навантаження ініціалізовано", extra={
        "service_name": service_name
    })


def get_load_predictor() -> LoadPredictor:
    """Отримання прогнозувача навантаження"""
    return load_predictor 