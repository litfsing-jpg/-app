# =============================================
# BACKEND API — ЧАСТЬ 1: КОНФИГУРАЦИЯ И МОДЕЛИ
# =============================================

# ============================================
# ФАЙЛ: backend/app/config.py
# ============================================

"""
Конфигурация приложения.
Все переменные загружаются из .env файла.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # === Приложение ===
    APP_NAME: str = "Content Automation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # === База данных ===
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/content_automation"
    
    # === Redis ===
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # === JWT ===
    JWT_SECRET_KEY: str = "jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # === AI API ===
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    HEYGEN_API_KEY: str = ""
    STABILITY_API_KEY: str = ""
    
    # === Социальные сети ===
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_SECRET: str = ""
    
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    
    YOUTUBE_API_KEY: str = ""
    
    TELEGRAM_BOT_TOKEN: str = ""
    
    # === Платежи ===
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # === Хранилище файлов ===
    S3_ENDPOINT_URL: str = ""  # Для Cloudflare R2
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "content-media"
    
    # === Прочее ===
    CORS_ORIGINS: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Кешированное получение настроек"""
    return Settings()


settings = get_settings()


# ============================================
# ФАЙЛ: backend/app/db/session.py
# ============================================

"""
Настройка подключения к базе данных.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Создаём движок базы данных
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=10,  # Размер пула соединений
    max_overflow=20,  # Максимум дополнительных соединений
    echo=settings.DEBUG  # Логирование SQL запросов в debug режиме
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии БД.
    Использование:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# ФАЙЛ: backend/app/models/__init__.py
# ============================================

"""
Экспорт всех моделей.
"""

from app.models.user import User
from app.models.niche import Niche
from app.models.affiliate import Affiliate
from app.models.proxy import Proxy
from app.models.account import Account
from app.models.content import Content
from app.models.publication import Publication
from app.models.metrics import Metrics
from app.models.lead import Lead
from app.models.conversion import Conversion
from app.models.scheduled_task import ScheduledTask

__all__ = [
    "User",
    "Niche", 
    "Affiliate",
    "Proxy",
    "Account",
    "Content",
    "Publication",
    "Metrics",
    "Lead",
    "Conversion",
    "ScheduledTask"
]


# ============================================
# ФАЙЛ: backend/app/models/user.py
# ============================================

"""
Модель пользователя системы.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    
    settings = Column(JSONB, default={
        "notifications": True,
        "timezone": "UTC",
        "language": "ru"
    })
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================
# ФАЙЛ: backend/app/models/niche.py
# ============================================

"""
Модель ниши для контента.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class NicheStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class CompetitionLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrendDirection(str, enum.Enum):
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"


class Niche(Base):
    __tablename__ = "niches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    status = Column(SQLEnum(NicheStatus), default=NicheStatus.ACTIVE, index=True)
    
    # Аналитика ниши
    potential_score = Column(Integer)  # 1-10
    competition_level = Column(SQLEnum(CompetitionLevel))
    avg_product_price = Column(Numeric(10, 2))
    search_volume = Column(Integer)
    trend = Column(SQLEnum(TrendDirection))
    
    # Метаданные
    keywords = Column(JSONB, default=[])
    target_audience = Column(JSONB, default={})
    content_pillars = Column(JSONB, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    affiliates = relationship("Affiliate", back_populates="niche")
    accounts = relationship("Account", back_populates="niche")
    content = relationship("Content", back_populates="niche")


# ============================================
# ФАЙЛ: backend/app/models/affiliate.py
# ============================================

"""
Модель партнёрской программы.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class CommissionType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    RECURRING = "recurring"


class AffiliateStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    REJECTED = "rejected"


class Affiliate(Base):
    __tablename__ = "affiliates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    niche_id = Column(UUID(as_uuid=True), ForeignKey("niches.id", ondelete="SET NULL"))
    
    name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)  # ClickBank, Amazon, etc.
    url = Column(Text, nullable=False)
    affiliate_link = Column(Text)
    
    # Финансы
    commission_type = Column(SQLEnum(CommissionType), nullable=False)
    commission_rate = Column(Numeric(5, 2), nullable=False)
    avg_order_value = Column(Numeric(10, 2))
    epc = Column(Numeric(10, 4))  # Earnings Per Click
    cookie_duration_days = Column(Integer, default=30)
    
    # Качество
    gravity_score = Column(Numeric(5, 2))
    refund_rate = Column(Numeric(5, 2))
    landing_quality = Column(Integer)  # 1-10
    
    status = Column(SQLEnum(AffiliateStatus), default=AffiliateStatus.ACTIVE, index=True)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    niche = relationship("Niche", back_populates="affiliates")
    content = relationship("Content", back_populates="affiliate")
    conversions = relationship("Conversion", back_populates="affiliate")


