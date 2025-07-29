# CI/CD Pipeline

> **Детальний опис процесів безперервної інтеграції та розгортання**

---

## Зміст

1. [Призначення](#призначення)
2. [Архітектура Pipeline](#архітектура-pipeline)
3. [Конфігурація](#конфігурація)
4. [Процес розгортання](#процес-розгортання)
5. [Моніторинг Pipeline](#моніторинг-pipeline)
6. [Безпека Pipeline](#безпека-pipeline)
7. [Чек-лист розгортання](#чек-лист-розгортання)
8. [Rollback Procedure](#rollback-procedure)

---

## Призначення

CI/CD pipeline забезпечує:
- Автоматичне тестування коду
- Безпечне розгортання
- Моніторинг якості коду
- Швидке відновлення після збоїв

---

## Архітектура Pipeline

### Етапи виконання

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
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
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run K6 load tests
        uses: grafana/k6-action@v0.3.0
        with:
          filename: load-tests/load-test.js

  build:
    needs: [test, security-scan, load-test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t upwork-app:${{ github.sha }} .
      - name: Push to Docker Hub (development)
        if: github.ref == 'refs/heads/develop'
        run: |
          docker push docker.io/upwork-app:${{ github.sha }}
      - name: Push to AWS ECR (production)
        if: github.ref == 'refs/heads/main'
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
          docker tag upwork-app:${{ github.sha }} ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/upwork-app:${{ github.sha }}
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/upwork-app:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: |
          kubectl set image deployment/upwork-app-staging upwork-app=upwork-app:${{ github.sha }}

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/upwork-app-prod upwork-app=upwork-app:${{ github.sha }}
```

---

## Конфігурація

### GitHub Actions

```yaml
# .github/workflows/security.yml
name: Security Checks

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # Щодня о 2:00

jobs:
  dependency-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check dependencies
        run: |
          pip install safety
          safety check

  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run linting
        run: |
          pip install flake8 black isort
          flake8 src/
          black --check src/
          isort --check-only src/
```

### Docker Compose для CI

```yaml
# docker-compose.ci.yml
version: '3.8'

services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5432:5432"

  test-redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  test-app:
    build: .
    environment:
      DATABASE_URL: postgresql://test_user:test_password@test-db:5432/test_db
      REDIS_URL: redis://test-redis:6379
    depends_on:
      - test-db
      - test-redis
    command: pytest
```

---

## Процес розгортання

### Staging Environment

```bash
#!/bin/bash
# deploy-staging.sh

echo "🚀 Deploying to staging..."

# Оновлення коду
git pull origin develop

# Встановлення залежностей
pip install -r requirements.txt

# Запуск міграцій
alembic upgrade head

# Запуск тестів
pytest --cov=src

# Збірка Docker image
docker build -t upwork-app:staging .

# Розгортання
kubectl apply -f k8s/staging/

echo "✅ Staging deployment completed"
```

### Production Environment

```bash
#!/bin/bash
# deploy-production.sh

echo "🚀 Deploying to production..."

# Перевірка безпеки
safety check
bandit -r src/

# Blue-green deployment
kubectl apply -f k8s/production-blue/
kubectl rollout status deployment/upwork-app-blue

# Перемикання трафіку
kubectl patch service upwork-app -p '{"spec":{"selector":{"version":"blue"}}}'

# Оновлення green
kubectl apply -f k8s/production-green/
kubectl rollout status deployment/upwork-app-green

# Перемикання на green
kubectl patch service upwork-app -p '{"spec":{"selector":{"version":"green"}}}'

echo "✅ Production deployment completed"
```

---

## Моніторинг Pipeline

### Метрики якості

```python
# scripts/pipeline_metrics.py
import json
import requests
from datetime import datetime

class PipelineMetrics:
    def __init__(self):
        self.metrics = {
            "build_time": 0,
            "test_coverage": 0,
            "security_score": 0,
            "deployment_time": 0
        }
    
    def collect_metrics(self):
        """Збір метрик з pipeline"""
# Збір даних з GitHub Actions API
# Аналіз результатів тестів
# Оцінка безпеки
        pass
    
    def generate_report(self):
        """Генерація звіту"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "status": "success" if self.metrics["security_score"] > 80 else "warning"
        }
        return report
```

### Сповіщення

```python
# scripts/notifications.py
import smtplib
from email.mime.text import MIMEText

class PipelineNotifications:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "ci-cd@upwork-app.com"
    
    def send_deployment_notification(self, environment, status):
        """Відправка сповіщення про розгортання"""
        subject = f"Deployment to {environment}: {status}"
        body = f"""
        Deployment Status: {status}
        Environment: {environment}
        Timestamp: {datetime.now()}
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = "team@upwork-app.com"
        
# Відправка email
        pass
```

---

## Безпека Pipeline

### Секрети та змінні середовища

```yaml
# .github/secrets.yml
DATABASE_URL: ${{ secrets.DATABASE_URL }}
REDIS_URL: ${{ secrets.REDIS_URL }}
UPWORK_CLIENT_ID: ${{ secrets.UPWORK_CLIENT_ID }}
UPWORK_CLIENT_SECRET: ${{ secrets.UPWORK_CLIENT_SECRET }}
JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
ENCRYPTION_KEY: ${{ secrets.ENCRYPTION_KEY }}
```

### Сканування безпеки

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main, develop]

jobs:
  snyk-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  bandit-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Bandit security scan
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
```

---

## Чек-лист розгортання

### Перед розгортанням

- [ ] Всі тести пройшли успішно
- [ ] Сканування безпеки не виявило вразливостей
- [ ] Покриття коду тестами > 80%
- [ ] Міграції бази даних готові
- [ ] Конфігурація середовища оновлена
- [ ] Резервна копія створена

### Під час розгортання

- [ ] Blue-green deployment активований
- [ ] Health checks пройшли успішно
- [ ] Моніторинг показує нормальну роботу
- [ ] Логи не містять критичних помилок

### Після розгортання

- [ ] Функціональні тести пройшли
- [ ] Продуктивність в межах норми
- [ ] Сповіщення відправлено команді
- [ ] Документація оновлена

---

## Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

ENVIRONMENT=$1
VERSION=$2

echo "🔄 Rolling back to version $VERSION in $ENVIRONMENT..."

if [ "$ENVIRONMENT" = "production" ]; then
# Відновлення попередньої версії
    kubectl rollout undo deployment/upwork-app-prod --to-revision=$VERSION
    
# Перевірка статусу
    kubectl rollout status deployment/upwork-app-prod
    
    echo "✅ Rollback completed"
else
    echo "❌ Invalid environment"
    exit 1
fi
```

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 16:45 