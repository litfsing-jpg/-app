# 🏗️ АРХИТЕКТУРА СИСТЕМЫ АВТОМАТИЧЕСКОГО КОНТЕНТА

## Общая схема системы

```
                                    ┌─────────────────────────┐
                                    │     👤 ПОЛЬЗОВАТЕЛЬ     │
                                    │  (Web Dashboard / Voice) │
                                    └───────────┬─────────────┘
                                                │
                                    ┌───────────▼─────────────┐
                                    │     🌐 NGINX / CDN      │
                                    │   (Reverse Proxy, SSL)  │
                                    └───────────┬─────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    │                           │                           │
        ┌───────────▼───────────┐   ┌───────────▼───────────┐   ┌───────────▼───────────┐
        │   🖥️ FRONTEND         │   │   🎙️ VOICE API        │   │   📱 TELEGRAM BOT     │
        │   React Dashboard     │   │   Whisper + TTS       │   │   Aiogram             │
        │   Port: 3000          │   │   Port: 8001          │   │   Webhook             │
        └───────────┬───────────┘   └───────────┬───────────┘   └───────────┬───────────┘
                    │                           │                           │
                    └───────────────────────────┼───────────────────────────┘
                                                │
                                    ┌───────────▼─────────────┐
                                    │   ⚡ BACKEND API        │
                                    │   FastAPI (Python)      │
                                    │   Port: 8000            │
                                    └───────────┬─────────────┘
                                                │
            ┌───────────────┬───────────────────┼───────────────────┬───────────────┐
            │               │                   │                   │               │
┌───────────▼───────┐ ┌─────▼─────┐ ┌───────────▼───────┐ ┌─────────▼─────┐ ┌───────▼───────┐
│   🗄️ PostgreSQL   │ │ 🔴 Redis  │ │  🤖 AI SERVICES   │ │ 📤 PUBLISHERS │ │ 💳 PAYMENTS   │
│   База данных     │ │ Кеш/Queue │ │  Claude, OpenAI   │ │ TikTok, YT    │ │ Stripe        │
└───────────────────┘ └───────────┘ │  ElevenLabs       │ │ Twitter, LI   │ └───────────────┘
                                    │  HeyGen, Runway   │ │ Telegram      │
                                    └───────────────────┘ └───────────────┘
                                                │
                                    ┌───────────▼─────────────┐
                                    │   📁 FILE STORAGE      │
                                    │   S3 / Cloudflare R2   │
                                    │   (видео, картинки)    │
                                    └─────────────────────────┘
```

---

## 📦 Технический стек

### Выбранные технологии (с обоснованием)

```
┌─────────────────┬─────────────────────┬─────────────────────────────────────┐
│ Компонент       │ Технология          │ Почему выбрали                      │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Backend         │ Python + FastAPI    │ Лучшая поддержка AI библиотек,      │
│                 │                     │ async, автодокументация API         │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Frontend        │ React + TypeScript  │ Популярный, много библиотек,        │
│                 │ + Tailwind CSS      │ легко найти помощь                  │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ База данных     │ PostgreSQL          │ Надёжность, масштабируемость,       │
│                 │                     │ JSON поддержка для гибкости         │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Кеш/Очереди     │ Redis               │ Быстрый кеш, очереди задач,         │
│                 │                     │ pub/sub для real-time               │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Task Queue      │ Celery + Redis      │ Фоновые задачи (генерация,          │
│                 │                     │ публикация по расписанию)           │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Файлы           │ Cloudflare R2       │ S3-совместимый, дешевле AWS,        │
│                 │                     │ бесплатный egress                   │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Хостинг Backend │ Railway             │ Простой деплой, PostgreSQL          │
│                 │                     │ включён, автоскейлинг               │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Хостинг Frontend│ Vercel              │ Бесплатный для React,               │
│                 │                     │ мгновенный деплой                   │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Voice (STT)     │ OpenAI Whisper      │ Лучшее качество распознавания       │
├─────────────────┼─────────────────────┼─────────────────────────────────────┤
│ Voice (TTS)     │ ElevenLabs          │ Самые реалистичные голоса           │
└─────────────────┴─────────────────────┴─────────────────────────────────────┘
```

