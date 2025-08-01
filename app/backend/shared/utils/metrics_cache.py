"""
Кешування метрик для швидшого доступу до даних
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, Callable, List
from functools import lru_cache, wraps
from datetime import datetime, timedelta
import asyncio
import threading

from shared.config.logging import get_logger


class MetricsCache:
    """Кеш для метрик продуктивності"""
    
    def __init__(self, cache_ttl: int = 300, max_size: int = 1000):
        self.cache_ttl = cache_ttl  # секунди
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_lock = threading.RLock()
        
        # Статистика кешу
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        
        self.logger = get_logger("metrics-cache")
        
        # Запуск очищення застарілих записів
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("Кеш метрик ініціалізовано", extra={
            "cache_ttl": cache_ttl,
            "max_size": max_size
        })
    
    def _generate_cache_key(self, service_name: str, metric_type: str, 
                           params: Dict[str, Any] = None) -> str:
        """Генерація ключа кешу"""
        key_data = {
            'service': service_name,
            'type': metric_type,
            'params': params or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, service_name: str, metric_type: str, 
            params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Отримання метрик з кешу"""
        cache_key = self._generate_cache_key(service_name, metric_type, params)
        
        with self.cache_lock:
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                
                # Перевірка терміну дії
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    self.stats['hits'] += 1
                    return cache_entry['data']
                else:
                    # Видалення застарілого запису
                    del self.cache[cache_key]
                    self.stats['size'] -= 1
            
            self.stats['misses'] += 1
            return None
    
    def set(self, service_name: str, metric_type: str, 
            data: Dict[str, Any], params: Dict[str, Any] = None):
        """Збереження метрик в кеш"""
        cache_key = self._generate_cache_key(service_name, metric_type, params)
        
        with self.cache_lock:
            # Перевірка розміру кешу
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'service_name': service_name,
                'metric_type': metric_type,
                'params': params
            }
            
            self.cache[cache_key] = cache_entry
            self.stats['size'] = len(self.cache)
    
    def _evict_oldest(self):
        """Видалення найстарішого запису"""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), 
                        key=lambda k: self.cache[k]['timestamp'])
        
        del self.cache[oldest_key]
        self.stats['evictions'] += 1
        self.stats['size'] = len(self.cache)
    
    def invalidate(self, service_name: str = None, metric_type: str = None):
        """Інвалідація кешу"""
        with self.cache_lock:
            keys_to_remove = []
            
            for key, entry in self.cache.items():
                if service_name and entry['service_name'] != service_name:
                    continue
                if metric_type and entry['metric_type'] != metric_type:
                    continue
                
                keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.cache[key]
            
            self.stats['size'] = len(self.cache)
            
            self.logger.info("Кеш інвалідовано", extra={
                "service_name": service_name,
                "metric_type": metric_type,
                "removed_entries": len(keys_to_remove)
            })
    
    def _cleanup_loop(self):
        """Цикл очищення застарілих записів"""
        while True:
            try:
                time.sleep(60)  # Перевірка кожну хвилину
                self._cleanup_expired()
            except Exception as e:
                self.logger.error("Помилка очищення кешу", extra={"error": str(e)})
    
    def _cleanup_expired(self):
        """Очищення застарілих записів"""
        current_time = time.time()
        expired_keys = []
        
        with self.cache_lock:
            for key, entry in self.cache.items():
                if current_time - entry['timestamp'] > self.cache_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            self.stats['size'] = len(self.cache)
        
        if expired_keys:
            self.logger.debug(f"Видалено {len(expired_keys)} застарілих записів")
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики кешу"""
        with self.cache_lock:
            hit_rate = (self.stats['hits'] / (self.stats['hits'] + self.stats['misses']) 
                       if (self.stats['hits'] + self.stats['misses']) > 0 else 0)
            
            return {
                **self.stats,
                'hit_rate': round(hit_rate, 3),
                'cache_size': len(self.cache),
                'cache_ttl': self.cache_ttl
            }


class CachedMetricsCollector:
    """Збірник метрик з кешуванням"""
    
    def __init__(self, cache: MetricsCache):
        self.cache = cache
        self.logger = get_logger("cached-metrics-collector")
    
    def get_cached_metrics(self, service_name: str, metric_type: str, 
                          params: Dict[str, Any] = None,
                          calculation_func: Callable = None) -> Dict[str, Any]:
        """Отримання кешованих метрик"""
        # Спробувати отримати з кешу
        cached_data = self.cache.get(service_name, metric_type, params)
        
        if cached_data is not None:
            self.logger.debug("Метрики отримано з кешу", extra={
                "service_name": service_name,
                "metric_type": metric_type
            })
            return cached_data
        
        # Обчислення метрик
        if calculation_func:
            try:
                metrics_data = calculation_func()
                
                # Збереження в кеш
                self.cache.set(service_name, metric_type, metrics_data, params)
                
                self.logger.debug("Метрики обчислено та збережено в кеш", extra={
                    "service_name": service_name,
                    "metric_type": metric_type
                })
                
                return metrics_data
                
            except Exception as e:
                self.logger.error("Помилка обчислення метрик", extra={
                    "error": str(e),
                    "service_name": service_name,
                    "metric_type": metric_type
                })
                return {}
        
        return {}
    
    def get_performance_summary(self, service_name: str, hours: int = 1) -> Dict[str, Any]:
        """Отримання зведення продуктивності з кешуванням"""
        params = {'hours': hours}
        
        def calculate_performance():
            from shared.utils.performance_metrics import get_metrics_summary
            return get_metrics_summary()
        
        return self.get_cached_metrics(
            service_name, 'performance_summary', params, calculate_performance
        )
    
    def get_error_summary(self, service_name: str, hours: int = 1) -> Dict[str, Any]:
        """Отримання зведення помилок з кешуванням"""
        params = {'hours': hours}
        
        def calculate_errors():
            from shared.utils.log_analyzer import LogAnalyzer
            analyzer = LogAnalyzer("logs")
            return analyzer.get_error_summary(hours=hours)
        
        return self.get_cached_metrics(
            service_name, 'error_summary', params, calculate_errors
        )
    
    def get_security_summary(self, service_name: str, hours: int = 1) -> Dict[str, Any]:
        """Отримання зведення безпеки з кешуванням"""
        params = {'hours': hours}
        
        def calculate_security():
            from shared.utils.log_analyzer import LogAnalyzer
            analyzer = LogAnalyzer("logs")
            return analyzer.get_security_summary(hours=hours)
        
        return self.get_cached_metrics(
            service_name, 'security_summary', params, calculate_security
        )


def cache_metrics(ttl: int = 300):
    """Декоратор для кешування результатів функцій"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерація ключа кешу
            key_data = {
                'func': func.__name__,
                'args': args,
                'kwargs': kwargs
            }
            cache_key = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
            
            # Перевірка кешу
            if hasattr(wrapper, '_cache') and cache_key in wrapper._cache:
                cache_entry = wrapper._cache[cache_key]
                if time.time() - cache_entry['timestamp'] < ttl:
                    return cache_entry['data']
            
            # Виконання функції
            result = func(*args, **kwargs)
            
            # Збереження в кеш
            if not hasattr(wrapper, '_cache'):
                wrapper._cache = {}
            
            wrapper._cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            return result
        
        return wrapper
    return decorator


