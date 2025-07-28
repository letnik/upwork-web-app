"""
Система Telegram сповіщень
"""

import requests
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from loguru import logger

from .logger import structured_logger


@dataclass
class TelegramConfig:
    """Конфігурація Telegram бота"""
    bot_token: str
    chat_ids: List[str]
    parse_mode: str = "HTML"  # HTML або Markdown


class TelegramNotifier:
    """Система Telegram сповіщень"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.base_url = f"https://api.telegram.org/bot{config.bot_token}"
    
    def send_message(self, 
                    text: str,
                    chat_id: Optional[str] = None,
                    parse_mode: Optional[str] = None) -> bool:
        """Відправка повідомлення"""
        try:
            parse_mode = parse_mode or self.config.parse_mode
            chat_ids = [chat_id] if chat_id else self.config.chat_ids
            
            for chat_id in chat_ids:
                payload = {
                    'chat_id': chat_id,
                    'text': text,
                    'parse_mode': parse_mode
                }
                
                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram повідомлення відправлено в чат {chat_id}")
                    
                    structured_logger.log_security_event(
                        event_type="telegram_sent",
                        message=f"Telegram повідомлення відправлено",
                        data={
                            "chat_id": chat_id,
                            "text_length": len(text)
                        }
                    )
                else:
                    logger.error(f"Помилка відправки Telegram: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Помилка відправки Telegram повідомлення: {e}")
            
            structured_logger.log_security_event(
                event_type="telegram_error",
                message=f"Помилка відправки Telegram: {e}",
                data={"error": str(e)}
            )
            
            return False
    
    def send_parsing_start_notification(self, 
                                       session_id: str,
                                       search_query: str,
                                       max_pages: int) -> bool:
        """Сповіщення про початок парсингу"""
        text = f"""
🚀 <b>Початок парсингу Upwork</b>

📋 <b>Деталі:</b>
• Сесія: <code>{session_id}</code>
• Пошуковий запит: <code>{search_query}</code>
• Максимум сторінок: <code>{max_pages}</code>
• Час початку: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</code>

Система буде надсилати оновлення про прогрес парсингу.
        """
        
        return self.send_message(text)
    
    def send_parsing_progress_notification(self,
                                          session_id: str,
                                          current_page: int,
                                          total_pages: int,
                                          jobs_found: int,
                                          jobs_parsed: int,
                                          errors_count: int) -> bool:
        """Сповіщення про прогрес парсингу"""
        progress_percent = (current_page / total_pages) * 100
        
        # Емодзі для прогрес-бару
        progress_bar = "█" * int(progress_percent / 10) + "░" * (10 - int(progress_percent / 10))
        
        text = f"""
📊 <b>Прогрес парсингу Upwork</b>

{progress_bar} <code>{progress_percent:.1f}%</code>

📈 <b>Статистика:</b>
• Сесія: <code>{session_id}</code>
• Сторінка: <code>{current_page}/{total_pages}</code>
• Знайдено робіт: <code>{jobs_found}</code>
• Збережено робіт: <code>{jobs_parsed}</code>
• Помилок: <code>{errors_count}</code>
• Час: <code>{datetime.utcnow().strftime('%H:%M:%S')} UTC</code>
        """
        
        return self.send_message(text)
    
    def send_parsing_complete_notification(self,
                                          session_id: str,
                                          total_jobs_found: int,
                                          jobs_parsed: int,
                                          errors_count: int,
                                          duration_minutes: float) -> bool:
        """Сповіщення про завершення парсингу"""
        text = f"""
✅ <b>Парсинг завершено успішно!</b>

🎉 <b>Результати:</b>
• Сесія: <code>{session_id}</code>
• Знайдено робіт: <code>{total_jobs_found}</code>
• Збережено робіт: <code>{jobs_parsed}</code>
• Помилок: <code>{errors_count}</code>
• Тривалість: <code>{duration_minutes:.1f} хв</code>
• Час завершення: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</code>

Дані збережено в базі даних та готові для експорту.
        """
        
        return self.send_message(text)
    
    def send_error_notification(self,
                               session_id: str,
                               error_message: str,
                               current_page: int = None) -> bool:
        """Сповіщення про помилку"""
        text = f"""
❌ <b>Помилка парсингу</b>

🚨 <b>Деталі помилки:</b>
• Сесія: <code>{session_id}</code>
• Помилка: <code>{error_message}</code>
• Сторінка: <code>{current_page if current_page else 'Невідомо'}</code>
• Час: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</code>

Перевірте логи для детальної інформації.
        """
        
        return self.send_message(text)
    
    def send_system_status_notification(self,
                                       status: str,
                                       details: Dict[str, Any]) -> bool:
        """Сповіщення про статус системи"""
        text = f"""
🔧 <b>Статус системи</b>

📊 <b>Інформація:</b>
• Статус: <code>{status}</code>
• Час: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</code>
        """
        
        # Додаємо деталі
        for key, value in details.items():
            text += f"• {key}: <code>{value}</code>\n"
        
        return self.send_message(text)
    
    def send_proxy_status_notification(self,
                                      active_proxies: int,
                                      total_proxies: int,
                                      failed_proxies: int) -> bool:
        """Сповіщення про статус проксі"""
        success_rate = ((active_proxies - failed_proxies) / active_proxies * 100) if active_proxies > 0 else 0
        
        text = f"""
🌐 <b>Статус проксі</b>

📈 <b>Статистика:</b>
• Активних проксі: <code>{active_proxies}</code>
• Всього проксі: <code>{total_proxies}</code>
• Невдалих проксі: <code>{failed_proxies}</code>
• Успішність: <code>{success_rate:.1f}%</code>
• Час: <code>{datetime.utcnow().strftime('%H:%M:%S')} UTC</code>
        """
        
        return self.send_message(text)
    
    def test_connection(self) -> bool:
        """Тестування підключення до Telegram"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Telegram бот підключений: @{bot_info['result']['username']}")
                
                # Відправляємо тестове повідомлення
                test_text = f"""
🤖 <b>Тест підключення</b>

✅ Telegram бот успішно підключений!
• Бот: <code>@{bot_info['result']['username']}</code>
• Час: <code>{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</code>

Система готова до роботи.
                """
                
                return self.send_message(test_text)
            else:
                logger.error(f"Помилка підключення до Telegram: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Помилка тестування Telegram: {e}")
            return False


# Глобальний екземпляр (потрібно буде ініціалізувати з конфігурацією)
telegram_notifier = None 