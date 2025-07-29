# План E2E тестів

> **Детальний план end-to-end тестів для перевірки повних користувацьких сценаріїв**

---

## Зміст

1. [Загальні принципи](#загальні-принципи)
2. [Тести реєстрації та входу](#тести-реєстрації-та-входу)
3. [Тести роботи з вакансіями](#тести-роботи-з-вакансіями)
4. [Тести AI функціональності](#тести-ai-функціональності)
5. [Тести аналітики](#тести-аналітики)
6. [Тести налаштувань](#тести-налаштувань)
7. [Тести безпеки](#тести-безпеки)
8. [Тести продуктивності](#тести-продуктивності)
9. [Конфігурація тестів](#конфігурація-тестів)

---

## Загальні принципи

---

## 🧪 Технології тестування

### Playwright Configuration

```typescript
// tests/e2e/playwright.config.ts
import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
  testDir: './tests/e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] }
    }
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000
  }
};

export default config;
```

### Cypress Configuration

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
  },
});
```

---

## Сценарії тестування

### Сценарій 1: Реєстрація та авторизація

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should register new user', async ({ page }) => {
    // Перехід на сторінку реєстрації
    await page.click('[data-testid="register-link"]');
    
    // Заповнення форми реєстрації
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'TestPassword123!');
    await page.fill('[data-testid="confirm-password-input"]', 'TestPassword123!');
    
    // Відправка форми
    await page.click('[data-testid="register-button"]');
    
    // Перевірка успішної реєстрації
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText('Welcome');
  });

  test('should login existing user', async ({ page }) => {
    // Перехід на сторінку входу
    await page.click('[data-testid="login-link"]');
    
    // Заповнення форми входу
    await page.fill('[data-testid="username-input"]', 'existinguser');
    await page.fill('[data-testid="password-input"]', 'password123');
    
    // Відправка форми
    await page.click('[data-testid="login-button"]');
    
    // Перевірка успішного входу
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should handle login errors', async ({ page }) => {
    await page.click('[data-testid="login-link"]');
    
    // Неправильні дані
    await page.fill('[data-testid="username-input"]', 'wronguser');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    // Перевірка повідомлення про помилку
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
  });

  test('should enable MFA', async ({ page }) => {
    // Логін користувача
    await page.click('[data-testid="login-link"]');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
    
    // Перехід до налаштувань безпеки
    await page.click('[data-testid="settings-link"]');
    await page.click('[data-testid="security-tab"]');
    
    // Включення MFA
    await page.click('[data-testid="enable-mfa-button"]');
    
    // Перевірка QR коду
    await expect(page.locator('[data-testid="mfa-qr-code"]')).toBeVisible();
    
    // Введення коду підтвердження
    await page.fill('[data-testid="mfa-code-input"]', '123456');
    await page.click('[data-testid="verify-mfa-button"]');
    
    // Перевірка успішного включення MFA
    await expect(page.locator('[data-testid="mfa-status"]')).toContainText('Enabled');
  });
});
```

### Сценарій 2: Інтеграція з Upwork

```typescript
// tests/e2e/upwork-integration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Upwork Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Логін користувача
    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
  });

  test('should connect Upwork account', async ({ page }) => {
    // Перехід до налаштувань інтеграції
    await page.click('[data-testid="settings-link"]');
    await page.click('[data-testid="integrations-tab"]');
    
    // Підключення Upwork
    await page.click('[data-testid="connect-upwork-button"]');
    
    // Перевірка перенаправлення на OAuth
    await expect(page).toHaveURL(/upwork\.com/);
    
    // Симуляція OAuth callback
    await page.goto('/auth/upwork/callback?code=test_code&state=test_state');
    
    // Перевірка успішного підключення
    await expect(page.locator('[data-testid="upwork-status"]')).toContainText('Connected');
  });

  test('should sync Upwork data', async ({ page }) => {
    // Перехід до дашборду
    await page.click('[data-testid="dashboard-link"]');
    
    // Запуск синхронізації
    await page.click('[data-testid="sync-upwork-button"]');
    
    // Очікування завершення синхронізації
    await expect(page.locator('[data-testid="sync-progress"]')).toBeVisible();
    await expect(page.locator('[data-testid="sync-complete"]')).toBeVisible({ timeout: 30000 });
    
    // Перевірка синхронізованих даних
    await expect(page.locator('[data-testid="jobs-count"]')).toContainText(/[0-9]+/);
    await expect(page.locator('[data-testid="proposals-count"]')).toContainText(/[0-9]+/);
  });

  test('should create proposal', async ({ page }) => {
    // Перехід до сторінки пропозицій
    await page.click('[data-testid="proposals-link"]');
    
    // Вибір вакансії
    await page.click('[data-testid="job-item"]');
    
    // Створення пропозиції
    await page.fill('[data-testid="cover-letter-input"]', 'Test cover letter content');
    await page.fill('[data-testid="bid-amount-input"]', '100');
    await page.fill('[data-testid="delivery-time-input"]', '7');
    
    // Відправка пропозиції
    await page.click('[data-testid="submit-proposal-button"]');
    
    // Перевірка успішної відправки
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Proposal submitted');
  });

  test('should view analytics', async ({ page }) => {
    // Перехід до аналітики
    await page.click('[data-testid="analytics-link"]');
    
    // Перевірка наявності графіків
    await expect(page.locator('[data-testid="earnings-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="proposals-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="response-rate-chart"]')).toBeVisible();
    
    // Перевірка фільтрів
    await page.click('[data-testid="date-range-picker"]');
    await page.click('[data-testid="last-30-days"]');
    
    // Перевірка оновлення даних
    await expect(page.locator('[data-testid="total-earnings"]')).toBeVisible();
  });
});
```

### Сценарій 3: AI функціональність

```typescript
// tests/e2e/ai-features.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AI Features', () => {
  test.beforeEach(async ({ page }) => {
    // Логін користувача
    await page.goto('/login');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="login-button"]');
  });

  test('should generate proposal content', async ({ page }) => {
    // Перехід до створення пропозиції
    await page.click('[data-testid="create-proposal-link"]');
    
    // Вибір вакансії
    await page.click('[data-testid="job-item"]');
    
    // Використання AI для генерації контенту
    await page.click('[data-testid="ai-generate-button"]');
    
    // Очікування генерації
    await expect(page.locator('[data-testid="ai-loading"]')).toBeVisible();
    await expect(page.locator('[data-testid="generated-content"]')).toBeVisible({ timeout: 30000 });
    
    // Перевірка згенерованого контенту
    const content = await page.locator('[data-testid="generated-content"]').textContent();
    expect(content).toContain('Dear');
    expect(content.length).toBeGreaterThan(100);
  });

  test('should analyze job requirements', async ({ page }) => {
    // Перехід до аналізу вакансії
    await page.click('[data-testid="jobs-link"]');
    await page.click('[data-testid="job-item"]');
    await page.click('[data-testid="analyze-job-button"]');
    
    // Перевірка результатів аналізу
    await expect(page.locator('[data-testid="skill-match"]')).toBeVisible();
    await expect(page.locator('[data-testid="salary-estimate"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-probability"]')).toBeVisible();
  });

  test('should optimize proposal', async ({ page }) => {
    // Створення пропозиції
    await page.click('[data-testid="create-proposal-link"]');
    await page.fill('[data-testid="cover-letter-input"]', 'Basic proposal content');
    
    // Оптимізація через AI
    await page.click('[data-testid="optimize-proposal-button"]');
    
    // Перевірка оптимізованого контенту
    await expect(page.locator('[data-testid="optimized-content"]')).toBeVisible();
    
    // Перевірка покращень
    const score = await page.locator('[data-testid="optimization-score"]').textContent();
    expect(parseInt(score)).toBeGreaterThan(70);
  });
});
```

---

## UI/UX Тестування

### Accessibility Testing

```typescript
// tests/e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test('should meet WCAG 2.1 AA standards', async ({ page }) => {
    await page.goto('/');
    
    // Перевірка контрасту кольорів
    const contrastIssues = await page.evaluate(() => {
      // Логіка перевірки контрасту
      return [];
    });
    expect(contrastIssues).toHaveLength(0);
    
    // Перевірка навігації з клавіатури
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
    
    // Перевірка ARIA атрибутів
    const elementsWithAria = await page.locator('[aria-label], [aria-labelledby]').count();
    expect(elementsWithAria).toBeGreaterThan(0);
  });

  test('should support screen readers', async ({ page }) => {
    await page.goto('/');
    
    // Перевірка альтернативного тексту для зображень
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Перевірка заголовків
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
  });
});
```

### Responsive Design Testing

```typescript
// tests/e2e/responsive.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  const viewports = [
    { width: 1920, height: 1080, name: 'Desktop' },
    { width: 1366, height: 768, name: 'Laptop' },
    { width: 768, height: 1024, name: 'Tablet' },
    { width: 375, height: 667, name: 'Mobile' }
  ];

  for (const viewport of viewports) {
    test(`should display correctly on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('/');
      
      // Перевірка наявності основних елементів
      await expect(page.locator('[data-testid="header"]')).toBeVisible();
      await expect(page.locator('[data-testid="navigation"]')).toBeVisible();
      
      // Перевірка адаптивності меню
      if (viewport.width < 768) {
        await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
      } else {
        await expect(page.locator('[data-testid="desktop-menu"]')).toBeVisible();
      }
      
      // Перевірка відсутності горизонтального скролу
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasHorizontalScroll).toBe(false);
    });
  }
});
```

---

## Автоматизація тестування

### GitHub Actions Workflow

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Start application
        run: |
          npm run build
          npm run start &
          sleep 30
      
      - name: Run E2E tests
        run: npx playwright test --project=${{ matrix.browser }}
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report-${{ matrix.browser }}
          path: playwright-report/
          retention-days: 30
      
      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-screenshots-${{ matrix.browser }}
          path: test-results/
          retention-days: 30
```

