# 📚 Documentation Scripts - Управління документацією

> **Скрипти для автоматизації роботи з документацією проекту**

---

## 📋 Огляд

Папка `documentation/` містить скрипти для управління документацією проекту:

- **Створення звітів** - автоматичне створення файлів звітів
- **Управління ID** - генерація та перевірка унікальних ID
- **Оновлення README** - автоматичне оновлення документації
- **Перевірка структури** - валідація документації

---

## 📁 Доступні скрипти

### **create_newspaper_file.sh** - Створення звітів
**Призначення**: Автоматичне створення файлів звітів з унікальними ID

**Використання:**
```bash
# Створення звіту
./tools/scripts/documentation/create_newspaper_file.sh report "назва-звіту"

# Створення плану кроків
./tools/scripts/documentation/create_newspaper_file.sh steps_plan "назва-плану"

# Створення оновлення
./tools/scripts/documentation/create_newspaper_file.sh update "назва-оновлення"

# Створення результатів роботи
./tools/scripts/documentation/create_newspaper_file.sh work_results "назва-результатів"
```

**Функціональність:**
- ✅ **Автоматична генерація ID** - послідовні унікальні ідентифікатори
- ✅ **Створення структури** - готовий шаблон файлу
- ✅ **Валідація назви** - перевірка на відповідність стандартам
- ✅ **Логування** - детальні логи процесу створення
- ✅ **Підтримка типів** - report, steps_plan, update, work_results

**Приклад використання:**
```bash
./tools/scripts/documentation/create_newspaper_file.sh report "api-integration-completed"
# Результат: docs/newspaper/report/0062-api-integration-completed.md
```

### **get_next_newspaper_id.sh** - Генерація ID
**Призначення**: Отримання наступного унікального ID для файлів

**Використання:**
```bash
# Отримання наступного ID
./tools/scripts/documentation/get_next_newspaper_id.sh

# Отримання ID для конкретної папки
./tools/scripts/documentation/get_next_newspaper_id.sh report
./tools/scripts/documentation/get_next_newspaper_id.sh steps_plan
./tools/scripts/documentation/get_next_newspaper_id.sh update
```

**Функціональність:**
- ✅ **Аналіз існуючих файлів** - сканування папок на наявність ID
- ✅ **Послідовна нумерація** - ID збільшується на 1
- ✅ **Підтримка папок** - різні ID для різних типів файлів
- ✅ **Валідація** - перевірка унікальності ID

**Приклад використання:**
```bash
./tools/scripts/documentation/get_next_newspaper_id.sh
# Результат: 0063
```

### **check_newspaper_ids.sh** - Перевірка ID
**Призначення**: Перевірка унікальності та послідовності ID

**Використання:**
```bash
# Перевірка всіх ID
./tools/scripts/documentation/check_newspaper_ids.sh

# Перевірка конкретної папки
./tools/scripts/documentation/check_newspaper_ids.sh report
./tools/scripts/documentation/check_newspaper_ids.sh steps_plan
```

**Функціональність:**
- ✅ **Перевірка унікальності** - виявлення дублікатів ID
- ✅ **Перевірка послідовності** - виявлення пропущених ID
- ✅ **Статистика** - кількість файлів та ID
- ✅ **Детальний звіт** - повна інформація про проблеми

**Приклад виводу:**
```bash
./tools/scripts/documentation/check_newspaper_ids.sh
# Результат:
# ✅ Всі ID унікальні
# 📊 Статистика:
#   - report: 45 файлів (ID 0001-0045)
#   - steps_plan: 12 файлів (ID 0001-0012)
#   - update: 8 файлів (ID 0001-0008)
```

### **fix_newspaper_ids.sh** - Виправлення ID
**Призначення**: Автоматичне виправлення проблем з ID

**Використання:**
```bash
# Виправлення всіх проблем
./tools/scripts/documentation/fix_newspaper_ids.sh

# Виправлення конкретної папки
./tools/scripts/documentation/fix_newspaper_ids.sh report
```

**Функціональність:**
- ✅ **Автоматичне перейменування** - виправлення дублікатів
- ✅ **Послідовна нумерація** - заповнення пропусків
- ✅ **Backup створення** - резервні копії перед змінами
- ✅ **Безпечне виправлення** - перевірка перед застосуванням

### **update_readme.sh** - Оновлення README
**Призначення**: Автоматичне оновлення README файлів

**Використання:**
```bash
# Оновлення всіх README
./tools/scripts/documentation/update_readme.sh

# Оновлення конкретного README
./tools/scripts/documentation/update_readme.sh README.md
./tools/scripts/documentation/update_readme.sh app/README.md
```

**Функціональність:**
- ✅ **Автоматичне оновлення дат** - поточна дата
- ✅ **Перевірка посилань** - валідація внутрішніх посилань
- ✅ **Оновлення статистики** - актуальні метрики
- ✅ **Форматування** - стандартизація структури

### **quick_report.sh** - Швидке створення звітів
**Призначення**: Швидке створення звітів з описом

**Використання:**
```bash
# Швидкий звіт з описом
./tools/scripts/documentation/quick_report.sh update "security-fix" "Виправлено вразливість в auth"
./tools/scripts/documentation/quick_report.sh work_results "api-integration" "Інтеграція з Upwork API"
```

