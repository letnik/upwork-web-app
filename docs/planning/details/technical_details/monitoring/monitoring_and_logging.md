# Моніторинг та логування

> **Система моніторингу, логування та сповіщень для Upwork Web App**

---

## Зміст

1. [Призначення](#-призначення)
2. [Архітектура моніторингу](#-архітектура-моніторингу)
3. [Метрики та показники](#метрики-та-показники)
4. [Логування](#логування)
5. [Система сповіщень](#система-сповіщень)
6. [Дашборди](#дашборди)
7. [Аналітика та звіти](#аналітика-та-звіти)

---

## Призначення

Система моніторингу забезпечує:
- Відстеження продуктивності системи
- Виявлення аномалій та збоїв
- Збір та аналіз логів
- Автоматичні сповіщення
- Аналітика використання

---

## Архітектура моніторингу

### Компоненти системи

```python
# src/monitoring/architecture.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MonitoringComponent:
    name: str
    type: str  # 'metric', 'log', 'alert'
    endpoint: str
    collection_interval: int  # seconds
    retention_period: int  # days

class MonitoringArchitecture:
    def __init__(self):
        self.components = {
            "application_metrics": MonitoringComponent(
                name="Application Metrics",
                type="metric",
                endpoint="/metrics",
                collection_interval=30,
                retention_period=90
            ),
            "security_logs": MonitoringComponent(
                name="Security Logs",
                type="log",
                endpoint="/logs/security",
                collection_interval=5,
                retention_period=365
            ),
            "performance_metrics": MonitoringComponent(
                name="Performance Metrics",
                type="metric",
                endpoint="/metrics/performance",
                collection_interval=60,
                retention_period=30
            )
        }
```

### Стек технологій

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200

volumes:
  prometheus_data:
  elasticsearch_data:
```
      - grafana_data:/var/lib/grafana

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
```

---

## Метрики та показники

### Application Metrics

```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

class ApplicationMetrics:
    def __init__(self):
# HTTP метрики
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
# Бізнес метрики
        self.upwork_api_calls = Counter(
            'upwork_api_calls_total',
            'Total Upwork API calls',
            ['endpoint', 'status']
        )
        
        self.proposals_created = Counter(
            'proposals_created_total',
            'Total proposals created',
            ['user_id', 'status']
        )
        
# Системні метрики
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        
        self.database_connections = Gauge(
            'database_connections',
            'Number of active database connections'
        )
    
    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Відстеження HTTP запиту"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def track_api_call(self, endpoint: str, status: str):
        """Відстеження виклику Upwork API"""
        self.upwork_api_calls.labels(endpoint=endpoint, status=status).inc()
    
    def track_proposal_creation(self, user_id: str, status: str):
        """Відстеження створення пропозиції"""
        self.proposals_created.labels(user_id=user_id, status=status).inc()
```

### Performance Metrics

```python
# src/monitoring/performance.py
import psutil
import asyncio
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Збір системних метрик"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict()
        }
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Збір метрик додатку"""
        return {
            "active_connections": len(asyncio.all_tasks()),
            "memory_usage": psutil.Process().memory_info().rss,
            "thread_count": psutil.Process().num_threads()
        }
    
    async def collect_database_metrics(self) -> Dict[str, Any]:
        """Збір метрик бази даних"""
# Підключення до PostgreSQL для збору метрик
        return {
            "active_connections": 0,  # Запит до БД
            "slow_queries": 0,        # Запит до БД
            "cache_hit_ratio": 0.0    # Запит до БД
        }
```

---

## Логування

### Структура логів

```python
# src/monitoring/logging.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """Налаштування логування"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
# File handler
        file_handler = logging.FileHandler('logs/application.log')
        file_handler.setFormatter(formatter)
        
# Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type: str, data: Dict[str, Any], level: str = "INFO"):
        """Логування події"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "level": level
        }
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
    
    def log_security_event(self, event_type: str, user_id: str, ip_address: str, details: Dict[str, Any]):
        """Логування подій безпеки"""
        security_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "severity": self._determine_severity(event_type)
        }
        
# Запис у окремий файл для безпеки
        with open('logs/security.log', 'a') as f:
            f.write(json.dumps(security_log) + '\n')
    
    def _determine_severity(self, event_type: str) -> str:
        """Визначення серйозності події"""
        high_severity = ['failed_login', 'suspicious_activity', 'data_breach']
        medium_severity = ['password_change', 'permission_change']
        
        if event_type in high_severity:
            return "HIGH"
        elif event_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"
```

### Log Aggregation

```python
# src/monitoring/log_aggregator.py
import asyncio
from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any

class LogAggregator:
    def __init__(self):
        self.es = AsyncElasticsearch(['http://localhost:9200'])
        self.index_name = "upwork-app-logs"
    
    async def index_log(self, log_entry: Dict[str, Any]):
        """Індексація логу в Elasticsearch"""
        try:
            await self.es.index(
                index=self.index_name,
                document=log_entry
            )
        except Exception as e:
            print(f"Error indexing log: {e}")
    
    async def search_logs(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Пошук логів"""
        try:
            response = await self.es.search(
                index=self.index_name,
                body=query
            )
            return response['hits']['hits']
        except Exception as e:
            print(f"Error searching logs: {e}")
            return []
    
    async def create_alert(self, condition: Dict[str, Any]):
        """Створення алерту на основі логів"""
# Логіка створення алертів
        pass
```

---

## Система сповіщень

### Alert Rules

```yaml
# monitoring/alert_rules.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionHigh
        expr: database_connections > 80
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connections: {{ $value }}"

      - alert: SecurityBreach
        expr: increase(security_events_total{event_type="failed_login"}[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Potential security breach"
          description: "Multiple failed login attempts detected"
```

### Notification Channels

```python
# src/monitoring/notifications.py
import smtplib
import requests
from email.mime.text import MIMEText
from typing import Dict, Any

class NotificationManager:
    def __init__(self):
        self.email_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "alerts@upwork-app.com",
            "sender_password": "app_password"
        }
        
        self.slack_webhook = "https://hooks.slack.com/services/YOUR_WEBHOOK"
        self.telegram_bot_token = "YOUR_BOT_TOKEN"
        self.telegram_chat_id = "YOUR_CHAT_ID"
    
    def send_email_alert(self, alert_data: Dict[str, Any]):
        """Відправка email сповіщення"""
        subject = f"Alert: {alert_data['summary']}"
        body = f"""
        Alert Details:
        - Summary: {alert_data['summary']}
        - Description: {alert_data['description']}
        - Severity: {alert_data['severity']}
        - Timestamp: {alert_data['timestamp']}
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_config['sender_email']
        msg['To'] = "team@upwork-app.com"
        
        try:
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def send_slack_alert(self, alert_data: Dict[str, Any]):
        """Відправка Slack сповіщення"""
        message = {
            "text": f"🚨 Alert: {alert_data['summary']}",
            "attachments": [{
                "color": "danger" if alert_data['severity'] == 'critical' else "warning",
                "fields": [
                    {"title": "Description", "value": alert_data['description']},
                    {"title": "Severity", "value": alert_data['severity']},
                    {"title": "Timestamp", "value": alert_data['timestamp']}
                ]
            }]
        }
        
        try:
            requests.post(self.slack_webhook, json=message)
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
    
    def send_telegram_alert(self, alert_data: Dict[str, Any]):
        """Відправка Telegram сповіщення"""
        message = f"""
🚨 Alert: {alert_data['summary']}

Description: {alert_data['description']}
Severity: {alert_data['severity']}
Timestamp: {alert_data['timestamp']}
        """
        
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            requests.post(url, data=data)
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")
```

---

## Дашборди

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Upwork App Monitoring",
    "panels": [
      {
        "title": "HTTP Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "active_users"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "database_connections"
          }
        ]
      }
    ]
  }
}
```

---

## Аналітика та звіти

### Report Generator

```python
# src/monitoring/reports.py
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd

class ReportGenerator:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
    
    async def generate_daily_report(self) -> Dict[str, Any]:
        """Генерація щоденного звіту"""
        yesterday = datetime.now() - timedelta(days=1)
        
        report = {
            "date": yesterday.strftime("%Y-%m-%d"),
            "summary": await self._get_daily_summary(yesterday),
            "performance": await self._get_performance_metrics(yesterday),
            "security": await self._get_security_events(yesterday),
            "business": await self._get_business_metrics(yesterday)
        }
        
        return report
    
    async def _get_daily_summary(self, date: datetime) -> Dict[str, Any]:
        """Отримання щоденного підсумку"""
        return {
            "total_requests": 0,  # Запит до метрик
            "unique_users": 0,     # Запит до метрик
            "avg_response_time": 0.0,  # Запит до метрик
            "error_rate": 0.0      # Запит до метрик
        }
    
    async def _get_performance_metrics(self, date: datetime) -> Dict[str, Any]:
        """Отримання метрик продуктивності"""
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_io": 0.0
        }
    
    async def _get_security_events(self, date: datetime) -> Dict[str, Any]:
        """Отримання подій безпеки"""
        return {
            "failed_logins": 0,
            "suspicious_activities": 0,
            "security_alerts": 0
        }
    
    async def _get_business_metrics(self, date: datetime) -> Dict[str, Any]:
        """Отримання бізнес метрик"""
        return {
            "proposals_created": 0,
            "api_calls": 0,
            "active_users": 0
        }
```

---

## Конфігурація

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'upwork-app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### Alertmanager Configuration

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@upwork-app.com'
  smtp_auth_username: 'alerts@upwork-app.com'
  smtp_auth_password: 'app_password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'team-email'

receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@upwork-app.com'
        send_resolved: true

  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR_WEBHOOK'
        channel: '#alerts'
        send_resolved: true
```

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:50 