---

## 🗄️ СХЕМА БАЗЫ ДАННЫХ

### ER-диаграмма

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    niches       │       │   affiliates    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │       │ id (PK)         │
│ email           │       │ name            │       │ name            │
│ password_hash   │       │ description     │       │ platform        │
│ name            │       │ status          │       │ url             │
│ role            │       │ potential_score │       │ commission_type │
│ settings (JSON) │       │ competition     │       │ commission_rate │
│ created_at      │       │ avg_ticket      │       │ avg_check       │
│ updated_at      │       │ created_at      │       │ cookie_days     │
└────────┬────────┘       └────────┬────────┘       │ niche_id (FK)   │
         │                         │                │ status          │
         │                         │                │ created_at      │
         │                         │                └────────┬────────┘
         │                         │                         │
         │    ┌────────────────────┴─────────────────────────┘
         │    │
         │    │         ┌─────────────────┐
         │    │         │   accounts      │
         │    │         ├─────────────────┤
         │    │         │ id (PK)         │
         │    └────────▶│ niche_id (FK)   │
         │              │ platform        │
         │              │ username        │
         │              │ credentials(ENC)│
         │              │ proxy_id (FK)   │
         │              │ status          │
         │              │ followers       │
         │              │ health_score    │
         │              │ last_posted_at  │
         │              │ created_at      │
         │              └────────┬────────┘
         │                       │
         │                       │
         │    ┌──────────────────┴──────────────────┐
         │    │                                     │
         │    │         ┌─────────────────┐         │
         │    │         │    content      │         │
         │    │         ├─────────────────┤         │
         │    │         │ id (PK)         │         │
         │    │         │ niche_id (FK)   │         │
         │    │         │ type            │         │
         │    │         │ platform        │         │
         │    │         │ title           │         │
         │    │         │ script          │         │
         │    │         │ media_url       │         │
         │    │         │ thumbnail_url   │         │
         │    │         │ status          │         │
         │    │         │ scheduled_at    │         │
         │    │         │ published_at    │         │
         │    │         │ affiliate_id(FK)│         │
         │    │         │ created_at      │         │
         │    │         └────────┬────────┘         │
         │    │                  │                  │
         │    │                  │                  │
         │    │    ┌─────────────┴───────────────┐  │
         │    │    │                             │  │
         │    │    │    ┌─────────────────┐      │  │
         │    │    │    │  publications   │      │  │
         │    │    │    ├─────────────────┤      │  │
         │    │    │    │ id (PK)         │      │  │
         │    │    └───▶│ content_id (FK) │      │  │
         │    │         │ account_id (FK) │◀─────┘  │
         │    │         │ platform_post_id│         │
         │    │         │ url             │         │
         │    │         │ status          │         │
         │    │         │ published_at    │         │
         │    │         └────────┬────────┘         │
         │    │                  │                  │
         │    │                  │                  │
         │    │    ┌─────────────┴─────────────┐    │
         │    │    │                           │    │
         │    │    │    ┌─────────────────┐    │    │
         │    │    │    │    metrics      │    │    │
         │    │    │    ├─────────────────┤    │    │
         │    │    │    │ id (PK)         │    │    │
         │    │    └───▶│ publication_id  │    │    │
         │    │         │ views           │    │    │
         │    │         │ likes           │    │    │
         │    │         │ comments        │    │    │
         │    │         │ shares          │    │    │
         │    │         │ clicks          │    │    │
         │    │         │ engagement_rate │    │    │
         │    │         │ recorded_at     │    │    │
         │    │         └─────────────────┘    │    │
         │    │                                │    │
         │    │    ┌───────────────────────────┘    │
         │    │    │                                │
         │    │    │    ┌─────────────────┐         │
         │    │    │    │     leads       │         │
         │    │    │    ├─────────────────┤         │
         │    │    │    │ id (PK)         │         │
         │    └────┴───▶│ account_id (FK) │◀────────┘
         │              │ content_id (FK) │
         │              │ source_platform │
         │              │ telegram_id     │
         │              │ email           │
         │              │ status          │
         │              │ funnel_stage    │
         │              │ created_at      │
         │              └────────┬────────┘
         │                       │
         │                       │
         │              ┌────────▼────────┐
         │              │   conversions   │
         │              ├─────────────────┤
         │              │ id (PK)         │
         │              │ lead_id (FK)    │
         │              │ affiliate_id(FK)│
         │              │ amount          │
         │              │ commission      │
         │              │ status          │
         │              │ external_id     │
         │              │ converted_at    │
         │              └─────────────────┘
         │
         │
         │              ┌─────────────────┐
         │              │    proxies      │
         │              ├─────────────────┤
         └─────────────▶│ id (PK)         │
                        │ type            │
                        │ host            │
                        │ port            │
                        │ username        │
                        │ password        │
                        │ country         │
                        │ status          │
                        │ assigned_to(FK) │
                        └─────────────────┘
