# Docker Конфігурація

> **Контейнеризація Upwork Web App з multi-stage builds та оптимізацією**

---

## Зміст

1. [Огляд конфігурації](#огляд-конфігурації)
2. [Backend Dockerfile](#backend-dockerfile)
3. [Frontend Dockerfile](#frontend-dockerfile)
4. [Docker Compose](#docker-compose)
5. [Оптимізація](#оптимізація)
6. [Безпека](#безпека)

---

## Огляд конфігурації

### Архітектура контейнерів
```
┌─────────────────────────────────────┐
│         Docker Environment          │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ Frontend    │ │   Backend   │   │
│  │ (React)     │ │ (FastAPI)   │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │ PostgreSQL  │ │   Redis     │   │
│  └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐   │
│  │   Nginx     │ │ Monitoring  │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

### Технології
- **Multi-stage builds** - оптимізація розміру образів
- **Alpine Linux** - мінімальні базові образи
- **Docker Compose** - оркестрація контейнерів
- **Health checks** - моніторинг стану сервісів
- **Container Registry**: Docker Hub (development), AWS ECR (production)
- **Infrastructure as Code**: Terraform

---

## Backend Dockerfile

### Основний Dockerfile
```dockerfile
# Multi-stage build для Python backend
FROM python:3.11-alpine AS base

# Встановлюємо системні залежності
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Створюємо користувача для безпеки
RUN addgroup -g 1000 app && \
    adduser -D -s /bin/sh -u 1000 -G app app

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо код додатку
COPY --chown=app:app . .

# Створюємо директорії для логів
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Переключаємося на користувача app
USER app

# Expose порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запускаємо додаток
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Dockerfile
```dockerfile
# Development версія з hot reload
FROM python:3.11-alpine AS development

# Встановлюємо системні залежності
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Встановлюємо Python залежності
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Створюємо користувача
RUN addgroup -g 1000 app && \
    adduser -D -s /bin/sh -u 1000 -G app app

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо код
COPY --chown=app:app . .

# Створюємо директорії
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Переключаємося на користувача
USER app

# Expose порт
EXPOSE 8000

# Запускаємо з auto-reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Production Dockerfile
```dockerfile
# Production версія з оптимізацією
FROM python:3.11-alpine AS production

# Встановлюємо системні залежності
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Створюємо користувача
RUN addgroup -g 1000 app && \
    adduser -D -s /bin/sh -u 1000 -G app app

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо код
COPY --chown=app:app . .

# Створюємо директорії
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Переключаємося на користувача
USER app

# Expose порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запускаємо з Gunicorn
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

---

## Frontend Dockerfile

### React Dockerfile
```dockerfile
# Multi-stage build для React frontend
FROM node:18-alpine AS builder

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо package файли
COPY package*.json ./

# Встановлюємо залежності
RUN npm ci --only=production

# Копіюємо код
COPY . .

# Білдимо додаток
RUN npm run build

# Production stage
FROM nginx:alpine AS production

# Копіюємо білд
COPY --from=builder /app/build /usr/share/nginx/html

# Копіюємо nginx конфігурацію
COPY nginx.conf /etc/nginx/nginx.conf

# Expose порт
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Запускаємо nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Development Frontend
```dockerfile
# Development версія React
FROM node:18-alpine AS development

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо package файли
COPY package*.json ./

# Встановлюємо залежності
RUN npm install

# Копіюємо код
COPY . .

# Expose порт
EXPOSE 3000

# Запускаємо dev сервер
CMD ["npm", "start"]
```

---

## Docker Compose

### Основний docker-compose.yml
```yaml
version: '3.8'

services:
# Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: upwork-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/upwork_app
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - UPWORK_CLIENT_ID=${UPWORK_CLIENT_ID}
      - UPWORK_CLIENT_SECRET=${UPWORK_CLIENT_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    networks:
      - upwork-network

# Frontend React
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    container_name: upwork-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - upwork-network

# PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: upwork-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=upwork_app
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - upwork-network

# Redis Cache
  redis:
    image: redis:7-alpine
    container_name: upwork-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - upwork-network

# Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: upwork-nginx
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    networks:
      - upwork-network

# Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: upwork-prometheus
    restart: unless-stopped
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
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - upwork-network

# Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: upwork-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    networks:
      - upwork-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  upwork-network:
    driver: bridge
```

### Development docker-compose.yml
```yaml
version: '3.8'

services:
# Backend API (Development)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: upwork-backend-dev
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/upwork_app_dev
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=dev_secret_key
      - DEBUG=true
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - upwork-network

# Frontend React (Development)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: upwork-frontend-dev
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - CHOKIDAR_USEPOLLING=true
    networks:
      - upwork-network

# PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: upwork-postgres-dev
    restart: unless-stopped
    environment:
      - POSTGRES_DB=upwork_app_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - upwork-network

# Redis Cache
  redis:
    image: redis:7-alpine
    container_name: upwork-redis-dev
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - upwork-network

volumes:
  postgres_dev_data:
  redis_dev_data:

networks:
  upwork-network:
    driver: bridge
```

---

## Оптимізація

### Multi-stage Builds
```dockerfile
# Оптимізований multi-stage build
FROM python:3.11-alpine AS base

# Встановлюємо системні залежності
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base AS development
RUN pip install --no-cache-dir -r requirements-dev.txt
WORKDIR /app
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production
WORKDIR /app
COPY --from=development /app .
RUN addgroup -g 1000 app && \
    adduser -D -s /bin/sh -u 1000 -G app app
USER app
CMD ["gunicorn", "src.main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### .dockerignore
```dockerignore
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Documentation
docs/
*.md
README*

# Tests
tests/
test_*
*_test.py

# Development
docker-compose*.yml
Dockerfile*
.dockerignore
```

---

## Безпека

### Security Best Practices
```dockerfile
# Безпечний Dockerfile
FROM python:3.11-alpine AS base

# Встановлюємо системні залежності
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

# Встановлюємо Python залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Створюємо користувача для безпеки
RUN addgroup -g 1000 app && \
    adduser -D -s /bin/sh -u 1000 -G app app

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо код з правильними правами
COPY --chown=app:app . .

# Створюємо директорії для логів
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Переключаємося на користувача app
USER app

# Expose порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запускаємо додаток
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Scanning
```yaml
# GitHub Actions security scanning
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'upwork-backend:latest'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
```

---

## Моніторинг

### Prometheus Configuration
```yaml
# prometheus.yml
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
  - job_name: 'upwork-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'upwork-frontend'
    static_configs:
      - targets: ['frontend:80']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 10s
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "id": null,
    "title": "Upwork Web App Dashboard",
    "tags": ["upwork", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"4..|5..\"}[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      }
    ]
  }
}
```

---

## Контрольні списки

### Реалізація
- [ ] Multi-stage Dockerfiles
- [ ] Docker Compose конфігурація
- [ ] Health checks
- [ ] Security scanning
- [ ] Monitoring setup
- [ ] Volume management

### Безпека
- [ ] Non-root користувач
- [ ] Security scanning
- [ ] Minimal base images
- [ ] No secrets in images
- [ ] Regular updates

### Оптимізація
- [ ] Multi-stage builds
- [ ] .dockerignore
- [ ] Layer caching
- [ ] Image size optimization
- [ ] Build time optimization

---

## Посилання

- [CI/CD pipeline](ci_cd_pipeline.md)
- [Налаштування моніторингу](monitoring_setup.md)
- [Системна архітектура](../architecture/system_architecture.md)

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 15:30 