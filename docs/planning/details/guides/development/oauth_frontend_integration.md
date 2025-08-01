# OAuth Frontend Integration Guide

## Огляд

Цей документ описує інтеграцію OAuth з Upwork та інших сервісів у фронтенд частині додатку.

## OAuth Flow з Upwork

### 1. Ініціалізація OAuth

```typescript
// services/upwork.ts
export const initUpworkOAuth = async (): Promise<string> => {
  try {
    const response = await api.get('/auth/upwork/init');
    return response.data.auth_url;
  } catch (error) {
    throw new Error('Помилка ініціалізації OAuth');
  }
};

// components/UpworkConnect.tsx
const UpworkConnect: React.FC = () => {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      const authUrl = await initUpworkOAuth();
      window.location.href = authUrl;
    } catch (error) {
      showError('Помилка підключення до Upwork');
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="upwork-connect">
      <h3>Підключення до Upwork</h3>
      <p>Для використання всіх функцій потрібно підключити ваш акаунт Upwork</p>
      
      <button 
        className="btn btn-primary"
        onClick={handleConnect}
        disabled={isConnecting}
      >
        {isConnecting ? 'Підключення...' : 'Підключити Upwork'}
      </button>
    </div>
  );
};
```

### 2. Обробка OAuth Callback

```typescript
// pages/OAuthCallback.tsx
const OAuthCallback: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const error = urlParams.get('error');
      
      if (error) {
        setStatus('error');
        setMessage('Помилка авторизації: ' + error);
        return;
      }
      
      if (!code || !state) {
        setStatus('error');
        setMessage('Неправильні параметри авторизації');
        return;
      }
      
      try {
        const response = await api.post('/auth/upwork/callback', {
          code,
          state
        });

        setStatus('success');
        setMessage('Успішно підключено до Upwork!');
        
        // Перенаправлення на головну сторінку через 2 секунди
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);
      } catch (error) {
        setStatus('error');
        setMessage('Помилка завершення авторизації');
      }
    };
    
    handleCallback();
  }, []);

  return (
    <div className="oauth-callback">
      <div className="callback-content">
      {status === 'loading' && (
          <>
            <div className="spinner"></div>
            <h3>Завершення авторизації...</h3>
          </>
      )}
      
      {status === 'success' && (
          <>
            <div className="success-icon">✅</div>
          <h3>Успішно!</h3>
          <p>{message}</p>
          </>
      )}
      
      {status === 'error' && (
          <>
            <div className="error-icon">❌</div>
          <h3>Помилка</h3>
          <p>{message}</p>
            <button
              className="btn btn-primary"
              onClick={() => window.location.href = '/dashboard'}
            >
            Повернутися на головну
          </button>
          </>
        )}
        </div>
    </div>
  );
};
```

## AI Settings Integration

### 1. Контекст для AI налаштувань

```typescript
// contexts/AISettingsContext.tsx
interface AISettingsContextType {
  settings: AISettings | null;
  loading: boolean;
  error: string | null;
  updateSettings: (settings: AISettings) => Promise<void>;
  resetSettings: () => Promise<void>;
  refreshSettings: () => Promise<void>;
}

const AISettingsContext = createContext<AISettingsContextType | undefined>(undefined);

export const AISettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/ai/settings');
      setSettings(response.data);
    } catch (err) {
      setError('Помилка завантаження налаштувань AI');
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (newSettings: AISettings) => {
    try {
      setLoading(true);
      const response = await api.put('/ai/settings', newSettings);
      setSettings(response.data);
      showSuccess('Налаштування збережено');
    } catch (err) {
      setError('Помилка збереження налаштувань');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetSettings = async () => {
    try {
      setLoading(true);
      const response = await api.post('/ai/settings/reset');
      setSettings(response.data);
      showSuccess('Налаштування скинуто до за замовчуванням');
    } catch (err) {
      setError('Помилка скидання налаштувань');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const value: AISettingsContextType = {
    settings,
    loading,
    error,
    updateSettings,
    resetSettings,
    refreshSettings: fetchSettings
  };

  return (
    <AISettingsContext.Provider value={value}>
      {children}
    </AISettingsContext.Provider>
  );
};

export const useAISettings = () => {
  const context = useContext(AISettingsContext);
  if (context === undefined) {
    throw new Error('useAISettings must be used within AISettingsProvider');
  }
  return context;
};
```