# ============================================
# ФАЙЛ: backend/app/models/proxy.py
# ============================================

"""
Модель прокси для аккаунтов.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class ProxyType(str, enum.Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"
    RESIDENTIAL = "residential"


class ProxyStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    BANNED = "banned"
    EXPIRED = "expired"


class Proxy(Base):
    __tablename__ = "proxies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    type = Column(SQLEnum(ProxyType), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100))
    password = Column(String(255))
    
    country = Column(String(2))  # ISO код
    city = Column(String(100))
    
    status = Column(SQLEnum(ProxyStatus), default=ProxyStatus.AVAILABLE, index=True)
    
    # Метрики
    last_checked_at = Column(DateTime)
    response_time_ms = Column(Integer)
    success_rate = Column(Numeric(5, 2))
    
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    accounts = relationship("Account", back_populates="proxy")


# ============================================
# ФАЙЛ: backend/app/models/account.py
# ============================================

"""
Модель аккаунта социальной сети.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class Platform(str, enum.Enum):
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    FACEBOOK = "facebook"
    THREADS = "threads"


class AccountStatus(str, enum.Enum):
    WARMING_UP = "warming_up"
    ACTIVE = "active"
    PAUSED = "paused"
    SHADOWBANNED = "shadowbanned"
    SUSPENDED = "suspended"
    BANNED = "banned"
    NEEDS_VERIFICATION = "needs_verification"


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    niche_id = Column(UUID(as_uuid=True), ForeignKey("niches.id", ondelete="SET NULL"))
    proxy_id = Column(UUID(as_uuid=True), ForeignKey("proxies.id", ondelete="SET NULL"))
    
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    username = Column(String(100), nullable=False)
    display_name = Column(String(200))
    bio = Column(Text)
    profile_image_url = Column(Text)
    
    # Учётные данные (зашифрованные)
    credentials = Column(JSONB, nullable=False)  # {access_token, refresh_token, etc}
    
    # Метрики
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2))
    
    # Здоровье аккаунта
    health_score = Column(Integer, default=100)  # 0-100
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, index=True)
    
    # Лимиты и расписание
    daily_post_limit = Column(Integer, default=5)
    posts_today = Column(Integer, default=0)
    last_posted_at = Column(DateTime)
    warmup_started_at = Column(DateTime)
    
    # Настройки
    settings = Column(JSONB, default={
        "auto_post": True,
        "posting_hours": [9, 12, 15, 18, 21],
        "timezone": "UTC"
    })
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    niche = relationship("Niche", back_populates="accounts")
    proxy = relationship("Proxy", back_populates="accounts")
    publications = relationship("Publication", back_populates="account")
    leads = relationship("Lead", back_populates="account")
    
    # Уникальность
    __table_args__ = (
        # Один username на платформу
        {"sqlite_autoincrement": True},
    )


# ============================================
# ФАЙЛ: backend/app/models/content.py
# ============================================

"""
Модель контента/креатива.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class ContentType(str, enum.Enum):
    SHORT_VIDEO = "short_video"
    LONG_VIDEO = "long_video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    TEXT_POST = "text_post"
    THREAD = "thread"
    STORY = "story"
    ARTICLE = "article"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Content(Base):
    __tablename__ = "content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    niche_id = Column(UUID(as_uuid=True), ForeignKey("niches.id", ondelete="SET NULL"))
    affiliate_id = Column(UUID(as_uuid=True), ForeignKey("affiliates.id", ondelete="SET NULL"))
    
    # Тип контента
    type = Column(SQLEnum(ContentType), nullable=False, index=True)
    target_platform = Column(String(30), nullable=False, index=True)
    
    # Контент
    title = Column(String(500))
    hook = Column(Text)  # Первые слова/кадры
    script = Column(Text)  # Полный сценарий
    caption = Column(Text)  # Подпись к посту
    hashtags = Column(JSONB, default=[])
    
    # Медиа файлы
    media_url = Column(Text)  # Основной файл
    thumbnail_url = Column(Text)
    additional_media = Column(JSONB, default=[])  # Для каруселей
    
    # CTA и ссылки
    call_to_action = Column(Text)
    link_url = Column(Text)  # Партнёрская ссылка
    link_shortcode = Column(String(50))  # bit.ly код
    
    # Статус
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, index=True)
    
    # Планирование
    scheduled_for = Column(DateTime, index=True)
    
    # AI метаданные
    ai_model = Column(String(50))
    generation_prompt = Column(Text)
    generation_cost = Column(Numeric(10, 4))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    niche = relationship("Niche", back_populates="content")
    affiliate = relationship("Affiliate", back_populates="content")
    publications = relationship("Publication", back_populates="content")
    leads = relationship("Lead", back_populates="content")


# ============================================
# ФАЙЛ: backend/app/models/publication.py
# ============================================

"""
Модель публикации контента.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class PublicationStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"
    REMOVED_BY_PLATFORM = "removed_by_platform"


