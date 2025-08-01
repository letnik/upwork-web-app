"""
Мікросервісна архітектура логування з централізованим сервісом
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib
from collections import defaultdict, deque
import threading

from shared.config.logging import get_logger


class LogLevel(Enum):
    """Рівні логування"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Категорії логів"""
    SYSTEM = "system"
    APPLICATION = "application"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATABASE = "database"
    API = "api"
    USER = "user"
    AUDIT = "audit"


@dataclass
class LogEntry:
    """Запис логу"""
    id: str
    service_name: str
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None


@dataclass
class LogBatch:
    """Пакет логів"""
    batch_id: str
    service_name: str
    entries: List[LogEntry]
    timestamp: datetime
    size: int


class CentralizedLoggingService:
    """Централізований сервіс логування"""
    
    def __init__(self, service_name: str, api_endpoint: str = "http://localhost:8000/logs"):
        self.service_name = service_name
        self.api_endpoint = api_endpoint
        self.logger = get_logger("centralized-logging")
        
        # Налаштування
        self.batch_size = 100
        self.batch_timeout = 5  # секунди
        self.retry_attempts = 3
        self.retry_delay = 1  # секунди
        
        # Буфери
        self.log_buffer = deque(maxlen=10000)
        self.batch_buffer = deque(maxlen=1000)
        
        # Статистика
        self.stats = {
            'logs_sent': 0,
            'logs_failed': 0,
            'batches_sent': 0,
            'batches_failed': 0,
            'last_send': None,
            'avg_send_time': 0.0
        }
        
        # HTTP сесія
        self.session = None
        
        # Фонові задачі
        self.batch_task = None
        self.cleanup_task = None
        self.running = False
        
        self.logger.info("Централізований сервіс логування ініціалізовано", extra={
            "service_name": service_name,
            "api_endpoint": api_endpoint
        })
    
    async def start(self):
        """Запуск сервісу"""
        if self.running:
            return
        
        self.running = True
        
        # Створення HTTP сесії
        self.session = aiohttp.ClientSession()
        
        # Запуск фоновых задач
        self.batch_task = asyncio.create_task(self._batch_processor())
        self.cleanup_task = asyncio.create_task(self._cleanup_processor())
        
        self.logger.info("Централізований сервіс логування запущено")
    
    async def stop(self):
        """Зупинка сервісу"""
        if not self.running:
            return
        
        self.running = False
        
        # Зупинка задач
        if self.batch_task:
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Закриття HTTP сесії
        if self.session:
            await self.session.close()
        
        # Фінальна відправка буфера
        await self._send_remaining_logs()
        
        self.logger.info("Централізований сервіс логування зупинено")
    
    async def log(self, level: LogLevel, category: LogCategory, message: str, 
                 context: Dict[str, Any] = None, metadata: Dict[str, Any] = None,
                 trace_id: str = None, span_id: str = None, parent_span_id: str = None):
        """Логування повідомлення"""
        try:
            log_entry = LogEntry(
                id=str(uuid.uuid4()),
                service_name=self.service_name,
                timestamp=datetime.utcnow(),
                level=level,
                category=category,
                message=message,
                context=context or {},
                metadata=metadata or {},
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id
            )
            
            # Додавання в буфер
            self.log_buffer.append(log_entry)
            
            # Перевірка розміру буфера
            if len(self.log_buffer) >= self.batch_size:
                await self._process_batch()
            
        except Exception as e:
            self.logger.error("Помилка логування", extra={"error": str(e)})
            self.stats['logs_failed'] += 1
    
    async def _batch_processor(self):
        """Обробник пакетів логів"""
        while self.running:
            try:
                await asyncio.sleep(self.batch_timeout)
                
                if self.log_buffer:
                    await self._process_batch()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Помилка обробки пакетів", extra={"error": str(e)})
    
    async def _process_batch(self):
        """Обробка пакету логів"""
        if not self.log_buffer:
            return
        
        try:
            # Створення пакету
            batch_entries = []
            while self.log_buffer and len(batch_entries) < self.batch_size:
                batch_entries.append(self.log_buffer.popleft())
            
            if not batch_entries:
                return
            
            batch = LogBatch(
                batch_id=str(uuid.uuid4()),
                service_name=self.service_name,
                entries=batch_entries,
                timestamp=datetime.utcnow(),
                size=len(batch_entries)
            )
            
            # Відправка пакету
            success = await self._send_batch(batch)
            
            if success:
                self.stats['batches_sent'] += 1
                self.stats['logs_sent'] += len(batch_entries)
            else:
                self.stats['batches_failed'] += 1
                self.stats['logs_failed'] += len(batch_entries)
                
                # Повернення логів в буфер при невдачі
                for entry in batch_entries:
                    self.log_buffer.appendleft(entry)
            
        except Exception as e:
            self.logger.error("Помилка обробки пакету", extra={"error": str(e)})
            self.stats['batches_failed'] += 1
    
    async def _send_batch(self, batch: LogBatch) -> bool:
        """Відправка пакету логів"""
        start_time = time.time()
        
        for attempt in range(self.retry_attempts):
            try:
                # Підготовка даних
                batch_data = {
                    'batch_id': batch.batch_id,
                    'service_name': batch.service_name,
                    'timestamp': batch.timestamp.isoformat(),
                    'entries': [
                        {
                            'id': entry.id,
                            'service_name': entry.service_name,
                            'timestamp': entry.timestamp.isoformat(),
                            'level': entry.level.value,
                            'category': entry.category.value,
                            'message': entry.message,
                            'context': entry.context,
                            'metadata': entry.metadata,
                            'trace_id': entry.trace_id,
                            'span_id': entry.span_id,
                            'parent_span_id': entry.parent_span_id
                        }
                        for entry in batch.entries
                    ]
                }
                
                # Відправка запиту
                async with self.session.post(
                    self.api_endpoint,
                    json=batch_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        send_time = time.time() - start_time
                        self.stats['avg_send_time'] = (
                            (self.stats['avg_send_time'] * (self.stats['batches_sent'] - 1) + send_time) 
                            / self.stats['batches_sent']
                        )
                        self.stats['last_send'] = datetime.utcnow().isoformat()
                        
                        self.logger.debug(f"Пакет логів відправлено: {batch.batch_id}", extra={
                            "batch_size": batch.size,
                            "send_time": send_time
                        })
                        
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.warning(f"Помилка відправки пакету: {response.status}", extra={
                            "error": error_text,
                            "attempt": attempt + 1
                        })
                
            except Exception as e:
                self.logger.warning(f"Помилка відправки пакету (спроба {attempt + 1})", extra={
                    "error": str(e),
                    "attempt": attempt + 1
                })
            
            # Затримка перед повторною спробою
            if attempt < self.retry_attempts - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return False
    
    async def _cleanup_processor(self):
        """Обробник очищення"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Кожні 5 хвилин
                
                # Очищення старих пакетів
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                self.batch_buffer = deque(
                    [batch for batch in self.batch_buffer if batch.timestamp > cutoff_time],
                    maxlen=1000
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Помилка очищення", extra={"error": str(e)})
    
    async def _send_remaining_logs(self):
        """Відправка залишкових логів"""
        if self.log_buffer:
            self.logger.info(f"Відправка {len(self.log_buffer)} залишкових логів")
            
            # Створення фінального пакету
            batch_entries = list(self.log_buffer)
            self.log_buffer.clear()
            
            batch = LogBatch(
                batch_id=str(uuid.uuid4()),
                service_name=self.service_name,
                entries=batch_entries,
                timestamp=datetime.utcnow(),
                size=len(batch_entries)
            )
            
            await self._send_batch(batch)
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики"""
        return {
            **self.stats,
            'buffer_size': len(self.log_buffer),
            'batch_buffer_size': len(self.batch_buffer),
            'running': self.running
        }


class DistributedLogProcessor:
    """Розподілений обробник логів"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = get_logger("distributed-log-processor")
        
        # Налаштування
        self.processing_workers = 4
        self.queue_size = 1000
        
        # Черги обробки
        self.log_queue = asyncio.Queue(maxsize=self.queue_size)
        self.result_queue = asyncio.Queue(maxsize=self.queue_size)
        
        # Воркери
        self.workers = []
        self.running = False
        
        # Статистика
        self.stats = {
            'logs_processed': 0,
            'logs_failed': 0,
            'avg_processing_time': 0.0,
            'active_workers': 0
        }
        
        self.logger.info("Розподілений обробник логів ініціалізовано", extra={
            "service_name": service_name,
            "workers": self.processing_workers
        })
    
    async def start(self):
        """Запуск обробника"""
        if self.running:
            return
        
        self.running = True
        
        # Запуск воркерів
        for i in range(self.processing_workers):
            worker = asyncio.create_task(self._log_worker(f"worker-{i}"))
            self.workers.append(worker)
        
        self.logger.info("Розподілений обробник логів запущено")
    
    async def stop(self):
        """Зупинка обробника"""
        if not self.running:
            return
        
        self.running = False
        
        # Зупинка воркерів
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        self.logger.info("Розподілений обробник логів зупинено")
    
    async def process_log(self, log_entry: LogEntry) -> Dict[str, Any]:
        """Обробка логу"""
        try:
            # Додавання в чергу обробки
            await self.log_queue.put(log_entry)
            
            # Очікування результату
            result = await asyncio.wait_for(
                self.result_queue.get(),
                timeout=30.0
            )
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.warning("Таймаут обробки логу")
            return {'status': 'timeout', 'error': 'Processing timeout'}
        except Exception as e:
            self.logger.error("Помилка обробки логу", extra={"error": str(e)})
            return {'status': 'error', 'error': str(e)}
    
    async def _log_worker(self, worker_name: str):
        """Воркер обробки логів"""
        self.stats['active_workers'] += 1
        
        while self.running:
            try:
                # Отримання логу з черги
                log_entry = await asyncio.wait_for(
                    self.log_queue.get(),
                    timeout=1.0
                )
                
                start_time = time.time()
                
                # Обробка логу
                result = await self._process_log_entry(log_entry)
                
                processing_time = time.time() - start_time
                
                # Оновлення статистики
                self.stats['logs_processed'] += 1
                self.stats['avg_processing_time'] = (
                    (self.stats['avg_processing_time'] * (self.stats['logs_processed'] - 1) + processing_time)
                    / self.stats['logs_processed']
                )
                
                # Додавання результату в чергу
                await self.result_queue.put(result)
                
                self.logger.debug(f"Лог оброблено воркером {worker_name}", extra={
                    "processing_time": processing_time,
                    "log_id": log_entry.id
                })
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Помилка воркера {worker_name}", extra={"error": str(e)})
                self.stats['logs_failed'] += 1
        
        self.stats['active_workers'] -= 1
    
    async def _process_log_entry(self, log_entry: LogEntry) -> Dict[str, Any]:
        """Обробка запису логу"""
        try:
            # Базова обробка
            result = {
                'log_id': log_entry.id,
                'status': 'processed',
                'timestamp': datetime.utcnow().isoformat(),
                'processing_steps': []
            }
            
            # Аналіз рівня логування
            if log_entry.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                result['processing_steps'].append('error_analysis')
                result['priority'] = 'high'
            else:
                result['priority'] = 'normal'
            
            # Аналіз категорії
            if log_entry.category == LogCategory.SECURITY:
                result['processing_steps'].append('security_analysis')
                result['priority'] = 'high'
            elif log_entry.category == LogCategory.PERFORMANCE:
                result['processing_steps'].append('performance_analysis')
            
            # Аналіз контексту
            if log_entry.context:
                result['processing_steps'].append('context_analysis')
                
                # Виявлення ключових метрик
                if 'duration_ms' in log_entry.context:
                    duration = log_entry.context['duration_ms']
                    if duration > 1000:
                        result['processing_steps'].append('slow_operation_detection')
                        result['priority'] = 'high'
                
                if 'error_rate' in log_entry.context:
                    error_rate = log_entry.context['error_rate']
                    if error_rate > 0.1:
                        result['processing_steps'].append('high_error_rate_detection')
                        result['priority'] = 'high'
            
            # Аналіз метаданих
            if log_entry.metadata:
                result['processing_steps'].append('metadata_analysis')
            
            # Трейсинг
            if log_entry.trace_id:
                result['processing_steps'].append('trace_analysis')
                result['trace_id'] = log_entry.trace_id
            
            return result
            
        except Exception as e:
            return {
                'log_id': log_entry.id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики"""
        return {
            **self.stats,
            'queue_size': self.log_queue.qsize(),
            'result_queue_size': self.result_queue.qsize(),
            'running': self.running
        }


class MicroserviceLoggingAPI:
    """API для мікросервісного логування"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.logger = get_logger("microservice-logging-api")
        
        # Зберігання логів
        self.logs_storage = deque(maxlen=100000)
        self.service_logs = defaultdict(lambda: deque(maxlen=10000))
        
        # Статистика
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_logs_received': 0,
            'services_count': 0
        }
        
        self.logger.info("API мікросервісного логування ініціалізовано", extra={
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
        app.router.add_get('/logs/{service_name}', self._get_service_logs)
        app.router.add_get('/stats', self._get_stats)
        app.router.add_get('/health', self._health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"API мікросервісного логування запущено на {self.host}:{self.port}")
    
    async def _handle_logs(self, request):
        """Обробка POST запитів з логами"""
        try:
            self.stats['total_requests'] += 1
            
            data = await request.json()
            
            # Обробка пакету логів
            if 'entries' in data:
                batch_id = data.get('batch_id', 'unknown')
                service_name = data.get('service_name', 'unknown')
                entries_data = data.get('entries', [])
                
                processed_count = 0
                for entry_data in entries_data:
                    try:
                        log_entry = LogEntry(
                            id=entry_data.get('id', str(uuid.uuid4())),
                            service_name=entry_data.get('service_name', service_name),
                            timestamp=datetime.fromisoformat(entry_data['timestamp']),
                            level=LogLevel(entry_data['level']),
                            category=LogCategory(entry_data['category']),
                            message=entry_data['message'],
                            context=entry_data.get('context', {}),
                            metadata=entry_data.get('metadata', {}),
                            trace_id=entry_data.get('trace_id'),
                            span_id=entry_data.get('span_id'),
                            parent_span_id=entry_data.get('parent_span_id')
                        )
                        
                        # Збереження логу
                        self.logs_storage.append(log_entry)
                        self.service_logs[service_name].append(log_entry)
                        
                        processed_count += 1
                        
                    except Exception as e:
                        self.logger.error("Помилка обробки запису логу", extra={
                            "error": str(e),
                            "entry_data": entry_data
                        })
                
                self.stats['total_logs_received'] += processed_count
                self.stats['successful_requests'] += 1
                
                self.logger.info(f"Оброблено пакет логів: {batch_id}", extra={
                    "service_name": service_name,
                    "processed_count": processed_count,
                    "total_entries": len(entries_data)
                })
                
                return web.json_response({
                    'status': 'success',
                    'batch_id': batch_id,
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
            offset = int(request.query.get('offset', 0))
            level = request.query.get('level')
            category = request.query.get('category')
            
            # Фільтрація логів
            filtered_logs = list(self.logs_storage)
            
            if level:
                filtered_logs = [log for log in filtered_logs if log.level.value == level]
            
            if category:
                filtered_logs = [log for log in filtered_logs if log.category.value == category]
            
            # Пагінація
            paginated_logs = filtered_logs[offset:offset + limit]
            
            return web.json_response({
                'logs': [
                    {
                        'id': log.id,
                        'service_name': log.service_name,
                        'timestamp': log.timestamp.isoformat(),
                        'level': log.level.value,
                        'category': log.category.value,
                        'message': log.message,
                        'context': log.context,
                        'metadata': log.metadata
                    }
                    for log in paginated_logs
                ],
                'total': len(filtered_logs),
                'limit': limit,
                'offset': offset
            })
            
        except Exception as e:
            self.logger.error("Помилка отримання логів", extra={"error": str(e)})
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def _get_service_logs(self, request):
        """Отримання логів конкретного сервісу"""
        try:
            service_name = request.match_info['service_name']
            limit = int(request.query.get('limit', 100))
            
            service_logs = list(self.service_logs[service_name])
            paginated_logs = service_logs[-limit:]
            
            return web.json_response({
                'service_name': service_name,
                'logs': [
                    {
                        'id': log.id,
                        'timestamp': log.timestamp.isoformat(),
                        'level': log.level.value,
                        'category': log.category.value,
                        'message': log.message,
                        'context': log.context
                    }
                    for log in paginated_logs
                ],
                'total': len(service_logs)
            })
            
        except Exception as e:
            self.logger.error("Помилка отримання логів сервісу", extra={"error": str(e)})
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
centralized_logging_service = None
distributed_log_processor = None
microservice_logging_api = None


def initialize_microservice_logging(service_name: str, api_endpoint: str = None):
    """Ініціалізація мікросервісного логування"""
    global centralized_logging_service, distributed_log_processor
    
    if api_endpoint is None:
        api_endpoint = "http://localhost:8000/logs"
    
    centralized_logging_service = CentralizedLoggingService(service_name, api_endpoint)
    distributed_log_processor = DistributedLogProcessor(service_name)
    
    logger = get_logger("microservice-logging-init")
    logger.info("Мікросервісне логування ініціалізовано", extra={
        "service_name": service_name,
        "api_endpoint": api_endpoint
    })


async def initialize_microservice_logging_api(host: str = "0.0.0.0", port: int = 8000):
    """Ініціалізація API мікросервісного логування"""
    global microservice_logging_api
    
    microservice_logging_api = MicroserviceLoggingAPI(host, port)
    await microservice_logging_api.start()


def get_centralized_logging_service() -> CentralizedLoggingService:
    """Отримання централізованого сервісу логування"""
    return centralized_logging_service


def get_distributed_log_processor() -> DistributedLogProcessor:
    """Отримання розподіленого обробника логів"""
    return distributed_log_processor


def get_microservice_logging_api() -> MicroserviceLoggingAPI:
    """Отримання API мікросервісного логування"""
    return microservice_logging_api 