```

---

### SQL Миграции (полная схема)

```sql
-- =============================================
-- ФАЙЛ: migrations/001_initial_schema.sql
-- =============================================

-- Расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================
-- ТАБЛИЦА: users (пользователи системы)
-- =============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    settings JSONB DEFAULT '{
        "notifications": true,
        "timezone": "UTC",
        "language": "ru"
    }'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_users_email ON users(email);

-- =============================================
-- ТАБЛИЦА: niches (ниши для контента)
-- =============================================
CREATE TABLE niches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'archived')),
    
    -- Аналитика ниши
    potential_score INTEGER CHECK (potential_score BETWEEN 1 AND 10),
    competition_level VARCHAR(20) CHECK (competition_level IN ('low', 'medium', 'high')),
    avg_product_price DECIMAL(10, 2),
    search_volume INTEGER,
    trend VARCHAR(20) CHECK (trend IN ('growing', 'stable', 'declining')),
    
    -- Метаданные
    keywords JSONB DEFAULT '[]'::jsonb,
    target_audience JSONB DEFAULT '{}'::jsonb,
    content_pillars JSONB DEFAULT '[]'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_niches_status ON niches(status);
CREATE INDEX idx_niches_slug ON niches(slug);

-- =============================================
-- ТАБЛИЦА: affiliates (партнёрские программы)
-- =============================================
CREATE TABLE affiliates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
    
    name VARCHAR(200) NOT NULL,
    platform VARCHAR(50) NOT NULL, -- ClickBank, Amazon, CJ, Direct
    url TEXT NOT NULL,
    affiliate_link TEXT,
    
    -- Финансы
    commission_type VARCHAR(20) NOT NULL CHECK (commission_type IN ('percentage', 'fixed', 'recurring')),
    commission_rate DECIMAL(5, 2) NOT NULL, -- процент или фиксированная сумма
    avg_order_value DECIMAL(10, 2),
    epc DECIMAL(10, 4), -- Earnings Per Click
    cookie_duration_days INTEGER DEFAULT 30,
    
    -- Качество
    gravity_score DECIMAL(5, 2), -- для ClickBank
    refund_rate DECIMAL(5, 2),
    landing_quality INTEGER CHECK (landing_quality BETWEEN 1 AND 10),
    
    -- Статус
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'expired', 'rejected')),
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_affiliates_niche ON affiliates(niche_id);
CREATE INDEX idx_affiliates_status ON affiliates(status);
CREATE INDEX idx_affiliates_platform ON affiliates(platform);