class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    
    # Идентификаторы платформы
    platform_post_id = Column(String(255))
    platform_url = Column(Text)
    
    # Статус
    status = Column(SQLEnum(PublicationStatus), default=PublicationStatus.PENDING, index=True)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Время
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    content = relationship("Content", back_populates="publications")
    account = relationship("Account", back_populates="publications")
    metrics = relationship("Metrics", back_populates="publication", uselist=False)


# ============================================
# ФАЙЛ: backend/app/models/metrics.py
# ============================================

"""
Модель метрик публикации.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class Metrics(Base):
    __tablename__ = "metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publication_id = Column(UUID(as_uuid=True), ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    
    # Основные метрики
    views = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    
    # Взаимодействия
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Вовлечённость
    engagement_rate = Column(Numeric(5, 2))
    avg_watch_time_seconds = Column(Integer)
    completion_rate = Column(Numeric(5, 2))
    
    # Конверсии
    clicks = Column(Integer, default=0)
    ctr = Column(Numeric(5, 4))
    
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Связи
    publication = relationship("Publication", back_populates="metrics")


# ============================================
# ФАЙЛ: backend/app/models/lead.py
# ============================================

"""
Модель лида (потенциального клиента).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class FunnelStage(str, enum.Enum):
    NEW = "new"
    ENGAGED = "engaged"
    INTERESTED = "interested"
    CONSIDERING = "considering"
    READY_TO_BUY = "ready_to_buy"
    CONVERTED = "converted"
    LOST = "lost"


class LeadStatus(str, enum.Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BLOCKED = "blocked"
    CONVERTED = "converted"


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Источник
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"))
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id", ondelete="SET NULL"))
    publication_id = Column(UUID(as_uuid=True), ForeignKey("publications.id", ondelete="SET NULL"))
    source_platform = Column(String(30))
    
    # Контактные данные
    telegram_user_id = Column(BigInteger, index=True)
    telegram_username = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(50))
    name = Column(String(200))
    
    # Воронка
    funnel_stage = Column(SQLEnum(FunnelStage), default=FunnelStage.NEW, index=True)
    
    # Взаимодействия
    interactions = Column(JSONB, default=[])
    last_interaction_at = Column(DateTime)
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    
    # Скоринг
    lead_score = Column(Integer, default=0)
    
    # UTM метки
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    landing_url = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    country = Column(String(2))
    
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.ACTIVE)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    account = relationship("Account", back_populates="leads")
    content = relationship("Content", back_populates="leads")
    conversions = relationship("Conversion", back_populates="lead")


# ============================================
# ФАЙЛ: backend/app/models/conversion.py
# ============================================

"""
Модель конверсии (продажи).
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class ConversionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REFUNDED = "refunded"
    CHARGEDBACK = "chargedback"


class Conversion(Base):
    __tablename__ = "conversions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    affiliate_id = Column(UUID(as_uuid=True), ForeignKey("affiliates.id", ondelete="SET NULL"))
    
    # Финансы
    order_amount = Column(Numeric(10, 2), nullable=False)
    commission_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Идентификаторы
    external_order_id = Column(String(255))  # ID в партнёрке
    stripe_payment_id = Column(String(255))  # Если свой продукт
    
    # Статус
    status = Column(SQLEnum(ConversionStatus), default=ConversionStatus.PENDING, index=True)
    
    # Атрибуция
    attribution_model = Column(String(30), default="last_click")
    click_id = Column(String(255))
    
    converted_at = Column(DateTime, default=datetime.utcnow, index=True)
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    lead = relationship("Lead", back_populates="conversions")
    affiliate = relationship("Affiliate", back_populates="conversions")


# ============================================
# ФАЙЛ: backend/app/models/scheduled_task.py
# ============================================

"""
Модель запланированной задачи.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.session import Base
import enum


