"""
E2E тести для Auth Flow з Playwright
"""

import pytest
from playwright.sync_api import sync_playwright, Page, expect
import time


class TestAuthFlow:
    """E2E тести для процесу авторизації"""
    
    @pytest.fixture(scope="class")
    def browser(self):
        """Фікстура для браузера"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            yield browser
            browser.close()
    
    @pytest.fixture
    def page(self, browser):
        """Фікстура для сторінки"""
        page = browser.new_page()
        yield page
        page.close()
    
    def test_user_registration_flow(self, page: Page):
        """Тест процесу реєстрації користувача"""
        # Переходимо на сторінку реєстрації
        page.goto("http://localhost:3000/register")
        
        # Заповнюємо форму реєстрації
        page.fill('[data-testid="email"]', "test@example.com")
        page.fill('[data-testid="password"]', "password123")
        page.fill('[data-testid="confirm-password"]', "password123")
        page.fill('[data-testid="first-name"]', "Іван")
        page.fill('[data-testid="last-name"]', "Петренко")
        
        # Натискаємо кнопку реєстрації
        page.click('[data-testid="register-button"]')
        
        # Перевіряємо що перейшли на dashboard
        expect(page).to_have_url("http://localhost:3000/dashboard")
        
        # Перевіряємо привітання
        expect(page.locator('[data-testid="welcome-message"]')).to_be_visible()
        expect(page.locator('[data-testid="welcome-message"]')).to_contain_text("Іван")
    
    def test_user_login_flow(self, page: Page):
        """Тест процесу входу користувача"""
        # Переходимо на сторінку входу
        page.goto("http://localhost:3000/login")
        
        # Заповнюємо форму входу
        page.fill('[data-testid="email"]', "test@example.com")
        page.fill('[data-testid="password"]', "password123")
        
        # Натискаємо кнопку входу
        page.click('[data-testid="login-button"]')
        
        # Перевіряємо що перейшли на dashboard
        expect(page).to_have_url("http://localhost:3000/dashboard")
        
        # Перевіряємо що користувач авторизований
        expect(page.locator('[data-testid="user-menu"]')).to_be_visible()
    
    def test_password_reset_flow(self, page: Page):
        """Тест процесу скидання пароля"""
        # Переходимо на сторінку входу
        page.goto("http://localhost:3000/login")
        
        # Натискаємо "Забули пароль?"
        page.click('[data-testid="forgot-password-link"]')
        
        # Перевіряємо що перейшли на сторінку скидання пароля
        expect(page).to_have_url("http://localhost:3000/reset-password")
        
        # Вводимо email
        page.fill('[data-testid="email"]', "test@example.com")
        
        # Натискаємо кнопку скидання
        page.click('[data-testid="reset-button"]')
        
        # Перевіряємо повідомлення про успіх
        expect(page.locator('[data-testid="success-message"]')).to_be_visible()
        expect(page.locator('[data-testid="success-message"]')).to_contain_text("Email відправлено")
    
    def test_logout_flow(self, page: Page):
        """Тест процесу виходу"""
        # Спочатку входимо в систему
        page.goto("http://localhost:3000/login")
        page.fill('[data-testid="email"]', "test@example.com")
        page.fill('[data-testid="password"]', "password123")
        page.click('[data-testid="login-button"]')
        
        # Перевіряємо що ми на dashboard
        expect(page).to_have_url("http://localhost:3000/dashboard")
        
        # Відкриваємо меню користувача
        page.click('[data-testid="user-menu"]')
        
        # Натискаємо "Вийти"
        page.click('[data-testid="logout-button"]')
        
        # Перевіряємо що перейшли на сторінку входу
        expect(page).to_have_url("http://localhost:3000/login")
    
    def test_invalid_login_attempts(self, page: Page):
        """Тест невалідних спроб входу"""
        # Переходимо на сторінку входу
        page.goto("http://localhost:3000/login")
        
        # Спробуємо ввійти з неправильними даними
        page.fill('[data-testid="email"]', "wrong@example.com")
        page.fill('[data-testid="password"]', "wrongpassword")
        page.click('[data-testid="login-button"]')
        
        # Перевіряємо повідомлення про помилку
        expect(page.locator('[data-testid="error-message"]')).to_be_visible()
        expect(page.locator('[data-testid="error-message"]')).to_contain_text("Невірні дані")
        
        # Перевіряємо що залишились на сторінці входу
        expect(page).to_have_url("http://localhost:3000/login")
    
    def test_form_validation(self, page: Page):
        """Тест валідації форм"""
        # Переходимо на сторінку реєстрації
        page.goto("http://localhost:3000/register")
        
        # Спробуємо відправити порожню форму
        page.click('[data-testid="register-button"]')
        
        # Перевіряємо повідомлення про помилки валідації
        expect(page.locator('[data-testid="email-error"]')).to_be_visible()
        expect(page.locator('[data-testid="password-error"]')).to_be_visible()
        
        # Вводимо невалідний email
        page.fill('[data-testid="email"]', "invalid-email")
        page.click('[data-testid="register-button"]')
        
        # Перевіряємо повідомлення про невалідний email
        expect(page.locator('[data-testid="email-error"]')).to_contain_text("Невалідний email")
        
        # Вводимо короткий пароль
        page.fill('[data-testid="email"]', "test@example.com")
        page.fill('[data-testid="password"]', "123")
        page.click('[data-testid="register-button"]')
        
        # Перевіряємо повідомлення про короткий пароль
        expect(page.locator('[data-testid="password-error"]')).to_contain_text("Мінімум 8 символів")


class TestDashboardFlow:
    """E2E тести для Dashboard"""
    
    @pytest.fixture
    def authenticated_page(self, browser):
        """Фікстура для авторизованої сторінки"""
        page = browser.new_page()
        
        # Авторизуємося
        page.goto("http://localhost:3000/login")
        page.fill('[data-testid="email"]', "test@example.com")
        page.fill('[data-testid="password"]', "password123")
        page.click('[data-testid="login-button"]')
        
        # Чекаємо завантаження dashboard
        page.wait_for_url("http://localhost:3000/dashboard")
        
        yield page
        page.close()
    
    def test_dashboard_loading(self, authenticated_page: Page):
        """Тест завантаження dashboard"""
        # Перевіряємо що dashboard завантажився
        expect(authenticated_page.locator('[data-testid="dashboard-header"]')).to_be_visible()
        expect(authenticated_page.locator('[data-testid="earnings-card"]')).to_be_visible()
        expect(authenticated_page.locator('[data-testid="proposals-card"]')).to_be_visible()
        expect(authenticated_page.locator('[data-testid="jobs-card"]')).to_be_visible()
    
    def test_navigation_menu(self, authenticated_page: Page):
        """Тест навігаційного меню"""
        # Перевіряємо навігаційне меню
        expect(authenticated_page.locator('[data-testid="nav-menu"]')).to_be_visible()
        
        # Переходимо на сторінку аналітики
        authenticated_page.click('[data-testid="nav-analytics"]')
        expect(authenticated_page).to_have_url("http://localhost:3000/analytics")
        
        # Переходимо на сторінку пошуку роботи
        authenticated_page.click('[data-testid="nav-jobs"]')
        expect(authenticated_page).to_have_url("http://localhost:3000/jobs")
        
        # Повертаємось на dashboard
        authenticated_page.click('[data-testid="nav-dashboard"]')
        expect(authenticated_page).to_have_url("http://localhost:3000/dashboard")
    
    def test_data_refresh(self, authenticated_page: Page):
        """Тест оновлення даних"""
        # Перевіряємо кнопку оновлення
        expect(authenticated_page.locator('[data-testid="refresh-button"]')).to_be_visible()
        
        # Натискаємо кнопку оновлення
        authenticated_page.click('[data-testid="refresh-button"]')
        
        # Перевіряємо що дані оновились (показник завантаження)
        expect(authenticated_page.locator('[data-testid="loading-indicator"]')).to_be_visible()
        
        # Чекаємо завершення завантаження
        authenticated_page.wait_for_selector('[data-testid="loading-indicator"]', state='hidden')
        
        # Перевіряємо що дані відображаються
        expect(authenticated_page.locator('[data-testid="earnings-amount"]')).to_be_visible()


class TestResponsiveDesign:
    """E2E тести для адаптивного дизайну"""
    
    def test_mobile_view(self, browser):
        """Тест мобільного вигляду"""
        page = browser.new_page(viewport={'width': 375, 'height': 667})
        
        # Переходимо на dashboard
        page.goto("http://localhost:3000/dashboard")
        
        # Перевіряємо мобільне меню
        expect(page.locator('[data-testid="mobile-menu-button"]')).to_be_visible()
        
        # Відкриваємо мобільне меню
        page.click('[data-testid="mobile-menu-button"]')
        
        # Перевіряємо що меню відкрилось
        expect(page.locator('[data-testid="mobile-menu"]')).to_be_visible()
        
        page.close()
    
    def test_tablet_view(self, browser):
        """Тест планшетного вигляду"""
        page = browser.new_page(viewport={'width': 768, 'height': 1024})
        
        # Переходимо на dashboard
        page.goto("http://localhost:3000/dashboard")
        
        # Перевіряємо що контент адаптується
        expect(page.locator('[data-testid="dashboard-grid"]')).to_be_visible()
        
        page.close()
    
    def test_desktop_view(self, browser):
        """Тест десктопного вигляду"""
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Переходимо на dashboard
        page.goto("http://localhost:3000/dashboard")
        
        # Перевіряємо що всі елементи відображаються
        expect(page.locator('[data-testid="sidebar"]')).to_be_visible()
        expect(page.locator('[data-testid="main-content"]')).to_be_visible()
        
        page.close()


class TestAccessibility:
    """E2E тести для доступності"""
    
    def test_keyboard_navigation(self, browser):
        """Тест навігації з клавіатури"""
        page = browser.new_page()
        
        # Переходимо на dashboard
        page.goto("http://localhost:3000/dashboard")
        
        # Навігуємо з клавіатури
        page.keyboard.press("Tab")
        expect(page.locator(':focus')).to_have_attribute('data-testid', 'nav-dashboard')
        
        page.keyboard.press("Tab")
        expect(page.locator(':focus')).to_have_attribute('data-testid', 'nav-analytics')
        
        page.close()
    
    def test_screen_reader_support(self, browser):
        """Тест підтримки screen reader"""
        page = browser.new_page()
        
        # Переходимо на dashboard
        page.goto("http://localhost:3000/dashboard")
        
        # Перевіряємо ARIA атрибути
        expect(page.locator('[data-testid="earnings-card"]')).to_have_attribute('aria-label')
        expect(page.locator('[data-testid="proposals-card"]')).to_have_attribute('aria-label')
        
        page.close() 