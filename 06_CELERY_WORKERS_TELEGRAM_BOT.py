# =============================================
# CELERY WORKERS И TELEGRAM BOT
# =============================================

# ============================================
# ФАЙЛ: backend/workers/celery_app.py
# ============================================

"""
Конфигурация Celery для фоновых задач.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Создаём приложение Celery
celery_app = Celery(
    "content_automation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "workers.tasks.content_tasks",
        "workers.tasks.publish_tasks",
        "workers.tasks.metrics_tasks",
        "workers.tasks.funnel_tasks"
    ]
)

# Конфигурация
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут максимум на задачу
    worker_prefetch_multiplier=1,
    worker_concurrency=4
)

# Расписание периодических задач
celery_app.conf.beat_schedule = {
    # Публикация запланированного контента каждую минуту
    "publish-scheduled-content": {
        "task": "workers.tasks.publish_tasks.publish_scheduled",
        "schedule": 60.0,  # каждую минуту
    },
    
    # Сбор метрик каждые 30 минут
    "collect-metrics": {
        "task": "workers.tasks.metrics_tasks.collect_all_metrics",
        "schedule": 30 * 60,  # каждые 30 минут
    },
    
    # Проверка здоровья аккаунтов каждый час
    "check-accounts-health": {
        "task": "workers.tasks.publish_tasks.check_accounts_health",
        "schedule": 60 * 60,  # каждый час
    },
    
    # Отправка сообщений воронки каждые 15 минут
    "send-funnel-messages": {
        "task": "workers.tasks.funnel_tasks.process_funnel_queue",
        "schedule": 15 * 60,  # каждые 15 минут
    },
    
    # Сброс дневных лимитов в полночь
    "reset-daily-limits": {
        "task": "workers.tasks.publish_tasks.reset_daily_limits",
        "schedule": crontab(hour=0, minute=0),  # в 00:00
    },
    
    # Еженедельный отчёт по понедельникам
    "weekly-report": {
        "task": "workers.tasks.metrics_tasks.generate_weekly_report",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),  # Пн 09:00
    }
}


# ============================================
# ФАЙЛ: backend/workers/tasks/content_tasks.py
# ============================================

"""
Задачи для генерации контента.
"""

from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.content import Content, ContentStatus
from app.services.ai.content_generator import ContentGeneratorService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_content_task(self, content_id: str, params: dict):
    """Генерация контента через AI"""
    
    db = SessionLocal()
    
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            logger.error(f"Content {content_id} not found")
            return
        
        generator = ContentGeneratorService()
        
        # Синхронно вызываем async функцию
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(generator.generate(
            niche_id=str(content.niche_id),
            content_type=params.get("type", content.type.value),
            platform=params.get("platform", content.target_platform),
            topic=params.get("topic"),
            tone=params.get("tone", "engaging"),
            include_cta=params.get("include_cta", True)
        ))
        
        loop.close()
        
        # Обновляем контент
        content.title = result.get("title")
        content.hook = result.get("hook")
        content.script = result.get("script")
        content.caption = result.get("caption")
        content.hashtags = result.get("hashtags", [])
        content.call_to_action = result.get("cta")
        content.ai_model = result.get("model")
        content.status = ContentStatus.READY
        
        db.commit()
        
        logger.info(f"Content {content_id} generated successfully")
        return {"status": "success", "content_id": content_id}
        
    except Exception as e:
        logger.error(f"Error generating content {content_id}: {e}")
        
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.status = ContentStatus.FAILED
            db.commit()
        
        # Повторная попытка
        raise self.retry(exc=e, countdown=60)
        
    finally:
        db.close()


@shared_task
def generate_batch_content(niche_id: str, count: int, platforms: list):
    """Пакетная генерация контента"""
    
    db = SessionLocal()
    
    try:
        from app.models.niche import Niche
        
        niche = db.query(Niche).filter(Niche.id == niche_id).first()
        if not niche:
            logger.error(f"Niche {niche_id} not found")
            return
        
        created_ids = []
        
        for platform in platforms:
            for i in range(count):
                # Создаём запись
                content = Content(
                    niche_id=niche_id,
                    type="short_video",
                    target_platform=platform,
                    status=ContentStatus.GENERATING
                )
                db.add(content)
                db.commit()
                db.refresh(content)
                
                # Запускаем генерацию
                generate_content_task.delay(
                    str(content.id),
                    {"type": "short_video", "platform": platform}
                )
                
                created_ids.append(str(content.id))
        
        logger.info(f"Batch generation started: {len(created_ids)} items")
        return {"created": created_ids}
        
    finally:
        db.close()


# ============================================
# ФАЙЛ: backend/workers/tasks/publish_tasks.py
# ============================================

"""
Задачи для публикации контента.
"""

from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.content import Content, ContentStatus
from app.models.publication import Publication, PublicationStatus
from app.models.account import Account, AccountStatus
from app.services.social.publisher import PublisherService
import logging

logger = logging.getLogger(__name__)


@shared_task
def publish_scheduled():
    """Публикация запланированного контента"""
    
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        # Находим публикации готовые к отправке
        publications = db.query(Publication).filter(
            Publication.status == PublicationStatus.PENDING,
            Publication.scheduled_at <= now
        ).all()
        
        for pub in publications:
            # Проверяем лимиты аккаунта
            account = db.query(Account).filter(Account.id == pub.account_id).first()
            
            if not account or account.status != AccountStatus.ACTIVE:
                pub.status = PublicationStatus.FAILED
                pub.error_message = "Account not active"
                continue
            
            if account.posts_today >= account.daily_post_limit:
                logger.warning(f"Account {account.username} reached daily limit")
                continue
            
            # Запускаем публикацию
            publish_single.delay(str(pub.id))
        
        db.commit()
        
        logger.info(f"Scheduled {len(publications)} publications for processing")
        
    finally:
        db.close()


@shared_task(bind=True, max_retries=3)
def publish_single(self, publication_id: str):
    """Публикация одного поста"""
    
    db = SessionLocal()
    
    try:
        pub = db.query(Publication).filter(Publication.id == publication_id).first()
        if not pub:
            return
        
        pub.status = PublicationStatus.PUBLISHING
        db.commit()
        
        content = db.query(Content).filter(Content.id == pub.content_id).first()
        account = db.query(Account).filter(Account.id == pub.account_id).first()
        
        if not content or not account:
            pub.status = PublicationStatus.FAILED
            pub.error_message = "Content or Account not found"
            db.commit()
            return
        
        # Публикуем
        publisher = PublisherService()
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(publisher.publish(
            platform=account.platform.value,
            credentials=account.credentials,
            content={
                "type": content.type.value,
                "caption": content.caption,
                "media_url": content.media_url,
                "link_url": content.link_url,
                "tweets": content.script.split("---") if content.type.value == "thread" else None
            }
        ))
        
        loop.close()
        
        # Обновляем статусы
        pub.platform_post_id = result.get("post_id")
        pub.platform_url = result.get("url")
        pub.status = PublicationStatus.PUBLISHED
        pub.published_at = datetime.utcnow()
        
        account.posts_today += 1
        account.last_posted_at = datetime.utcnow()
        account.total_posts += 1
        
        content.status = ContentStatus.PUBLISHED
        
        db.commit()
        
        logger.info(f"Published {publication_id} to {account.platform.value}")
        return {"status": "published", "url": result.get("url")}
        
    except Exception as e:
        logger.error(f"Error publishing {publication_id}: {e}")
        
        pub = db.query(Publication).filter(Publication.id == publication_id).first()
        if pub:
            pub.status = PublicationStatus.FAILED
            pub.error_message = str(e)
            pub.retry_count += 1
            db.commit()
        
        raise self.retry(exc=e, countdown=300)  # Повтор через 5 мин
        
    finally:
        db.close()


@shared_task
def check_accounts_health():
    """Проверка здоровья всех аккаунтов"""
    
    db = SessionLocal()
    
    try:
        accounts = db.query(Account).filter(
            Account.status.in_([AccountStatus.ACTIVE, AccountStatus.SHADOWBANNED])
        ).all()
        
        for account in accounts:
            # Проверяем последние публикации
            recent_pubs = db.query(Publication).filter(
                Publication.account_id == account.id,
                Publication.published_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            failed_count = sum(1 for p in recent_pubs if p.status == PublicationStatus.FAILED)
            
            # Обновляем health_score
            if failed_count > 5:
                account.health_score = max(0, account.health_score - 20)
            elif failed_count > 2:
                account.health_score = max(0, account.health_score - 10)
            else:
                account.health_score = min(100, account.health_score + 5)
            
            # Меняем статус если нужно
            if account.health_score < 30:
                account.status = AccountStatus.NEEDS_VERIFICATION
        
        db.commit()
        
        logger.info(f"Health check completed for {len(accounts)} accounts")
        
    finally:
        db.close()


@shared_task
def reset_daily_limits():
    """Сброс дневных лимитов"""
    
    db = SessionLocal()
    
    try:
        db.query(Account).update({"posts_today": 0})
        db.commit()
        
        logger.info("Daily limits reset")
        
    finally:
        db.close()


# ============================================
# ФАЙЛ: backend/workers/tasks/metrics_tasks.py
# ============================================

"""
Задачи для сбора метрик.
"""

from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.publication import Publication, PublicationStatus
from app.models.account import Account
from app.models.metrics import Metrics
from app.services.social.publisher import PublisherService
import logging

logger = logging.getLogger(__name__)


@shared_task
def collect_all_metrics():
    """Сбор метрик со всех платформ"""
    
    db = SessionLocal()
    
    try:
        # Публикации за последние 7 дней
        publications = db.query(Publication).filter(
            Publication.status == PublicationStatus.PUBLISHED,
            Publication.published_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        for pub in publications:
            collect_publication_metrics.delay(str(pub.id))
        
        logger.info(f"Scheduled metrics collection for {len(publications)} publications")
        
    finally:
        db.close()


@shared_task
def collect_publication_metrics(publication_id: str):
    """Сбор метрик одной публикации"""
    
    db = SessionLocal()
    
    try:
        pub = db.query(Publication).filter(Publication.id == publication_id).first()
        if not pub or not pub.platform_post_id:
            return
        
        account = db.query(Account).filter(Account.id == pub.account_id).first()
        if not account:
            return
        
        publisher = PublisherService()
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        metrics_data = loop.run_until_complete(publisher.get_metrics(
            platform=account.platform.value,
            credentials=account.credentials,
            post_id=pub.platform_post_id
        ))
        
        loop.close()
        
        # Сохраняем или обновляем метрики
        metrics = db.query(Metrics).filter(Metrics.publication_id == publication_id).first()
        
        if not metrics:
            metrics = Metrics(publication_id=publication_id)
            db.add(metrics)
        
        metrics.views = metrics_data.get("views", 0)
        metrics.likes = metrics_data.get("likes", 0)
        metrics.comments = metrics_data.get("comments", 0)
        metrics.shares = metrics_data.get("shares", 0)
        metrics.recorded_at = datetime.utcnow()
        
        # Рассчитываем engagement rate
        if metrics.views > 0:
            total_engagement = metrics.likes + metrics.comments + metrics.shares
            metrics.engagement_rate = (total_engagement / metrics.views) * 100
        
        db.commit()
        
        logger.info(f"Collected metrics for publication {publication_id}")
        
    except Exception as e:
        logger.error(f"Error collecting metrics for {publication_id}: {e}")
        
    finally:
        db.close()


@shared_task
def generate_weekly_report():
    """Генерация еженедельного отчёта"""
    
    db = SessionLocal()
    
    try:
        from sqlalchemy import func
        from app.models.conversion import Conversion
        from app.models.lead import Lead
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Собираем статистику
        total_views = db.query(func.sum(Metrics.views)).filter(
            Metrics.recorded_at >= week_ago
        ).scalar() or 0
        
        total_leads = db.query(Lead).filter(
            Lead.created_at >= week_ago
        ).count()
        
        total_revenue = db.query(func.sum(Conversion.commission_amount)).filter(
            Conversion.converted_at >= week_ago,
            Conversion.status.in_(["approved", "paid"])
        ).scalar() or 0
        
        report = {
            "period": "weekly",
            "start_date": week_ago.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "total_views": total_views,
            "total_leads": total_leads,
            "total_revenue": float(total_revenue),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # TODO: Отправить отчёт (email, Telegram, etc)
        logger.info(f"Weekly report generated: {report}")
        
        return report
        
    finally:
        db.close()


# ============================================
# ФАЙЛ: backend/workers/tasks/funnel_tasks.py
# ============================================

"""
Задачи для воронки продаж.
"""

from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.lead import Lead, FunnelStage
from app.config import settings
import httpx
import logging

logger = logging.getLogger(__name__)

# Шаблоны сообщений воронки
FUNNEL_MESSAGES = {
    "day_0": {
        "stage": "new",
        "message": """
