# План Performance тестів

> **Детальний план тестів продуктивності для всіх компонентів системи**

---

## Зміст

1. [Загальні принципи](#загальні-принципи)
2. [Типи тестів продуктивності](#типи-тестів-продуктивності)
3. [Інструменти тестування](#інструменти-тестування)
4. [Сценарії тестування](#сценарії-тестування)
5. [Метрики продуктивності](#метрики-продуктивності)
6. [Налаштування тестового середовища](#налаштування-тестового-середовища)
7. [Аналіз результатів](#аналіз-результатів)
8. [Автоматизація тестування](#автоматизація-тестування)

---

## Загальні принципи

---

## Типи тестів продуктивності

### Load Testing
- **Призначення**: Перевірка поведінки системи під нормальним навантаженням
- **Тривалість**: 15-30 хвилин
- **Користувачі**: 100-1000 одночасних користувачів

### Stress Testing
- **Призначення**: Визначення меж продуктивності
- **Тривалість**: 30-60 хвилин
- **Користувачі**: 1000-5000 одночасних користувачів

### Spike Testing
- **Призначення**: Перевірка реакції на різкі зміни навантаження
- **Тривалість**: 5-15 хвилин
- **Користувачі**: Різке збільшення з 100 до 2000 користувачів

### Endurance Testing
- **Призначення**: Перевірка стабільності протягом тривалого часу
- **Тривалість**: 2-8 годин
- **Користувачі**: 500-1000 одночасних користувачів

---

## Інструменти тестування

### JMeter Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Upwork App Performance Test">
      <elementProp name="TestPlan.arguments" elementType="Arguments">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="API Load Test">
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">10</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">100</stringProp>
        <stringProp name="ThreadGroup.ramp_time">30</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Login Request">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="username" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">test_user</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
              <elementProp name="password" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">test_password</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain">localhost</stringProp>
          <stringProp name="HTTPSampler.port">8000</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.path">/auth/login</stringProp>
          <stringProp name="HTTPSampler.method">POST</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
        </HTTPSamplerProxy>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

### Locust Configuration

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import json

class UpworkAppUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Логін користувача"""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post("/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_dashboard(self):
        """Отримання дашборду"""
        self.client.get("/api/dashboard")
    
    @task(2)
    def get_proposals(self):
        """Отримання пропозицій"""
        self.client.get("/api/proposals")
    
    @task(1)
    def create_proposal(self):
        """Створення пропозиції"""
        proposal_data = {
            "job_id": "test_job_123",
            "cover_letter": "Test proposal content",
            "bid_amount": 100
        }
        self.client.post("/api/proposals", json=proposal_data)
    
    @task(1)
    def sync_upwork_data(self):
        """Синхронізація з Upwork"""
        self.client.post("/api/upwork/sync")
```

---

## Сценарії тестування

### Сценарій 1: Авторизація та основний функціонал

```python
# tests/performance/scenarios/auth_scenario.py
import asyncio
import aiohttp
import time
from typing import List, Dict

class AuthPerformanceTest:
    def __init__(self, base_url: str, num_users: int):
        self.base_url = base_url
        self.num_users = num_users
        self.results = []
    
    async def run_login_test(self):
        """Тест продуктивності авторизації"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.num_users):
                task = self._login_user(session, f"user_{i}")
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            return {
                "total_time": end_time - start_time,
                "avg_response_time": sum(results) / len(results),
                "success_rate": len([r for r in results if not isinstance(r, Exception)]) / len(results)
            }
    
    async def _login_user(self, session: aiohttp.ClientSession, username: str) -> float:
        """Логін одного користувача"""
        start_time = time.time()
        
        login_data = {
            "username": username,
            "password": "test_password"
        }
        
        try:
            async with session.post(f"{self.base_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    return time.time() - start_time
                else:
                    raise Exception(f"Login failed: {response.status}")
        except Exception as e:
            raise e
```

### Сценарій 2: API інтеграція з Upwork

```python
# tests/performance/scenarios/upwork_api_scenario.py
class UpworkAPIPerformanceTest:
    def __init__(self, base_url: str, num_requests: int):
        self.base_url = base_url
        self.num_requests = num_requests
    
    async def run_api_test(self):
        """Тест продуктивності Upwork API"""
        endpoints = [
            "/api/upwork/jobs",
            "/api/upwork/proposals",
            "/api/upwork/contracts",
            "/api/upwork/payments"
        ]
        
        results = {}
        for endpoint in endpoints:
            endpoint_results = await self._test_endpoint(endpoint)
            results[endpoint] = endpoint_results
        
        return results
    
    async def _test_endpoint(self, endpoint: str) -> Dict:
        """Тест конкретного endpoint"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.num_requests):
                task = self._make_request(session, endpoint)
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            return {
                "endpoint": endpoint,
                "total_requests": self.num_requests,
                "total_time": end_time - start_time,
                "avg_response_time": sum(results) / len(results),
                "success_rate": len([r for r in results if not isinstance(r, Exception)]) / len(results)
            }
    
    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str) -> float:
        """Виконання одного запиту"""
        start_time = time.time()
        
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                if response.status == 200:
                    return time.time() - start_time
                else:
                    raise Exception(f"Request failed: {response.status}")
        except Exception as e:
            raise e
```

---

## Метрики продуктивності

### Ключові показники

```python
# tests/performance/metrics.py
from dataclasses import dataclass
from typing import List, Dict
import statistics

@dataclass
class PerformanceMetrics:
    response_time_avg: float
    response_time_95th: float
    response_time_99th: float
    throughput: float  # requests per second
    error_rate: float
    concurrent_users: int
    cpu_usage: float
    memory_usage: float
    database_connections: int

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = []
    
    def add_metrics(self, metrics: PerformanceMetrics):
        """Додавання метрик"""
        self.metrics.append(metrics)
    
    def analyze_results(self) -> Dict:
        """Аналіз результатів тестування"""
        if not self.metrics:
            return {}
        
        return {
            "avg_response_time": statistics.mean([m.response_time_avg for m in self.metrics]),
            "max_response_time": max([m.response_time_99th for m in self.metrics]),
            "avg_throughput": statistics.mean([m.throughput for m in self.metrics]),
            "avg_error_rate": statistics.mean([m.error_rate for m in self.metrics]),
            "max_concurrent_users": max([m.concurrent_users for m in self.metrics]),
            "avg_cpu_usage": statistics.mean([m.cpu_usage for m in self.metrics]),
            "avg_memory_usage": statistics.mean([m.memory_usage for m in self.metrics])
        }
    
    def check_sla_compliance(self, sla_requirements: Dict) -> Dict:
        """Перевірка відповідності SLA"""
        analysis = self.analyze_results()
        
        compliance = {}
        for metric, requirement in sla_requirements.items():
            if metric in analysis:
                compliance[metric] = analysis[metric] <= requirement
        
        return compliance
```

### SLA Вимоги

```yaml
# tests/performance/sla_requirements.yml
performance_sla:
  response_time_avg: 200  # milliseconds
  response_time_95th: 500  # milliseconds
  response_time_99th: 1000  # milliseconds
  throughput_min: 100  # requests per second
  error_rate_max: 0.01  # 1%
  cpu_usage_max: 80  # percent
  memory_usage_max: 85  # percent
  database_connections_max: 100

api_sla:
  upwork_api_response_time: 5000  # milliseconds
  upwork_api_success_rate: 0.95  # 95%
  sync_operation_timeout: 30000  # milliseconds

security_sla:
  authentication_time: 1000  # milliseconds
  encryption_overhead: 50  # milliseconds
  session_timeout: 1800  # seconds
```

---

## Налаштування тестового середовища

### Docker Compose для тестування

```yaml
# docker-compose.performance.yml
version: '3.8'

services:
  performance-test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: performance_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_performance_data:/var/lib/postgresql/data

  performance-test-redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  jmeter:
    image: justb4/jmeter:latest
    ports:
      - "8080:8080"
    volumes:
      - ./tests/performance/jmeter:/opt/apache-jmeter/bin
      - ./test-results:/opt/apache-jmeter/bin/results

  locust:
    image: locustio/locust:latest
    ports:
      - "8089:8089"
    volumes:
      - ./tests/performance:/mnt/locust
    command: -f /mnt/locust/locustfile.py --host=http://app:8000

  monitoring:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_performance_data:/var/lib/grafana

volumes:
  postgres_performance_data:
  grafana_performance_data:
```

### Скрипт запуску тестів

```bash
#!/bin/bash
# scripts/run_performance_tests.sh

echo "🚀 Starting performance tests..."

# Запуск тестового середовища
docker-compose -f docker-compose.performance.yml up -d

# Очікування готовності сервісів
sleep 30

# Запуск JMeter тестів
echo "Running JMeter tests..."
docker run --rm -v $(pwd)/tests/performance/jmeter:/opt/apache-jmeter/bin \
  -v $(pwd)/test-results:/opt/apache-jmeter/bin/results \
  justb4/jmeter:latest -n -t /opt/apache-jmeter/bin/upwork_app_test.jmx \
  -l /opt/apache-jmeter/bin/results/jmeter_results.jtl

# Запуск Locust тестів
echo "Running Locust tests..."
docker run --rm -v $(pwd)/tests/performance:/mnt/locust \
  locustio/locust:latest -f /mnt/locust/locustfile.py \
  --host=http://localhost:8000 --users 100 --spawn-rate 10 \
  --run-time 10m --headless

# Аналіз результатів
echo "Analyzing results..."
python scripts/analyze_performance_results.py

# Генерація звіту
echo "Generating report..."
python scripts/generate_performance_report.py

echo "✅ Performance tests completed"
```

---

## Аналіз результатів

### Report Generator

```python
# scripts/generate_performance_report.py
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

class PerformanceReportGenerator:
    def __init__(self):
        self.results = {}
    
    def load_results(self, file_path: str):
        """Завантаження результатів тестування"""
        with open(file_path, 'r') as f:
            self.results = json.load(f)
    
    def generate_summary_report(self) -> Dict:
        """Генерація зведеного звіту"""
        return {
            "test_date": datetime.now().isoformat(),
            "total_requests": self.results.get("total_requests", 0),
            "avg_response_time": self.results.get("avg_response_time", 0),
            "throughput": self.results.get("throughput", 0),
            "error_rate": self.results.get("error_rate", 0),
            "sla_compliance": self.results.get("sla_compliance", {})
        }
    
    def create_response_time_chart(self, output_path: str):
        """Створення графіку часу відповіді"""
        response_times = self.results.get("response_times", [])
        
        plt.figure(figsize=(12, 6))
        plt.plot(response_times)
        plt.title("Response Time Over Time")
        plt.xlabel("Request Number")
        plt.ylabel("Response Time (ms)")
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()
    
    def create_throughput_chart(self, output_path: str):
        """Створення графіку пропускної здатності"""
        throughput_data = self.results.get("throughput_data", [])
        
        plt.figure(figsize=(12, 6))
        plt.plot(throughput_data)
        plt.title("Throughput Over Time")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Requests per Second")
        plt.grid(True)
        plt.savefig(output_path)
        plt.close()
    
    def generate_html_report(self, output_path: str):
        """Генерація HTML звіту"""
        summary = self.generate_summary_report()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
                .sla-compliant {{ color: green; }}
                .sla-violation {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Performance Test Report</h1>
            <p><strong>Test Date:</strong> {summary['test_date']}</p>
            
            <div class="metric">
                <h3>Summary Metrics</h3>
                <p><strong>Total Requests:</strong> {summary['total_requests']}</p>
                <p><strong>Average Response Time:</strong> {summary['avg_response_time']:.2f} ms</p>
                <p><strong>Throughput:</strong> {summary['throughput']:.2f} req/s</p>
                <p><strong>Error Rate:</strong> {summary['error_rate']:.2%}</p>
            </div>
            
            <div class="metric">
                <h3>SLA Compliance</h3>
                {self._generate_sla_html(summary['sla_compliance'])}
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _generate_sla_html(self, sla_compliance: Dict) -> str:
        """Генерація HTML для SLA відповідності"""
        html = ""
        for metric, compliant in sla_compliance.items():
            status_class = "sla-compliant" if compliant else "sla-violation"
            status_text = "✅ Compliant" if compliant else "❌ Violation"
            html += f'<p class="{status_class}"><strong>{metric}:</strong> {status_text}</p>'
        return html
```

---

## Автоматизація тестування

### GitHub Actions Workflow

```yaml
# .github/workflows/performance-tests.yml
name: Performance Tests

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * 0'  # Щонеділі о 2:00

jobs:
  performance-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust aiohttp matplotlib pandas
      
      - name: Start test environment
        run: |
          docker-compose -f docker-compose.performance.yml up -d
          sleep 60
      
      - name: Run performance tests
        run: |
          python tests/performance/run_tests.py
      
      - name: Generate report
        run: |
          python scripts/generate_performance_report.py
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-test-results
          path: test-results/
      
      - name: Send notification
        if: always()
        run: |
          python scripts/send_performance_notification.py
```

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:55 