# Docker конфігурації проекту

> **🐳 Всі Docker файли та конфігурації Upwork AI Assistant**

---

## 🏛️ Правила для Docker конфігурацій

### **Критичні принципи:**
- **Централізація**: Всі Docker файли зберігаються в папці `docker/`. Заборонено docker-compose.yml в сервісах!
- **Структура**: Dockerfile в кожному сервісі, але docker-compose.yml тільки в `docker/`
- **Безпека**: Не комітити секрети, використовувати .env файли
- **Оптимізація**: Використовувати multi-stage builds, мінімальні образи
- **Версійність**: Фіксувати версії базових образів
- **Документація**: Кожен сервіс має коментарі в Dockerfile

### **Правила для Dockerfile:**
- **Базовий образ**: Використовувати офіційні образи (python:3.11-slim)
- **Залежності**: Використовувати централізовані requirements (див. приклади)
- **Безпека**: Не root користувач, мінімальні права
- **Розмір**: Оптимізувати розмір образу (multi-stage, .dockerignore)
- **Кешування**: Правильний порядок слоїв для кешування

### **Чекліст для ревʼю Docker:**
- [ ] Dockerfile використовує централізовані requirements
- [ ] Не містить секретів або .env файлів
- [ ] Використовує non-root користувача
- [ ] Містить .dockerignore файл
- [ ] Оптимізований розмір образу
- [ ] Фіксовані версії базових образів
- [ ] Містить коментарі для складних команд
- [ ] Тестований на різних платформах
- [ ] Документований в README
- [ ] Використовує health checks

### **Приклад правильного Dockerfile:**
```dockerfile
# Використання централізованих requirements
FROM python:3.11-slim

WORKDIR /app

# Копіювання централізованих залежностей
COPY ../../requirements/base.txt requirements/
COPY ../../requirements/service-name.txt requirements/

# Встановлення залежностей
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/service-name.txt

# Копіювання коду
COPY src/ ./src/

# Non-root користувач
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Автоматизація Docker:**
```bash
# Використовувати централізовані скрипти
./tools/scripts/project/manage.sh start    # Запуск через Docker
./tools/scripts/project/manage.sh stop     # Зупинка Docker
./tools/scripts/project/manage.sh clean    # Очищення Docker

# Або прямі команди
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml down
```

### **Заборонено:**
- ❌ docker-compose.yml в `app/backend/` або сервісах
- ❌ Секрети в Dockerfile або docker-compose.yml
- ❌ Root користувач в контейнерах
- ❌ Великі образи без оптимізації
- ❌ Відсутність health checks

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Використання](#використання)
4. [Архітектура](#архітектура)
5. [Середовища](#середовища)

---

## Огляд

Папка `docker/` містить всі Docker конфігурації проекту:

- **`docker-compose.yml`** - Основна конфігурація (мікросервіси)
- **`docker-compose.dev.yml`** - Development середовище
- **`docker-compose.prod.yml`** - Production середовище
- **`nginx/`** - Nginx конфігурації

---

## Структура

```
docker/
├── docker-compose.yml     # 🐳 Основна конфігурація (мікросервіси)
├── docker-compose.dev.yml # 🔧 Development
├── docker-compose.prod.yml # 🚀 Production
├── nginx/                 # 🌐 Nginx конфігурації
│   ├── nginx.conf        # Основний конфіг
│   └── ssl/              # SSL налаштування
└── README.md             # Цей файл
```

---

## Використання

### **Основна конфігурація (мікросервіси)**
```bash
# Запуск всіх сервісів
docker-compose -f docker/docker-compose.yml up -d

# Зупинка всіх сервісів
docker-compose -f docker/docker-compose.yml down

# Перегляд логів
docker-compose -f docker/docker-compose.yml logs -f
```

### **Development середовище**
```bash
# Запуск з debug режимом
docker-compose -f docker/docker-compose.dev.yml up -d

# Зупинка
docker-compose -f docker/docker-compose.dev.yml down
```

### **Production середовище**
```bash
# Запуск оптимізованої версії
docker-compose -f docker/docker-compose.prod.yml up -d

# Зупинка
docker-compose -f docker/docker-compose.prod.yml down
```

### **Окремі сервіси**
```bash
# Запуск тільки backend
docker-compose -f docker/docker-compose.yml up -d api-gateway auth-service

