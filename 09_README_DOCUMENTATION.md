# =============================================
# README И ДОКУМЕНТАЦИЯ
# =============================================

# ============================================
# ФАЙЛ: README.md
# ============================================

# 🚀 Content Automation System

Полностью автоматизированная система генерации и публикации контента в социальных сетях с монетизацией через affiliate marketing.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-green)
![React](https://img.shields.io/badge/react-18.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Возможности

### 🎯 Контент
- **AI-генерация контента** — сценарии для видео, посты, threads
- **Мультиплатформенность** — TikTok, YouTube, Twitter/X, LinkedIn, Telegram
- **Автопостинг** — планирование и автоматическая публикация
- **Batch-генерация** — создание контента пакетами

### 💰 Монетизация
- **Affiliate маркетинг** — интеграция с партнёрскими программами
- **Воронка продаж** — автоматические Telegram-воронки
- **Трекинг конверсий** — отслеживание продаж и комиссий
- **Аналитика ROI** — полная финансовая отчётность

### 📊 Аналитика
- **Real-time дашборд** — все метрики в одном месте
- **A/B тестирование** — оптимизация контента
- **Отчёты** — еженедельные автоматические отчёты
- **Jarvis** — голосовой AI-ассистент

### 🔒 Безопасность
- **Мультиаккаунтинг** — безопасное управление аккаунтами
- **Прокси-ротация** — защита от банов
- **Health мониторинг** — отслеживание здоровья аккаунтов

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│                     Dashboard + Voice UI                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                     │
│         Auth │ Content │ Analytics │ Accounts │ Voice        │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     ┌──────────┐      ┌──────────┐      ┌──────────┐
     │ PostgreSQL│      │  Redis   │      │ Celery   │
     │    DB    │      │  Cache   │      │ Workers  │
     └──────────┘      └──────────┘      └──────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
     ┌──────────┐      ┌──────────┐      ┌──────────┐
     │ Claude   │      │ Social   │      │ Telegram │
     │ AI API   │      │ Media    │      │   Bot    │
     └──────────┘      │  APIs    │      └──────────┘
                       └──────────┘
```

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose
- 4GB RAM минимум
- API ключи (см. ниже)

### Установка

```bash
# Клонируем репозиторий
git clone https://github.com/your-repo/content-automation.git
cd content-automation

# Запускаем установку
make setup

# Или вручную:
cp .env.example .env
# Заполните .env своими API ключами
docker-compose up -d
```

### Первый вход
- URL: http://localhost:3000
- Email: admin@example.com
- Пароль: admin123

## ⚙️ Конфигурация

### Необходимые API ключи

| Сервис | Для чего | Где получить |
|--------|----------|--------------|
| Anthropic | AI генерация | https://console.anthropic.com |
| OpenAI | Whisper STT | https://platform.openai.com |
| ElevenLabs | Голос Jarvis | https://elevenlabs.io |
| HeyGen | AI видео | https://heygen.com |
| TikTok | Публикация | https://developers.tiktok.com |
| Twitter | Публикация | https://developer.twitter.com |
| Telegram | Бот воронки | https://t.me/BotFather |

### Примерный бюджет

| Статья | Стоимость/мес |
|--------|---------------|
| Claude API | $50-200 |
| ElevenLabs | $22-99 |
| HeyGen | $48-144 |
| VPS хостинг | $20-50 |
| Прокси | $30-100 |
| **Итого** | **$170-600** |

## 📁 Структура проекта

```
content-automation-system/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/          # API эндпоинты
│   │   ├── core/            # AI агенты, security
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── services/        # Бизнес-логика
│   │   │   ├── ai/          # AI сервисы
│   │   │   ├── social/      # Публикаторы
│   │   │   └── analytics/   # Аналитика
│   │   └── db/              # База данных
│   ├── workers/             # Celery задачи
│   ├── migrations/          # Alembic миграции
│   └── tests/               # Тесты
│
├── frontend/                 # React dashboard
│   ├── src/
│   │   ├── components/      # UI компоненты
│   │   ├── pages/           # Страницы
│   │   ├── services/        # API клиент
│   │   └── store/           # Zustand store
│   └── public/
│
├── telegram-bot/            # Telegram бот
│   └── bot.py
│
├── scripts/                 # Скрипты
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── docker-compose.yml       # Docker конфиг
├── .env.example             # Пример переменных
├── Makefile                 # Команды
└── README.md
```

## 🎯 Использование

### Создание контента

```bash
# Через API
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "niche_id": "uuid",
    "type": "short_video",
    "target_platform": "tiktok",
    "topic": "5 лайфхаков для продуктивности"
  }'
```

### Jarvis голосовой запрос

```bash
# Текстовый запрос
curl -X POST "http://localhost:8000/api/v1/voice/query?query=сколько я заработал сегодня"