-- =============================================
-- ТАБЛИЦА: proxies (прокси для аккаунтов)
-- =============================================
CREATE TABLE proxies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    type VARCHAR(20) NOT NULL CHECK (type IN ('http', 'https', 'socks5', 'residential')),
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(100),
    password VARCHAR(255),
    
    country VARCHAR(2), -- ISO код страны
    city VARCHAR(100),
    
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'banned', 'expired')),
    
    -- Метрики
    last_checked_at TIMESTAMP WITH TIME ZONE,
    response_time_ms INTEGER,
    success_rate DECIMAL(5, 2),
    
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_proxies_status ON proxies(status);
CREATE INDEX idx_proxies_country ON proxies(country);

-- =============================================
-- ТАБЛИЦА: accounts (аккаунты соц. сетей)
-- =============================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
    proxy_id UUID REFERENCES proxies(id) ON DELETE SET NULL,
    
    platform VARCHAR(30) NOT NULL CHECK (platform IN (
        'tiktok', 'youtube', 'twitter', 'linkedin', 
        'instagram', 'telegram', 'facebook', 'threads'
    )),
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    bio TEXT,
    profile_image_url TEXT,
    
    -- Учётные данные (зашифрованные)
    credentials JSONB NOT NULL, -- {access_token, refresh_token, api_key, etc}
    
    -- Метрики
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    total_posts INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2),
    
    -- Здоровье аккаунта
    health_score INTEGER DEFAULT 100 CHECK (health_score BETWEEN 0 AND 100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'warming_up', 'active', 'paused', 'shadowbanned', 
        'suspended', 'banned', 'needs_verification'
    )),
    
    -- Лимиты и расписание
    daily_post_limit INTEGER DEFAULT 5,
    posts_today INTEGER DEFAULT 0,
    last_posted_at TIMESTAMP WITH TIME ZONE,
    warmup_started_at TIMESTAMP WITH TIME ZONE,
    
    -- Настройки
    settings JSONB DEFAULT '{
        "auto_post": true,
        "posting_hours": [9, 12, 15, 18, 21],
        "timezone": "UTC"
    }'::jsonb,
    
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(platform, username)
);

-- Индексы
CREATE INDEX idx_accounts_platform ON accounts(platform);
CREATE INDEX idx_accounts_niche ON accounts(niche_id);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_health ON accounts(health_score);

-- =============================================
-- ТАБЛИЦА: content (контент/креативы)
-- =============================================
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
    affiliate_id UUID REFERENCES affiliates(id) ON DELETE SET NULL,
    
    -- Тип контента
    type VARCHAR(30) NOT NULL CHECK (type IN (
        'short_video', 'long_video', 'image', 'carousel',
        'text_post', 'thread', 'story', 'article'
    )),
    target_platform VARCHAR(30) NOT NULL, -- Для какой платформы создан
    
    -- Контент
    title VARCHAR(500),
    hook TEXT, -- Первые слова/кадры
    script TEXT, -- Полный сценарий
    caption TEXT, -- Подпись к посту
    hashtags JSONB DEFAULT '[]'::jsonb,
    
    -- Медиа файлы
    media_url TEXT, -- Основной файл (видео/картинка)
    thumbnail_url TEXT,
    additional_media JSONB DEFAULT '[]'::jsonb, -- Для каруселей
    
    -- CTA и ссылки
    call_to_action TEXT,
    link_url TEXT, -- Партнёрская ссылка
    link_shortcode VARCHAR(50), -- bit.ly код
    
    -- Статус
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN (
        'draft', 'generating', 'ready', 'scheduled', 
        'published', 'failed', 'archived'
    )),
    
    -- Планирование
    scheduled_for TIMESTAMP WITH TIME ZONE,
    
    -- AI метаданные
    ai_model VARCHAR(50), -- claude-3, gpt-4, etc
    generation_prompt TEXT,
    generation_cost DECIMAL(10, 4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_content_niche ON content(niche_id);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_type ON content(type);
CREATE INDEX idx_content_platform ON content(target_platform);
CREATE INDEX idx_content_scheduled ON content(scheduled_for) WHERE status = 'scheduled';

-- =============================================
-- ТАБЛИЦА: publications (публикации)
-- =============================================
CREATE TABLE publications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    
    -- Идентификаторы платформы
    platform_post_id VARCHAR(255), -- ID поста на платформе
    platform_url TEXT, -- Прямая ссылка на пост
    
    -- Статус
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'publishing', 'published', 
        'failed', 'deleted', 'removed_by_platform'
    )),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Время
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_publications_content ON publications(content_id);
CREATE INDEX idx_publications_account ON publications(account_id);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_publications_published ON publications(published_at);