class TaskType(str, enum.Enum):
    PUBLISH_CONTENT = "publish_content"
    GENERATE_CONTENT = "generate_content"
    FETCH_METRICS = "fetch_metrics"
    WARM_UP_ACCOUNT = "warm_up_account"
    SEND_FUNNEL_MESSAGE = "send_funnel_message"
    CHECK_HEALTH = "check_health"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    task_type = Column(SQLEnum(TaskType), nullable=False, index=True)
    
    # Связанные сущности
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id", ondelete="CASCADE"))
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    
    # Параметры
    payload = Column(JSONB, default={})
    
    # Расписание
    scheduled_at = Column(DateTime, nullable=False, index=True)
    priority = Column(Integer, default=5)  # 1-10
    
    # Статус
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    last_error = Column(Text)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================
# ФАЙЛ: backend/app/schemas/__init__.py
# ============================================

"""
Экспорт всех Pydantic схем.
"""

from app.schemas.user import *
from app.schemas.niche import *
from app.schemas.account import *
from app.schemas.content import *
from app.schemas.analytics import *


# ============================================
# ФАЙЛ: backend/app/schemas/user.py
# ============================================

"""
Pydantic схемы для пользователей.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    settings: Optional[dict] = None


class UserResponse(UserBase):
    id: UUID
    role: str
    settings: dict
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


# ============================================
# ФАЙЛ: backend/app/schemas/niche.py
# ============================================

"""
Pydantic схемы для ниш.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class NicheBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class NicheCreate(NicheBase):
    potential_score: Optional[int] = None
    competition_level: Optional[str] = None
    avg_product_price: Optional[Decimal] = None
    keywords: Optional[List[str]] = []
    content_pillars: Optional[List[str]] = []


class NicheUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    potential_score: Optional[int] = None
    competition_level: Optional[str] = None
    keywords: Optional[List[str]] = None


class NicheResponse(NicheBase):
    id: UUID
    status: str
    potential_score: Optional[int]
    competition_level: Optional[str]
    avg_product_price: Optional[Decimal]
    search_volume: Optional[int]
    trend: Optional[str]
    keywords: List
    content_pillars: List
    created_at: datetime
    
    class Config:
        from_attributes = True


class NicheAnalysis(BaseModel):
    """Результат анализа ниши от AI"""
    name: str
    potential_score: int
    competition_level: str
    trend: str
    monthly_search_volume: int
    avg_product_price: Decimal
    recommended_affiliates: List[str]
    content_pillars: List[str]
    target_audience: dict
    recommendation: str


# ============================================
# ФАЙЛ: backend/app/schemas/account.py
# ============================================

"""
Pydantic схемы для аккаунтов.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class AccountBase(BaseModel):
    platform: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None


class AccountCreate(AccountBase):
    niche_id: Optional[UUID] = None
    proxy_id: Optional[UUID] = None
    credentials: dict


class AccountUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    status: Optional[str] = None
    niche_id: Optional[UUID] = None
    proxy_id: Optional[UUID] = None
    daily_post_limit: Optional[int] = None
    settings: Optional[dict] = None


class AccountResponse(AccountBase):
    id: UUID
    niche_id: Optional[UUID]
    followers: int
    following: int
    total_posts: int
    engagement_rate: Optional[Decimal]
    health_score: int
    status: str
    daily_post_limit: int
    posts_today: int
    last_posted_at: Optional[datetime]
    settings: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class AccountStats(BaseModel):
    """Статистика аккаунта"""
    id: UUID
    platform: str
    username: str
    followers: int
    total_views: int
    total_likes: int
    avg_engagement: Decimal
    publications_count: int
    health_score: int
    status: str


# ============================================
# ФАЙЛ: backend/app/schemas/content.py
# ============================================

"""
Pydantic схемы для контента.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class ContentBase(BaseModel):
    type: str
    target_platform: str
    title: Optional[str] = None


