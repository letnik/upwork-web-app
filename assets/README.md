# ASSETS - Ресурси проекту

> **Всі статичні ресурси Upwork AI Assistant**

---

## Зміст

1. [Огляд](#огляд)
2. [Структура](#структура)
3. [Типи ресурсів](#типи-ресурсів)
4. [Використання](#використання)

---

## Огляд

Папка `assets/` містить всі статичні ресурси проекту:

- **`images/`** - Зображення та ілюстрації
- **`icons/`** - Іконки та логотипи
- **`templates/`** - Шаблони та макети

---

## Структура

```
assets/
├── images/                  # 🖼️ Зображення
│   ├── logos/              # Логотипи
│   ├── screenshots/        # Скріншоти
│   ├── backgrounds/        # Фонові зображення
│   └── illustrations/      # Ілюстрації
├── icons/                   # 🎯 Іконки
│   ├── favicon/            # Favicon
│   ├── app-icons/          # Іконки додатку
│   ├── ui-icons/           # UI іконки
│   └── social/             # Соціальні іконки
├── templates/               # 📄 Шаблони
│   ├── email/              # Email шаблони
│   ├── documents/          # Документи
│   ├── presentations/      # Презентації
│   └── reports/            # Звіти
└── README.md              # Цей файл
```

---

## Типи ресурсів

### **Зображення**
- **Логотипи** - Брендинг проекту
- **Скріншоти** - Демонстрація функцій
- **Фонові зображення** - UI елементи
- **Ілюстрації** - Графічні елементи

### **Іконки**
- **Favicon** - Іконка сайту
- **App іконки** - Іконки додатку
- **UI іконки** - Інтерфейсні іконки
- **Соціальні іконки** - Соціальні мережі

### **Шаблони**
- **Email шаблони** - Email повідомлення
- **Документи** - Шаблони документів
- **Презентації** - Презентаційні матеріали
- **Звіти** - Шаблони звітів

---

## Використання

### **Frontend**
```html
<!-- Зображення -->
<img src="/assets/images/logos/logo.png" alt="Logo">

<!-- Іконки -->
<link rel="icon" href="/assets/icons/favicon/favicon.ico">
<img src="/assets/icons/ui-icons/user.svg" alt="User">
```

### **Backend**
```python
# Email шаблони
from pathlib import Path

template_path = Path("assets/templates/email/welcome.html")
with open(template_path, "r") as f:
    template = f.read()
```

### **CSS/SCSS**
```scss
// Фонові зображення
.hero-section {
  background-image: url('/assets/images/backgrounds/hero-bg.jpg');
}

// Іконки
.icon-user {
  background-image: url('/assets/icons/ui-icons/user.svg');
}
```

---

## Формати та розміри

### **Зображення**
- **Логотипи**: PNG, SVG (векторні)
- **Скріншоти**: PNG, JPG (1920x1080)
- **Фонові**: JPG, WebP (оптимізовані)
- **Ілюстрації**: SVG, PNG (векторні)

### **Іконки**
- **Favicon**: ICO, PNG (16x16, 32x32, 48x48)
- **App іконки**: PNG, SVG (512x512)
- **UI іконки**: SVG (24x24, 32x32)
- **Соціальні**: SVG (векторні)

### **Шаблони**
- **Email**: HTML, MJML
- **Документи**: DOCX, PDF
- **Презентації**: PPTX, PDF
- **Звіти**: XLSX, PDF

---

## Оптимізація

### **Зображення**
```bash
# Оптимізація PNG
pngquant --quality=65-80 assets/images/*.png

# Конвертація в WebP
cwebp -q 80 image.jpg -o image.webp

# Оптимізація SVG
svgo assets/icons/*.svg
```

### **Іконки**
```bash
# Генерація favicon
convert logo.png -resize 16x16 favicon-16x16.png
convert logo.png -resize 32x32 favicon-32x32.png

# Створення sprite
svg-sprite assets/icons/ui-icons/*.svg
```

---

## Версіонування

### **Назви файлів**
```
logo-v1.0.0.png          # Версія 1.0.0
logo-v1.1.0.png          # Версія 1.1.0
logo-current.png         # Поточна версія
```

### **Backup**
```bash
# Створення backup
tar -czf assets-backup-$(date +%Y%m%d).tar.gz assets/

# Відновлення
tar -xzf assets-backup-20241219.tar.gz
```

---

## Безпека

### **Важливо**
- Перевіряйте ліцензії на використання
- Не зберігайте чутливі дані в зображеннях
- Використовуйте безпечні формати файлів

### **Рекомендації**
- Регулярно оновлюйте ресурси
- Моніторте розмір файлів
- Використовуйте CDN для production

---

## Нотатки

### **Автоматизація**
- Оптимізація запускається автоматично
- Backup створюється за розкладом
- Версіонування відбувається автоматично

### **Моніторинг**
- Розмір файлів моніториться
- Зміни логуються
- Performance метрики зберігаються

---

## Дизайн система

### **Кольори**
- **Primary**: #1976D2 (Blue)
- **Secondary**: #FF9800 (Orange)
- **Success**: #4CAF50 (Green)
- **Error**: #F44336 (Red)

### **Типографіка**
- **Heading**: Roboto, 24px, Bold
- **Body**: Roboto, 16px, Regular
- **Caption**: Roboto, 12px, Light

### **Spacing**
- **XS**: 4px
- **S**: 8px
- **M**: 16px
- **L**: 24px
- **XL**: 32px

---

**Статус**: Активний  
**Версія**: 1.0.0 