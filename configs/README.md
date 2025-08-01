# CONFIGS - Конфігурації проекту

> **Конфігураційні файли Upwork AI Assistant (без Docker)**

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Використання](#використання)
4. [Середовища](#середовища)

---

## Огляд

Папка `configs/` містить конфігураційні файли проекту (крім Docker):

- **`environments/`** - Змінні середовища
- **`nginx/`** - Nginx конфігурації (застаріло)
- **`ssl/`** - SSL сертифікати

> **⚠️ УВАГА**: Docker конфігурації перенесено в папку `docker/` в корені проекту.

---

## Структура

```
configs/
├── environments/           # 🌍 Змінні середовища
│   ├── .env.example       # Приклад змінних
│   ├── .env.development   # Development
│   ├── .env.staging       # Staging
│   └── .env.production    # Production
├── nginx/                  # 🌐 Nginx конфігурації (застаріло)
│   └── README.md          # Інформація про перенесення
├── ssl/                    # 🔒 SSL сертифікати
│   ├── certificates/      # Сертифікати
│   └── private/           # Приватні ключі
└── README.md              # Цей файл
```

---

## Використання

### **Docker конфігурації**
> **Нова локація**: `docker/` в корені проекту

```bash
# Development
docker-compose -f docker/docker-compose.dev.yml up -d

# Production
docker-compose -f docker/docker-compose.prod.yml up -d

# Основна конфігурація
docker-compose -f docker/docker-compose.yml up -d
```

### **Змінні середовища**
```bash
# Копіювання для development
cp configs/environments/.env.development .env

# Копіювання для production
cp configs/environments/.env.production .env
```

### **Nginx конфігурації**
> **Нова локація**: `docker/nginx/`

```bash
# Копіювання конфігурації
sudo cp docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Перезапуск Nginx
sudo systemctl reload nginx
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

## Зміни в структурі

### **Що змінилося:**
- ✅ Docker конфігурації перенесено в `docker/`
- ✅ Видалено застарілі монолітні конфігурації
- ✅ Встановлено мікросервісну архітектуру як основну

### **Нова структура Docker:**
```
docker/
├── docker-compose.yml     # Основна конфігурація (мікросервіси)
├── docker-compose.dev.yml # Development
├── docker-compose.prod.yml # Production
└── nginx/                 # Nginx конфігурації
```

### **Переваги нової структури:**
1. **Централізоване управління** - всі Docker файли в одному місці
2. **Простота використання** - `docker-compose up` з кореня проекту
3. **Стандартна практика** - відповідає загальноприйнятим стандартам
4. **Зручність CI/CD** - простіше налаштувати автоматизацію

---

## Міграція

### **Для існуючих користувачів:**
```bash
# Старий спосіб (не працює)
docker-compose -f configs/docker/docker-compose.yml up

# Новий спосіб
docker-compose -f docker/docker-compose.yml up
```

### **Оновлення скриптів:**
```bash
# Оновіть шляхи в ваших скриптах
# З: configs/docker/docker-compose.yml
# На: docker/docker-compose.yml
```

---

*Останнє оновлення: 2024-12-19*
*Версія: v2.0.0* 
**Статус**: Активний  
**Версія**: 1.0.0 