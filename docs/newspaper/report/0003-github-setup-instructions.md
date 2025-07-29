# GitHub Setup Instructions

## Створення репозиторію на GitHub

### Крок 1: Створення нового репозиторію

1. Перейдіть на [GitHub](https://github.com)
2. Увійдіть в свій акаунт
3. Натисніть кнопку **"New"** або **"+"** → **"New repository"**

### Крок 2: Налаштування репозиторію

**Назва репозиторію:** `upwork-web-app`

**Опис:** `AI-Powered Freelancing Platform for Upwork Automation`

**Налаштування:**
- ✅ **Public** (рекомендовано для open source)
- ❌ **Private** (якщо потрібна приватність)

**Ініціалізація:**
- ❌ **Add a README file** (у нас вже є)
- ❌ **Add .gitignore** (у нас вже є)
- ❌ **Choose a license** (у нас вже є)

### Крок 3: Створення репозиторію

Натисніть **"Create repository"**

### Крок 4: Підключення локального репозиторію

Після створення репозиторію, виконайте команди:

```bash
# Перевірте поточний remote
git remote -v

# Якщо потрібно змінити URL
git remote set-url origin https://github.com/YOUR_USERNAME/upwork-web-app.git

# Відправте код на GitHub
git push -u origin main
```

### Крок 5: Перевірка

1. Перейдіть на сторінку репозиторію
2. Переконайтеся, що всі файли завантажені
3. Перевірте README.md на головній сторінці

---

## Налаштування GitHub Pages (опціонально)

### Для документації:

1. Перейдіть в **Settings** репозиторію
2. Прокрутіть до **Pages**
3. В **Source** виберіть **Deploy from a branch**
4. Виберіть **main** branch та папку **/docs**
5. Натисніть **Save**

---

## Налаштування GitHub Actions (опціонально)

### Для CI/CD:

Створіть файл `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r app/backend/requirements.txt
    
    - name: Run tests
      run: |
        pytest app/backend/tests/
```

---

## Налаштування Issues та Projects

### Створення шаблонів:

1. **Issue Template:**
   - Створіть `.github/ISSUE_TEMPLATE/bug_report.md`
   - Створіть `.github/ISSUE_TEMPLATE/feature_request.md`

2. **Pull Request Template:**
   - Створіть `.github/pull_request_template.md`

---

## Налаштування Branch Protection

1. Перейдіть в **Settings** → **Branches**
2. Додайте rule для **main** branch:
   - ✅ **Require pull request reviews**
   - ✅ **Require status checks to pass**
   - ✅ **Require branches to be up to date**

---

## Налаштування Collaborators

1. Перейдіть в **Settings** → **Collaborators**
2. Додайте співробітників за їх GitHub username
3. Виберіть відповідні права доступу

---

## Корисні посилання

- [GitHub Guides](https://guides.github.com/)
- [GitHub Pages](https://pages.github.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Security](https://docs.github.com/en/github/managing-security-vulnerabilities)

---

**Дата створення:** 2024-12-19  
**Статус:** Готово до виконання 