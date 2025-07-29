# Модуль аналітики

> **Модуль для збору, аналізу та візуалізації даних про роботу з Upwork**

---

## Зміст

1. [Огляд модуля](#огляд-модуля)
2. [Архітектура модуля](#-архітектура-модуля)
3. [API Endpoints](#-api-endpoints)
4. [Аспекти безпеки](#аспекти-безпеки)
5. [Інтеграція](#інтеграція)
6. [Тестування](#тестування)
7. [Моніторинг](#моніторинг)

---

## Огляд модуля

### Призначення
- Збір та аналіз даних про активність користувачів
- Відстеження ефективності пропозицій та контрактів
- Аналіз ринкових трендів та конкурентів
- Генерація звітів та дашбордів
- Прогнозування доходів та успішності

### Основні функції
- Збір метрик з Upwork API
- Аналіз продуктивності користувачів
- Створення інтерактивних дашбордів
- Генерація звітів
- Аналіз конкурентів

---

## Архітектура модуля

### Компоненти

```
┌─────────────────────────────────────────────────────────────┐
│                    Analytics Module                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Data Collector│  │ Data Processor│  │ Report Gen │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Dashboard   │  │ Metrics     │  │ Trend Analyzer│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Competitor  │  │ Performance │  │ Forecasting │        │
│  │ Analyzer    │  │ Tracker     │  │ Engine      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**Analytics Platforms:**
- **Google Analytics** для базової аналітики
- **Mixpanel** для детальної аналітики користувачів та user journey

### Взаємодія з іншими модулями

- **Upwork Integration**: Отримання даних для аналізу
- **AI Module**: Надання даних для ML моделей
- **Web Interface**: Відображення дашбордів
- **Database**: Збереження аналітичних даних

---

## API Endpoints

### Метрики користувача

```python
# Отримання основних метрик
GET /analytics/metrics/user/{user_id}
Query params: period (daily, weekly, monthly, yearly)
Response: {
    "period": "monthly",
    "metrics": {
        "proposals_sent": 45,
        "proposals_won": 12,
        "win_rate": 0.27,
        "total_earnings": 8500,
        "average_rate": 85,
        "active_contracts": 3
    },
    "trends": {
        "earnings_growth": 0.15,
        "win_rate_change": 0.05
    }
}

# Детальна статистика пропозицій
GET /analytics/proposals/{user_id}
Query params: status, category, date_from, date_to
Response: {
    "total_proposals": 150,
    "by_status": {
        "pending": 25,
        "interviewing": 8,
        "hired": 12,
        "rejected": 105
    },
    "by_category": {
        "web_development": 45,
        "mobile_development": 30,
        "design": 25
    },
    "timeline": [
        {"date": "2024-01", "count": 12, "won": 3},
        {"date": "2024-02", "count": 15, "won": 4}
    ]
}
```

### Аналіз конкурентів

```python
# Аналіз конкурентів в категорії
POST /analytics/competitors/analyze
{
    "category": "web_development",
    "budget_range": "1000-5000",
    "skills": ["React", "Node.js"]
}
Response: {
    "competitor_count": 1250,
    "average_rate": 75,
    "rate_distribution": {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.2
    },
    "top_competitors": [
        {
            "profile_id": "~0123456789",
            "rate": 95,
            "success_rate": 0.85,
            "reviews_count": 150
        }
    ],
    "market_position": "competitive"
}

# Порівняння з конкурентами
POST /analytics/competitors/compare
{
    "user_id": "user_123",
    "competitor_ids": ["~0123456789", "~0987654321"]
}
Response: {
    "user_metrics": {
        "rate": 85,
        "success_rate": 0.27,
        "response_time": 2.5
    },
    "competitors_metrics": [
        {
            "profile_id": "~0123456789",
            "rate": 95,
            "success_rate": 0.85,
            "response_time": 1.2
        }
    ],
    "recommendations": [
        "Підвищити відгуки клієнтів",
        "Зменшити час відповіді"
    ]
}
```

### Звіти та дашборди

```python
# Генерація звіту
POST /analytics/reports/generate
{
    "report_type": "monthly_performance",
    "user_id": "user_123",
    "period": "2024-01",
    "include_charts": true
}
Response: {
    "report_id": "report_456",
    "download_url": "/reports/report_456.pdf",
    "summary": {
        "total_earnings": 8500,
        "proposals_sent": 45,
        "win_rate": 0.27,
        "growth_rate": 0.15
    },
    "charts": [
        {
            "type": "earnings_timeline",
            "data": [...]
        }
    ]
}

# Отримання дашборду
GET /analytics/dashboard/{user_id}
Response: {
    "widgets": [
        {
            "type": "earnings_chart",
            "title": "Доходи за місяць",
            "data": [...]
        },
        {
            "type": "proposals_status",
            "title": "Статус пропозицій",
            "data": {...}
        },
        {
            "type": "top_skills",
            "title": "Популярні навички",
            "data": [...]
        }
    ],
    "last_updated": "2024-12-19T15:50:00Z"
}
```

---

## Аспекти безпеки

### Захист даних аналітики

```python
class AnalyticsSecurity:
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.access_control = AccessControl()
        
    def validate_data_access(self, user_id: str, requested_user_id: str) -> bool:
        """Перевіряє права доступу до даних"""
# Користувач може бачити тільки свої дані
        if user_id != requested_user_id:
            return False
            
# Перевірка активності акаунту
        if not self.access_control.is_account_active(user_id):
            return False
            
        return True
    
    def anonymize_sensitive_data(self, data: dict) -> dict:
        """Анонімізує чутливі дані"""
        anonymized = data.copy()
        
# Видалення особистих даних
        if 'client_name' in anonymized:
            anonymized['client_name'] = 'Client_' + str(hash(anonymized['client_name']))
            
        if 'project_description' in anonymized:
# Видалення контактної інформації
            anonymized['project_description'] = self.remove_contact_info(
                anonymized['project_description']
            )
            
        return anonymized
    
    def encrypt_analytics_data(self, data: dict) -> str:
        """Шифрує дані аналітики"""
        return self.encryption_manager.encrypt(json.dumps(data))
    
    def decrypt_analytics_data(self, encrypted_data: str) -> dict:
        """Розшифровує дані аналітики"""
        decrypted = self.encryption_manager.decrypt(encrypted_data)
        return json.loads(decrypted)
```

### Rate Limiting для аналітики

```python
class AnalyticsRateLimiter:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.limits = {
            'metrics_query': {'requests': 100, 'window': 3600},
            'report_generation': {'requests': 10, 'window': 3600},
            'competitor_analysis': {'requests': 50, 'window': 3600}
        }
    
    def check_analytics_rate_limit(self, operation: str, user_id: str) -> bool:
        """Перевіряє rate limit для аналітичних операцій"""
        key = f"analytics_rate_limit:{operation}:{user_id}"
        current = self.redis_client.get(key)
        
        if current and int(current) >= self.limits[operation]['requests']:
            return False
        
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.limits[operation]['window'])
        pipe.execute()
        return True
    
    def get_analytics_usage(self, user_id: str) -> dict:
        """Повертає статистику використання аналітики"""
        usage = {}
        for operation in self.limits:
            key = f"analytics_rate_limit:{operation}:{user_id}"
            current = self.redis_client.get(key)
            usage[operation] = {
                'used': int(current) if current else 0,
                'limit': self.limits[operation]['requests']
            }
        return usage
```

---

## Інтеграція

### Інтеграція з Upwork API

```python
class UpworkAnalyticsCollector:
    def __init__(self):
        self.upwork_client = UpworkAPIClient()
        self.db = DatabaseConnection()
        self.security = AnalyticsSecurity()
        
    async def collect_user_metrics(self, user_id: str) -> dict:
        """Збирає метрики користувача"""
        try:
# Отримуємо дані з Upwork API
            profile_data = await self.upwork_client.get_user_profile(user_id)
            proposals_data = await self.upwork_client.get_user_proposals(user_id)
            contracts_data = await self.upwork_client.get_user_contracts(user_id)
            
# Обчислюємо метрики
            metrics = self.calculate_user_metrics(
                profile_data, proposals_data, contracts_data
            )
            
# Зберігаємо в базу даних
            await self.save_user_metrics(user_id, metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics for user {user_id}: {e}")
            raise AnalyticsError("Failed to collect user metrics")
    
    def calculate_user_metrics(self, profile: dict, proposals: dict, contracts: dict) -> dict:
        """Обчислює метрики користувача"""
        total_proposals = len(proposals.get('proposals', []))
        won_proposals = len([p for p in proposals.get('proposals', []) 
                           if p.get('status') == 'hired'])
        
        total_earnings = sum([c.get('total_amount', 0) 
                            for c in contracts.get('contracts', [])])
        
        return {
            'proposals_sent': total_proposals,
            'proposals_won': won_proposals,
            'win_rate': won_proposals / total_proposals if total_proposals > 0 else 0,
            'total_earnings': total_earnings,
            'average_rate': profile.get('hourly_rate', 0),
            'active_contracts': len([c for c in contracts.get('contracts', []) 
                                   if c.get('status') == 'active'])
        }
```

### Інтеграція з базою даних

```python
class AnalyticsDataProcessor:
    def __init__(self):
        self.db = DatabaseConnection()
        self.security = AnalyticsSecurity()
        
    async def save_user_metrics(self, user_id: str, metrics: dict):
        """Зберігає метрики користувача"""
        encrypted_metrics = self.security.encrypt_analytics_data(metrics)
        
        await self.db.execute("""
            INSERT INTO user_analytics (user_id, metrics_data, updated_at)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                metrics_data = $2,
                updated_at = $3
        """, user_id, encrypted_metrics, datetime.utcnow())
    
    async def get_user_metrics(self, user_id: str, period: str = 'monthly') -> dict:
        """Отримує метрики користувача"""
# Перевіряємо права доступу
        if not self.security.validate_data_access(user_id, user_id):
            raise AccessDenied("Access denied to analytics data")
        
        result = await self.db.fetch_one("""
            SELECT metrics_data FROM user_analytics 
            WHERE user_id = $1
        """, user_id)
        
        if not result:
            return {}
        
        metrics_data = self.security.decrypt_analytics_data(result['metrics_data'])
        return self.filter_metrics_by_period(metrics_data, period)
    
    async def generate_trends(self, user_id: str) -> dict:
        """Генерує тренди для користувача"""
        historical_data = await self.get_historical_metrics(user_id)
        
        if len(historical_data) < 2:
            return {}
        
# Обчислюємо тренди
        current = historical_data[-1]
        previous = historical_data[-2]
        
        return {
            'earnings_growth': (current['total_earnings'] - previous['total_earnings']) / previous['total_earnings'],
            'win_rate_change': current['win_rate'] - previous['win_rate'],
            'proposals_growth': (current['proposals_sent'] - previous['proposals_sent']) / previous['proposals_sent']
        }
```

---

## 🧪 Тестування

### Unit Tests

```python
class TestAnalyticsModule:
    def test_data_anonymization(self):
        """Тест анонімізації даних"""
        security = AnalyticsSecurity()
        
        test_data = {
            'client_name': 'John Smith',
            'project_description': 'Contact me at john@email.com',
            'earnings': 1000
        }
        
        anonymized = security.anonymize_sensitive_data(test_data)
        
        assert 'John Smith' not in str(anonymized)
        assert 'john@email.com' not in str(anonymized)
        assert anonymized['earnings'] == 1000
    
    def test_access_validation(self):
        """Тест валідації доступу"""
        security = AnalyticsSecurity()
        
# Валідний доступ
        assert security.validate_data_access('user_123', 'user_123')
        
# Невалідний доступ
        assert not security.validate_data_access('user_123', 'user_456')
    
    def test_rate_limiting(self):
        """Тест rate limiting для аналітики"""
        rate_limiter = AnalyticsRateLimiter()
        user_id = "test_user"
        
# Перші запити повинні пройти
        assert rate_limiter.check_analytics_rate_limit('metrics_query', user_id)
        
# Після перевищення ліміту
        for _ in range(100):
            rate_limiter.check_analytics_rate_limit('metrics_query', user_id)
        
        assert not rate_limiter.check_analytics_rate_limit('metrics_query', user_id)
```

### Integration Tests

```python
class TestAnalyticsIntegration:
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Тест збору метрик"""
        collector = UpworkAnalyticsCollector()
        user_id = "test_user"
        
        metrics = await collector.collect_user_metrics(user_id)
        
        assert 'proposals_sent' in metrics
        assert 'win_rate' in metrics
        assert 'total_earnings' in metrics
        assert 0 <= metrics['win_rate'] <= 1
    
    @pytest.mark.asyncio
    async def test_trends_generation(self):
        """Тест генерації трендів"""
        processor = AnalyticsDataProcessor()
        user_id = "test_user"
        
        trends = await processor.generate_trends(user_id)
        
        if trends:
            assert 'earnings_growth' in trends
            assert 'win_rate_change' in trends
```

---

## Моніторинг

### Метрики аналітики

```python
class AnalyticsMetrics:
    def __init__(self):
        self.prometheus_client = PrometheusClient()
        
    def record_metrics_query(self, user_id: str, query_type: str, duration: float):
        """Записує метрику запиту"""
        self.prometheus_client.counter(
            'analytics_queries_total',
            labels={'user_id': user_id, 'query_type': query_type}
        ).inc()
        
        self.prometheus_client.histogram(
            'analytics_query_duration_seconds',
            labels={'query_type': query_type}
        ).observe(duration)
    
    def record_report_generation(self, report_type: str, success: bool):
        """Записує метрику генерації звіту"""
        self.prometheus_client.counter(
            'analytics_reports_generated_total',
            labels={'report_type': report_type, 'success': str(success)}
        ).inc()
    
    def record_data_collection(self, data_source: str, records_count: int):
        """Записує метрику збору даних"""
        self.prometheus_client.counter(
            'analytics_data_collected_total',
            labels={'data_source': data_source}
        ).inc(records_count)
```

### Логування аналітики

```python
class AnalyticsLogger:
    def __init__(self):
        self.logger = logging.getLogger('analytics_module')
        
    def log_metrics_query(self, user_id: str, query_type: str, duration: float):
        """Логує запит метрик"""
        self.logger.info(
            f"Metrics query - User: {user_id}, Type: {query_type}, "
            f"Duration: {duration:.2f}s"
        )
        
    def log_report_generation(self, user_id: str, report_type: str, success: bool):
        """Логує генерацію звіту"""
        self.logger.info(
            f"Report generation - User: {user_id}, Type: {report_type}, "
            f"Success: {success}"
        )
        
    def log_data_collection(self, data_source: str, records_count: int):
        """Логує збір даних"""
        self.logger.info(
            f"Data collection - Source: {data_source}, Records: {records_count}"
        )
```

---

## Чек-лист реалізації

### Безпека
- [ ] Валідація прав доступу
- [ ] Анонімізація чутливих даних
- [ ] Шифрування аналітичних даних
- [ ] Rate limiting для аналітики
- [ ] Логування всіх операцій

### Функціональність
- [ ] Збір метрик з Upwork API
- [ ] Обчислення статистики користувачів
- [ ] Аналіз конкурентів
- [ ] Генерація звітів
- [ ] Створення дашбордів

### Тестування
- [ ] Unit тести для анонімізації
- [ ] Unit тести для валідації доступу
- [ ] Unit тести для rate limiting
- [ ] Integration тести для збору метрик
- [ ] Integration тести для генерації трендів

### Моніторинг
- [ ] Метрики запитів аналітики
- [ ] Метрики генерації звітів
- [ ] Метрики збору даних
- [ ] Логування запитів метрик
- [ ] Логування генерації звітів

---

**Версія**: 1.0.0 