👋 Привет! Рад что ты здесь.

Я приготовил для тебя кое-что полезное — [бесплатный гайд/чеклист].

Забирай: [ссылка]

Если есть вопросы — пиши, отвечу лично! 💬
""",
        "next_stage": "engaged"
    },
    "day_1": {
        "stage": "engaged",
        "message": """
🎯 Знаешь какая главная ошибка [в нише]?

[Описание ошибки и как её избежать]

Подробнее рассказал тут: [ссылка на контент]

Уже применяешь? Напиши "+" если да 👇
""",
        "next_stage": "interested"
    },
    "day_3": {
        "stage": "interested",
        "message": """
💡 История одного из моих [учеников/клиентов]:

[Краткая история успеха]

Результат: [конкретные цифры]

Хочешь так же? Могу показать как 👀
""",
        "next_stage": "considering"
    },
    "day_5": {
        "stage": "considering",
        "message": """
🚀 Специально для тебя — особое предложение.

[Описание продукта/услуги]

Обычная цена: $XXX
Твоя цена: $YYY (скидка 30%)

Только до [дата]: [ссылка на оплату]

Есть вопросы? Отвечу на любые 💬
""",
        "next_stage": "ready_to_buy"
    },
    "day_7": {
        "stage": "ready_to_buy",
        "message": """
