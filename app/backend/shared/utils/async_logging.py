"""
Асинхронне логування з буферизацією для покращення продуктивності
"""

import asyncio
import json
import threading
import time
from collections import deque
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import queue
import logging

from shared.config.logging import get_logger


@dataclass
class BufferedLogEntry:
    """Буферизований запис логу"""
    timestamp: datetime
    level: str
    message: str
    service_name: str
    context: Dict[str, Any]
    extra: Dict[str, Any]


class AsyncLogBuffer:
    """Асинхронний буфер для логів"""
    
    def __init__(self, max_size: int = 1000, flush_interval: int = 5, 
                 batch_size: int = 100, enable_compression: bool = True):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.enable_compression = enable_compression
        
        # Буфер для логів
        self.buffer = deque(maxlen=max_size)
        self.buffer_lock = threading.Lock()
        
        # Черга для асинхронної обробки
        self.log_queue = asyncio.Queue(maxsize=max_size * 2)
        
        # Статус роботи
        self.running = False
        self.flush_task = None
        self.processor_task = None
        
        # Статистика
        self.stats = {
            'logs_buffered': 0,
            'logs_flushed': 0,
            'flush_operations': 0,
            'errors': 0,
            'last_flush': None
        }
        
        self.logger = get_logger("async-log-buffer")
        
        self.logger.info("Асинхронний буфер логів ініціалізовано", extra={
            "max_size": max_size,
            "flush_interval": flush_interval,
            "batch_size": batch_size
        })
    
    async def start(self):
        """Запуск асинхронного логування"""
        if self.running:
            return
        
        self.running = True
        
        # Запуск задач
        self.flush_task = asyncio.create_task(self._flush_loop())
        self.processor_task = asyncio.create_task(self._process_logs())
        
        self.logger.info("Асинхронне логування запущено")
    
    async def stop(self):
        """Зупинка асинхронного логування"""
        if not self.running:
            return
        
        self.running = False
        
        # Очікування завершення задач
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        
        # Фінальне очищення буфера
        await self.flush_buffer()
        
        self.logger.info("Асинхронне логування зупинено", extra=self.stats)
    
    async def add_log(self, level: str, message: str, service_name: str, 
                     context: Dict[str, Any], extra: Dict[str, Any] = None):
        """Додавання логу в буфер"""
        try:
            log_entry = BufferedLogEntry(
                timestamp=datetime.utcnow(),
                level=level,
                message=message,
                service_name=service_name,
                context=context or {},
                extra=extra or {}
            )
            
            # Додавання в чергу
            await self.log_queue.put(log_entry)
            
            with self.buffer_lock:
                self.stats['logs_buffered'] += 1
            
        except Exception as e:
            self.logger.error("Помилка додавання логу в буфер", extra={
                "error": str(e),
                "level": level,
                "message": message
            })
            with self.buffer_lock:
                self.stats['errors'] += 1
    
    async def _process_logs(self):
        """Обробка логів з черги"""
        while self.running:
            try:
                # Отримання логу з черги
                log_entry = await asyncio.wait_for(
                    self.log_queue.get(), 
                    timeout=1.0
                )
                
                # Додавання в буфер
                with self.buffer_lock:
                    self.buffer.append(log_entry)
                
                # Очищення буфера якщо переповнений
                if len(self.buffer) >= self.batch_size:
                    await self.flush_buffer()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error("Помилка обробки логу", extra={"error": str(e)})
                with self.buffer_lock:
                    self.stats['errors'] += 1
    
    async def _flush_loop(self):
        """Цикл очищення буфера"""
        while self.running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush_buffer()
                
            except Exception as e:
                self.logger.error("Помилка в циклі очищення", extra={"error": str(e)})
                with self.buffer_lock:
                    self.stats['errors'] += 1
    
    async def flush_buffer(self):
        """Очищення буфера"""
        with self.buffer_lock:
            if not self.buffer:
                return
            
            logs_to_flush = list(self.buffer)
            self.buffer.clear()
        
        if not logs_to_flush:
            return
        
        try:
            # Масове записування логів
            await self._write_logs_batch(logs_to_flush)
            
            with self.buffer_lock:
                self.stats['logs_flushed'] += len(logs_to_flush)
                self.stats['flush_operations'] += 1
                self.stats['last_flush'] = datetime.utcnow().isoformat()
            
            self.logger.debug(f"Буфер очищено: {len(logs_to_flush)} логів")
            
        except Exception as e:
            self.logger.error("Помилка очищення буфера", extra={
                "error": str(e),
                "logs_count": len(logs_to_flush)
            })
            with self.buffer_lock:
                self.stats['errors'] += 1
    
    async def _write_logs_batch(self, logs: List[BufferedLogEntry]):
        """Масове записування логів"""
        # Групування логів по типах
        log_groups = {
            'main': [],
            'error': [],
            'security': [],
            'performance': [],
            'api': [],
            'database': []
        }
        
        for log in logs:
            # Визначення типу логу
            log_type = self._determine_log_type(log)
            log_groups[log_type].append(log)
        
        # Паралельне записування в різні файли
        tasks = []
        for log_type, type_logs in log_groups.items():
            if type_logs:
                task = asyncio.create_task(
                    self._write_logs_to_file(log_type, type_logs)
                )
                tasks.append(task)
        
        # Очікування завершення всіх задач
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _determine_log_type(self, log: BufferedLogEntry) -> str:
        """Визначення типу логу"""
        message = log.message.lower()
        
        if 'security:' in message or 'login' in message or 'auth' in message:
            return 'security'
        elif 'performance:' in message or 'duration' in message:
            return 'performance'
        elif 'api:' in message or 'http' in message:
            return 'api'
        elif 'database:' in message or 'sql' in message or 'query' in message:
            return 'database'
        elif log.level == 'ERROR':
            return 'error'
        else:
            return 'main'
    
    async def _write_logs_to_file(self, log_type: str, logs: List[BufferedLogEntry]):
        """Записування логів в файл"""
        try:
            filename = f"logs/{logs[0].service_name}_{log_type}.log"
            
            # Підготовка даних для запису
            log_lines = []
            for log in logs:
                log_data = {
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level,
                    'message': log.message,
                    'service_name': log.service_name,
                    'context': log.context,
                    'extra': log.extra
                }
                log_lines.append(json.dumps(log_data, ensure_ascii=False))
            
            # Асинхронний запис в файл
            async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
                await f.write('\n'.join(log_lines) + '\n')
            
        except Exception as e:
            self.logger.error(f"Помилка запису в файл {log_type}", extra={
                "error": str(e),
                "logs_count": len(logs)
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики буфера"""
        with self.buffer_lock:
            return {
                **self.stats,
                'buffer_size': len(self.buffer),
                'queue_size': self.log_queue.qsize(),
                'running': self.running
            }


class AsyncStructuredLogger:
    """Асинхронний структурований логер"""
    
    def __init__(self, service_name: str, buffer_config: Dict[str, Any] = None):
        self.service_name = service_name
        self.buffer = AsyncLogBuffer(**(buffer_config or {}))
        self.logger = get_logger(f"async-{service_name}")
        
        # Контекст для логування
        self.context = {}
    
    async def start(self):
        """Запуск асинхронного логера"""
        await self.buffer.start()
    
    async def stop(self):
        """Зупинка асинхронного логера"""
        await self.buffer.stop()
    
    def set_context(self, **kwargs):
        """Встановлення контексту"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Очищення контексту"""
        self.context.clear()
    
    async def debug(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування DEBUG"""
        await self.buffer.add_log('DEBUG', message, self.service_name, self.context, extra)
    
    async def info(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування INFO"""
        await self.buffer.add_log('INFO', message, self.service_name, self.context, extra)
    
    async def warning(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування WARNING"""
        await self.buffer.add_log('WARNING', message, self.service_name, self.context, extra)
    
    async def error(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування ERROR"""
        await self.buffer.add_log('ERROR', message, self.service_name, self.context, extra)
    
    async def critical(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування CRITICAL"""
        await self.buffer.add_log('CRITICAL', message, self.service_name, self.context, extra)
    
    async def performance(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування продуктивності"""
        await self.buffer.add_log('INFO', f"Performance: {message}", self.service_name, self.context, extra)
    
    async def security(self, message: str, extra: Dict[str, Any] = None):
        """Асинхронне логування безпеки"""
        await self.buffer.add_log('INFO', f"Security: {message}", self.service_name, self.context, extra)
    
    async def api_call(self, method: str, endpoint: str, status_code: int, 
                      duration: float, extra: Dict[str, Any] = None):
        """Асинхронне логування API викликів"""
        api_extra = {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_ms': round(duration * 1000, 2),
            'success': 200 <= status_code < 400
        }
        if extra:
            api_extra.update(extra)
        
        await self.buffer.add_log('INFO', f"API: {method} {endpoint}", 
                                self.service_name, self.context, api_extra)
    
    async def database(self, operation: str, table: str, duration: float, 
                      rows_affected: int = None, extra: Dict[str, Any] = None):
        """Асинхронне логування операцій з БД"""
        db_extra = {
            'operation': operation,
            'table': table,
            'duration_ms': round(duration * 1000, 2),
            'rows_affected': rows_affected
        }
        if extra:
            db_extra.update(extra)
        
        await self.buffer.add_log('INFO', f"Database: {operation} {table}", 
                                self.service_name, self.context, db_extra)
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики"""
        return self.buffer.get_stats()


# Глобальний екземпляр асинхронного логера
async_logger = None


async def initialize_async_logging(service_name: str, buffer_config: Dict[str, Any] = None):
    """Ініціалізація асинхронного логування"""
    global async_logger
    
    async_logger = AsyncStructuredLogger(service_name, buffer_config)
    await async_logger.start()
    
    logger = get_logger("async-logging")
    logger.info("Асинхронне логування ініціалізовано", extra={
        "service_name": service_name,
        "buffer_config": buffer_config
    })


async def get_async_logger() -> AsyncStructuredLogger:
    """Отримання асинхронного логера"""
    return async_logger


async def shutdown_async_logging():
    """Зупинка асинхронного логування"""
    global async_logger
    
    if async_logger:
        await async_logger.stop()
        async_logger = None 