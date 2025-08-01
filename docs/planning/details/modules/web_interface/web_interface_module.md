# Web Interface Модуль

## Огляд

Web Interface модуль забезпечує сучасний та інтуїтивний користувацький інтерфейс для роботи з Upwork AI Assistant.

## Основні компоненти

### 1. Dashboard (Головна панель)
- Огляд статистики та метрик
- Швидкий доступ до основних функцій
- Графіки та аналітика

### 2. Job Search (Пошук вакансій)
- Розширений пошук з фільтрами
- Збереження улюблених вакансій
- Аналіз підходящості

### 3. Proposal Creator (Створення відгуків)
- AI-генерація відгуків
- Редагування та валідація
- Шаблони та історія

### 4. Analytics (Аналітика)
- Детальна статистика
- Графіки продуктивності
- Експорт даних

## AI Settings Interface (Інтерфейс налаштувань AI)

### Компонент налаштувань AI

#### Структура компонента
```typescript
interface AISettingsPanel {
  aiDisclosure: AIDisclosureSettings;
  editing: EditingSettings;
  validation: ValidationSettings;
  preferences: UserPreferences;
}
```

#### AI Disclosure Settings (Налаштування розкриття AI)
```typescript
interface AIDisclosureSettings {
  enabled: boolean;
  position: 'start' | 'end' | 'none';
  template: 'default' | 'minimal' | 'detailed' | 'custom';
  customText: string;
  autoAdd: boolean;
}
```

#### Editing Settings (Налаштування редагування)
```typescript
interface EditingSettings {
  autoSave: boolean;
  saveInterval: number; // секунди
  draftRetention: number; // дні
  validation: {
    minLength: number;
    maxLength: number;
    checkSpam: boolean;
    requireReview: boolean;
  };
}
```

### UI Компоненти

#### AI Settings Panel
```tsx
const AISettingsPanel: React.FC = () => {
  const [settings, setSettings] = useState<AISettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(false);

  const handleSave = async (newSettings: AISettings) => {
    setIsLoading(true);
    try {
      await updateAISettings(newSettings);
      setSettings(newSettings);
      showSuccess('Налаштування збережено');
    } catch (error) {
      showError('Помилка збереження налаштувань');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="ai-settings-panel">
      <h2>Налаштування AI</h2>
      
      {/* AI Disclosure Section */}
      <section className="disclosure-settings">
        <h3>Розкриття AI</h3>
        
        <div className="setting-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={settings.aiDisclosure.enabled}
              onChange={(e) => handleDisclosureToggle(e.target.checked)}
            />
            <span>Включити розкриття AI</span>
          </label>
          <p className="setting-description">
            Автоматично додавати інформацію про використання AI в згенерований контент
          </p>
        </div>

        {settings.aiDisclosure.enabled && (
          <>
            <div className="setting-group">
              <label>Позиція розкриття:</label>
              <select
                value={settings.aiDisclosure.position}
                onChange={(e) => handlePositionChange(e.target.value)}
              >
                <option value="start">На початку</option>
                <option value="end">В кінці</option>
                <option value="none">Не додавати</option>
              </select>
            </div>

            <div className="setting-group">
              <label>Шаблон розкриття:</label>
              <select
                value={settings.aiDisclosure.template}
                onChange={(e) => handleTemplateChange(e.target.value)}
              >
                <option value="minimal">Мінімальний</option>
                <option value="default">Стандартний</option>
                <option value="detailed">Детальний</option>
                <option value="custom">Кастомний</option>
              </select>
            </div>

            {settings.aiDisclosure.template === 'custom' && (
              <div className="setting-group">
                <label>Кастомний текст:</label>
                <textarea
                  value={settings.aiDisclosure.customText}
                  onChange={(e) => handleCustomTextChange(e.target.value)}
                  placeholder="Введіть власний текст розкриття..."
                  rows={3}
                />
              </div>
            )}

            <div className="setting-group">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={settings.aiDisclosure.autoAdd}
                  onChange={(e) => handleAutoAddChange(e.target.checked)}
                />
                <span>Автоматично додавати розкриття</span>
              </label>
            </div>
          </>
        )}
      </section>

      {/* Editing Settings Section */}
      <section className="editing-settings">
        <h3>Налаштування редагування</h3>
        
        <div className="setting-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={settings.editing.autoSave}
              onChange={(e) => handleAutoSaveChange(e.target.checked)}
            />
            <span>Автозбереження чернеток</span>
          </label>
        </div>

        {settings.editing.autoSave && (
          <div className="setting-group">
            <label>Інтервал збереження (секунди):</label>
            <input
              type="number"
              min="10"
              max="300"
              value={settings.editing.saveInterval}
              onChange={(e) => handleSaveIntervalChange(parseInt(e.target.value))}
            />
          </div>
        )}

        <div className="setting-group">
          <label>Зберігати чернетки (дні):</label>
          <input
            type="number"
            min="1"
            max="90"
            value={settings.editing.draftRetention}
            onChange={(e) => handleRetentionChange(parseInt(e.target.value))}
          />
        </div>
      </section>

      {/* Validation Settings Section */}
      <section className="validation-settings">
        <h3>Валідація контенту</h3>
        
        <div className="setting-group">
          <label>Мінімальна довжина (символів):</label>
          <input
            type="number"
            min="50"
            value={settings.editing.validation.minLength}
            onChange={(e) => handleMinLengthChange(parseInt(e.target.value))}
          />
        </div>

        <div className="setting-group">
          <label>Максимальна довжина (символів):</label>
          <input
            type="number"
            max="5000"
            value={settings.editing.validation.maxLength}
            onChange={(e) => handleMaxLengthChange(parseInt(e.target.value))}
          />
        </div>

        <div className="setting-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={settings.editing.validation.checkSpam}
              onChange={(e) => handleSpamCheckChange(e.target.checked)}
            />
            <span>Перевіряти на спам</span>
          </label>
        </div>

        <div className="setting-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={settings.editing.validation.requireReview}
              onChange={(e) => handleReviewRequirementChange(e.target.checked)}
            />
            <span>Вимагати перегляду перед відправкою</span>
          </label>
        </div>
      </section>

      {/* Action Buttons */}
      <div className="settings-actions">
        <button
          className="btn btn-primary"
          onClick={() => handleSave(settings)}
          disabled={isLoading}
        >
          {isLoading ? 'Збереження...' : 'Зберегти налаштування'}
        </button>
        
        <button
          className="btn btn-secondary"
          onClick={handleReset}
          disabled={isLoading}
        >
          Скинути до за замовчуванням
        </button>
      </div>
    </div>
  );
};
```