⏰ Напоминаю — предложение заканчивается сегодня!

Скидка 30% пропадёт в полночь.

Последний шанс: [ссылка]

Увидимся внутри? 🤝
""",
        "next_stage": "ready_to_buy"
    }
}


@shared_task
def process_funnel_queue():
    """Обработка очереди сообщений воронки"""
    
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        # Находим лидов для каждого этапа
        for day_key, template in FUNNEL_MESSAGES.items():
            day_num = int(day_key.split("_")[1])
            
            # Лиды которые подписались N дней назад
            target_date = now - timedelta(days=day_num)
            
            leads = db.query(Lead).filter(
                Lead.funnel_stage == template["stage"],
                Lead.status == "active",
                Lead.created_at >= target_date - timedelta(hours=12),
                Lead.created_at < target_date + timedelta(hours=12)
            ).all()
            
            for lead in leads:
                # Проверяем что не отправляли уже
                if lead.messages_sent > day_num:
                    continue
                
                send_funnel_message.delay(
                    str(lead.id),
                    template["message"],
                    template["next_stage"]
                )
        
    finally:
        db.close()


@shared_task
def send_funnel_message(lead_id: str, message: str, next_stage: str):
    """Отправка сообщения лиду"""
    
    db = SessionLocal()
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead or lead.status != "active":
            return
        
        if lead.telegram_user_id:
            # Отправляем в Telegram
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def send():
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": lead.telegram_user_id,
                            "text": message,
                            "parse_mode": "HTML"
                        }
                    )
            
            loop.run_until_complete(send())
            loop.close()
            
            # Обновляем лида
            lead.messages_sent += 1
            lead.last_interaction_at = datetime.utcnow()
            lead.funnel_stage = next_stage
            
            # Добавляем в историю
            if not lead.interactions:
                lead.interactions = []
            lead.interactions.append({
                "type": "funnel_message",
                "stage": next_stage,
                "sent_at": datetime.utcnow().isoformat()
            })
            
            db.commit()
            
            logger.info(f"Sent funnel message to lead {lead_id}")
        
    except Exception as e:
        logger.error(f"Error sending funnel message to {lead_id}: {e}")
        
    finally:
        db.close()


# ============================================
# ФАЙЛ: telegram-bot/bot.py
# ============================================

"""
Telegram бот для сбора лидов и воронки.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import httpx
import os

