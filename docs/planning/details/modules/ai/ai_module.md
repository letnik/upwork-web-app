# AI Модуль - Детальний опис

## Огляд

AI модуль забезпечує інтелектуальну генерацію контенту для роботи з Upwork, включаючи аналіз вакансій, створення відгуків та рекомендацій.

## Основні функції

### 1. AI інструкції природною мовою
- Створення AI інструкцій природною мовою
- Шаблони AI інструкцій для різних сценаріїв
- Тестування AI інструкцій на прикладах
- Оцінка ефективності AI інструкцій
- Рекомендації для покращення (раз в день)

### 2. Аналіз вакансій
- Оцінка підходящості вакансії через активні профілі
- AI аналіз через налаштовані фільтри
- Визначення підходящості вакансій
- НЕ генерація відгуків одразу - тільки визначення підходящості

### 3. Генерація відгуків
- Створення персоналізованих відгуків при запиті користувача
- Вибір шаблону + стилю
- Персоналізація під конкретну вакансію
- Адаптація під профіль фрілансера
- Врахування специфіки проекту
- **Затримка 1 хвилина перед відправкою**
- **Обмеження на кількість відгуків на день**

### 4. Шаблони відгуків
- Створення до 10 шаблонів на користувача
- Категорії: Загальний, Веб-розробка, Мобільні додатки, Дизайн
- Змінні: {client_name}, {project_type}, {budget}
- Відстеження успішності кожного шаблону
- Стилі: Формальний, Дружній, Технічний
- **Приклади для AI (не готові відгуки)**

### 5. A/B тестування
- 2 варіанти одночасно
- Мінімальний період тестування - тиждень
- Можливість примусового завершення
- Перегляд проміжних результатів
- Критерії успішності: відсоток відповідей, найнято, зароблено

### 6. Аналіз клієнтів
- Оцінка рейтингу та історії клієнта
- Аналіз платіжної поведінки
- Рекомендації щодо співпраці

## Налаштування AI

### AI Розкриття (AI Disclosure)

#### Опис функції
Система надає можливість користувачу контролювати, чи вказувати в згенерованому контенті інформацію про використання штучного інтелекту.

#### Налаштування
```json
{
  "ai_disclosure": {
    "enabled": true,
    "position": "end", // "start", "end", "none"
    "template": "default", // "default", "minimal", "detailed", "custom"
    "custom_text": "",
    "auto_add": true
  }
}
```

#### Варіанти розкриття

**Мінімальне:**
```
*AI-генерований контент*
```

**Стандартне:**
```
---
**Розкриття:** Цей відгук був створений за допомогою штучного інтелекту та відредагований для адаптації під ваш проект.
```

**Детальне:**
```
---
**Розкриття:** Цей відгук використовував AI для аналізу вимог та створення структурованої пропозиції. Весь контент був переглянутий та адаптований фахівцем для забезпечення релевантності та якості.
```

**Кастомне:**
Користувач може ввести власний текст розкриття.

### Редагування перед відправкою

#### Опис функції
Система забезпечує можливість редагування згенерованого контенту перед відправкою, включаючи попередній перегляд та валідацію.

#### Компоненти редагування

**1. Попередній перегляд**
- Відображення згенерованого контенту
- Підсвічування AI-генерованих частин
- Можливість редагування в реальному часі

**2. Валідація контенту**
- Перевірка довжини відгуку
- Валідація на спам-контент
- Перевірка наявності ключових елементів

**3. Інструменти редагування**
- Текстове поле з підтримкою Markdown
- Автозбереження чернеток
- Історія змін

#### Налаштування редагування
```json
{
  "editing": {
    "auto_save": true,
    "save_interval": 30, // секунди
    "draft_retention": 7, // дні
    "validation": {
      "min_length": 100,
      "max_length": 2000,
      "check_spam": true,
      "require_review": true
    }
  }
}
```

## Технічна реалізація

### База даних