## Proposal Editor (Редактор відгуків)

### Структура редактора
```typescript
interface ProposalEditor {
  draftId?: string;
  jobId: string;
  content: string;
  aiGenerated: boolean;
  aiDisclosureIncluded: boolean;
  validationStatus: 'pending' | 'valid' | 'invalid' | 'warning';
  validationErrors: string[];
  lastSaved: Date;
  isDirty: boolean;
  wordCount: number;
  characterCount: number;
}
```

### Компонент редактора
```tsx
const ProposalEditor: React.FC<ProposalEditorProps> = ({ jobId, initialContent }) => {
  const [editor, setEditor] = useState<ProposalEditor>({
    jobId,
    content: initialContent || '',
    aiGenerated: false,
    aiDisclosureIncluded: false,
    validationStatus: 'pending',
    validationErrors: [],
    lastSaved: new Date(),
    isDirty: false,
    wordCount: 0,
    characterCount: 0
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  // Автозбереження
  useEffect(() => {
    if (editor.isDirty && editor.content.length > 0) {
      const timer = setTimeout(() => {
        handleAutoSave();
      }, 30000); // 30 секунд

      return () => clearTimeout(timer);
    }
  }, [editor.content, editor.isDirty]);

  // Підрахунок слів та символів
  useEffect(() => {
    const wordCount = editor.content.trim().split(/\s+/).length;
    const characterCount = editor.content.length;
    
    setEditor(prev => ({
      ...prev,
      wordCount,
      characterCount
    }));
  }, [editor.content]);

  const handleGenerateAI = async () => {
    setIsGenerating(true);
    try {
      const response = await generateProposal({
        jobId: editor.jobId,
        includeDisclosure: true
      });

      setEditor(prev => ({
        ...prev,
        content: response.content,
        aiGenerated: true,
        aiDisclosureIncluded: response.aiDisclosureIncluded,
        isDirty: true
      }));

      showSuccess('Відгук згенеровано успішно');
    } catch (error) {
      showError('Помилка генерації відгуку');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContentChange = (newContent: string) => {
    setEditor(prev => ({
      ...prev,
      content: newContent,
      isDirty: true
    }));
  };

  const handleAutoSave = async () => {
    if (!editor.isDirty) return;

    setIsSaving(true);
    try {
      const response = await saveDraft({
        jobId: editor.jobId,
        content: editor.content,
        aiGenerated: editor.aiGenerated,
        aiDisclosureIncluded: editor.aiDisclosureIncluded
      });

      setEditor(prev => ({
        ...prev,
        draftId: response.draftId,
        isDirty: false,
        lastSaved: new Date()
      }));
    } catch (error) {
      showError('Помилка автозбереження');
    } finally {
      setIsSaving(false);
    }
  };

  const handleValidate = async () => {
    try {
      const validation = await validateProposal({
        content: editor.content,
        jobId: editor.jobId,
        aiDisclosureIncluded: editor.aiDisclosureIncluded
      });

      setEditor(prev => ({
        ...prev,
        validationStatus: validation.isValid ? 'valid' : 'invalid',
        validationErrors: validation.errors
      }));

      if (validation.isValid) {
        showSuccess('Відгук валідний');
      } else {
        showWarning('Знайдено помилки валідації');
      }
    } catch (error) {
      showError('Помилка валідації');
    }
  };

  const handleSend = async () => {
    if (editor.validationStatus !== 'valid') {
      showError('Спочатку валідуйте відгук');
      return;
    }

    try {
      await sendProposal({
        draftId: editor.draftId,
        jobId: editor.jobId,
        finalContent: editor.content
      });

      showSuccess('Відгук відправлено успішно');
      // Перенаправлення на сторінку відгуків
    } catch (error) {
      showError('Помилка відправки відгуку');
    }
  };
    
    return (
    <div className="proposal-editor">
      <div className="editor-header">
        <h2>Редактор відгуку</h2>
        
        <div className="editor-actions">
          <button
            className="btn btn-primary"
            onClick={handleGenerateAI}
            disabled={isGenerating}
          >
            {isGenerating ? 'Генерація...' : 'Згенерувати AI'}
          </button>
          
          <button
            className="btn btn-secondary"
            onClick={() => setShowPreview(!showPreview)}
          >
            {showPreview ? 'Редагувати' : 'Попередній перегляд'}
          </button>
          
          <button
            className="btn btn-success"
            onClick={handleValidate}
          >
            Валідувати
          </button>
          
          <button
            className="btn btn-primary"
            onClick={handleSend}
            disabled={editor.validationStatus !== 'valid'}
          >
            Відправити
          </button>
      </div>
      </div>

      <div className="editor-content">
        {showPreview ? (
          <div className="preview-panel">
            <h3>Попередній перегляд</h3>
            <div className="preview-content">
              {editor.content.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        ) : (
          <div className="editor-panel">
            <div className="editor-toolbar">
              <div className="toolbar-group">
                <button className="toolbar-btn" title="Жирний">B</button>
                <button className="toolbar-btn" title="Курсив">I</button>
                <button className="toolbar-btn" title="Підкреслений">U</button>
              </div>
              
              <div className="toolbar-group">
                <button className="toolbar-btn" title="Список">•</button>
                <button className="toolbar-btn" title="Нумерований список">1.</button>
              </div>
            </div>

            <textarea
              className="content-editor"
              value={editor.content}
              onChange={(e) => handleContentChange(e.target.value)}
              placeholder="Введіть текст відгуку..."
              rows={15}
            />

            {editor.aiGenerated && (
              <div className="ai-warning">
                <div className="warning-icon">⚠️</div>
                <div className="warning-text">
                  <strong>AI-генерований контент</strong>
                  <p>Перегляньте та відредагуйте перед відправкою</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="editor-sidebar">
        <div className="sidebar-section">
          <h4>Статистика</h4>
          <div className="stats">
            <div className="stat-item">
              <span className="stat-label">Слова:</span>
              <span className="stat-value">{editor.wordCount}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Символи:</span>
              <span className="stat-value">{editor.characterCount}</span>
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h4>Статус</h4>
          <div className="status-indicators">
            <div className={`status-item ${editor.validationStatus}`}>
              <span className="status-icon">
                {editor.validationStatus === 'valid' && '✅'}
                {editor.validationStatus === 'invalid' && '❌'}
                {editor.validationStatus === 'warning' && '⚠️'}
                {editor.validationStatus === 'pending' && '⏳'}
              </span>
              <span className="status-text">
                {editor.validationStatus === 'valid' && 'Валідний'}
                {editor.validationStatus === 'invalid' && 'Помилки'}
                {editor.validationStatus === 'warning' && 'Попередження'}
                {editor.validationStatus === 'pending' && 'Очікує валідації'}
              </span>
            </div>
            
            <div className="status-item">
              <span className="status-icon">
                {isSaving ? '💾' : '💾'}
              </span>
              <span className="status-text">
                {isSaving ? 'Збереження...' : 'Збережено'}
              </span>
            </div>
          </div>
        </div>

        {editor.validationErrors.length > 0 && (
          <div className="sidebar-section">
            <h4>Помилки валідації</h4>
            <div className="validation-errors">
              {editor.validationErrors.map((error, index) => (
                <div key={index} className="error-item">
                  <span className="error-icon">❌</span>
                  <span className="error-text">{error}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="sidebar-section">
          <h4>Дії</h4>
          <div className="action-buttons">
            <button
              className="btn btn-sm btn-secondary"
              onClick={handleAutoSave}
              disabled={!editor.isDirty || isSaving}
            >
              Зберегти чернетку
            </button>
            
            <button
              className="btn btn-sm btn-outline"
              onClick={() => setShowPreview(!showPreview)}
            >
              {showPreview ? 'Редагувати' : 'Перегляд'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

## Стилі CSS

### AI Settings Panel Styles
```css
.ai-settings-panel {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.setting-group {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: #f8f9fa;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.toggle-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.setting-description {
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
}

.settings-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e1e5e9;
}
```

### Proposal Editor Styles
```css
.proposal-editor {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  height: calc(100vh - 100px);
}

