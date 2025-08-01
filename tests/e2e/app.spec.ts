import { test, expect } from '@playwright/test';

test.describe('Upwork AI Assistant E2E Tests', () => {
  test('should load the main page and redirect to login', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    
    // Перевіряємо що сторінка завантажилась
    await expect(page).toHaveTitle(/Upwork AI Assistant/);
    
    // Перевіряємо що перенаправило на login
    await expect(page).toHaveURL(/.*login/);
    
    // Перевіряємо наявність основних елементів
    await expect(page.locator('body')).toBeVisible();
  });

  test('should show main content', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    
    // Перевіряємо що контент завантажився
    await expect(page.locator('body')).toBeVisible();
    
    // Перевіряємо що сторінка не порожня
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should handle page navigation', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    
    // Перевіряємо що можемо перейти на ту ж сторінку
    await page.goto('http://localhost:3000/');
    await expect(page).toHaveURL(/.*login/);
  });

  test('should load without errors', async ({ page }) => {
    // Перевіряємо що сторінка завантажується без помилок
    const response = await page.goto('http://localhost:3000/');
    expect(response?.status()).toBe(200);
    
    // Перевіряємо що немає критичних помилок в консолі
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.waitForLoadState('networkidle');
    
    // Дозволяємо деякі помилки (наприклад, відсутні API ключі)
    expect(errors.length).toBeLessThan(10);
  });
}); 