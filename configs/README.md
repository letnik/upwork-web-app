# CONFIGS - Конфігурації проекту

> **Всі конфігураційні файли Upwork AI Assistant**

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Використання](#використання)
4. [Середовища](#середовища)

---

## Огляд

Папка `configs/` містить всі конфігураційні файли проекту:

- **`docker/`** - Docker конфігурації
- **`nginx/`** - Nginx конфігурації
- **`ssl/`** - SSL сертифікати
- **`environments/`** - Змінні середовища

---

## Структура

```
configs/
├── docker/                 # 🐳 Docker конфігурації
│   ├── docker-compose.yml  # Основний compose файл
│   ├── docker-compose.dev.yml    # Development
│   ├── docker-compose.staging.yml # Staging
│   └── docker-compose.prod.yml   # Production
├── nginx/                  # 🌐 Nginx конфігурації
│   ├── nginx.conf         # Основний конфіг
│   ├── ssl/               # SSL налаштування
│   └── sites/             # Віртуальні хости
├── ssl/                    # 🔒 SSL сертифікати
│   ├── certificates/      # Сертифікати
│   └── private/           # Приватні ключі
├── environments/           # 🌍 Змінні середовища
│   ├── .env.example       # Приклад змінних
│   ├── .env.development   # Development
│   ├── .env.staging       # Staging
│   └── .env.production    # Production
└── README.md              # Цей файл
```

---

## Використання

### **Docker конфігурації**
```bash
# Development
docker-compose -f configs/docker/docker-compose.dev.yml up -d

# Staging
docker-compose -f configs/docker/docker-compose.staging.yml up -d

# Production
docker-compose -f configs/docker/docker-compose.prod.yml up -d
```

### **Nginx конфігурації**
```bash
# Копіювання конфігурації
sudo cp configs/nginx/nginx.conf /etc/nginx/nginx.conf

# Перезапуск Nginx
sudo systemctl reload nginx
```

### **Змінні середовища**
```bash
# Копіювання для development
cp configs/environments/.env.development .env

# Копіювання для production
cp configs/environments/.env.production .env
```

---

## Середовища

### **Development**
- Локальна розробка
- Debug режим
- Тестові дані

### **Staging**
- Тестування перед production
- Production-подібне середовище
- Тестові API ключі

### **Production**
- Продакшн середовище
- Оптимізовані налаштування
- Реальні API ключі

---

## Безпека

### **Важливо**
- **НЕ комітьте** `.env` файли в Git
- **НЕ зберігайте** SSL ключі в репозиторії
- Використовуйте `.env.example` як шаблон
- Регулярно оновлюйте сертифікати

### **Рекомендації**
- Використовуйте секрети для production
- Шифруйте чутливі дані
- Обмежуйте доступ до конфігурацій
- Ведіть лог змін конфігурацій

---

## Нотатки

### **Автоматизація**
- Скрипти в `tools/scripts/` автоматично використовують ці конфігурації
- CI/CD пайплайни використовують staging конфігурації
- Production розгортання використовує production конфігурації

### **Моніторинг**
- Конфігурації моніторяться в `tools/monitoring/`
- Зміни логуються автоматично
- Backup конфігурацій створюється перед змінами

---

**Статус**: Активний  
**Версія**: 1.0.0 