-- =============================================
-- ТАБЛИЦА: metrics (метрики публикаций)
-- =============================================
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publication_id UUID NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
    
    -- Основные метрики
    views INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    
    -- Взаимодействия
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    
    -- Вовлечённость
    engagement_rate DECIMAL(5, 2),
    avg_watch_time_seconds INTEGER,
    completion_rate DECIMAL(5, 2), -- % досмотров
    
    -- Конверсии (если отслеживается)
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5, 4), -- Click-Through Rate
    
    -- Когда записано
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_metrics_publication ON metrics(publication_id);
CREATE INDEX idx_metrics_recorded ON metrics(recorded_at);

-- Партиционирование по месяцам (для больших объёмов)
-- CREATE TABLE metrics_2024_01 PARTITION OF metrics
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- =============================================
-- ТАБЛИЦА: leads (лиды/потенциальные клиенты)
-- =============================================
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Источник
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    content_id UUID REFERENCES content(id) ON DELETE SET NULL,
    publication_id UUID REFERENCES publications(id) ON DELETE SET NULL,
    source_platform VARCHAR(30),
    
    -- Контактные данные
    telegram_user_id BIGINT,
    telegram_username VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(200),
    
    -- Воронка
    funnel_stage VARCHAR(30) DEFAULT 'new' CHECK (funnel_stage IN (
        'new', 'engaged', 'interested', 
        'considering', 'ready_to_buy', 'converted', 'lost'
    )),
    
    -- Взаимодействия
    interactions JSONB DEFAULT '[]'::jsonb, -- История сообщений
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    messages_sent INTEGER DEFAULT 0,
    messages_received INTEGER DEFAULT 0,
    
    -- Скоринг
    lead_score INTEGER DEFAULT 0,
    
    -- Метаданные
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    landing_url TEXT,
    ip_address INET,
    user_agent TEXT,
    country VARCHAR(2),
    
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'blocked', 'converted')),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_leads_telegram ON leads(telegram_user_id);
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_stage ON leads(funnel_stage);
CREATE INDEX idx_leads_source ON leads(source_platform);
CREATE INDEX idx_leads_created ON leads(created_at);

-- =============================================
-- ТАБЛИЦА: conversions (продажи/конверсии)
-- =============================================
CREATE TABLE conversions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    affiliate_id UUID REFERENCES affiliates(id) ON DELETE SET NULL,
    
    -- Финансы
    order_amount DECIMAL(10, 2) NOT NULL,
    commission_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Идентификаторы
    external_order_id VARCHAR(255), -- ID в партнёрке
    stripe_payment_id VARCHAR(255), -- Если свой продукт
    
    -- Статус
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'approved', 'paid', 'refunded', 'chargedback'
    )),
    
    -- Атрибуция
    attribution_model VARCHAR(30) DEFAULT 'last_click',
    click_id VARCHAR(255),
    
    converted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_conversions_lead ON conversions(lead_id);
CREATE INDEX idx_conversions_affiliate ON conversions(affiliate_id);
CREATE INDEX idx_conversions_status ON conversions(status);
CREATE INDEX idx_conversions_date ON conversions(converted_at);