#### Таблиця налаштувань AI
```sql
CREATE TABLE ai_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ai_disclosure_enabled BOOLEAN DEFAULT true,
    ai_disclosure_position VARCHAR(10) DEFAULT 'end',
    ai_disclosure_template VARCHAR(20) DEFAULT 'default',
    ai_disclosure_custom_text TEXT,
    auto_add_disclosure BOOLEAN DEFAULT true,
    auto_save_drafts BOOLEAN DEFAULT true,
    save_interval INTEGER DEFAULT 30,
    draft_retention_days INTEGER DEFAULT 7,
    min_proposal_length INTEGER DEFAULT 100,
    max_proposal_length INTEGER DEFAULT 2000,
    check_spam_content BOOLEAN DEFAULT true,
    require_review_before_sending BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Таблиця чернеток
```sql
CREATE TABLE proposal_drafts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    job_id VARCHAR(50),
    content TEXT,
    ai_generated_content TEXT,
    user_edited_content TEXT,
    ai_disclosure_included BOOLEAN DEFAULT false,
    validation_status VARCHAR(20) DEFAULT 'pending',
    validation_errors JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_edited_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

#### Налаштування AI
```python
# Отримання налаштувань AI
GET /api/ai/settings

# Оновлення налаштувань AI
PUT /api/ai/settings

# Скидання налаштувань до за замовчуванням
POST /api/ai/settings/reset
```

#### Генерація та редагування відгуків
```python
# Генерація відгуку
POST /api/ai/generate-proposal

# Збереження чернетки
POST /api/ai/drafts

# Отримання чернетки
GET /api/ai/drafts/{draft_id}

# Оновлення чернетки
PUT /api/ai/drafts/{draft_id}

# Валідація відгуку
POST /api/ai/validate-proposal

# Відправка відгуку
POST /api/ai/send-proposal
```

### Frontend компоненти

#### AI Settings Panel
```typescript
interface AISettings {
  aiDisclosure: {
    enabled: boolean;
    position: 'start' | 'end' | 'none';
    template: 'default' | 'minimal' | 'detailed' | 'custom';
    customText: string;
    autoAdd: boolean;
  };
  editing: {
    autoSave: boolean;
    saveInterval: number;
    draftRetention: number;
    validation: {
      minLength: number;
      maxLength: number;
      checkSpam: boolean;
      requireReview: boolean;
    };
  };
}
```

#### Proposal Editor
```typescript
interface ProposalEditor {
  content: string;
  aiGenerated: boolean;
  aiDisclosureIncluded: boolean;
  validationStatus: 'pending' | 'valid' | 'invalid';
  validationErrors: string[];
  lastSaved: Date;
  isDirty: boolean;
}
```

## Безпека та відповідність

### Валідація контенту
- Перевірка на спам-індикатори
- Валідація довжини контенту
- Перевірка на заборонені фрази
- Валідація наявності AI розкриття (якщо увімкнено)

### Логування
- Логування всіх AI генерацій
- Відстеження змін у чернетках
- Логування налаштувань користувачів
- Аудит відправлених відгуків

### Відповідність Upwork
- Дотримання політик автоматизації
- Повага до rate limiting
- Прозорість використання AI
- Можливість ручного редагування

## Користувацький інтерфейс

### Налаштування AI
- Перемикач увімкнення/вимкнення AI розкриття
- Вибір позиції розкриття (початок/кінець)
- Вибір шаблону розкриття
- Поле для кастомного тексту
- Налаштування автозбереження

### Редактор відгуків
- Текстове поле з підтримкою Markdown
- Підсвічування AI-генерованих частин
- Індикатор збереження
- Кнопки попереднього перегляду та валідації
- Історія змін

### Валідація
- Попередження про помилки валідації
- Підказки щодо покращення контенту
- Перевірка наявності AI розкриття
- Підтвердження перед відправкою

## Тестування

### Unit тести
- Тестування генерації AI розкриття
- Валідація налаштувань
- Тестування збереження чернеток
- Перевірка валідації контенту

### Integration тести
- Тестування повного циклу генерації
- Перевірка збереження налаштувань
- Тестування API endpoints
- Валідація відповідності Upwork

### E2E тести
- Тестування користувацького інтерфейсу
- Перевірка роботи редактора
- Тестування налаштувань
- Валідація відправки відгуків 