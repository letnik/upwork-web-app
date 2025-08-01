# Правила структури проекту

## Огляд

Цей документ містить правила та рекомендації для підтримки чистої та логічної структури проекту Upwork AI Assistant.

## 🔴 Критичні правила

### 1. **Dockerfile правила**
- ✅ **Тільки один CMD** в кожному Dockerfile
- ✅ **Використовувати централізовані requirements** з папки `requirements/`
- ✅ **Не дублювати CMD рядки**
- ❌ **Заборонено** requirements.txt в сервісах

**Приклад правильного Dockerfile:**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../../../requirements/base.txt requirements/
COPY ../../../requirements/[SERVICE]-service.txt requirements/

RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/[SERVICE]-service.txt

COPY src/ ./src/
RUN mkdir -p logs

EXPOSE [PORT]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "[PORT]"]
```

### 2. **Імпорти правила**
- ✅ **Перевіряти існування файлів** перед імпортом
- ✅ **Використовувати відносні імпорти** для локальних модулів
- ❌ **Заборонено** імпортувати неіснуючі файли

**Приклад правильного імпорту:**
```python
# ✅ Правильно
from .models import User
from .oauth import router as oauth_router

# ❌ Неправильно (файл не існує)
from .test_oauth import router as test_oauth_router
```

### 3. **Файли кешу**
- ✅ **Додавати в .gitignore** всі файли кешу
- ✅ **Регулярно очищати** кеш файли
- ❌ **Заборонено** зберігати кеш в репозиторії

**Файли, які НЕ повинні бути в репозиторії:**
- `.DS_Store`
- `.coverage`
- `.pytest_cache/`
- `logs/`
- `exports/`
- `sessions/`
- `*.log`

## 🟡 Правила середньої важливості

### 4. **Порожні файли**
- ✅ **Видаляти порожні файли** (0 байт)
- ✅ **Використовувати .gitkeep** для порожніх папок
- ❌ **Заборонено** порожні файли без призначення

### 5. **Структура папок**
- ✅ **Логічна організація** файлів
- ✅ **Одна відповідальність** на папку
- ✅ **Зрозумілі назви** папок та файлів

## 🧹 Процедури очищення

### Автоматичне очищення
```bash
# Видалити всі .DS_Store файли
find . -name ".DS_Store" -delete

# Видалити .coverage файли
find . -name ".coverage" -delete

# Видалити .pytest_cache директорії
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# Видалити порожні файли (крім .gitkeep)
find . -type f -size 0 -not -name ".gitkeep" -delete
```

### Перевірка структури
```bash
# Запустити перевірку структури
./tools/scripts/project/validate_structure.sh
```

## 📋 Чек-лист перед комітом

### Dockerfile
- [ ] Тільки один CMD
- [ ] Використовуються централізовані requirements
- [ ] Немає дублікатів

### Імпорти
- [ ] Всі імпортовані файли існують
- [ ] Відносні імпорти для локальних модулів
- [ ] Немає неіснуючих імпортів

### Файли кешу
- [ ] Немає .DS_Store файлів
- [ ] Немає .coverage файлів
- [ ] Немає .pytest_cache директорій
- [ ] Немає порожніх файлів

### .gitignore
- [ ] Всі необхідні правила додані
- [ ] logs/, exports/, sessions/ в .gitignore
- [ ] *.log в .gitignore

## 🚀 Автоматизація

### Pre-commit hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-structure
        name: Validate project structure
        entry: ./tools/scripts/project/validate_structure.sh
        language: system
        pass_filenames: false
```

### CI/CD перевірки
```yaml
# GitHub Actions
- name: Validate project structure
  run: |
    ./tools/scripts/project/validate_structure.sh
```

## 📊 Метрики якості

### Цільові показники
- ✅ 0 дублікатів CMD в Dockerfile
- ✅ 0 неіснуючих імпортів
- ✅ 0 файлів кешу в репозиторії
- ✅ 0 порожніх файлів
- ✅ 100% покриття .gitignore правил

### Регулярні перевірки
- **Щодня**: Автоматична перевірка структури
- **Щотижня**: Ручна перевірка та очищення
- **Щомісяця**: Оновлення правил та документації

## 🔧 Виправлення проблем

### Якщо знайдено дублікат CMD
1. Відкрити Dockerfile
2. Знайти дублікат CMD
3. Видалити зайвий рядок
4. Залишити тільки один CMD

### Якщо знайдено неіснуючий імпорт
1. Знайти файл з імпортом
2. Видалити рядок імпорту
3. Видалити використання імпортованого об'єкта
4. Перевірити, чи потрібен цей функціонал

### Якщо знайдено файли кешу
1. Видалити файли кешу
2. Додати правила в .gitignore
3. Перевірити, чи всі правила додані

## 📚 Додаткові ресурси

- [Скрипт перевірки структури](validate_structure.sh)
- [Правила .gitignore](../.gitignore)
- [Централізовані requirements](../../requirements/)

---
*Останнє оновлення: $(date)*
*Автор: AI Assistant* 