-- =============================================
-- ТАБЛИЦА: expenses (расходы на API и сервисы)
-- =============================================
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'ai_api', 'hosting', 'proxy', 'video_generation',
        'voice_generation', 'storage', 'other'
    )),
    service_name VARCHAR(100) NOT NULL, -- Claude, OpenAI, ElevenLabs, etc
    
    amount DECIMAL(10, 4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    description TEXT,
    
    -- Связь с контентом (если есть)
    content_id UUID REFERENCES content(id) ON DELETE SET NULL,
    
    period_start DATE,
    period_end DATE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_service ON expenses(service_name);
CREATE INDEX idx_expenses_date ON expenses(created_at);

-- =============================================
-- ТАБЛИЦА: scheduled_tasks (запланированные задачи)
-- =============================================
CREATE TABLE scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN (
        'publish_content', 'generate_content', 'fetch_metrics',
        'warm_up_account', 'send_funnel_message', 'check_health'
    )),
    
    -- Связанные сущности
    content_id UUID REFERENCES content(id) ON DELETE CASCADE,
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    
    -- Параметры
    payload JSONB DEFAULT '{}'::jsonb,
    
    -- Расписание
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    
    -- Статус
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    )),
    
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_error TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_tasks_scheduled ON scheduled_tasks(scheduled_at) WHERE status = 'pending';
CREATE INDEX idx_tasks_status ON scheduled_tasks(status);
CREATE INDEX idx_tasks_type ON scheduled_tasks(task_type);

-- =============================================
-- ТАБЛИЦА: audit_log (лог действий)
-- =============================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    
    old_values JSONB,
    new_values JSONB,
    
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_date ON audit_log(created_at);

-- =============================================
-- ФУНКЦИИ И ТРИГГЕРЫ
-- =============================================

-- Автообновление updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Применяем триггер ко всем таблицам с updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_niches_updated_at BEFORE UPDATE ON niches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Сброс счётчика постов каждый день
CREATE OR REPLACE FUNCTION reset_daily_post_counts()
RETURNS void AS $$
BEGIN
    UPDATE accounts SET posts_today = 0;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- VIEWS (представления для удобства)
-- =============================================

-- Общая статистика по аккаунтам
CREATE VIEW v_account_stats AS
SELECT 
    a.id,
    a.platform,
    a.username,
    a.followers,
    a.status,
    a.health_score,
    n.name as niche_name,
    COUNT(DISTINCT p.id) as total_publications,
    COALESCE(SUM(m.views), 0) as total_views,
    COALESCE(SUM(m.likes), 0) as total_likes,
    COALESCE(AVG(m.engagement_rate), 0) as avg_engagement
FROM accounts a
LEFT JOIN niches n ON a.niche_id = n.id
LEFT JOIN publications p ON p.account_id = a.id AND p.status = 'published'
LEFT JOIN metrics m ON m.publication_id = p.id
GROUP BY a.id, a.platform, a.username, a.followers, a.status, a.health_score, n.name;

-- Воронка продаж
CREATE VIEW v_funnel_stats AS
SELECT
    date_trunc('day', l.created_at) as date,
    COUNT(*) as total_leads,
    COUNT(*) FILTER (WHERE funnel_stage IN ('interested', 'considering', 'ready_to_buy', 'converted')) as engaged,
    COUNT(*) FILTER (WHERE funnel_stage = 'converted') as converted,
    SUM(c.commission_amount) as revenue
FROM leads l
LEFT JOIN conversions c ON c.lead_id = l.id AND c.status IN ('approved', 'paid')
GROUP BY date_trunc('day', l.created_at)
ORDER BY date DESC;

-- Топ контента
CREATE VIEW v_top_content AS
SELECT 
    c.id,
    c.title,
    c.type,
    c.target_platform,
    n.name as niche,
    COUNT(p.id) as times_published,
    COALESCE(SUM(m.views), 0) as total_views,
    COALESCE(SUM(m.clicks), 0) as total_clicks,
    COALESCE(AVG(m.engagement_rate), 0) as avg_engagement,
    CASE WHEN SUM(m.views) > 0 
         THEN (SUM(m.clicks)::float / SUM(m.views) * 100)
         ELSE 0 END as ctr
