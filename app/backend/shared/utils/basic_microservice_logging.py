"""
Базова мікросервісна архітектура логування (Phase 3)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from shared.config.logging import get_logger


class LogLevel(Enum):
    """Рівні логування"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class BasicLogEntry:
    """Базовий запис логу"""
    id: str
    service_name: str
    timestamp: datetime
    level: LogLevel
    message: str
    context: Dict[str, Any]


class BasicCentralizedLogger:
    """Базовий централізований логер"""
    
    def __init__(self, service_name: str, api_endpoint: str = "http://localhost:8000/logs"):
        self.service_name = service_name
        self.api_endpoint = api_endpoint
        self.logger = get_logger("basic-centralized-logger")
        
        # Налаштування
        self.batch_size = 50
        self.retry_attempts = 3
        
        # Буфер
        self.log_buffer = []
        
        # Статистика
        self.stats = {
            'logs_sent': 0,
            'logs_failed': 0,
            'last_send': None
        }
        
        self.logger.info("Базовий централізований логер ініціалізовано", extra={
            "service_name": service_name,
            "api_endpoint": api_endpoint
        })
    
    async def log(self, level: LogLevel, message: str, context: Dict[str, Any] = None):
        """Логування повідомлення"""
        try:
            log_entry = BasicLogEntry(
                id=str(uuid.uuid4()),
                service_name=self.service_name,
                timestamp=datetime.utcnow(),
                level=level,
                message=message,
                context=context or {}
            )
            
            # Додавання в буфер
            self.log_buffer.append(log_entry)
            
            # Перевірка розміру буфера
            if len(self.log_buffer) >= self.batch_size:
                await self._send_batch()
            
        except Exception as e:
            self.logger.error("Помилка логування", extra={"error": str(e)})
            self.stats['logs_failed'] += 1
    
    async def _send_batch(self):
        """Відправка пакету логів"""
        if not self.log_buffer:
            return
        
        try:
            # Підготовка даних
            batch_data = {
                'service_name': self.service_name,
                'timestamp': datetime.utcnow().isoformat(),
                'entries': [
                    {
                        'id': entry.id,
                        'service_name': entry.service_name,
                        'timestamp': entry.timestamp.isoformat(),
                        'level': entry.level.value,
                        'message': entry.message,
                        'context': entry.context
                    }
                    for entry in self.log_buffer
                ]
            }
            
            # Відправка запиту
            for attempt in range(self.retry_attempts):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self.api_endpoint,
                            json=batch_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                self.stats['logs_sent'] += len(self.log_buffer)
                                self.stats['last_send'] = datetime.utcnow().isoformat()
                                
                                self.logger.debug(f"Пакет логів відправлено: {len(self.log_buffer)} записів")
                                break
                            else:
                                self.logger.warning(f"Помилка відправки: {response.status}")
                                
                except Exception as e:
                    self.logger.warning(f"Спроба {attempt + 1} невдала", extra={"error": str(e)})
                    
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(1)
            
            # Очищення буфера
            self.log_buffer.clear()
            
        except Exception as e:
            self.logger.error("Помилка відправки пакету", extra={"error": str(e)})
            self.stats['logs_failed'] += len(self.log_buffer)
    
    async def flush(self):
        """Примусова відправка буфера"""
        if self.log_buffer:
            await self._send_batch()
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики"""
        return {
            **self.stats,
            'buffer_size': len(self.log_buffer)
        }


class BasicLogAPI:
    """Базовий API для логування"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.logger = get_logger("basic-log-api")
        
        # Зберігання логів
        self.logs_storage = []
        self.service_logs = {}
        
        # Статистика
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_logs_received': 0
        }
        
        self.logger.info("Базовий API логування ініціалізовано", extra={
            "host": host,
            "port": port
        })
    
    async def start(self):
        """Запуск API"""
        from aiohttp import web
        
        app = web.Application()
        
        # Маршрути
        app.router.add_post('/logs', self._handle_logs)
        app.router.add_get('/logs', self._get_logs)
        app.router.add_get('/stats', self._get_stats)
        app.router.add_get('/health', self._health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"Базовий API логування запущено на {self.host}:{self.port}")
    
    async def _handle_logs(self, request):
        """Обробка POST запитів з логами"""
        try:
            self.stats['total_requests'] += 1
            
            data = await request.json()
            
            # Обробка пакету логів
            if 'entries' in data:
                service_name = data.get('service_name', 'unknown')
                entries_data = data.get('entries', [])
                
                processed_count = 0
                for entry_data in entries_data:
                    try:
                        log_entry = BasicLogEntry(
                            id=entry_data.get('id', str(uuid.uuid4())),
                            service_name=entry_data.get('service_name', service_name),
                            timestamp=datetime.fromisoformat(entry_data['timestamp']),
                            level=LogLevel(entry_data['level']),
                            message=entry_data['message'],
                            context=entry_data.get('context', {})
                        )
                        
                        # Збереження логу
                        self.logs_storage.append(log_entry)
                        
                        # Групування по сервісах
                        if service_name not in self.service_logs:
                            self.service_logs[service_name] = []
                        self.service_logs[service_name].append(log_entry)
                        
                        processed_count += 1
                        
                    except Exception as e:
                        self.logger.error("Помилка обробки запису логу", extra={
                            "error": str(e),
                            "entry_data": entry_data
                        })
                
                self.stats['total_logs_received'] += processed_count
                self.stats['successful_requests'] += 1
                
                self.logger.info(f"Оброблено пакет логів", extra={
                    "service_name": service_name,
                    "processed_count": processed_count
                })
                
                return web.json_response({
                    'status': 'success',
                    'processed_count': processed_count
                })
            
            else:
                return web.json_response({
                    'status': 'error',
                    'message': 'Invalid request format'
                }, status=400)
                
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.logger.error("Помилка обробки запиту", extra={"error": str(e)})
            
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def _get_logs(self, request):
        """Отримання логів"""
        try:
            limit = int(request.query.get('limit', 100))
            service_name = request.query.get('service')
            level = request.query.get('level')
            
            # Фільтрація логів
            filtered_logs = self.logs_storage
            
            if service_name:
                filtered_logs = [log for log in filtered_logs if log.service_name == service_name]
            
            if level:
                filtered_logs = [log for log in filtered_logs if log.level.value == level]
            
            # Пагінація
            paginated_logs = filtered_logs[-limit:]
            
            return web.json_response({
                'logs': [
                    {
                        'id': log.id,
                        'service_name': log.service_name,
                        'timestamp': log.timestamp.isoformat(),
                        'level': log.level.value,
                        'message': log.message,
                        'context': log.context
                    }
                    for log in paginated_logs
                ],
                'total': len(filtered_logs),
                'limit': limit
            })
            
        except Exception as e:
            self.logger.error("Помилка отримання логів", extra={"error": str(e)})
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def _get_stats(self, request):
        """Отримання статистики"""
        return web.json_response({
            **self.stats,
            'services_count': len(self.service_logs),
            'total_logs_stored': len(self.logs_storage),
            'services': list(self.service_logs.keys())
        })
    
    async def _health_check(self, request):
        """Перевірка здоров'я API"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services_count': len(self.service_logs)
        })


# Глобальні екземпляри
basic_centralized_logger = None
basic_log_api = None


def initialize_basic_microservice_logging(service_name: str, api_endpoint: str = None):
    """Ініціалізація базового мікросервісного логування"""
    global basic_centralized_logger
    
    if api_endpoint is None:
        api_endpoint = "http://localhost:8000/logs"
    
    basic_centralized_logger = BasicCentralizedLogger(service_name, api_endpoint)
    
    logger = get_logger("basic-microservice-logging-init")
    logger.info("Базове мікросервісне логування ініціалізовано", extra={
        "service_name": service_name,
        "api_endpoint": api_endpoint
    })


async def initialize_basic_log_api(host: str = "0.0.0.0", port: int = 8000):
    """Ініціалізація базового API логування"""
    global basic_log_api
    
    basic_log_api = BasicLogAPI(host, port)
    await basic_log_api.start()


def get_basic_centralized_logger() -> BasicCentralizedLogger:
    """Отримання базового централізованого логера"""
    return basic_centralized_logger


def get_basic_log_api() -> BasicLogAPI:
    """Отримання базового API логування"""
    return basic_log_api 