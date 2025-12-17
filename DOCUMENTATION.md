# 🎯 Тренер социальных навыков

## Описание проекта

**Тренер социальных навыков** — это десктопное приложение с искусственным интеллектом для развития коммуникационных навыков. Приложение позволяет практиковаться в различных социальных сценариях через диалоги с ИИ, получать обратную связь и отслеживать прогресс.

### Ключевые возможности

- 💬 **Интерактивные диалоги** — практика общения с ИИ-собеседником
- 📊 **Анализ коммуникации** — оценка стиля общения, эмоций и паттернов
- 📚 **Библиотека знаний** — техники эффективной коммуникации
- 🏋️ **Упражнения** — практические задания для развития навыков
- 📈 **Отслеживание прогресса** — статистика и рекомендации
- 🤖 **Собственная AI модель** — обучаемая PyTorch модель с Gradio интерфейсом

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│                   Electron + React + MUI                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Чаты    │  │Библиотека│  │Упражнения│  │    Прогресс      │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│                         │                                        │
│                   Zustand State                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST API (axios)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND                                   │
│                    FastAPI + SQLAlchemy                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      API Routes                           │   │
│  │  /users  │  /chats  │  /analysis  │  /library  │ /exercises│  │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────┴───────────────────────────────────┐   │
│  │                    Services Layer                         │   │
│  │  UserService │ ChatService │ AIService │ AnalysisService  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────┴───────────────────────────────────┐   │
│  │                   Data Layer (MySQL)                      │   │
│  │    Users │ Chats │ Messages │ Progress │ Knowledge        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI MODULE                                  │
│                  PyTorch + Gradio + FAISS                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │  Custom Model  │  │  RAG Retriever │  │  Analysis Module   │ │
│  │  (Transformer) │  │  (FAISS+MySQL) │  │  (Sentiment/Style) │ │
│  └────────────────┘  └────────────────┘  └────────────────────┘ │
│                         │                                        │
│  ┌──────────────────────┴───────────────────────────────────┐   │
│  │              Training UI (Gradio :7860)                   │   │
│  │         SFT Training │ DPO Training │ Testing             │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Структура проекта