### 2. Хук для роботи з AI розкриттям

```typescript
// hooks/useAIDisclosure.ts
interface AIDisclosureOptions {
  enabled: boolean;
  position: 'start' | 'end' | 'none';
  template: 'default' | 'minimal' | 'detailed' | 'custom';
  customText: string;
}

export const useAIDisclosure = () => {
  const { settings } = useAISettings();

  const getDisclosureText = (template: string, customText?: string): string => {
    if (!settings?.aiDisclosure.enabled) return '';

    switch (template) {
      case 'minimal':
        return '*AI-генерований контент*';
      
      case 'detailed':
        return `
---
**Розкриття:** Цей відгук використовував AI для аналізу вимог та створення структурованої пропозиції. Весь контент був переглянутий та адаптований фахівцем для забезпечення релевантності та якості.
        `.trim();
      
      case 'custom':
        return customText || '';
      
      default:
        return `
---
**Розкриття:** Цей відгук був створений за допомогою штучного інтелекту та відредагований для адаптації під ваш проект.
        `.trim();
    }
  };

  const addDisclosureToContent = (content: string, options?: Partial<AIDisclosureOptions>): string => {
    const disclosureOptions = {
      enabled: settings?.aiDisclosure.enabled ?? true,
      position: settings?.aiDisclosure.position ?? 'end',
      template: settings?.aiDisclosure.template ?? 'default',
      customText: settings?.aiDisclosure.customText ?? '',
      ...options
    };

    if (!disclosureOptions.enabled) return content;

    const disclosureText = getDisclosureText(disclosureOptions.template, disclosureOptions.customText);
    
    if (!disclosureText) return content;

    switch (disclosureOptions.position) {
      case 'start':
        return `${disclosureText}\n\n${content}`;
      case 'end':
        return `${content}\n\n${disclosureText}`;
      default:
        return content;
    }
  };

  const shouldShowDisclosureWarning = (): boolean => {
    return settings?.aiDisclosure.enabled ?? false;
  };

  return {
    addDisclosureToContent,
    getDisclosureText,
    shouldShowDisclosureWarning,
    settings: settings?.aiDisclosure
  };
};
```

### 3. Компонент попередження про AI

```typescript
// components/AIDisclosureWarning.tsx
interface AIDisclosureWarningProps {
  show: boolean;
  onDismiss?: () => void;
}

const AIDisclosureWarning: React.FC<AIDisclosureWarningProps> = ({ show, onDismiss }) => {
  if (!show) return null;

  return (
    <div className="ai-disclosure-warning">
      <div className="warning-content">
        <div className="warning-icon">⚠️</div>
        <div className="warning-text">
          <h4>AI-генерований контент</h4>
          <p>
            Цей контент створений за допомогою штучного інтелекту. 
            Обов'язково перегляньте та відредагуйте перед використанням.
          </p>
        </div>
        {onDismiss && (
          <button
            className="warning-dismiss"
            onClick={onDismiss}
            aria-label="Закрити попередження"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

// Стилі для попередження
const styles = `
.ai-disclosure-warning {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  max-width: 400px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.warning-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
}

.warning-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.warning-text h4 {
  margin: 0 0 8px 0;
  color: #856404;
  font-size: 16px;
  font-weight: 600;
}

.warning-text p {
  margin: 0;
  color: #856404;
  font-size: 14px;
  line-height: 1.4;
}