class ContentCreate(ContentBase):
    niche_id: Optional[UUID] = None
    affiliate_id: Optional[UUID] = None
    hook: Optional[str] = None
    script: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = []
    call_to_action: Optional[str] = None
    link_url: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class ContentGenerate(BaseModel):
    """Запрос на генерацию контента через AI"""
    niche_id: UUID
    type: str
    target_platform: str
    topic: Optional[str] = None
    affiliate_id: Optional[UUID] = None
    tone: Optional[str] = "engaging"  # engaging, professional, casual
    include_cta: bool = True


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    hook: Optional[str] = None
    script: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class ContentResponse(ContentBase):
    id: UUID
    niche_id: Optional[UUID]
    affiliate_id: Optional[UUID]
    hook: Optional[str]
    script: Optional[str]
    caption: Optional[str]
    hashtags: List
    media_url: Optional[str]
    thumbnail_url: Optional[str]
    call_to_action: Optional[str]
    link_url: Optional[str]
    link_shortcode: Optional[str]
    status: str
    scheduled_for: Optional[datetime]
    ai_model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentBatchGenerate(BaseModel):
    """Запрос на пакетную генерацию"""
    niche_id: UUID
    types: List[str]  # ["short_video", "thread", "text_post"]
    platforms: List[str]  # ["tiktok", "twitter", "linkedin"]
    count_per_type: int = 1
    affiliate_id: Optional[UUID] = None


# ============================================
# ФАЙЛ: backend/app/schemas/analytics.py
# ============================================

"""
Pydantic схемы для аналитики.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class MetricsResponse(BaseModel):
    """Метрики одной публикации"""
    publication_id: UUID
    views: int
    impressions: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: Optional[Decimal]
    clicks: int
    ctr: Optional[Decimal]
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class DailyStats(BaseModel):
    """Дневная статистика"""
    date: date
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_clicks: int
    new_followers: int
    new_leads: int
    conversions: int
    revenue: Decimal


class PlatformStats(BaseModel):
    """Статистика по платформе"""
    platform: str
    accounts_count: int
    total_followers: int
    total_views: int
    total_engagement: int
    avg_engagement_rate: Decimal
    publications_count: int


class FunnelStats(BaseModel):
    """Статистика воронки"""
    total_leads: int
    new_leads: int
    engaged_leads: int
    interested_leads: int
    ready_to_buy: int
    converted: int
    lost: int
    conversion_rate: Decimal


class RevenueStats(BaseModel):
    """Статистика доходов"""
    period: str  # "day", "week", "month"
    total_revenue: Decimal
    total_commission: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    roi: Decimal
    conversions_count: int
    avg_order_value: Decimal


class DashboardSummary(BaseModel):
    """Сводка для дашборда"""
    # Общие метрики
    total_accounts: int
    active_accounts: int
    total_followers: int
    followers_growth: int  # За период
    
    # Контент
    total_content: int
    scheduled_content: int
    published_today: int
    
    # Воронка
    total_leads: int
    new_leads_today: int
    conversion_rate: Decimal
    
    # Финансы
    revenue_today: Decimal
    revenue_month: Decimal
    expenses_month: Decimal
    profit_month: Decimal
    
    # Здоровье системы
    accounts_needing_attention: int
    failed_publications: int
    
    # Топ контент
    top_content: List[dict]
    
    # По платформам
    platforms_stats: List[PlatformStats]


class ReportRequest(BaseModel):
    """Запрос на генерацию отчёта"""
    report_type: str  # "daily", "weekly", "monthly", "custom"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    platforms: Optional[List[str]] = None
    include_sections: Optional[List[str]] = None  # ["revenue", "engagement", "funnel"]


# ============================================
# ФАЙЛ: backend/requirements.txt
# ============================================

"""
# FastAPI и сервер
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# База данных
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Redis и очереди
redis==5.0.1
celery==5.3.6

# Валидация и настройки
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Аутентификация
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# AI сервисы
anthropic==0.18.1
openai==1.12.0

# HTTP клиент
httpx==0.26.0
aiohttp==3.9.3

# Работа с файлами
boto3==1.34.34  # S3/R2
Pillow==10.2.0
python-magic==0.4.27

# Утилиты
python-dateutil==2.8.2
pytz==2024.1

# Логирование
loguru==0.7.2

# Тестирование
pytest==8.0.0
pytest-asyncio==0.23.4
httpx==0.26.0
"""