**Функціональність:**
- ✅ **Швидке створення** - мінімальний шаблон
- ✅ **Автоматичний ID** - унікальна нумерація
- ✅ **Готовий шаблон** - структурований контент
- ✅ **Час створення** - точний час

### **background_report.sh** - Фонове створення
**Призначення**: Створення звітів в фоновому режимі

**Використання:**
```bash
# Створення в фоновому режимі
./tools/scripts/documentation/background_report.sh update "quick-fix" "Швидке виправлення" &
./tools/scripts/documentation/background_report.sh work_results "daily-work" "Щоденна робота" &
```

**Функціональність:**
- ✅ **Фонове виконання** - не блокує термінал
- ✅ **Мінімальний вивід** - короткі повідомлення
- ✅ **Швидке створення** - оптимізований процес
- ✅ **Автоматичний ID** - унікальна нумерація

### **fast_report.sh** - Створення за шаблонами
**Призначення**: Створення звітів за попередньо визначеними шаблонами

**Використання:**
```bash
# Звіт про безпеку
./tools/scripts/documentation/fast_report.sh security "auth-vulnerability-fix"

# Звіт про виправлення багу
./tools/scripts/documentation/fast_report.sh bugfix "api-endpoint-error"

# Звіт про нову функцію
./tools/scripts/documentation/fast_report.sh feature "oauth-integration"

# Щоденний звіт
./tools/scripts/documentation/fast_report.sh daily "daily-work"

# Тижневий звіт
./tools/scripts/documentation/fast_report.sh weekly "weekly-summary"
```

**Функціональність:**
- ✅ **Готові шаблони** - 5 типів звітів
- ✅ **Спеціалізований контент** - відповідно до типу
- ✅ **Швидке створення** - один параметр
- ✅ **Професійний вигляд** - структуровані шаблони

---

## 🚀 Швидкий старт

### **Створення нового звіту (повний):**
```bash
# 1. Створити звіт
./tools/scripts/documentation/create_newspaper_file.sh report "назва-звіту"

# 2. Перевірити ID
./tools/scripts/documentation/check_newspaper_ids.sh

# 3. Оновити README
./tools/scripts/documentation/update_readme.sh
```

### **Швидке створення звітів:**
```bash
# Швидкий звіт з описом
./tools/scripts/documentation/quick_report.sh update "security-fix" "Виправлено вразливість в auth"

# Фонове створення
./tools/scripts/documentation/background_report.sh update "quick-fix" "Швидке виправлення" &

# Створення за шаблоном
./tools/scripts/documentation/fast_report.sh security "auth-vulnerability-fix"
./tools/scripts/documentation/fast_report.sh bugfix "api-endpoint-error"
./tools/scripts/documentation/fast_report.sh feature "oauth-integration"
./tools/scripts/documentation/fast_report.sh daily "daily-work"
./tools/scripts/documentation/fast_report.sh weekly "weekly-summary"
```

### **Перевірка документації:**
```bash
# Перевірка всіх ID
./tools/scripts/documentation/check_newspaper_ids.sh

# Виправлення проблем
./tools/scripts/documentation/fix_newspaper_ids.sh

# Оновлення всіх README
./tools/scripts/documentation/update_readme.sh
```

---

## 📊 Статистика документації

### **Поточні показники:**
- **Загальна кількість файлів**: 150+
- **Звіти (report)**: 45 файлів
- **Плани кроків (steps_plan)**: 12 файлів
- **Оновлення (update)**: 8 файлів
- **Результати роботи (work_results)**: 15 файлів

### **Метрики якості:**
- **Унікальність ID**: 100%
- **Послідовність ID**: 100%
- **Актуальність README**: 95%
- **Покриття документацією**: 90%

---

## 🔧 Налаштування

### **Конфігурація ID:**
```bash
# Формат ID: XXXX (4 цифри)
# Діапазон: 0001-9999
# Типи файлів:
#   - report: 0001-9999
#   - steps_plan: 0001-9999
#   - update: 0001-9999
#   - work_results: 0001-9999
```

### **Шаблони файлів:**
```bash
# Структура звіту
docs/newspaper/report/XXXX_update_назва-звіту.md
docs/newspaper/report/XXXX_work_results_назва-результатів.md
docs/newspaper/report/XXXX_steps_plan_назва-плану.md

# Структура дослідження
docs/newspaper/research/XXXX_research_назва-дослідження.md
```

---

## 📚 Документація

### **Корисні посилання:**
- **[Головна документація проекту](../../../docs/README.md)**
- **[Newspaper документація](../../../docs/newspaper/README.md)**
- **[AI інструкції](../../../docs/instruction_ai/README.md)**

### **Стандарти документації:**
- **[Управління файлами](../../../docs/instruction_ai/FILE_MANAGEMENT.md)**
- **[Робочий процес](../../../docs/instruction_ai/WORKFLOW_PROCESS.md)**

---

## 🎯 Переваги

### **✅ Автоматизація:**
- **Один скрипт** для створення файлів
- **Автоматична генерація** унікальних ID
- **Стандартизовані шаблони** для всіх типів

### **✅ Надійність:**
- **Перевірка унікальності** ID
- **Backup перед змінами**
- **Валідація структури**

### **✅ Зручність:**
- **Простий інтерфейс** команд
- **Детальна документація**
- **Приклади використання**

---

**Статус**: Активний  
**Версія**: 1.0.0  
**Останнє оновлення**: 2025-01-30 