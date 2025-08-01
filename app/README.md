# APP - Джерельний код додатку

> **Всі джерельні коди Upwork AI Assistant**

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Розробка](#розробка)
4. [Збірка](#збірка)

---

## Огляд

Папка `app/` містить весь джерельний код додатку:

- **`backend/`** - Python FastAPI сервер
- **`frontend/`** - React TypeScript додаток
- **Майбутні модулі** - AI, Analytics, тощо

---

## Структура

```
app/
├── backend/                # 🔧 Python FastAPI додаток
│   ├── src/               # Вихідний код
│   │   ├── api/           # API endpoints
│   │   ├── services/      # Бізнес-логіка
│   │   ├── models/        # Database моделі
│   │   ├── utils/         # Допоміжні функції
│   │   └── main.py        # Точка входу
│   ├── tests/             # Тести
│   ├── requirements.txt   # Python залежності
│   ├── Dockerfile         # Docker образ
│   └── README.md          # Backend документація
├── frontend/              # 🎨 React TypeScript додаток
│   ├── src/               # Вихідний код
│   │   ├── components/    # React компоненти
│   │   ├── pages/         # Сторінки
│   │   ├── services/      # API клієнти
│   │   └── utils/         # Допоміжні функції
│   ├── public/            # Статичні файли
│   ├── package.json       # Node.js залежності
│   └── README.md          # Frontend документація
└── README.md              # Цей файл
```

---

## Розробка

### **Backend розробка**
```bash
# Перехід в backend
cd app/backend

# Встановлення залежностей
pip install -r requirements.txt

# Запуск в режимі розробки
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Запуск тестів (з кореневої папки)
npm run test:backend
# або
./tools/scripts/run_tests.sh backend
```

### **Frontend розробка**
```bash
# Перехід в frontend
cd app/frontend

# Встановлення залежностей
npm install

# Запуск в режимі розробки
npm start

# Запуск тестів (з кореневої папки)
npm run test:frontend
# або
./tools/scripts/run_tests.sh frontend
```

### **Повна розробка**
```bash
# З кореневої папки проекту

# Backend (термінал 1)
cd app/backend && uvicorn src.main:app --reload

# Frontend (термінал 2)
cd app/frontend && npm start

# Docker (термінал 3)
docker-compose up -d
```

---

## Збірка

### **Локальна збірка**
```bash
# З кореневої папки проекту

# Збірка backend
cd app/backend
pip install -r requirements.txt
# Backend готовий до запуску

# Збірка frontend
cd app/frontend
npm install
npm run build
# Зібрані файли в app/frontend/build/
```

### **Production збірка**
```bash
# Використання скриптів збірки
./scripts/build.sh all

# Результат в папці dist/
```

---

## Docker

### **Локальний запуск**
```bash
# З кореневої папки проекту
docker-compose up -d

# Доступні сервіси:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### **Розробка з Docker**
```bash
# Тільки база даних та Redis
docker-compose up postgres redis -d

# Backend з локальним кодом
cd app/backend && uvicorn src.main:app --reload

# Frontend з локальним кодом
cd app/frontend && npm start
```

---

## Моніторинг

### **Backend моніторинг**
```bash
# Логи backend
docker-compose logs -f backend

# Health check
curl http://localhost:8000/health

# API документація
open http://localhost:8000/docs
```

### **Frontend моніторинг**
```bash
# Логи frontend
docker-compose logs -f frontend

# Перевірка доступності
curl http://localhost:3000
```

---

## Зв'язок між компонентами

### **API інтеграція**
- **Frontend** → **Backend**: HTTP запити на `http://localhost:8000`
- **Backend** → **Database**: PostgreSQL через SQLAlchemy
- **Backend** → **Cache**: Redis для кешування
- **Backend** → **External APIs**: Upwork API, OpenAI API

### **Схема взаємодії**
```
┌─────────────┐    HTTP     ┌─────────────┐
│  Frontend   │ ──────────► │   Backend   │
│  (React)    │             │  (FastAPI)  │
└─────────────┘             └─────────────┘
                                    │
                                    ▼
                            ┌─────────────┐
                            │ PostgreSQL  │
                            │    Redis    │
                            └─────────────┘
```

---

## Наступні кроки

### **Негайні завдання**
1. **Реалізувати базову безпеку** (SECURITY-001 до SECURITY-004)
2. **Створити базові React компоненти**
3. **Налаштувати API інтеграцію**

### **Середньострокові завдання**
1. **Додати AI модуль** в `app/ai/`
2. **Створити Analytics модуль** в `app/analytics/`
3. **Додати мобільний додаток** в `app/mobile/`

---

## Нотатки

### **Важливо**
- Всі зміни в `app/` автоматично відображаються в Docker
- Frontend використовує proxy для API запитів
- Backend має hot reload для розробки
- Тести запускаються в окремих папках

### **Рекомендації**
- Використовуйте TypeScript для frontend
- Дотримуйтесь PEP 8 для Python
- Пишіть тести для всіх функцій
- Документуйте API endpoints

---

**Статус**: В розробці  
**Версія**: 1.0.0 