# Frontend - Upwork AI Assistant

> **React TypeScript frontend для Upwork AI Assistant**

---

## Зміст

1. [Огляд](#огляд)
2. [Технології](#технології)
3. [Швидкий старт](#швидкий-старт)
4. [Структура проекту](#структура-проекту)
5. [Розробка](#розробка)

---

## Огляд

Frontend частина Upwork AI Assistant - це React додаток з TypeScript, який надає зручний веб-інтерфейс для:

- 🔐 Авторизації та управління профілем
- 🔍 Пошуку та фільтрації вакансій
- 🤖 Генерації AI пропозицій
- 📊 Перегляду аналітики та метрик
- ⚙️ Налаштування системи

---

## Технології

- **React 18** - UI бібліотека
- **TypeScript** - типізація
- **Material-UI (MUI)** - компоненти інтерфейсу
- **React Router** - навігація
- **Axios** - HTTP клієнт
- **ESLint** - лінтинг коду

---

## Швидкий старт

### **Встановлення залежностей**
```bash
npm install
```

### **Запуск в режимі розробки**
```bash
npm start
```

Додаток буде доступний за адресою: http://localhost:3000

### **Збірка для продакшену**
```bash
npm run build
```

### **Тестування**
```bash
npm test
```

---

## Структура проекту

```
frontend/
├── public/                 # Статичні файли
│   ├── index.html         # Головна HTML сторінка
│   ├── favicon.ico        # Іконка сайту
│   └── manifest.json      # PWA маніфест
├── src/                   # Вихідний код
│   ├── components/        # React компоненти
│   │   ├── common/        # Загальні компоненти
│   │   ├── layout/        # Компоненти макету
│   │   └── forms/         # Форми
│   ├── pages/             # Сторінки додатку
│   │   ├── auth/          # Авторизація
│   │   ├── dashboard/     # Головна панель
│   │   ├── jobs/          # Вакансії
│   │   ├── proposals/     # Пропозиції
│   │   └── analytics/     # Аналітика
│   ├── services/          # API сервіси
│   │   ├── api.ts         # Базовий API клієнт
│   │   ├── auth.ts        # Авторизація
│   │   ├── jobs.ts        # Вакансії
│   │   └── ai.ts          # AI функції
│   ├── hooks/             # React хуки
│   ├── utils/             # Допоміжні функції
│   ├── types/             # TypeScript типи
│   ├── styles/            # Стилі
│   ├── App.tsx            # Головний компонент
│   └── index.tsx          # Точка входу
├── package.json           # Залежності
└── tsconfig.json          # TypeScript конфігурація
```

---

## Розробка

### **Стандарти коду**
- **TypeScript** для типізації
- **ESLint** для лінтингу
- **Prettier** для форматування
- **Material-UI** для компонентів

### **Компоненти**
```typescript
// Приклад компонента
import React from 'react';
import { Box, Typography } from '@mui/material';

interface JobCardProps {
  job: Job;
  onApply: (jobId: string) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onApply }) => {
  return (
    <Box sx={{ p: 2, border: 1, borderColor: 'grey.300', borderRadius: 1 }}>
      <Typography variant="h6">{job.title}</Typography>
      <Typography variant="body2">{job.description}</Typography>
      <Button onClick={() => onApply(job.id)}>
        Apply
      </Button>
    </Box>
  );
};
```

### **API інтеграція**
```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для додавання токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

## Зв'язок з Backend

Frontend взаємодіє з backend через REST API:

- **Авторизація**: `/api/v1/auth/*`
- **Вакансії**: `/api/v1/upwork/jobs`
- **AI функції**: `/api/v1/ai/*`
- **Аналітика**: `/api/v1/analytics/*`

---

## Responsive Design

Додаток повністю адаптивний та працює на:
- 📱 Мобільних пристроях
- 💻 Планшетах
- 🖥️ Десктопах

---

## 🧪 Тестування

### **Unit тести**
```bash
npm test
```

### **E2E тести**
```bash
npm run test:e2e
```

---

## Розгортання

### **Development**
```bash
npm start
```

### **Production**
```bash
npm run build
```

Збудовані файли знаходяться в папці `build/`

---

**Статус**: В розробці  
**Версія**: 1.0.0 