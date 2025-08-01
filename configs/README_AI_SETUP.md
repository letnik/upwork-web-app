# AI API Configuration Setup

Цей документ містить інструкції для налаштування API ключів для OpenAI та Anthropic.

## Кроки для налаштування

### 1. Створення файлу .env

Створіть файл `.env` в корені проекту на основі `env.example`:

```bash
cp env.example .env
```

### 2. Додавання API ключів

Відредагуйте файл `.env` та додайте ваші API ключі:

```env
# AI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# AI Model Configuration (опціонально)
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Додаткові налаштування (опціонально)
AI_REQUEST_TIMEOUT=30
AI_MAX_RETRIES=3
```

### 3. Перевірка конфігурації

Запустіть тест конфігурації:

```bash
python -c "from configs.ai_config import ai_config; print('Config valid:', ai_config.validate_config())"
```

## Безпека

⚠️ **ВАЖЛИВО:**
- Ніколи не комітьте файл `.env` до Git
- Файл `.env` вже додано до `.gitignore`
- Зберігайте API ключі в безпечному місці
- Регулярно ротуйте API ключі

## Використання в коді

```python
from configs.ai_config import ai_config

# Отримання конфігурації OpenAI
openai_config = ai_config.get_openai_config()

# Отримання конфігурації Anthropic
anthropic_config = ai_config.get_anthropic_config()

# Перевірка наявності ключів
if ai_config.validate_config():
    print("API keys configured successfully")
else:
    print("Please configure API keys")
```

## Отримання API ключів

### OpenAI API Key
1. Перейдіть на https://platform.openai.com/api-keys
2. Створіть новий API ключ
3. Скопіюйте ключ (починається з `sk-`)

### Anthropic API Key
1. Перейдіть на https://console.anthropic.com/keys
2. Створіть новий API ключ
3. Скопіюйте ключ (починається з `sk-ant-`)

## Тестування

Після налаштування можете протестувати підключення:

```python
# Тест OpenAI
import openai
from configs.ai_config import ai_config

openai.api_key = ai_config.openai_api_key
# Тестовий запит...

# Тест Anthropic
import anthropic
from configs.ai_config import ai_config

client = anthropic.Anthropic(api_key=ai_config.anthropic_api_key)
# Тестовий запит...
``` 