FROM content c
LEFT JOIN niches n ON c.niche_id = n.id
LEFT JOIN publications p ON p.content_id = c.id
LEFT JOIN metrics m ON m.publication_id = p.id
WHERE c.status = 'published'
GROUP BY c.id, c.title, c.type, c.target_platform, n.name
ORDER BY total_views DESC;
```

---

## 📁 Структура проекта

```
content-automation-system/
│
├── 📂 backend/                    # FastAPI приложение
│   ├── 📂 app/
│   │   ├── __init__.py
│   │   ├── main.py               # Точка входа FastAPI
│   │   ├── config.py             # Конфигурация
│   │   │
│   │   ├── 📂 api/               # API эндпоинты
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Зависимости (auth, db)
│   │   │   ├── v1/
│   │   │   │   ├── accounts.py
│   │   │   │   ├── content.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── niches.py
│   │   │   │   ├── affiliates.py
│   │   │   │   ├── publications.py
│   │   │   │   ├── leads.py
│   │   │   │   ├── voice.py      # Jarvis API
│   │   │   │   └── webhooks.py   # Stripe, партнёрки
│   │   │
│   │   ├── 📂 core/              # Бизнес-логика
│   │   │   ├── __init__.py
│   │   │   ├── security.py       # JWT, пароли
│   │   │   ├── ai_agents.py      # Промпты ролей
│   │   │   └── scheduler.py      # Планировщик задач
│   │   │
│   │   ├── 📂 services/          # Сервисы
│   │   │   ├── __init__.py
│   │   │   ├── ai/
│   │   │   │   ├── claude_service.py
│   │   │   │   ├── openai_service.py
│   │   │   │   ├── content_generator.py
│   │   │   │   └── niche_analyzer.py
│   │   │   ├── media/
│   │   │   │   ├── video_generator.py
│   │   │   │   ├── voice_generator.py
│   │   │   │   └── image_generator.py
│   │   │   ├── social/
│   │   │   │   ├── tiktok_publisher.py
│   │   │   │   ├── youtube_publisher.py
│   │   │   │   ├── twitter_publisher.py
│   │   │   │   ├── linkedin_publisher.py
│   │   │   │   └── telegram_bot.py
│   │   │   ├── analytics/
│   │   │   │   ├── metrics_collector.py
│   │   │   │   └── report_generator.py
│   │   │   └── payments/
│   │   │       ├── stripe_service.py
│   │   │       └── affiliate_tracker.py
│   │   │
│   │   ├── 📂 models/            # SQLAlchemy модели
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── niche.py
│   │   │   ├── account.py
│   │   │   ├── content.py
│   │   │   ├── publication.py
│   │   │   ├── lead.py
│   │   │   └── conversion.py
│   │   │
│   │   ├── 📂 schemas/           # Pydantic схемы
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── niche.py
│   │   │   ├── account.py
│   │   │   ├── content.py
│   │   │   └── analytics.py
│   │   │
│   │   └── 📂 db/                # База данных
│   │       ├── __init__.py
│   │       ├── session.py        # Сессии SQLAlchemy
│   │       └── migrations/       # Alembic миграции
│   │
│   ├── 📂 workers/               # Celery воркеры
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── tasks/
│   │   │   ├── content_tasks.py
│   │   │   ├── publish_tasks.py
│   │   │   ├── metrics_tasks.py
│   │   │   └── funnel_tasks.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── 📂 frontend/                  # React приложение
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── Dashboard/
│   │   │   ├── Accounts/
│   │   │   ├── Content/
│   │   │   ├── Analytics/
│   │   │   ├── Funnel/
│   │   │   └── Voice/           # Jarvis интерфейс
│   │   ├── 📂 pages/
│   │   ├── 📂 hooks/
│   │   ├── 📂 services/
│   │   ├── 📂 store/            # Redux/Zustand
│   │   └── App.tsx
│   │
│   ├── package.json
│   └── Dockerfile
│
├── 📂 telegram-bot/             # Telegram бот (отдельно)
│   ├── bot.py
│   ├── handlers/
│   └── Dockerfile
│
├── 📂 docs/                     # Документация
│   ├── API.md
│   ├── SETUP.md
│   └── DEPLOYMENT.md
│
├── 📂 scripts/                  # Утилиты
│   ├── seed_data.py
│   └── backup.sh
│
├── .env.example
├── docker-compose.yml           # Всё вместе
└── README.md
```

---

## 🔄 Потоки данных

### 1. Генерация и публикация контента

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ПОТОК: ГЕНЕРАЦИЯ КОНТЕНТА                            │
└─────────────────────────────────────────────────────────────────────────┘

1. ТРИГГЕР                    2. ГЕНЕРАЦИЯ                 3. МЕДИА
   │                             │                            │
   │ • По расписанию             │ • Claude генерирует        │ • ElevenLabs: голос
   │ • Ручной запуск             │   сценарий по роли         │ • HeyGen: видео
   │ • API запрос                │   "copywriter"             │ • Stability: картинки
   │                             │                            │
   ▼                             ▼                            ▼
┌─────────┐               ┌─────────────┐              ┌─────────────┐
│ Celery  │──────────────▶│   Claude    │─────────────▶│  Media API  │
│  Task   │               │    API      │              │  (parallel) │
└─────────┘               └─────────────┘              └─────────────┘
                                                              │
                                                              ▼
4. СОХРАНЕНИЕ                5. ПЛАНИРОВАНИЕ           6. ПУБЛИКАЦИЯ
   │                             │                         │
   │ • content → DB              │ • Выбор времени         │ • Platform API
   │ • media → S3/R2             │ • Выбор аккаунта        │ • Проверка лимитов
   │                             │ • scheduled_tasks       │ • Retry при ошибках
   │                             │                         │
   ▼                             ▼                         ▼
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│ PostgreSQL  │◀──────────│  Scheduler  │──────────▶│  Publisher  │
│ + Storage   │           │             │           │   Service   │
└─────────────┘           └─────────────┘           └─────────────┘
```