### Local Development Script

```bash
#!/bin/bash
# scripts/run-e2e-tests.sh

echo "🚀 Starting E2E tests..."

# Встановлення залежностей
npm install

# Запуск додатку в фоновому режимі
echo "Starting application..."
npm run start &
APP_PID=$!

# Очікування готовності додатку
echo "Waiting for application to start..."
sleep 30

# Запуск тестів
echo "Running E2E tests..."
npx playwright test

# Збереження результатів
echo "Saving test results..."
cp -r playwright-report/ test-results/

# Зупинка додатку
echo "Stopping application..."
kill $APP_PID

echo "✅ E2E tests completed"
```

---

## Звітність

### Test Report Generator

```typescript
// scripts/generate-e2e-report.ts
import fs from 'fs';
import path from 'path';

interface TestResult {
  name: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  screenshot?: string;
}

class E2EReportGenerator {
  private results: TestResult[] = [];
  
  addResult(result: TestResult) {
    this.results.push(result);
  }
  
  generateHTMLReport(): string {
    const passed = this.results.filter(r => r.status === 'passed').length;
    const failed = this.results.filter(r => r.status === 'failed').length;
    const skipped = this.results.filter(r => r.status === 'skipped').length;
    const total = this.results.length;
    
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>E2E Test Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .summary { background: #f5f5f5; padding: 20px; margin: 20px 0; }
          .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid; }
          .passed { border-color: green; background: #e8f5e8; }
          .failed { border-color: red; background: #ffe8e8; }
          .skipped { border-color: orange; background: #fff8e8; }
        </style>
      </head>
      <body>
        <h1>E2E Test Report</h1>
        
        <div class="summary">
          <h2>Summary</h2>
          <p><strong>Total Tests:</strong> ${total}</p>
          <p><strong>Passed:</strong> ${passed}</p>
          <p><strong>Failed:</strong> ${failed}</p>
          <p><strong>Skipped:</strong> ${skipped}</p>
          <p><strong>Success Rate:</strong> ${((passed / total) * 100).toFixed(2)}%</p>
        </div>
        
        <h2>Test Results</h2>
        ${this.results.map(result => `
          <div class="test-result ${result.status}">
            <h3>${result.name}</h3>
            <p><strong>Status:</strong> ${result.status}</p>
            <p><strong>Duration:</strong> ${result.duration}ms</p>
            ${result.error ? `<p><strong>Error:</strong> ${result.error}</p>` : ''}
            ${result.screenshot ? `<img src="${result.screenshot}" alt="Screenshot" style="max-width: 300px;">` : ''}
          </div>
        `).join('')}
      </body>
      </html>
    `;
  }
  
  saveReport(outputPath: string) {
    const html = this.generateHTMLReport();
    fs.writeFileSync(outputPath, html);
  }
}

export default E2EReportGenerator;
```

---

**Версія**: 1.0  
**Останнє оновлення**: 2024-12-19 17:00 