# Запуск тільки бази даних
docker-compose -f docker/docker-compose.yml up -d postgres redis
```

---

## Архітектура

### **Мікросервісна архітектура**

Проект використовує мікросервісну архітектуру з 5 основними сервісами:

#### **1. API Gateway (порт 8000)**
- Центральний шлюз для всіх запитів
- Маршрутизація до мікросервісів
- Аутентифікація та авторизація
- Rate limiting

#### **2. Auth Service (порт 8001)**
- Управління користувачами
- OAuth 2.0 інтеграція з Upwork
- JWT токени
- MFA (двофакторна автентифікація)

#### **3. Upwork Service (порт 8002)**
- Інтеграція з Upwork API
- Управління завданнями
- Пошук роботи
- Аналітика

#### **4. AI Service (порт 8003)**
- AI асистент
- Аналіз завдань
- Рекомендації
- Автоматизація

#### **5. Analytics Service (порт 8004)**
- Збір аналітики
- Звіти
- Метрики
- Dashboard

#### **6. Notification Service (порт 8005)**
- Email сповіщення
- Telegram бот
- Push повідомлення
- SMS

### **Інфраструктурні сервіси**

#### **PostgreSQL (порт 5432)**
- Основна база даних
- Зберігання користувачів
- Історія транзакцій
- Аналітичні дані

#### **Redis (порт 6379)**
- Кешування
- Сесії
- Rate limiting
- Черги повідомлень

#### **Nginx (порти 80, 443)**
- Reverse proxy
- SSL термінація
- Load balancing
- Статичні файли

---

## Середовища

### **Development**
```yaml
# docker-compose.dev.yml
environment:
  - DEBUG=true
  - ENVIRONMENT=development
  - LOG_LEVEL=DEBUG
```

**Особливості:**
- Debug режим увімкнено
- Детальне логування
- Hot reload для коду
- Тестові дані

### **Production**
```yaml
# docker-compose.prod.yml
environment:
  - DEBUG=false
  - ENVIRONMENT=production
  - LOG_LEVEL=INFO
```

**Особливості:**
- Оптимізована продуктивність
- Мінімальне логування
- SSL сертифікати
- Backup стратегії

---

## Команди для розробки

### **Запуск проекту**
```bash
# Повний запуск
docker-compose -f docker/docker-compose.yml up -d

# Тільки інфраструктура
docker-compose -f docker/docker-compose.yml up -d postgres redis

# Тільки backend сервіси
docker-compose -f docker/docker-compose.yml up -d api-gateway auth-service upwork-service
```

### **Моніторинг**
```bash
# Перегляд статусу
docker-compose -f docker/docker-compose.yml ps

# Перегляд логів
docker-compose -f docker/docker-compose.yml logs -f api-gateway

# Перегляд ресурсів
docker stats
```

### **Очищення**
```bash
# Зупинка та видалення контейнерів
docker-compose -f docker/docker-compose.yml down

# Видалення volumes
docker-compose -f docker/docker-compose.yml down -v

# Повне очищення
docker system prune -a
```

---

## Troubleshooting

### **Проблеми з портами**
```bash
# Перевірка зайнятих портів
lsof -i :8000
lsof -i :5432
lsof -i :6379

# Зміна портів в docker-compose.yml
ports:
  - "8001:8000"  # Зовнішній:Внутрішній
```

### **Проблеми з volumes**
```bash
# Перевірка volumes
docker volume ls

# Видалення volumes
docker volume rm upwork_postgres_data
```

### **Проблеми з мережею**
```bash
# Перевірка мереж
docker network ls

# Створення мережі
docker network create upwork-network
```

---

## Безпека

### **Важливі моменти:**
- ✅ Використовуйте `.env` файли для секретів
- ✅ НЕ комітьте `.env` файли в Git
- ✅ Регулярно оновлюйте базові образи
- ✅ Використовуйте non-root користувачів
- ✅ Обмежуйте доступ до Docker socket

### **Рекомендації:**
- Використовуйте Docker secrets для production
- Скануйте образи на вразливості
- Регулярно оновлюйте залежності
- Моніторте використання ресурсів

---

*Останнє оновлення: 2024-12-19*
*Версія: v1.0.0* 
 