.editor-header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #fff;
  border-bottom: 1px solid #e1e5e9;
}

.editor-actions {
  display: flex;
  gap: 0.5rem;
}

.editor-content {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  border-bottom: 1px solid #e1e5e9;
  background: #f8f9fa;
}

.toolbar-group {
  display: flex;
  gap: 0.25rem;
}

.toolbar-btn {
  padding: 0.25rem 0.5rem;
  border: 1px solid #dee2e6;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.toolbar-btn:hover {
  background: #e9ecef;
}

.content-editor {
  width: 100%;
  min-height: 400px;
  padding: 1rem;
  border: none;
  resize: vertical;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.ai-warning {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  margin: 1rem;
}

.warning-icon {
  font-size: 1.5rem;
}

.warning-text strong {
  color: #856404;
}

.editor-sidebar {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e1e5e9;
}

.sidebar-section:last-child {
  border-bottom: none;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  background: #f8f9fa;
}

.status-item.valid {
  background: #d4edda;
  color: #155724;
}

.status-item.invalid {
  background: #f8d7da;
  color: #721c24;
}

.status-item.warning {
  background: #fff3cd;
  color: #856404;
}

.validation-errors {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.error-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f8d7da;
  border-radius: 4px;
  color: #721c24;
}

.error-text {
  font-size: 0.9rem;
  line-height: 1.4;
}
```

## Інтеграція з API

### Хуки для роботи з API
```typescript
// Хук для налаштувань AI
const useAISettings = () => {
  const [settings, setSettings] = useState<AISettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/ai/settings');
      setSettings(response.data);
    } catch (err) {
      setError('Помилка завантаження налаштувань');
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (newSettings: AISettings) => {
    try {
      const response = await api.put('/ai/settings', newSettings);
      setSettings(response.data);
      return response.data;
    } catch (err) {
      throw new Error('Помилка збереження налаштувань');
    }
  };

  const resetSettings = async () => {
    try {
      const response = await api.post('/ai/settings/reset');
      setSettings(response.data);
      return response.data;
    } catch (err) {
      throw new Error('Помилка скидання налаштувань');
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  return {
    settings,
    loading,
    error,
    updateSettings,
    resetSettings,
    refetch: fetchSettings
  };
};

// Хук для редактора відгуків
const useProposalEditor = (jobId: string) => {
  const [draft, setDraft] = useState<ProposalDraft | null>(null);
  const [loading, setLoading] = useState(false);

  const generateProposal = async (options: GenerateOptions) => {
    try {
      setLoading(true);
      const response = await api.post('/ai/generate-proposal', {
        job_id: jobId,
        ...options
      });
      return response.data;
    } catch (err) {
      throw new Error('Помилка генерації відгуку');
    } finally {
      setLoading(false);
    }
  };

  const saveDraft = async (draftData: DraftData) => {
    try {
      const response = await api.post('/ai/drafts', draftData);
      setDraft(response.data);
      return response.data;
    } catch (err) {
      throw new Error('Помилка збереження чернетки');
    }
  };

  const validateProposal = async (content: string) => {
    try {
      const response = await api.post('/ai/validate-proposal', {
        content,
        job_id: jobId
      });
      return response.data;
    } catch (err) {
      throw new Error('Помилка валідації');
    }
  };

  const sendProposal = async (proposalData: SendProposalData) => {
    try {
      const response = await api.post('/ai/send-proposal', proposalData);
      return response.data;
    } catch (err) {
      throw new Error('Помилка відправки відгуку');
    }
  };

  return {
    draft,
    loading,
    generateProposal,
    saveDraft,
    validateProposal,
    sendProposal
  };
};
```

## Тестування компонентів

### Unit тести для AI Settings
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AISettingsPanel } from './AISettingsPanel';

describe('AISettingsPanel', () => {
  it('should render all settings sections', () => {
    render(<AISettingsPanel />);
    
    expect(screen.getByText('Налаштування AI')).toBeInTheDocument();
    expect(screen.getByText('Розкриття AI')).toBeInTheDocument();
    expect(screen.getByText('Налаштування редагування')).toBeInTheDocument();
    expect(screen.getByText('Валідація контенту')).toBeInTheDocument();
  });

  it('should toggle AI disclosure settings', () => {
    render(<AISettingsPanel />);
    
    const disclosureToggle = screen.getByLabelText('Включити розкриття AI');
    fireEvent.click(disclosureToggle);
    
    expect(screen.getByText('Позиція розкриття:')).toBeInTheDocument();
    expect(screen.getByText('Шаблон розкриття:')).toBeInTheDocument();
  });

  it('should save settings successfully', async () => {
    const mockUpdateSettings = jest.fn().mockResolvedValue({});
    render(<AISettingsPanel onUpdateSettings={mockUpdateSettings} />);
    
    const saveButton = screen.getByText('Зберегти налаштування');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockUpdateSettings).toHaveBeenCalled();
    });
  });
});
```

### Unit тести для Proposal Editor
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProposalEditor } from './ProposalEditor';

describe('ProposalEditor', () => {
  const mockJobId = '~0123456789012345';

  it('should render editor with all components', () => {
    render(<ProposalEditor jobId={mockJobId} />);
    
    expect(screen.getByText('Редактор відгуку')).toBeInTheDocument();
    expect(screen.getByText('Згенерувати AI')).toBeInTheDocument();
    expect(screen.getByText('Валідувати')).toBeInTheDocument();
    expect(screen.getByText('Відправити')).toBeInTheDocument();
  });

  it('should generate AI proposal', async () => {
    const mockGenerateProposal = jest.fn().mockResolvedValue({
      content: 'Generated content',
      aiDisclosureIncluded: true
    });
    
    render(<ProposalEditor jobId={mockJobId} onGenerateProposal={mockGenerateProposal} />);
    
    const generateButton = screen.getByText('Згенерувати AI');
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(mockGenerateProposal).toHaveBeenCalledWith({
        jobId: mockJobId,
        includeDisclosure: true
      });
    });
  });

  it('should validate proposal content', async () => {
    const mockValidateProposal = jest.fn().mockResolvedValue({
      isValid: true,
      errors: []
    });
    
    render(<ProposalEditor jobId={mockJobId} onValidateProposal={mockValidateProposal} />);
    
    const validateButton = screen.getByText('Валідувати');
    fireEvent.click(validateButton);
    
    await waitFor(() => {
      expect(mockValidateProposal).toHaveBeenCalled();
    });
  });
});
``` 