```
Socialskillscoach/
│
├── 📄 README.md                 # Краткое описание
├── 📄 DOCUMENTATION.md          # Эта документация
├── 📄 .env.example              # Шаблон переменных окружения
├── 📄 docker-compose.yml        # Docker конфигурация
│
├── 🔧 setup.bat                 # Установка зависимостей
├── 🔧 run-backend.bat           # Запуск Backend
├── 🔧 run-ai.bat                # Запуск AI Training UI
├── 🔧 run-frontend.bat          # Запуск Frontend dev server
├── 🔧 run-electron.bat          # Запуск Electron приложения
│
├── 📂 Backend/                  # FastAPI Backend сервер
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # Точка входа FastAPI
│       ├── config.py            # Настройки из .env
│       ├── database.py          # Async SQLAlchemy
│       ├── api/                 # REST API эндпоинты
│       │   ├── router.py        # Главный роутер
│       │   ├── users.py         # /api/users/*
│       │   ├── chats.py         # /api/chats/*
│       │   ├── analysis.py      # /api/analysis/*
│       │   ├── library.py       # /api/library/*
│       │   └── exercises.py     # /api/exercises/*
│       ├── schemas/             # Pydantic модели
│       ├── models/              # SQLAlchemy ORM
│       └── services/            # Бизнес-логика
│
├── 📂 AI/                       # AI модуль
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.py                # Настройки AI
│   ├── training_ui.py           # 🎯 Gradio интерфейс
│   │
│   ├── core/                    # Ядро AI
│   │   ├── model.py             # PyTorch Transformer
│   │   ├── llm_client.py        # Unified LLM клиент
│   │   ├── embeddings.py        # Sentence embeddings
│   │   └── prompts.py           # Шаблоны промптов
│   │
│   ├── training/                # Обучение модели
│   │   ├── trainer.py           # SFT Trainer
│   │   ├── dpo_trainer.py       # DPO Trainer
│   │   └── dataset.py           # Датасеты
│   │
│   ├── rag/                     # Retrieval-Augmented Generation
│   │   ├── faiss_store.py       # FAISS векторный индекс
│   │   └── retriever.py         # RAG retriever
│   │
│   └── analysis/                # Анализ коммуникации
│       ├── sentiment.py         # Анализ эмоций
│       ├── patterns.py          # Паттерны общения
│       └── classifier.py        # Классификация стилей
│
└── 📂 Frontend/                 # Electron + React приложение
    ├── Dockerfile
    ├── package.json
    │
    ├── electron/                # Electron процессы
    │   ├── main.js              # Main process
    │   └── preload.js           # Preload скрипт
    │
    ├── public/
    │   └── index.html
    │
    └── src/
        ├── index.js             # React entry point
        ├── index.css            # Глобальные стили
        ├── App.js               # Главный компонент
        ├── theme.js             # MUI тема (тёмная)
        │
        ├── services/
        │   └── api.js           # Axios API клиент
        │
        ├── stores/              # Zustand state management
        │   ├── authStore.js     # Авторизация
        │   ├── chatStore.js     # Чаты и сообщения
        │   └── libraryStore.js  # Библиотека знаний
        │
        ├── components/          # React компоненты
        │   ├── Layout.js        # Основной layout с sidebar
        │   ├── ChatWindow.js    # Окно чата
        │   └── ChatList.js      # Список диалогов
        │
        └── pages/               # Страницы приложения
            ├── ChatPage.js      # Диалоги с ИИ
            ├── LibraryPage.js   # Библиотека знаний
            ├── ExercisesPage.js # Упражнения
            ├── ProgressPage.js  # Статистика
            └── SettingsPage.js  # Настройки
```

---

## 🚀 Запуск проекта

### Требования

- **Python 3.11+**
- **Node.js 18+**
- **MySQL 8.0+** (или Docker)
- **CUDA** (опционально, для GPU)

### Вариант 1: Ручной запуск

#### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd Socialskillscoach

# Копируем .env
copy .env.example .env
# Редактируем .env своими настройками
```

#### 2. Установка зависимостей

```bash
# Запускаем скрипт установки
setup.bat
```

Или вручную:

```bash
# Backend
cd Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# AI
cd ../AI
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../Frontend
npm install
```

#### 3. Запуск сервисов

В **трёх разных терминалах**:

```bash
# Терминал 1 - Backend API
run-backend.bat
# Доступен на http://localhost:8000
# Swagger docs: http://localhost:8000/docs

# Терминал 2 - AI Training UI
run-ai.bat
# Доступен на http://localhost:7860

