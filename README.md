# 🎯 Social Skills Coach

Десктопное приложение с ИИ для развития коммуникативных навыков, подготовки к сложным разговорам и анализа переписки.

## 📋 Архитектура

Приложение состоит из двух частей:
1. **Social Skills Coach** (этот репозиторий) - Frontend + Backend
2. **DASA AI Server** (отдельный сервер) - AI API для обработки запросов

```
┌────────────────────────────────┐     ┌──────────────────────────┐
│    Social Skills Coach         │     │    DASA AI Server        │
│  ┌──────────────────────────┐ │     │                          │
│  │   Frontend (Electron)    │ │     │   AI API                 │
│  │   React + Material UI    │ │     │   - Text Generation      │
│  └───────────┬──────────────┘ │     │   - Dialogue Simulation  │
│              │                │     │   - Text Analysis        │
│  ┌───────────▼──────────────┐ │     │   - RAG Search          │
│  │   Backend (FastAPI)      │─┼────▶│                          │
│  │   - Users, Chats         │ │HTTP │   Local PyTorch Model    │
│  │   - Analysis, Library    │ │     │                          │
│  └──────────────────────────┘ │     └──────────────────────────┘
└────────────────────────────────┘
```

## 🚀 Быстрый старт

### 1. Установка

```bash
# Запустите скрипт установки
setup.bat
```

### 2. Настройка подключения к AI Server

Отредактируйте файл `.env`:

```env
# URL AI сервера (DASA)
AI_API_URL=http://localhost:8100/api/v1

# API ключ (должен совпадать с ключом на DASA сервере)
AI_API_KEY=your-secret-api-key-here
```

### 3. Запуск

```bash
# Запустить Backend
run-backend.bat

# Запустить Frontend (в отдельном терминале)
run-frontend.bat

# Или запустить Electron приложение
run-electron.bat
```

## 📁 Структура проекта

```
Socialskillscoach/
├── Backend/
│   ├── app/
│   │   ├── api/           # API эндпоинты
│   │   ├── models/        # SQLAlchemy модели
│   │   ├── schemas/       # Pydantic схемы
│   │   └── services/      # Бизнес-логика
│   │       ├── ai_api_client.py  # HTTP клиент для AI API
│   │       └── ai_service.py     # Сервис AI операций
│   └── requirements.txt
├── Frontend/
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   ├── pages/         # Страницы приложения
│   │   ├── services/      # API клиенты
│   │   └── stores/        # Zustand stores
│   ├── electron/          # Electron main process
│   └── package.json
├── .env.example
├── setup.bat
├── run-backend.bat
└── run-frontend.bat
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `AI_API_URL` | URL AI API сервера | `http://localhost:8100/api/v1` |
| `AI_API_KEY` | API ключ для аутентификации | - |
| `AI_API_TIMEOUT` | Таймаут запросов (сек) | `60` |
| `BACKEND_HOST` | Хост Backend сервера | `localhost` |
| `BACKEND_PORT` | Порт Backend сервера | `8000` |
| `DB_TYPE` | Тип БД (sqlite/mysql) | `sqlite` |

## 🔌 Интеграция с DASA AI Server

Приложение подключается к внешнему AI серверу через HTTP API.

### Проверка подключения

```bash
# Проверить доступность AI сервера
curl http://localhost:8100/api/v1/health
```

### Используемые эндпоинты

- `POST /api/v1/generate` - Генерация текста
- `POST /api/v1/conversation/plan` - Планирование разговора
- `POST /api/v1/dialogue/respond` - Симуляция диалога
- `POST /api/v1/analyze` - Анализ текста
- `POST /api/v1/rag/search` - Поиск по базе знаний

## 🛠️ Разработка

### Запуск в режиме разработки

```bash
# Backend
cd Backend
.\venv\Scripts\activate
uvicorn app.main:app --reload

# Frontend
cd Frontend
npm run dev
```

### API Документация

После запуска Backend доступна по адресу:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📦 Docker (опционально)

```bash
docker-compose up
```

## ❗ Важно

Для работы приложения **необходим запущенный DASA AI Server**!

Убедитесь, что:
1. DASA AI Server запущен и доступен
2. Настроен правильный `AI_API_URL` в `.env`
3. API ключи совпадают на обоих серверах
