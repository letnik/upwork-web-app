# 📁 Управління файлами в newspaper

> **Повний гайд по створенню та управлінню файлами в newspaper**

🚨 **КРИТИЧНО ВАЖЛИВО: Звіти створювати ТІЛЬКИ за явним запитом користувача!**

**❌ ЗАБОРОНА:**
- НЕ створювати звіти автоматично після завершення завдань
- НЕ створювати звіти без прямого запиту користувача
- НЕ створювати звіти "для документації" без запиту

---

## 📋 **Зміст**

1. [Критичні правила](#критичні-правила)
2. [Структура папок](#структура-папок)
3. [Алгоритм створення](#алгоритм-створення)
4. [Команди](#команди)
5. [Шаблони](#шаблони)
6. [Типи файлів](#типи-файлів)
7. [Обмеження](#обмеження)

---

## 🚨 **Критичні правила**

### **ЗАБОРОНА ручного створення файлів:**
- ❌ **НЕ створювати файли вручну** з випадковими ID
- ❌ **НЕ використовувати** `edit_file` для створення файлів в newspaper
- ❌ **НЕ придумувати ID самостійно** (0001, 0002, тощо)
- ❌ **НЕ ігнорувати** скрипти для управління ID

### **ОБОВ'ЯЗКОВЕ використання скриптів:**
- ✅ **ЗАВЖДИ використовувати** `./tools/scripts/documentation/create_newspaper_file.sh`
- ✅ **ЗАВЖДИ перевіряти** унікальність через `./tools/scripts/documentation/check_newspaper_ids.sh`
- ✅ **ЗАВЖДИ отримувати** наступний ID через `./tools/scripts/documentation/get_next_newspaper_id.sh`

---

## 📁 **Структура папок**

### **Папки для автоматичного створення:**
- `docs/newspaper/report/` - Всі звіти (плани, результати, оновлення)
- `docs/newspaper/research/` - Дослідження та аналіз
- `docs/newspaper/security_documentation_backup/` - Резервні копії безпеки

### **Системні файли** (не перейменовуються):
- `docs/newspaper/README.md` - Головний файл документації
- `docs/newspaper/_sandbox.md` - Пісочниця для тестування

### **Обмеження файлів**:
- **report/**: Максимум 10 файлів (старі переміщуються в _old)
- **research/**: Без обмежень
- **Версії**: Не дозволяються в назвах файлів

---

## 🔄 **Алгоритм створення файлів**

### **Крок 1: Перевірка поточного стану**
```bash
./tools/scripts/documentation/check_newspaper_ids.sh
```

### **Крок 2: Отримання наступного ID (опціонально)**
```bash
./tools/scripts/documentation/get_next_newspaper_id.sh [тип]
```

### **Крок 3: Створення файлу через скрипт**
```bash
./tools/scripts/documentation/create_newspaper_file.sh [тип] "[назва-файлу]"
```

### **Крок 4: Перевірка після створення**
```bash
./tools/scripts/documentation/check_newspaper_ids.sh
```

---

## 🛠️ **Команди**

### **🚀 Швидке створення файлів:**
```bash
# Створення звіту
./tools/scripts/documentation/create_newspaper_file.sh report "назва-звіту"

# Створення результату роботи
./tools/scripts/documentation/create_newspaper_file.sh work_results "назва-результату"

# Створення плану
./tools/scripts/documentation/create_newspaper_file.sh steps_plan "назва-плану"

# Створення оновлення
./tools/scripts/documentation/create_newspaper_file.sh update "назва-оновлення"

# Створення дослідження
./tools/scripts/documentation/create_newspaper_file.sh research "назва-дослідження"
```

### **🔍 Перевірка наступного ID:**
```bash
# Отримати наступний ID для конкретного типу
./tools/scripts/documentation/get_next_newspaper_id.sh report
./tools/scripts/documentation/get_next_newspaper_id.sh work_results
./tools/scripts/documentation/get_next_newspaper_id.sh steps_plan
```

### **✅ Перевірка унікальності:**
```bash
# Перевірити всі ID на унікальність
./tools/scripts/documentation/check_newspaper_ids.sh
```

### **📊 Управління файлами в report:**
```bash
# Автоматичне управління (обмеження до 10 файлів)
./tools/scripts/documentation/manage_report_files.sh auto

# Показати статистику
./tools/scripts/documentation/manage_report_files.sh stats

# Показати список файлів
./tools/scripts/documentation/manage_report_files.sh list

# Очистити старі файли в _old
./tools/scripts/documentation/manage_report_files.sh cleanup
```

---

## 📝 **Шаблони**

### **📰 Report (звіти) - Швидкий шаблон:**
```markdown
# [НАЗВА ЗВІТУ]

## 📋 **Загальна інформація**
**Дата**: YYYY-MM-DD  
**Тип роботи**: [Тестування/Документація/Аналіз]  
**Статус**: ✅ Завершено  

## 🎯 **Мета роботи**
[Опис мети]

## ✅ **Виконані завдання**
[Список завдань]

## 📊 **Результати**
[Що було досягнуто]
```

### **🔧 Work Results (розробка) - Швидкий шаблон:**
```markdown
# Звіт про [НАЗВА РОЗРОБКИ] - YYYY-MM-DD

## ✅ **Виконані завдання**
- [x] Завдання 1
- [x] Завдання 2

## 📊 **Результати**
- Створено компонент X
- Реалізовано функціонал Y

## 🚀 **Наступні кроки**
- [ ] Наступне завдання
```

### **📋 Steps Plan (плани) - Швидкий шаблон:**
```markdown
# План [НАЗВА ПЛАНУ]

**Дата**: YYYY-MM-DD  
**Основа**: [MASTER_TASKS.md](../../planning/MASTER_TASKS.md)  
**Статус**: Готовий до виконання

## 📋 **Детальний план дій**

### **ТИЖДЕНЬ 1: Назва модуля**

#### **День 1-2: Опис завдання**
**Завдання:**
- [ ] Завдання 1
- [ ] Завдання 2

**Результат:**
[Що буде досягнуто]
```

---

## 🎯 **Типи файлів та їх призначення**

### **📰 `report` - Всі звіти та аналізи**
```bash
./tools/scripts/documentation/create_newspaper_file.sh report "назва-звіту"
```
**Що включати:**
- Тестування та валідація
- Оновлення документації
- Аналізи та аудит
- Виправлення помилок
- Експерименти та дослідження

### **🔧 `work_results` - Безпосередня розробка**
```bash
./tools/scripts/documentation/create_newspaper_file.sh work_results "назва-розробки"
```
**Що включати:**
- Реалізація коду
- Створення компонентів
- Розробка функціоналу
- Інтеграція сервісів

### **📋 `steps_plan` - Плани розробки**
```bash
./tools/scripts/documentation/create_newspaper_file.sh steps_plan "назва-плану"
```
**Що включати:**
- Детальні плани наступних кроків
- Roadmap розробки
- Технічні специфікації

### **🔬 `research` - Дослідження та аналіз**
```bash
./tools/scripts/documentation/create_newspaper_file.sh research "назва-дослідження"
```
**Що включати:**
- Технічні дослідження
- Аналіз технологій
- Порівняння рішень
- Експерименти

---

## ⚡ **Швидкі команди для AI**

### **Створення звіту:**
```bash
./tools/scripts/documentation/create_newspaper_file.sh report "testing-report"
```

### **Створення результату розробки:**
```bash
./tools/scripts/documentation/create_newspaper_file.sh work_results "auth-service-implementation"
```

### **Створення плану:**
```bash
./tools/scripts/documentation/create_newspaper_file.sh steps_plan "next-development-phase"
```

### **Створення дослідження:**
```bash
./tools/scripts/documentation/create_newspaper_file.sh research "api-integration-analysis"
```

---

## 📊 **Обмеження та правила**

### **Формат назви файлу:**
```
ID_TYPE_NAME.md
```

**Приклади:**
- `0001_newspaper_upwork-api-application-checklist.md`
- `0037_newspaper_UPWORK_DEVELOPER_SETUP.md`
- `0038_update_newspaper_reorganization_report.md`
- `0039_update_system_files_correction.md`

### **Правила іменування:**
- **ID**: 4-значний унікальний ідентифікатор (0001-9999)
- **TYPE**: Тип документа (newspaper, update, work_results, steps_plan, research)
- **NAME**: Описова назва файлу (без версій)
- **Розширення**: Завжди `.md`

### **Системні файли** (без ID):
- `README.md` - Головний файл документації
- `_sandbox.md` - Пісочниця для тестування

---

**Версія**: 1.0.0  
**Дата**: 2024-12-19  
**Статус**: Активний 