# Терминал 3 - Frontend
run-frontend.bat
# Доступен на http://localhost:3000
```

#### 4. Запуск Electron (опционально)

```bash
run-electron.bat
```

### Вариант 2: Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

---

## 🤖 AI модуль

### Архитектура модели

```
┌─────────────────────────────────────────────────────────────┐
│                    SocialSkillsModel                         │
│                   (PyTorch Transformer)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │  Embedding  │───▶│  Transformer │───▶│    LM Head      │  │
│  │   Layer     │    │   Blocks     │    │   (Output)      │  │
│  │  (512 dim)  │    │  (6 layers)  │    │                 │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
│                                                              │
│  Параметры по умолчанию:                                    │
│  • vocab_size: 32000 (SentencePiece)                        │
│  • d_model: 512                                              │
│  • n_heads: 8                                                │
│  • n_layers: 6                                               │
│  • d_ff: 2048                                                │
│  • max_seq_len: 1024                                         │
└─────────────────────────────────────────────────────────────┘
```

### Training UI (Gradio)

Веб-интерфейс для обучения модели доступен на **http://localhost:7860**

#### Вкладки:

1. **🔄 Загрузка модели**
   - Загрузка существующей модели
   - Создание новой модели
   - Сохранение обученной модели

2. **📚 SFT Training** (Supervised Fine-Tuning)
   - Обучение на диалогах
   - Настройка: learning_rate, batch_size, epochs
   - Формат данных: JSON с полями `input`, `output`

3. **🎯 DPO Training** (Direct Preference Optimization)
   - Обучение на предпочтениях
   - Формат: `prompt`, `chosen`, `rejected`
   - Настройка beta параметра

4. **📚 Обучение на документах** (NEW!)
   - Загрузка книг и документов (PDF, DOCX, EPUB, TXT)
   - Автоматическая обработка и чанкинг
   - Интеграция с RAG для поиска по базе знаний
   - Поддержка обучения из папки с книгами

5. **🧪 Тестирование**
   - Генерация ответов
   - Настройка: temperature, max_tokens, top_p

### Обучение на книгах и документах

Модуль поддерживает обучение на документах следующих форматов:
- **PDF** (.pdf)
- **Microsoft Word** (.docx, .doc)
- **EPUB** (.epub) - электронные книги
- **Текст** (.txt, .md)

#### Использование через веб-интерфейс:

1. Откройте Training UI: http://localhost:7860
2. Перейдите во вкладку "📚 Обучение на документах"
3. Загрузите файлы или укажите путь к папке с книгами
4. Выберите тип данных:
   - **knowledge** - для RAG (поиск по базе знаний)
   - **sft** - для дообучения модели
   - **qa** - формат вопрос-ответ
5. Нажмите "Обработать"
6. Запустите обучение на подготовленных данных

#### Использование через код:

```python
from training.document_loader import DocumentLoader, process_books_for_training

# Обработка книг из папки
results = process_books_for_training(
    input_dir="path/to/books/",
    output_dir="data/documents/",
    chunk_size=1000
)
```

#### Рекомендуемые книги для обучения:

- Дейл Карнеги - "Как завоёвывать друзей"
- Марк Гоулстон - "Я слышу вас насквозь"
- Керри Паттерсон - "Трудные диалоги"
- Крис Восс - "Никаких компромиссов"
- Маршалл Розенберг - "Ненасильственное общение"

### Форматы данных для обучения

#### SFT Dataset (JSON Lines)
```json
{"input": "Как мне начать разговор?", "output": "Начните с открытого вопроса..."}
{"input": "Что делать в конфликте?", "output": "Сохраняйте спокойствие..."}
```

#### DPO Dataset (JSON Lines)
```json
{
  "prompt": "Коллега критикует мою работу",
  "chosen": "Спасибо за обратную связь. Можете уточнить...",
  "rejected": "Это несправедливо! Вы не правы!"
}
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### Users
| Method | Endpoint | Описание |
|--------|----------|----------|
| POST | `/users/register` | Регистрация |
| POST | `/users/login` | Вход |
| GET | `/users/me` | Профиль |
| PUT | `/users/me` | Обновить профиль |
| GET | `/users/me/progress` | Прогресс пользователя |

#### Chats
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/chats` | Список чатов |
| POST | `/chats` | Создать чат |
| GET | `/chats/{id}` | Получить чат |
| DELETE | `/chats/{id}` | Удалить чат |
| POST | `/chats/{id}/messages` | Отправить сообщение |

#### Analysis
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/analysis/chat/{id}` | Анализ чата |
| GET | `/analysis/chat/{id}/patterns` | Паттерны общения |
| GET | `/analysis/chat/{id}/sentiment` | Анализ эмоций |
| GET | `/analysis/recommendations` | Рекомендации |
| POST | `/analysis/text` | Анализ текста |

