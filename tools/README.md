# TOOLS - Інструменти проекту

> **Всі інструменти та скрипти для автоматизації Upwork AI Assistant**

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Скрипти](#скрипти)
4. [CI/CD](#cicd)
5. [Моніторинг](#моніторинг)

---

## Огляд

Папка `tools/` містить всі інструменти для автоматизації проекту:

- **`scripts/`** - Bash скрипти для збірки та розгортання
- **`ci/`** - CI/CD конфігурації
- **`monitoring/`** - Інструменти моніторингу

---

## Структура

```
tools/
├── scripts/                # 🔧 Bash скрипти
│   ├── build.sh           # Збірка проекту
│   ├── deploy.sh          # Розгортання
│   ├── migrate.sh         # Міграції БД
│   ├── backup.sh          # Backup системи
│   └── health-check.sh    # Перевірка здоров'я
├── ci/                     # 🔄 CI/CD конфігурації
│   ├── github/            # GitHub Actions
│   ├── gitlab/            # GitLab CI
│   └── jenkins/           # Jenkins пайплайни
├── monitoring/             # 📊 Моніторинг
│   ├── prometheus/        # Prometheus конфігурації
│   ├── grafana/           # Grafana дашборди
│   └── alerts/            # Сповіщення
└── README.md              # Цей файл
```

---

## Скрипти

### **build.sh** - Збірка проекту
```bash
# Збірка всього проекту
./tools/scripts/build.sh all

# Збірка тільки frontend
./tools/scripts/build.sh frontend

# Збірка тільки backend
./tools/scripts/build.sh backend
```

### **deploy.sh** - Розгортання
```bash
# Локальне розгортання
./tools/scripts/deploy.sh local

# Розробка
./tools/scripts/deploy.sh dev

# Staging
./tools/scripts/deploy.sh staging

# Production
./tools/scripts/deploy.sh production
```

### **migrate.sh** - Міграції бази даних
```bash
# Запуск міграцій
./tools/scripts/migrate.sh

# Створення нової міграції
./tools/scripts/migrate.sh create "опис міграції"
```

### **backup.sh** - Backup системи
```bash
# Створення backup
./tools/scripts/backup.sh

# Відновлення з backup
./tools/scripts/backup.sh restore
```

### **health-check.sh** - Перевірка здоров'я
```bash
# Перевірка всіх сервісів
./tools/scripts/health-check.sh

# Детальна перевірка
./tools/scripts/health-check.sh detailed
```

### **run_tests.sh** - Запуск тестів
```bash
# Всі тести
./tools/scripts/testing/run_tests.sh

# Конкретні типи тестів
./tools/scripts/testing/run_tests.sh backend
./tools/scripts/testing/run_tests.sh frontend
./tools/scripts/testing/run_tests.sh coverage
./tools/scripts/testing/run_tests.sh full

# Допомога
./tools/scripts/testing/run_tests.sh help
```

---

## CI/CD

### **GitHub Actions**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: ./tools/scripts/test.sh
```

### **GitLab CI**
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - ./tools/scripts/test.sh
```

### **Jenkins**
```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh './tools/scripts/test.sh'
            }
        }
    }
}
```

---

## Моніторинг

### **Prometheus конфігурації**
```yaml
# tools/monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'upwork-backend'
    static_configs:
      - targets: ['localhost:8000']
```

### **Grafana дашборди**
```json
// tools/monitoring/grafana/dashboard.json
{
  "dashboard": {
    "title": "Upwork AI Assistant",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph"
      }
    ]
  }
}
```

### **Сповіщення**
```yaml
# tools/monitoring/alerts/alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
```

---

## Використання

### **Швидкий старт**
```bash
# Клонування репозиторію
git clone <repository-url>
cd upwork-ai-assistant

# Встановлення залежностей
./tools/scripts/setup.sh

# Запуск розробки
./tools/scripts/deploy.sh dev
```

### **Production розгортання**
```bash
# Збірка проекту
./tools/scripts/build.sh all

# Розгортання
./tools/scripts/deploy.sh production

# Перевірка здоров'я
./tools/scripts/health-check.sh
```

### **Моніторинг**
```bash
# Запуск моніторингу
docker-compose -f tools/monitoring/docker-compose.yml up -d

# Перегляд метрик
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
```

---

## Безпека

### **Важливо**
- Всі скрипти мають права на виконання
- Production скрипти вимагають підтвердження
- Backup створюється перед кожним розгортанням
- Логи зберігаються для аудиту

### **Рекомендації**
- Регулярно оновлюйте скрипти
- Тестуйте скрипти в staging середовищі
- Використовуйте секрети для чутливих даних
- Моніторте виконання скриптів

---

## Нотатки

### **Автоматизація**
- Всі скрипти інтегровані з CI/CD
- Моніторинг працює автоматично
- Backup створюється за розкладом

### **Розширення**
- Легко додавати нові скрипти
- Модульна архітектура
- Підтримка різних середовищ

---

**Статус**: Активний  
**Версія**: 1.0.0 