# Настройка
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


class LeadStates(StatesGroup):
    """Состояния для сбора данных"""
    waiting_email = State()
    waiting_name = State()


# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработка /start"""
    
    user = message.from_user
    
    # Регистрируем лида через API
    async with httpx.AsyncClient() as client:
        try:
            # Парсим UTM метки из deep link
            utm_data = {}
            if message.text and len(message.text.split()) > 1:
                params = message.text.split()[1]
                for param in params.split("_"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        utm_data[f"utm_{key}"] = value
            
            response = await client.post(
                f"{API_URL}/leads",
                json={
                    "telegram_user_id": user.id,
                    "telegram_username": user.username,
                    "name": user.full_name,
                    "source_platform": "telegram",
                    **utm_data
                }
            )
            
            if response.status_code == 200:
                logger.info(f"New lead registered: {user.id}")
        except Exception as e:
            logger.error(f"Error registering lead: {e}")
    
    # Приветственное сообщение
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Получить бесплатный гайд", callback_data="get_freebie")],
        [InlineKeyboardButton(text="📚 Смотреть контент", callback_data="show_content")],
        [InlineKeyboardButton(text="💬 Задать вопрос", callback_data="ask_question")]
    ])
    
    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Рад видеть тебя здесь! 🎉\n\n"
        f"Я помогу тебе [описание ценности].\n\n"
        f"Выбери что тебя интересует:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "get_freebie")