### 2. Воронка лидов

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ПОТОК: ВОРОНКА ПРОДАЖ                                │
└─────────────────────────────────────────────────────────────────────────┘

    СОЦСЕТИ                    ТЕЛЕГРАМ                    КОНВЕРСИЯ
       │                          │                           │
       │ Пользователь             │ Подписка на бота          │ Покупка через
       │ видит контент            │ или канал                 │ Stripe/партнёрку
       │                          │                           │
       ▼                          ▼                           ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│   Клик на   │───────────▶│  Telegram   │───────────▶│   Stripe    │
│   ссылку    │  redirect  │    Bot      │   ссылка   │  Checkout   │
└─────────────┘            └─────────────┘            └─────────────┘
       │                          │                           │
       │ UTM метки                │ Сохранение lead           │ Webhook
       │                          │ Отправка в воронку        │ payment.success
       │                          │                           │
       ▼                          ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           PostgreSQL                                    │
│  ┌─────────┐         ┌─────────┐         ┌─────────────┐               │
│  │  leads  │◀────────│ funnel  │────────▶│ conversions │               │
│  │         │         │ messages│         │             │               │
│  └─────────┘         └─────────┘         └─────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
       │
       │ Автоматические сообщения
       │ по воронке (Celery)
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ВОРОНКА СООБЩЕНИЙ (пример)                           │
├─────────────────────────────────────────────────────────────────────────┤
│ День 0: Приветствие + бесплатная ценность                              │
│ День 1: Полезный контент #1                                            │
│ День 2: История успеха / кейс                                          │
│ День 3: Полезный контент #2                                            │
│ День 4: Мягкое предложение                                             │
│ День 5: Дедлайн / скидка                                               │
│ День 7: Последний шанс                                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

*Артефакт 2 из N. Следующий: Backend API код (FastAPI).*