# Голосовой (через UI)
# Откройте http://localhost:3000/voice и нажмите на микрофон
```

### Планирование публикации

```bash
curl -X POST "http://localhost:8000/api/v1/content/{content_id}/schedule" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "scheduled_for": "2024-01-15T19:00:00Z",
    "account_ids": ["uuid1", "uuid2"]
  }'
```

## 🤖 AI Агенты

Система использует 9 специализированных AI-агентов:

| Агент | Роль |
|-------|------|
| 🔍 Niche Analyst | Поиск прибыльных ниш |
| 💰 Monetization Strategist | Стратегия монетизации |
| 📝 Content Strategist | Контент-планирование |
| ✍️ Copywriter | Написание текстов |
| 🎬 Video Producer | ТЗ для видео |
| 📱 SMM Manager | Управление аккаунтами |
| 📊 Data Analyst | Аналитика |
| 🔗 Integrator | Интеграции |
| 🤖 Jarvis | Главный координатор |

## 📊 API Документация

После запуска доступна по адресам:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Основные эндпоинты

```
POST   /api/v1/auth/login          # Авторизация
GET    /api/v1/analytics/dashboard  # Дашборд
GET    /api/v1/accounts            # Список аккаунтов
POST   /api/v1/content/generate    # Генерация контента
POST   /api/v1/voice/query         # Запрос к Jarvis
```

## 🔧 Разработка

```bash
# Запуск в dev режиме
make dev

# Просмотр логов
make logs

# Запуск тестов
make test

# Миграции БД
make migrate

