# Newspaper - Документація проекту

> **Центральна папка для всієї документації проекту Upwork AI Assistant**

---

## 📋 **Зміст**

1. [Структура папки](#-структура-папки)
2. [Правила іменування файлів](#-правила-іменування-файлів)
3. [Статистика документації](#-статистика-документації)
4. [Типи документів](#-типи-документів)
5. [Команди для роботи](#-команди-для-роботи)
6. [Корисні посилання](#-корисні-посилання)
7. [Переваги нової структури](#-переваги-нової-структури)
8. [Історія змін](#-історія-змін)
9. [Пошук документів](#-пошук-документів)

---

## 📁 Структура папки

```
newspaper/
├── report/                    # Всі звіти та аналізи
│   ├── XXXX_update_name.md    # Оновлення документації
│   ├── XXXX_work_results_name.md  # Результати розробки
│   ├── XXXX_steps_plan_name.md    # Плани наступних кроків
│   └── _old/                  # Старі файли (архів)
├── research/                  # Дослідження та аналіз
│   └── XXXX_research_name.md  # Дослідження проекту
├── README.md                   # Цей файл
└── _sandbox.md                 # Пісочниця для тестування
```

---

## 📋 Правила іменування файлів

### **Формат назви**: `ID_TYPE_NAME.md`

- **ID**: 4-значний унікальний ідентифікатор (0001-9999)
- **TYPE**: Тип документа
  - `update` - Оновлення документації
  - `work_results` - Результати розробки
  - `steps_plan` - Плани наступних кроків
  - `research` - Дослідження та аналіз
  - `newspaper` - Файли в корені папки (крім системних)
- **NAME**: Описова назва файлу

### **Системні файли** (не перейменовуються):
- `README.md` - Головний файл документації
- `_sandbox.md` - Пісочниця для тестування

### **Файли в report/** (переміщені з кореня):
- `0037_newspaper_UPWORK_DEVELOPER_SETUP.md` - Налаштування розробника Upwork
- `0001_newspaper_upwork-api-application-checklist.md` - Чекліст заявки API

### **Обмеження файлів**:
- **report/**: Максимум 10 файлів (старі переміщуються в _old)
- **research/**: Без обмежень
- **Версії**: Не дозволяються в назвах файлів

### **Приклади**:
```
0032_update_mvp_launch_tasks_report.md
0031_work_results_project_completion_final_report.md
0007_next_steps_plan_steps_plan.md
0034_research_project_structure_post_fixes_analysis.md
```

---

## 📊 Статистика документації

### **Поточні показники**:
- **Загальна кількість файлів**: 35+
- **Звіти (report)**: Останні 10 файлів (стара кількість: 25 файлів)
- **Дослідження (research)**: 3 файли
- **Системні файли**: 2 файли (README.md, _sandbox.md)
- **Архів (_old)**: Старі файли з report

### **Метрики якості**:
- **Унікальність ID**: 100%
- **Послідовність ID**: 100%
- **Актуальність документації**: 95%
- **Покриття проекту**: 90%

---

## 🔧 Типи документів

### **📝 Update (Оновлення)**
**Призначення**: Оновлення документації, зміни в проекті
**Приклади**:
- `0032_update_mvp_launch_tasks_report.md`
- `0033_update_tech_stack_compliance_report.md`

### **📊 Work Results (Результати роботи)**
**Призначення**: Звіти про виконану роботу, результати розробки
**Приклади**:
- `0031_work_results_project_completion_final_report.md`
- `0030_work_results_daily_work_summary.md`

### **📋 Steps Plan (Плани кроків)**
**Призначення**: Плани наступних дій, стратегії розвитку
**Приклади**:
- `0007_next_steps_plan_steps_plan.md`
- `0006_upwork_api_integration_plan_steps_plan.md`

### **🔬 Research (Дослідження)**
**Призначення**: Аналіз, дослідження, технічні огляди
**Приклади**:
- `0034_research_project_structure_post_fixes_analysis.md`
- `0035_research_project_structure_fixes_report.md`

---

## 🛠️ Інструменти для роботи

### **Автоматичне створення файлів**:
```bash
# Створити новий звіт
./tools/scripts/documentation/create_newspaper_file.sh work_results "назва звіту"

# Створити план
./tools/scripts/documentation/create_newspaper_file.sh steps_plan "назва плану"

# Створити оновлення
./tools/scripts/documentation/create_newspaper_file.sh update "назва оновлення"

# Створити дослідження
./tools/scripts/documentation/create_newspaper_file.sh research "назва дослідження"
```

### **Управління файлами в report**:
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

### **Перевірка та виправлення**:
```bash
# Перевірка всіх ID
./tools/scripts/documentation/check_newspaper_ids.sh

# Виправлення проблем
./tools/scripts/documentation/fix_newspaper_ids.sh

# Отримання наступного ID
./tools/scripts/documentation/get_next_newspaper_id.sh work_results
```

---

## 📚 Корисні посилання

### **Документація проекту**:
- **[Головна документація](../README.md)**
- **[Планування проекту](../planning/README.md)**
- **[AI інструкції](../instruction_ai/README.md)**

### **Стандарти документації**:
- **[Управління файлами](../instruction_ai/FILE_MANAGEMENT.md)**
- **[Робочий процес](../instruction_ai/WORKFLOW_PROCESS.md)**
- **[Чекліст відповідності](../instruction_ai/COMPLIANCE_CHECKLIST.md)**

### **Інструменти**:
- **[Скрипти документації](../../tools/scripts/documentation/README.md)**
- **[Перевірка ID](../../tools/scripts/documentation/check_newspaper_ids.sh)**
- **[Створення файлів](../../tools/scripts/documentation/create_newspaper_file.sh)**
- **[Управління report файлами](../../tools/scripts/documentation/manage_report_files.sh)**

---

## 🎯 Переваги нової структури

### **✅ Спрощення**:
- **Одна папка** для всіх звітів
- **Чіткі правила** іменування
- **Уніфікована структура**

### **✅ Організація**:
- **Логічне групування** за типами
- **Легкий пошук** файлів
- **Автоматична нумерація**

### **✅ Масштабованість**:
- **Гнучка система** ID
- **Підтримка нових типів**
- **Зворотна сумісність**

---

## 📈 Історія змін

### **Версія 2.0.0 (2024-12-19)**:
- ✅ Об'єднано папки `update/`, `work_results/`, `steps_plan/` в `report/`
- ✅ Перейменовано `for_you_with_love/` в `research/`
- ✅ Впроваджено новий формат іменування: `ID_TYPE_NAME.md`
- ✅ Додано ID до всіх файлів в `newspaper/`
- ✅ Оновлено всі інструкції та скрипти

### **Версія 1.0.0 (2024-07-30)**:
- ✅ Створено базову структуру
- ✅ Впроваджено систему ID
- ✅ Налаштовано автоматизацію

---

## 🔍 Пошук документів

### **За типом**:
```bash
# Знайти всі оновлення
find docs/newspaper/report -name "*_update_*.md"

# Знайти всі результати роботи
find docs/newspaper/report -name "*_work_results_*.md"

# Знайти всі плани
find docs/newspaper/report -name "*_steps_plan_*.md"

# Знайти всі дослідження
find docs/newspaper/research -name "*_research_*.md"
```

### **За ID**:
```bash
# Знайти файл за ID
find docs/newspaper -name "0032_*.md"
```

### **За датою**:
```bash
# Знайти файли за датою
find docs/newspaper -name "*2024-12-19*.md"
```

---

**Статус**: Активний  
**Версія**: 2.0.0  
**Останнє оновлення**: 2024-12-19  
**Автор**: AI Assistant 