#### Library
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/library/topics` | Список тем |
| GET | `/library/topics/{id}` | Тема |
| GET | `/library/techniques` | Техники |
| GET | `/library/techniques/{id}` | Техника |
| GET | `/library/search?q=` | Поиск |

#### Exercises
| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/exercises` | Список упражнений |
| GET | `/exercises/{id}` | Упражнение |
| POST | `/exercises/{id}/start` | Начать |
| POST | `/exercises/{id}/submit` | Отправить ответ |

---

## 🔧 Конфигурация

### Переменные окружения (.env)

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=socialskills
DB_PASSWORD=your_password
DB_NAME=socialskills

# Security
SECRET_KEY=your-secret-key-change-in-production

# AI
AI_MODULE_URL=http://localhost:7860
DEVICE=cuda  # или cpu

# External APIs (опционально)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Настройки AI модели (AI/config.py)

```python
# Модель
model.vocab_size = 32000
model.d_model = 512
model.n_heads = 8
model.n_layers = 6

# Обучение
training.learning_rate = 1e-4
training.batch_size = 4
training.epochs = 3

# RAG
rag.chunk_size = 512
rag.top_k = 5
```

---

## 🎨 Frontend

### Технологии

- **Electron** — десктопное приложение
- **React 18** — UI библиотека
- **Material UI 5** — компоненты
- **Zustand** — state management
- **React Router** — навигация
- **Axios** — HTTP клиент

### Структура страниц

```
/chat              — Диалоги с ИИ
/chat/:id          — Конкретный диалог
/library           — Библиотека знаний
/exercises         — Упражнения
/progress          — Прогресс и статистика
/settings          — Настройки
```

### Тема оформления

Тёмная тема с фиолетовым акцентом:
- Primary: `#7c3aed` (фиолетовый)
- Background: `#1a1a2e` (тёмно-синий)
- Paper: `#16213e`

---

## 🧪 Разработка

### Запуск тестов

```bash
# Backend
cd Backend
pytest

# Frontend
cd Frontend
npm test
```

### Линтинг

```bash
# Python
ruff check .
black .

# JavaScript
npm run lint
```

### Сборка для продакшена

```bash
# Frontend + Electron
cd Frontend
npm run electron:build
```

---

## 📊 База данных

### Схема

```sql
-- Пользователи
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    created_at TIMESTAMP
);

-- Чаты
CREATE TABLE chats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT REFERENCES users(id),
    title VARCHAR(255),
    scenario VARCHAR(50),
    created_at TIMESTAMP
);

-- Сообщения
CREATE TABLE chat_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chat_id INT REFERENCES chats(id),
    role ENUM('user', 'assistant'),
    content TEXT,
    created_at TIMESTAMP
);

-- Прогресс
CREATE TABLE progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT REFERENCES users(id),
    skill VARCHAR(100),
    level INT,
    updated_at TIMESTAMP
);

-- База знаний
CREATE TABLE knowledge_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    topic_id INT,
    title VARCHAR(255),
    content TEXT,
    embedding BLOB
);
```

---

## 🔒 Безопасность

- JWT токены для авторизации
- Хеширование паролей (bcrypt)
- CORS настройки
- Rate limiting
- Валидация входных данных (Pydantic)

---

## 📝 Лицензия

MIT License

---

## 🤝 Контрибьютинг

1. Fork репозитория
2. Создайте ветку (`git checkout -b feature/amazing`)
3. Commit изменений (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing`)
5. Создайте Pull Request

---

## ❓ FAQ

**Q: Как добавить свои данные для обучения?**
A: Создайте JSON файл в формате SFT/DPO и загрузите через Gradio UI на вкладке обучения.

**Q: Можно ли использовать без GPU?**
A: Да, установите `DEVICE=cpu` в .env. Обучение будет медленнее.

**Q: Как подключить внешний LLM (GPT-4)?**
A: Добавьте `OPENAI_API_KEY` в .env и выберите provider в настройках AI.

**Q: Где хранятся обученные модели?**
A: В папке `AI/models/` в формате PyTorch checkpoint.