.warning-dismiss {
  background: none;
  border: none;
  font-size: 20px;
  color: #856404;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.warning-dismiss:hover {
  background-color: rgba(133, 100, 4, 0.1);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
`;
```

### 4. Інтеграція з редактором відгуків

```typescript
// components/ProposalEditor.tsx
const ProposalEditor: React.FC<ProposalEditorProps> = ({ jobId, initialContent }) => {
  const { addDisclosureToContent, shouldShowDisclosureWarning } = useAIDisclosure();
  const [showDisclosureWarning, setShowDisclosureWarning] = useState(false);
  const [content, setContent] = useState(initialContent || '');
  const [isAIGenerated, setIsAIGenerated] = useState(false);

  const handleGenerateAI = async () => {
    try {
      const response = await api.post('/ai/generate-proposal', {
        job_id: jobId,
        include_disclosure: true
      });

      const generatedContent = response.data.content;
      const contentWithDisclosure = addDisclosureToContent(generatedContent);
      
      setContent(contentWithDisclosure);
      setIsAIGenerated(true);
      
      if (shouldShowDisclosureWarning()) {
        setShowDisclosureWarning(true);
      }
    } catch (error) {
      showError('Помилка генерації відгуку');
    }
  };

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    // Якщо користувач редагує AI-генерований контент, приховуємо попередження
    if (isAIGenerated && newContent !== content) {
      setShowDisclosureWarning(false);
    }
  };

  return (
    <div className="proposal-editor">
      <AIDisclosureWarning
        show={showDisclosureWarning}
        onDismiss={() => setShowDisclosureWarning(false)}
      />
      
      <div className="editor-header">
        <h2>Редактор відгуку</h2>
                <button 
          className="btn btn-primary"
          onClick={handleGenerateAI}
                >
          Згенерувати AI
                </button>
            </div>

      <div className="editor-content">
        <textarea
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          placeholder="Введіть текст відгуку..."
          className="content-editor"
        />
        
        {isAIGenerated && (
          <div className="ai-content-indicator">
            <span className="indicator-icon">🤖</span>
            <span className="indicator-text">AI-генерований контент</span>
        </div>
      )}
      </div>
    </div>
  );
};
```

## Валідація та обробка помилок

### 1. Валідація AI налаштувань

```typescript
// utils/validation.ts
export const validateAISettings = (settings: AISettings): ValidationResult => {
  const errors: string[] = [];

  // Перевірка інтервалу збереження
  if (settings.editing.saveInterval < 10 || settings.editing.saveInterval > 300) {
    errors.push('Інтервал збереження повинен бути від 10 до 300 секунд');
  }

  // Перевірка довжини контенту
  if (settings.editing.validation.minLength < 50) {
    errors.push('Мінімальна довжина не може бути менше 50 символів');
  }

  if (settings.editing.validation.maxLength > 5000) {
    errors.push('Максимальна довжина не може перевищувати 5000 символів');
  }

  if (settings.editing.validation.minLength >= settings.editing.validation.maxLength) {
    errors.push('Мінімальна довжина повинна бути менше максимальної');
  }

  // Перевірка кастомного тексту розкриття
  if (settings.aiDisclosure.template === 'custom' && !settings.aiDisclosure.customText.trim()) {
    errors.push('Кастомний текст розкриття не може бути порожнім');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};
```

### 2. Обробка помилок API

```typescript
// services/api.ts
export const handleAPIError = (error: any): string => {
  if (error.response) {
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.message || 'Неправильний запит';
    case 401:
        return 'Необхідна авторизація';
      case 403:
        return 'Доступ заборонено';
      case 404:
        return 'Ресурс не знайдено';
      case 422:
        return data.message || 'Помилка валідації';
      case 429:
        return 'Перевищено ліміт запитів';
    case 500:
        return 'Внутрішня помилка сервера';
    default:
        return 'Невідома помилка';
    }
  }
  
  if (error.request) {
    return 'Помилка з'єднання з сервером';
  }
  
  return error.message || 'Невідома помилка';
};

// Хук для обробки помилок
export const useErrorHandler = () => {
  const showError = (message: string) => {
    // Інтеграція з системою сповіщень
    toast.error(message);
  };

  const handleAPIError = (error: any) => {
    const errorMessage = handleAPIError(error);
    showError(errorMessage);
  };

  return { showError, handleAPIError };
};
```

## Тестування інтеграції

### 1. Тестування OAuth flow

```typescript
// tests/oauth.test.ts
describe('OAuth Integration', () => {
  it('should initiate OAuth flow', async () => {
    const mockAuthUrl = 'https://www.upwork.com/oauth/authorize?client_id=...';
    api.get.mockResolvedValue({ data: { auth_url: mockAuthUrl } });

    const authUrl = await initUpworkOAuth();
    expect(authUrl).toBe(mockAuthUrl);
  });

  it('should handle OAuth callback', async () => {
    const mockToken = 'access_token_123';
    api.post.mockResolvedValue({ data: { access_token: mockToken } });

    const result = await handleOAuthCallback('code_123', 'state_456');
    expect(result.access_token).toBe(mockToken);
  });
});
```

### 2. Тестування AI налаштувань

```typescript
// tests/ai-settings.test.ts
describe('AI Settings Integration', () => {
  it('should add AI disclosure to content', () => {
    const { addDisclosureToContent } = useAIDisclosure();
    
    const content = 'Test proposal content';
    const result = addDisclosureToContent(content, {
      enabled: true,
      position: 'end',
      template: 'default'
    });
    
    expect(result).toContain('Розкриття:');
    expect(result).toContain(content);
  });

  it('should validate AI settings', () => {
    const validSettings: AISettings = {
      aiDisclosure: {
        enabled: true,
        position: 'end',
        template: 'default',
        customText: '',
        autoAdd: true
      },
      editing: {
        autoSave: true,
        saveInterval: 30,
        draftRetention: 7,
        validation: {
          minLength: 100,
          maxLength: 2000,
          checkSpam: true,
          requireReview: true
        }
      }
    };

    const result = validateAISettings(validSettings);
    expect(result.isValid).toBe(true);
  });
});
```

## Безпека та приватність

### 1. Захист токенів

```typescript
// utils/security.ts
export const secureTokenStorage = {
  setToken: (token: string) => {
    // Зберігаємо токен в httpOnly cookie або зашифрованому localStorage
    const encryptedToken = encryptData(token);
    localStorage.setItem('upwork_token', encryptedToken);
  },

  getToken: (): string | null => {
    const encryptedToken = localStorage.getItem('upwork_token');
    if (!encryptedToken) return null;
    
    try {
      return decryptData(encryptedToken);
    } catch (error) {
      // Якщо токен пошкоджений, видаляємо його
      localStorage.removeItem('upwork_token');
      return null;
    }
  },

  removeToken: () => {
    localStorage.removeItem('upwork_token');
     }
   };
   ```

### 2. Валідація вхідних даних

```typescript
// utils/sanitization.ts
export const sanitizeContent = (content: string): string => {
  // Видалення потенційно небезпечних тегів
  return content
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .trim();
};

export const validateProposalContent = (content: string): ValidationResult => {
  const errors: string[] = [];

  if (content.length < 100) {
    errors.push('Відгук занадто короткий (мінімум 100 символів)');
  }

  if (content.length > 5000) {
    errors.push('Відгук занадто довгий (максимум 5000 символів)');
  }

  // Перевірка на спам
  const spamKeywords = ['buy now', 'click here', 'limited time'];
  const hasSpam = spamKeywords.some(keyword => 
    content.toLowerCase().includes(keyword)
  );

  if (hasSpam) {
    errors.push('Контент містить спам-індикатори');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};
``` 