# Подключение к БД
make psql
```

## 🚢 Деплой

### Railway (рекомендуется)

1. Форкните репозиторий
2. Подключите к Railway
3. Добавьте переменные окружения
4. Деплой автоматический

### VPS

```bash
# На сервере
git clone https://github.com/your-repo/content-automation.git
cd content-automation
cp .env.example .env
# Заполните .env
./scripts/setup.sh
```

## 📈 Roadmap

- [x] MVP с базовой функциональностью
- [ ] Instagram интеграция
- [ ] YouTube длинные видео
- [ ] Расширенная аналитика
- [ ] Mobile приложение
- [ ] White-label версия

## 🤝 Contributing

1. Fork репозитория
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Откройте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 💬 Поддержка

- Issues: https://github.com/your-repo/issues
- Telegram: @your_support_bot


# ============================================
# ФАЙЛ: docs/API.md
# ============================================

# API Documentation

## Authentication

### Login
```http
POST /api/v1/auth/login
```

**Parameters:**
- `email` (string): User email
- `password` (string): User password

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

---

## Content

### Generate Content
```http
POST /api/v1/content/generate
Authorization: Bearer {token}
```

**Body:**
```json
{
  "niche_id": "uuid",
  "type": "short_video",
  "target_platform": "tiktok",
  "topic": "optional topic",
  "tone": "engaging",
  "include_cta": true,
  "affiliate_id": "optional uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Generated title",
  "hook": "First 2 seconds hook",
  "script": "Full script",
  "caption": "Post caption",
  "hashtags": ["tag1", "tag2"],
  "status": "generating",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### List Content
```http
GET /api/v1/content?status=ready&platform=tiktok&limit=20
Authorization: Bearer {token}
```

### Schedule Content
```http
POST /api/v1/content/{content_id}/schedule
Authorization: Bearer {token}
```

**Body:**
```json
{
  "scheduled_for": "2024-01-15T19:00:00Z",
  "account_ids": ["uuid1", "uuid2"]
}
```

---

## Accounts

### List Accounts
```http
GET /api/v1/accounts?platform=tiktok&status=active
Authorization: Bearer {token}
```

### Create Account
```http
POST /api/v1/accounts
Authorization: Bearer {token}
```

**Body:**
```json
{
  "platform": "tiktok",
  "username": "myaccount",
  "display_name": "My Account",
  "niche_id": "uuid",
  "proxy_id": "uuid",
  "credentials": {
    "access_token": "xxx"
  }
}
```

### Get Account Stats
```http
GET /api/v1/accounts/{account_id}/stats
Authorization: Bearer {token}
```

---

## Analytics

### Dashboard Summary
```http
GET /api/v1/analytics/dashboard
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_accounts": 25,
  "active_accounts": 20,
  "total_followers": 150000,
  "published_today": 15,
  "revenue_month": 2500.00,
  "new_leads_today": 45,
  "conversion_rate": 3.5,
  "platforms_stats": [...]
}
```

### Funnel Stats
```http
GET /api/v1/analytics/funnel?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

### Revenue Stats
```http
GET /api/v1/analytics/revenue?period=month
Authorization: Bearer {token}
```

---

## Voice Assistant

### Text Query
```http
POST /api/v1/voice/query?query=сколько заработал сегодня
Authorization: Bearer {token}
```

**Response:**
```json
{
  "response": "Сегодня вы заработали $150. Это на 20% больше чем вчера!"
}
```

### Voice Query
```http
POST /api/v1/voice/speak
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Body:**
- `audio`: audio file (webm/mp3)

**Response:**
```json
{
  "query": "transcribed text",
  "response": "AI response",
  "audio": "base64 encoded audio"
}
```

---

## Niches

### Analyze Niche
```http
POST /api/v1/niches/analyze?niche_name=productivity tools
Authorization: Bearer {token}
```

### Suggest Niches
```http
POST /api/v1/niches/suggest?category=health&count=5
Authorization: Bearer {token}
```

---

## Webhooks

### Stripe Payment
```http
POST /api/v1/webhooks/stripe
Stripe-Signature: {signature}
```

### Telegram Updates
```http
POST /api/v1/webhooks/telegram
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error


# ============================================
# ФАЙЛ: docs/SETUP.md
# ============================================

# Полный гайд по настройке

## 1. Получение API ключей

### Anthropic (Claude AI)
1. Зайдите на https://console.anthropic.com
2. Создайте аккаунт
3. Перейдите в Settings → API Keys
4. Создайте новый ключ
5. Скопируйте в `ANTHROPIC_API_KEY`

### OpenAI (Whisper)
1. Зайдите на https://platform.openai.com
2. Создайте API key
3. Скопируйте в `OPENAI_API_KEY`

### ElevenLabs (Voice)
1. Зайдите на https://elevenlabs.io
2. Зарегистрируйтесь
3. Перейдите в Profile → API Key
4. Скопируйте в `ELEVENLABS_API_KEY`

### TikTok Developer
1. Зайдите на https://developers.tiktok.com
2. Создайте приложение
3. Получите Client Key и Secret
4. Настройте OAuth redirect URL

### Twitter/X Developer
1. Зайдите на https://developer.twitter.com
2. Создайте проект и приложение
3. Получите API Key, Secret, Bearer Token
4. Настройте OAuth 1.0a

### Telegram Bot
1. Напишите @BotFather в Telegram
2. Отправьте /newbot
3. Следуйте инструкциям
4. Скопируйте токен в `TELEGRAM_BOT_TOKEN`

## 2. Настройка прокси

Для безопасного мультиаккаунтинга нужны резидентные прокси.

Рекомендуемые провайдеры:
- Bright Data
- Smartproxy
- Oxylabs

Настройка в системе:
```sql
INSERT INTO proxies (type, host, port, username, password, country)
VALUES ('residential', 'proxy.example.com', 10000, 'user', 'pass', 'US');
```

## 3. Подключение аккаунтов

### TikTok
1. Получите OAuth токен через TikTok Login Kit
2. Добавьте в систему:
```json
{
  "platform": "tiktok",
  "credentials": {
    "access_token": "xxx",
    "refresh_token": "xxx"
  }
}
```

### Twitter
1. Авторизуйте приложение через OAuth
2. Сохраните access_token и access_token_secret

### LinkedIn
1. Используйте OAuth 2.0
2. Запросите scope: w_member_social

## 4. Настройка воронки

### Telegram Bot
1. Создайте канал для контента
2. Добавьте бота администратором
3. Настройте webhook:
```bash
curl "https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://yourdomain.com/api/v1/webhooks/telegram"
```

### Шаблоны сообщений
Отредактируйте в `workers/tasks/funnel_tasks.py`:
```python
FUNNEL_MESSAGES = {
    "day_0": {
        "message": "Ваше приветственное сообщение..."
    }
}
```

## 5. Stripe интеграция

1. Создайте аккаунт на https://stripe.com
2. Получите API ключи (test и live)
3. Настройте webhook endpoint
4. Добавьте события: payment_intent.succeeded, charge.refunded

## 6. Cloudflare R2 (Storage)

1. Создайте аккаунт Cloudflare
2. Создайте R2 bucket
3. Получите API токен с правами на R2
4. Настройте публичный домен для CDN

## 7. Первый запуск

```bash
# 1. Клонируем
git clone https://github.com/your-repo/content-automation.git
cd content-automation

# 2. Настраиваем окружение
cp .env.example .env
nano .env  # Заполняем все ключи

# 3. Запускаем
make setup

# 4. Проверяем
curl http://localhost:8000/health
```

## 8. Тестирование

```bash
# Тест генерации контента
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"niche_id": "test", "type": "short_video", "target_platform": "tiktok"}'

# Тест Jarvis
curl "http://localhost:8000/api/v1/voice/query?query=привет"
```

## Troubleshooting

### Ошибка подключения к БД
```bash
docker-compose logs postgres
# Проверьте что порт 5432 свободен
```

### Celery задачи не выполняются
```bash
docker-compose logs celery_worker
# Проверьте подключение к Redis
```

### AI генерация не работает
```bash
# Проверьте API ключ
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```
