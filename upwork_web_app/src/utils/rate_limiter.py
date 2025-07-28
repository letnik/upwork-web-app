"""
Система rate limiting для парсингу
"""

import time
import random
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger


@dataclass
class RateLimitConfig:
    """Конфігурація rate limiting"""
    requests_per_minute: int = 20
    requests_per_hour: int = 1000
    min_delay: float = 1.0  # секунди
    max_delay: float = 5.0  # секунди
    adaptive_delay: bool = True
    backoff_factor: float = 1.5


class RateLimiter:
    """Система обмеження швидкості запитів"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.request_history: Dict[str, list] = {}  # IP -> список часу запитів
        self.domain_history: Dict[str, list] = {}   # Домен -> список часу запитів
        self.blocked_ips: set = set()
        self.blocked_domains: set = set()
        self.backoff_times: Dict[str, float] = {}  # IP/домен -> час блокування
    
    def can_make_request(self, identifier: str, domain: str = None) -> bool:
        """Перевірка, чи можна зробити запит"""
        current_time = time.time()
        
        # Перевірка блокування
        if identifier in self.blocked_ips:
            if current_time < self.backoff_times.get(identifier, 0):
                return False
            else:
                self.blocked_ips.remove(identifier)
                self.backoff_times.pop(identifier, None)
        
        if domain and domain in self.blocked_domains:
            if current_time < self.backoff_times.get(domain, 0):
                return False
            else:
                self.blocked_domains.remove(domain)
                self.backoff_times.pop(domain, None)
        
        # Перевірка лімітів
        if not self._check_rate_limits(identifier, current_time):
            return False
        
        if domain and not self._check_domain_limits(domain, current_time):
            return False
        
        return True
    
    def _check_rate_limits(self, identifier: str, current_time: float) -> bool:
        """Перевірка лімітів для IP"""
        if identifier not in self.request_history:
            self.request_history[identifier] = []
        
        # Очищення старих записів
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        self.request_history[identifier] = [
            t for t in self.request_history[identifier] 
            if t > hour_ago
        ]
        
        # Перевірка лімітів
        requests_last_minute = len([t for t in self.request_history[identifier] if t > minute_ago])
        requests_last_hour = len(self.request_history[identifier])
        
        if requests_last_minute >= self.config.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {identifier}: {requests_last_minute} requests per minute")
            self._block_identifier(identifier, "minute")
            return False
        
        if requests_last_hour >= self.config.requests_per_hour:
            logger.warning(f"Rate limit exceeded for {identifier}: {requests_last_hour} requests per hour")
            self._block_identifier(identifier, "hour")
            return False
        
        return True
    
    def _check_domain_limits(self, domain: str, current_time: float) -> bool:
        """Перевірка лімітів для домену"""
        if domain not in self.domain_history:
            self.domain_history[domain] = []
        
        # Очищення старих записів
        minute_ago = current_time - 60
        self.domain_history[domain] = [
            t for t in self.domain_history[domain] 
            if t > minute_ago
        ]
        
        # Більш жорсткі ліміти для доменів
        requests_last_minute = len(self.domain_history[domain])
        if requests_last_minute >= self.config.requests_per_minute // 2:  # Половина ліміту
            logger.warning(f"Domain rate limit exceeded for {domain}: {requests_last_minute} requests per minute")
            self._block_domain(domain)
            return False
        
        return True
    
    def _block_identifier(self, identifier: str, block_type: str):
        """Блокування IP"""
        self.blocked_ips.add(identifier)
        
        # Адаптивний час блокування
        if block_type == "minute":
            block_time = 60 * self.config.backoff_factor
        else:  # hour
            block_time = 3600 * self.config.backoff_factor
        
        self.backoff_times[identifier] = time.time() + block_time
        logger.warning(f"Blocked {identifier} for {block_time} seconds")
    
    def _block_domain(self, domain: str):
        """Блокування домену"""
        self.blocked_domains.add(domain)
        block_time = 300  # 5 хвилин
        self.backoff_times[domain] = time.time() + block_time
        logger.warning(f"Blocked domain {domain} for {block_time} seconds")
    
    def record_request(self, identifier: str, domain: str = None, response_time: float = None):
        """Запис запиту"""
        current_time = time.time()
        
        # Запис для IP
        if identifier not in self.request_history:
            self.request_history[identifier] = []
        self.request_history[identifier].append(current_time)
        
        # Запис для домену
        if domain:
            if domain not in self.domain_history:
                self.domain_history[domain] = []
            self.domain_history[domain].append(current_time)
        
        # Адаптивна затримка
        if self.config.adaptive_delay and response_time:
            self._adjust_delays(identifier, response_time)
    
    def _adjust_delays(self, identifier: str, response_time: float):
        """Адаптивна настройка затримок"""
        if response_time > 5000:  # Більше 5 секунд
            # Збільшуємо затримку
            self.config.min_delay = min(self.config.min_delay * 1.2, 10.0)
            self.config.max_delay = min(self.config.max_delay * 1.1, 15.0)
            logger.info(f"Increased delays due to slow response: {response_time}ms")
        elif response_time < 1000:  # Менше 1 секунди
            # Зменшуємо затримку
            self.config.min_delay = max(self.config.min_delay * 0.9, 0.5)
            self.config.max_delay = max(self.config.max_delay * 0.95, 2.0)
            logger.info(f"Decreased delays due to fast response: {response_time}ms")
    
    def get_delay(self, identifier: str = None) -> float:
        """Отримання затримки перед наступним запитом"""
        if self.config.adaptive_delay:
            # Адаптивна затримка на основі історії
            if identifier and identifier in self.request_history:
                recent_requests = len([t for t in self.request_history[identifier] 
                                    if t > time.time() - 60])
                if recent_requests > self.config.requests_per_minute * 0.8:
                    return self.config.max_delay
        
        # Випадкова затримка в межах конфігурації
        return random.uniform(self.config.min_delay, self.config.max_delay)
    
    def get_stats(self) -> Dict:
        """Статистика rate limiter"""
        current_time = time.time()
        
        stats = {
            "blocked_ips": len(self.blocked_ips),
            "blocked_domains": len(self.blocked_domains),
            "active_ips": len(self.request_history),
            "active_domains": len(self.domain_history),
            "config": {
                "requests_per_minute": self.config.requests_per_minute,
                "requests_per_hour": self.config.requests_per_hour,
                "min_delay": self.config.min_delay,
                "max_delay": self.config.max_delay
            }
        }
        
        # Статистика по IP
        ip_stats = {}
        for ip, times in self.request_history.items():
            recent_requests = len([t for t in times if t > current_time - 60])
            ip_stats[ip] = {
                "requests_last_minute": recent_requests,
                "total_requests": len(times),
                "is_blocked": ip in self.blocked_ips
            }
        stats["ip_stats"] = ip_stats
        
        return stats


# Глобальний екземпляр rate limiter
rate_limiter = RateLimiter() 