async def get_freebie(callback: types.CallbackQuery):
    """Отправка бесплатного материала"""
    
    await callback.answer()
    
    # Обновляем стадию воронки
    async with httpx.AsyncClient() as client:
        try:
            await client.patch(
                f"{API_URL}/leads/telegram/{callback.from_user.id}",
                json={"funnel_stage": "engaged"}
            )
        except:
            pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать гайд", url="https://example.com/freebie")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "🎁 Отлично! Вот твой бесплатный гайд:\n\n"
        "[Описание что внутри]\n\n"
        "После изучения — напиши как тебе!",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "show_content")
async def show_content(callback: types.CallbackQuery):
    """Показ контента"""
    
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 YouTube канал", url="https://youtube.com/@channel")],
        [InlineKeyboardButton(text="📱 TikTok", url="https://tiktok.com/@account")],
        [InlineKeyboardButton(text="🐦 Twitter", url="https://twitter.com/account")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        "📚 Мой контент:\n\n"
        "Выбери платформу где тебе удобнее смотреть:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "ask_question")
async def ask_question(callback: types.CallbackQuery):
    """Задать вопрос"""
    
    await callback.answer()
    
    await callback.message.edit_text(
        "💬 Напиши свой вопрос прямо сюда, и я отвечу как можно скорее!\n\n"
        "Обычно отвечаю в течение 24 часов."
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Получить бесплатный гайд", callback_data="get_freebie")],
        [InlineKeyboardButton(text="📚 Смотреть контент", callback_data="show_content")],
        [InlineKeyboardButton(text="💬 Задать вопрос", callback_data="ask_question")]
    ])
    
    await callback.message.edit_text(
        "Выбери что тебя интересует:",
        reply_markup=keyboard
    )


@router.message()
async def handle_message(message: types.Message):
    """Обработка всех сообщений"""
    
    user_id = message.from_user.id
    text = message.text
    
    # Сохраняем сообщение как взаимодействие
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{API_URL}/leads/telegram/{user_id}/interaction",
                json={
                    "type": "message",
                    "text": text
                }
            )
        except:
            pass
    
    # Простой автоответ
    if any(word in text.lower() for word in ["цена", "стоимость", "сколько"]):
        await message.answer(
            "💰 По поводу цен — напишу подробно!\n\n"
            "Скинь свой email, и я отправлю полную информацию 📧"
        )
    elif any(word in text.lower() for word in ["спасибо", "благодарю"]):
        await message.answer("😊 Рад помочь! Если будут ещё вопросы — пиши!")
    else:
        await message.answer(
            "Получил твоё сообщение! ✅\n\n"
            "Отвечу как можно скорее 💬"
        )


# ============================================
# WEBHOOK ЭНДПОИНТ (для продакшена)
# ============================================

async def on_startup(bot: Bot):
    """Установка webhook при старте"""
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")


async def on_shutdown(bot: Bot):
    """Удаление webhook при остановке"""
    await bot.delete_webhook()


# ============================================
# ЗАПУСК
# ============================================

async def main():
    """Запуск бота"""
    
    dp.include_router(router)
    
    # Polling для разработки
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# ============================================
# ФАЙЛ: telegram-bot/requirements.txt
# ============================================
"""
aiogram==3.3.0
httpx==0.26.0
python-dotenv==1.0.0
"""