class AsyncMetricsCache:
    """Асинхронний кеш для метрик"""
    
    def __init__(self, cache_ttl: int = 300, max_size: int = 1000):
        self.cache_ttl = cache_ttl
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        
        self.logger = get_logger("async-metrics-cache")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Асинхронне отримання з кешу"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['hits'] += 1
                return cache_entry['data']
            else:
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None
    
    async def set(self, key: str, data: Dict[str, Any]):
        """Асинхронне збереження в кеш"""
        if len(self.cache) >= self.max_size:
            await self._evict_oldest()
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    async def _evict_oldest(self):
        """Видалення найстарішого запису"""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), 
                        key=lambda k: self.cache[k]['timestamp'])
        
        del self.cache[oldest_key]
        self.stats['evictions'] += 1
    
    async def invalidate_pattern(self, pattern: str):
        """Інвалідація по патерну"""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        
        for key in keys_to_remove:
            del self.cache[key]
        
        self.logger.info(f"Інвалідовано {len(keys_to_remove)} записів по патерну: {pattern}")


# Глобальні екземпляри кешу
metrics_cache = None
cached_collector = None
async_metrics_cache = None


def initialize_metrics_cache(cache_ttl: int = 300, max_size: int = 1000):
    """Ініціалізація кешу метрик"""
    global metrics_cache, cached_collector
    
    metrics_cache = MetricsCache(cache_ttl, max_size)
    cached_collector = CachedMetricsCollector(metrics_cache)
    
    logger = get_logger("metrics-cache-init")
    logger.info("Кеш метрик ініціалізовано", extra={
        "cache_ttl": cache_ttl,
        "max_size": max_size
    })


async def initialize_async_metrics_cache(cache_ttl: int = 300, max_size: int = 1000):
    """Ініціалізація асинхронного кешу метрик"""
    global async_metrics_cache
    
    async_metrics_cache = AsyncMetricsCache(cache_ttl, max_size)
    
    logger = get_logger("async-metrics-cache-init")
    logger.info("Асинхронний кеш метрик ініціалізовано", extra={
        "cache_ttl": cache_ttl,
        "max_size": max_size
    })


def get_metrics_cache() -> MetricsCache:
    """Отримання кешу метрик"""
    return metrics_cache


def get_cached_collector() -> CachedMetricsCollector:
    """Отримання збірника кешованих метрик"""
    return cached_collector


async def get_async_metrics_cache() -> AsyncMetricsCache:
    """Отримання асинхронного кешу метрик"""
    return async_metrics_cache 