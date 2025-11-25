# =============================================
# BACKEND API — ЧАСТЬ 3: AI СЕРВИСЫ И ПУБЛИКАЦИЯ
# =============================================

# ============================================
# ФАЙЛ: backend/app/services/ai/claude_service.py
# ============================================

"""
Сервис для работы с Claude API.
"""

import anthropic
from typing import Optional, Dict, Any, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ClaudeService:
    """Сервис для генерации контента через Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Генерация текста через Claude"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def generate_with_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Генерация с ожиданием JSON ответа"""
        
        import json
        
        response = await self.generate(
            system_prompt=system_prompt + "\n\nОтвечай ТОЛЬКО валидным JSON без markdown.",
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=0.5  # Ниже для более предсказуемого JSON
        )
        
        # Очищаем от возможных markdown тегов
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return json.loads(cleaned.strip())


# ============================================
# ФАЙЛ: backend/app/services/ai/niche_analyzer.py
# ============================================

"""
Сервис анализа ниш через AI.
"""

from typing import Optional, List, Dict, Any
from app.services.ai.claude_service import ClaudeService
from app.core.ai_agents import NICHE_ANALYST_PROMPT
import logging

logger = logging.getLogger(__name__)


class NicheAnalyzerService:
    """Анализ и поиск прибыльных ниш"""
    
    def __init__(self):
        self.claude = ClaudeService()
    
    async def analyze_niche(self, niche_name: str) -> Dict[str, Any]:
        """Полный анализ ниши"""
        
        prompt = f"""
Проанализируй нишу "{niche_name}" для создания контента и affiliate marketing.

Верни результат в формате JSON:
{{
    "name": "название ниши",
    "potential_score": число от 1 до 10,
    "competition_level": "low" | "medium" | "high",
    "trend": "growing" | "stable" | "declining",
    "monthly_search_volume": примерное число,
    "avg_product_price": средняя цена продукта в USD,
    "recommended_affiliates": ["список рекомендуемых партнёрок"],
    "content_pillars": ["5 основных тем для контента"],
    "target_audience": {{
        "demographics": "описание",
        "pain_points": ["основные боли"],
        "desires": ["желания"]
    }},
    "best_platforms": ["лучшие платформы для этой ниши"],
    "content_types": ["лучшие типы контента"],
    "recommendation": "общая рекомендация - входить или нет"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=NICHE_ANALYST_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def suggest_niches(
        self,
        category: Optional[str] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Предложить прибыльные ниши"""
        
        category_filter = f" в категории '{category}'" if category else ""
        
        prompt = f"""
Предложи {count} прибыльных ниш{category_filter} для affiliate marketing и контент-маркетинга.

Критерии хорошей ниши:
- Вечнозелёная (постоянный интерес)
- Есть партнёрские программы с комиссией > 20%
- Средний чек продукта > $50
- Можно создавать контент без показа лица
- Низкая/средняя конкуренция

Верни JSON массив:
[
    {{
        "name": "название ниши",
        "slug": "url-friendly-name",
        "potential_score": число 1-10,
        "why_good": "почему это хорошая ниша",
        "estimated_monthly_income": "примерный доход при 10K подписчиков",
        "top_affiliate_program": "лучшая партнёрка для этой ниши"
    }}
]
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=NICHE_ANALYST_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def find_affiliates(self, niche_name: str) -> List[Dict[str, Any]]:
        """Найти партнёрские программы для ниши"""
        
        prompt = f"""
Найди лучшие партнёрские программы для ниши "{niche_name}".

Верни JSON массив с 5-10 программами:
[
    {{
        "name": "название программы/продукта",
        "platform": "ClickBank" | "Amazon" | "CJ" | "ShareASale" | "Direct",
        "url": "ссылка на партнёрку",
        "commission_type": "percentage" | "fixed" | "recurring",
        "commission_rate": число (процент или сумма),
        "avg_order_value": средний чек в USD,
        "cookie_days": дни хранения куки,
        "pros": ["преимущества"],
        "cons": ["недостатки"],
        "recommendation_score": число 1-10
    }}
]
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=NICHE_ANALYST_PROMPT,
            user_prompt=prompt
        )
        
        return result


# ============================================
# ФАЙЛ: backend/app/services/ai/content_generator.py
# ============================================

"""
Сервис генерации контента через AI.
"""

from typing import Optional, Dict, Any
from app.services.ai.claude_service import ClaudeService
from app.core.ai_agents import (
    CONTENT_STRATEGIST_PROMPT,
    COPYWRITER_PROMPT,
    VIDEO_PRODUCER_PROMPT
)
import logging

logger = logging.getLogger(__name__)


class ContentGeneratorService:
    """Генерация различных типов контента"""
    
    def __init__(self):
        self.claude = ClaudeService()
    
    async def generate(
        self,
        niche_id: str,
        content_type: str,
        platform: str,
        topic: Optional[str] = None,
        tone: str = "engaging",
        include_cta: bool = True,
        affiliate_link: Optional[str] = None
    ) -> Dict[str, Any]:
        """Главный метод генерации контента"""
        
        # Выбираем генератор по типу контента
        if content_type in ["short_video", "long_video"]:
            return await self._generate_video_content(
                niche_id, platform, topic, tone, include_cta, affiliate_link
            )
        elif content_type == "thread":
            return await self._generate_thread(
                niche_id, platform, topic, tone, include_cta, affiliate_link
            )
        elif content_type == "text_post":
            return await self._generate_post(
                niche_id, platform, topic, tone, include_cta, affiliate_link
            )
        else:
            return await self._generate_generic(
                niche_id, content_type, platform, topic, tone, include_cta
            )
    
    async def _generate_video_content(
        self,
        niche_id: str,
        platform: str,
        topic: Optional[str],
        tone: str,
        include_cta: bool,
        affiliate_link: Optional[str]
    ) -> Dict[str, Any]:
        """Генерация сценария для видео"""
        
        cta_instruction = """
Включи призыв к действию в конце:
- Подписаться на канал
- Перейти по ссылке в био/описании
""" if include_cta else ""
        
        prompt = f"""
Создай сценарий для короткого видео (30-60 секунд) для платформы {platform}.

Ниша: {niche_id}
Тема: {topic or "выбери актуальную тему для этой ниши"}
Тон: {tone}

{cta_instruction}

Верни JSON:
{{
    "title": "рабочее название видео",
    "hook": "первые 2 секунды - цепляющая фраза",
    "script": "полный сценарий с таймкодами",
    "caption": "подпись для публикации (до 300 символов)",
    "hashtags": ["релевантные", "хештеги", "5-10 штук"],
    "cta": "призыв к действию",
    "visual_notes": "заметки по визуалу",
    "estimated_duration": число секунд,
    "model": "claude-sonnet-4-20250514"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=COPYWRITER_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def _generate_thread(
        self,
        niche_id: str,
        platform: str,
        topic: Optional[str],
        tone: str,
        include_cta: bool,
        affiliate_link: Optional[str]
    ) -> Dict[str, Any]:
        """Генерация Twitter/X thread"""
        
        prompt = f"""
Создай Twitter thread (5-10 твитов) на тему в нише.

Ниша: {niche_id}
Тема: {topic or "выбери вирусную тему"}
Тон: {tone}

Правила:
- Первый твит - мощный hook
- Каждый твит до 280 символов
- Последний твит - CTA
- Добавь эмодзи где уместно

Верни JSON:
{{
    "title": "название thread",
    "hook": "первый твит (hook)",
    "script": "все твиты через разделитель ---",
    "tweets": ["твит 1", "твит 2", "..."],
    "caption": "описание thread",
    "hashtags": ["хештеги"],
    "cta": "финальный призыв",
    "model": "claude-sonnet-4-20250514"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=COPYWRITER_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def _generate_post(
        self,
        niche_id: str,
        platform: str,
        topic: Optional[str],
        tone: str,
        include_cta: bool,
        affiliate_link: Optional[str]
    ) -> Dict[str, Any]:
        """Генерация текстового поста"""
        
        platform_instructions = {
            "linkedin": "Профессиональный storytelling, 1300+ символов, личная история",
            "telegram": "Дружеский тон, можно длинный, эмодзи уместны",
            "twitter": "Один твит до 280 символов, дерзко и ёмко",
            "instagram": "До 2200 символов, визуальный storytelling"
        }
        
        instruction = platform_instructions.get(platform, "Стандартный пост")
        
        prompt = f"""
Создай пост для {platform}.

Ниша: {niche_id}
Тема: {topic or "выбери актуальную тему"}
Тон: {tone}
Особенности платформы: {instruction}

Верни JSON:
{{
    "title": "заголовок/тема поста",
    "hook": "первые строки",
    "script": "полный текст поста",
    "caption": "короткое описание",
    "hashtags": ["хештеги"],
    "cta": "призыв к действию",
    "model": "claude-sonnet-4-20250514"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=COPYWRITER_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def _generate_generic(
        self,
        niche_id: str,
        content_type: str,
        platform: str,
        topic: Optional[str],
        tone: str,
        include_cta: bool
    ) -> Dict[str, Any]:
        """Генерация любого типа контента"""
        
        prompt = f"""
Создай контент типа "{content_type}" для {platform}.

Ниша: {niche_id}
Тема: {topic or "выбери актуальную тему"}
Тон: {tone}
Включить CTA: {"да" if include_cta else "нет"}

Верни JSON:
{{
    "title": "название",
    "hook": "привлекающее начало",
    "script": "основной контент",
    "caption": "подпись",
    "hashtags": ["хештеги"],
    "cta": "призыв к действию",
    "model": "claude-sonnet-4-20250514"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=COPYWRITER_PROMPT,
            user_prompt=prompt
        )
        
        return result
    
    async def generate_content_plan(
        self,
        niche_id: str,
        platforms: list,
        days: int = 7
    ) -> Dict[str, Any]:
        """Генерация контент-плана на период"""
        
        prompt = f"""
Создай контент-план на {days} дней.

Ниша: {niche_id}
Платформы: {", ".join(platforms)}

Правила:
- Разнообразие типов контента
- Соотношение: 70% развлекательный/полезный, 20% образовательный, 10% продающий
- Учитывай лучшее время публикации для каждой платформы

Верни JSON:
{{
    "plan": [
        {{
            "day": 1,
            "date": "понедельник",
            "posts": [
                {{
                    "platform": "tiktok",
                    "type": "short_video",
                    "time": "19:00",
                    "topic": "тема",
                    "hook_idea": "идея для hook"
                }}
            ]
        }}
    ],
    "total_posts": число,
    "summary": "краткое описание стратегии"
}}
"""
        
        result = await self.claude.generate_with_json(
            system_prompt=CONTENT_STRATEGIST_PROMPT,
            user_prompt=prompt
        )
        
        return result


# ============================================
# ФАЙЛ: backend/app/services/ai/voice_assistant.py
# ============================================

"""
Голосовой ассистент Jarvis.
"""

import io
import base64
from typing import Optional, Dict, Any
import httpx
from app.services.ai.claude_service import ClaudeService
from app.core.ai_agents import JARVIS_PROMPT
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class VoiceAssistantService:
    """Jarvis - голосовой ассистент системы"""
    
    def __init__(self):
        self.claude = ClaudeService()
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Транскрибация аудио через Whisper API"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                files={"file": ("audio.webm", audio_data, "audio/webm")},
                data={"model": "whisper-1", "language": "ru"}
            )
            
            result = response.json()
            return result.get("text", "")
    
    async def generate_speech(self, text: str) -> bytes:
        """Генерация речи через ElevenLabs"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                headers={
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            )
            
            return response.content
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Обработка запроса к Jarvis"""
        
        # Формируем контекст с данными системы
        system_context = ""
        if context:
            system_context = f"""
Текущие данные системы:
- Всего аккаунтов: {context.get('total_accounts', 0)}
- Активных: {context.get('active_accounts', 0)}
- Подписчиков: {context.get('total_followers', 0)}
- Доход за месяц: ${context.get('revenue_month', 0)}
- Лидов: {context.get('total_leads', 0)}
- Публикаций сегодня: {context.get('published_today', 0)}
"""
        
        prompt = f"""
{system_context}

Вопрос пользователя: {query}

Отвечай кратко, информативно и дружелюбно. Если нужны конкретные данные, 
используй информацию выше. Если данных нет - скажи что можешь уточнить.
"""
        
        response = await self.claude.generate(
            system_prompt=JARVIS_PROMPT,
            user_prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        return response
    
    async def process_voice(
        self,
        audio_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Полный цикл обработки голосового запроса"""
        
        # 1. Транскрибируем
        text = await self.transcribe_audio(audio_data)
        logger.info(f"Transcribed: {text}")
        
        # 2. Получаем ответ от Jarvis
        response_text = await self.process_query(text, context)
        logger.info(f"Jarvis response: {response_text}")
        
        # 3. Генерируем аудио ответ
        audio_response = await self.generate_speech(response_text)
        
        return {
            "query": text,
            "response": response_text,
            "audio": base64.b64encode(audio_response).decode()
        }


# ============================================
# ФАЙЛ: backend/app/api/v1/voice.py
# ============================================

"""
API эндпоинты для голосового ассистента.
"""

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ai.voice_assistant import VoiceAssistantService
from app.api.v1.analytics import get_dashboard

router = APIRouter()


@router.post("/query")
async def voice_query(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Текстовый запрос к Jarvis"""
    
    # Получаем контекст дашборда
    dashboard = await get_dashboard(current_user, db)
    context = dashboard.model_dump()
    
    assistant = VoiceAssistantService()
    response = await assistant.process_query(query, context)
    
    return {"response": response}


@router.post("/speak")
async def voice_speak(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Голосовой запрос к Jarvis"""
    
    # Получаем контекст
    dashboard = await get_dashboard(current_user, db)
    context = dashboard.model_dump()
    
    # Читаем аудио
    audio_data = await audio.read()
    
    assistant = VoiceAssistantService()
    result = await assistant.process_voice(audio_data, context)
    
    return result


@router.post("/tts")
async def text_to_speech(
    text: str,
    current_user: User = Depends(get_current_user)
):
    """Преобразование текста в речь"""
    
    assistant = VoiceAssistantService()
    audio = await assistant.generate_speech(text)
    
    import base64
    return {"audio": base64.b64encode(audio).decode()}


# ============================================
# ФАЙЛ: backend/app/services/social/publisher.py
# ============================================

"""
Сервис публикации контента в соцсети.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class BasePublisher(ABC):
    """Базовый класс для публикаторов"""
    
    @abstractmethod
    async def publish(
        self,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Опубликовать контент"""
        pass
    
    @abstractmethod
    async def delete(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> bool:
        """Удалить публикацию"""
        pass
    
    @abstractmethod
    async def get_metrics(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        """Получить метрики публикации"""
        pass


class TikTokPublisher(BasePublisher):
    """Публикация в TikTok"""
    
    async def publish(
        self,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Публикация видео в TikTok"""
        
        access_token = credentials.get("access_token")
        
        # TikTok Content Posting API
        async with httpx.AsyncClient() as client:
            # 1. Инициализируем загрузку
            init_response = await client.post(
                "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "post_info": {
                        "title": content.get("caption", "")[:150],
                        "privacy_level": "PUBLIC_TO_EVERYONE",
                        "disable_comment": False,
                        "disable_duet": False,
                        "disable_stitch": False
                    },
                    "source_info": {
                        "source": "PULL_FROM_URL",
                        "video_url": content.get("media_url")
                    }
                }
            )
            
            result = init_response.json()
            
            if init_response.status_code == 200:
                return {
                    "post_id": result.get("data", {}).get("publish_id"),
                    "status": "published"
                }
            else:
                raise Exception(f"TikTok API error: {result}")
    
    async def delete(self, credentials: Dict[str, str], post_id: str) -> bool:
        # TikTok не поддерживает удаление через API
        return False
    
    async def get_metrics(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        """Получить метрики видео"""
        
        access_token = credentials.get("access_token")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://open.tiktokapis.com/v2/video/query/",
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "filters": {"video_ids": [post_id]},
                    "fields": ["like_count", "comment_count", "share_count", "view_count"]
                }
            )
            
            data = response.json().get("data", {}).get("videos", [{}])[0]
            
            return {
                "views": data.get("view_count", 0),
                "likes": data.get("like_count", 0),
                "comments": data.get("comment_count", 0),
                "shares": data.get("share_count", 0)
            }


class TwitterPublisher(BasePublisher):
    """Публикация в Twitter/X"""
    
    async def publish(
        self,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Публикация твита"""
        
        # Используем OAuth 1.0a
        import tweepy
        
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )
        auth.set_access_token(
            credentials.get("access_token"),
            credentials.get("access_token_secret")
        )
        
        api = tweepy.API(auth)
        client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=credentials.get("access_token"),
            access_token_secret=credentials.get("access_token_secret")
        )
        
        # Публикуем
        if content.get("type") == "thread":
            # Thread - несколько твитов
            tweets = content.get("tweets", [content.get("caption")])
            first_tweet = client.create_tweet(text=tweets[0])
            last_id = first_tweet.data["id"]
            
            for tweet_text in tweets[1:]:
                response = client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=last_id
                )
                last_id = response.data["id"]
            
            return {
                "post_id": first_tweet.data["id"],
                "url": f"https://twitter.com/i/status/{first_tweet.data['id']}",
                "status": "published"
            }
        else:
            # Одиночный твит
            response = client.create_tweet(text=content.get("caption", ""))
            
            return {
                "post_id": response.data["id"],
                "url": f"https://twitter.com/i/status/{response.data['id']}",
                "status": "published"
            }
    
    async def delete(self, credentials: Dict[str, str], post_id: str) -> bool:
        import tweepy
        
        client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=credentials.get("access_token"),
            access_token_secret=credentials.get("access_token_secret")
        )
        
        client.delete_tweet(post_id)
        return True
    
    async def get_metrics(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        import tweepy
        
        client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=credentials.get("access_token"),
            access_token_secret=credentials.get("access_token_secret")
        )
        
        tweet = client.get_tweet(
            post_id,
            tweet_fields=["public_metrics"]
        )
        
        metrics = tweet.data.public_metrics
        
        return {
            "views": metrics.get("impression_count", 0),
            "likes": metrics.get("like_count", 0),
            "comments": metrics.get("reply_count", 0),
            "shares": metrics.get("retweet_count", 0)
        }


class LinkedInPublisher(BasePublisher):
    """Публикация в LinkedIn"""
    
    async def publish(
        self,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Публикация поста в LinkedIn"""
        
        access_token = credentials.get("access_token")
        person_id = credentials.get("person_id")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                },
                json={
                    "author": f"urn:li:person:{person_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": content.get("caption", "")
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
            )
            
            if response.status_code == 201:
                post_id = response.headers.get("x-restli-id", "")
                return {
                    "post_id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
                    "status": "published"
                }
            else:
                raise Exception(f"LinkedIn API error: {response.text}")
    
    async def delete(self, credentials: Dict[str, str], post_id: str) -> bool:
        access_token = credentials.get("access_token")
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"https://api.linkedin.com/v2/ugcPosts/{post_id}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.status_code == 204
    
    async def get_metrics(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        # LinkedIn metrics требуют отдельного API
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}


class TelegramPublisher(BasePublisher):
    """Публикация в Telegram канал"""
    
    async def publish(
        self,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Публикация в Telegram канал"""
        
        bot_token = credentials.get("bot_token", settings.TELEGRAM_BOT_TOKEN)
        channel_id = credentials.get("channel_id")
        
        async with httpx.AsyncClient() as client:
            if content.get("media_url"):
                # Публикация с медиа
                if content.get("type") in ["short_video", "long_video"]:
                    response = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendVideo",
                        json={
                            "chat_id": channel_id,
                            "video": content.get("media_url"),
                            "caption": content.get("caption", "")[:1024]
                        }
                    )
                else:
                    response = await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                        json={
                            "chat_id": channel_id,
                            "photo": content.get("media_url"),
                            "caption": content.get("caption", "")[:1024]
                        }
                    )
            else:
                # Текстовый пост
                response = await client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": channel_id,
                        "text": content.get("caption", ""),
                        "parse_mode": "HTML"
                    }
                )
            
            result = response.json()
            
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                return {
                    "post_id": str(message_id),
                    "url": f"https://t.me/c/{channel_id}/{message_id}",
                    "status": "published"
                }
            else:
                raise Exception(f"Telegram API error: {result}")
    
    async def delete(self, credentials: Dict[str, str], post_id: str) -> bool:
        bot_token = credentials.get("bot_token", settings.TELEGRAM_BOT_TOKEN)
        channel_id = credentials.get("channel_id")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/deleteMessage",
                json={
                    "chat_id": channel_id,
                    "message_id": int(post_id)
                }
            )
            return response.json().get("ok", False)
    
    async def get_metrics(
        self,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        # Telegram не предоставляет метрики через Bot API
        # Нужен Telegram Statistics API для каналов
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}


class PublisherService:
    """Главный сервис публикации"""
    
    def __init__(self):
        self.publishers = {
            "tiktok": TikTokPublisher(),
            "twitter": TwitterPublisher(),
            "linkedin": LinkedInPublisher(),
            "telegram": TelegramPublisher()
        }
    
    async def publish(
        self,
        platform: str,
        credentials: Dict[str, str],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Публикация на выбранную платформу"""
        
        publisher = self.publishers.get(platform)
        if not publisher:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return await publisher.publish(credentials, content)
    
    async def delete(
        self,
        platform: str,
        credentials: Dict[str, str],
        post_id: str
    ) -> bool:
        """Удаление публикации"""
        
        publisher = self.publishers.get(platform)
        if not publisher:
            return False
        
        return await publisher.delete(credentials, post_id)
    
    async def get_metrics(
        self,
        platform: str,
        credentials: Dict[str, str],
        post_id: str
    ) -> Dict[str, Any]:
        """Получение метрик"""
        
        publisher = self.publishers.get(platform)
        if not publisher:
            return {}
        
        return await publisher.get_metrics(credentials, post_id)


# ============================================
# ФАЙЛ: backend/app/core/ai_agents.py
# ============================================

"""
Системные промпты для AI-агентов.
"""

NICHE_ANALYST_PROMPT = """
Ты — Senior Market Research Analyst с 15-летним опытом в digital-маркетинге и affiliate marketing. 
Специализация: поиск прибыльных ниш, анализ трендов, оценка конкуренции.

КРИТЕРИИ ХОРОШЕЙ НИШИ:
✅ Вечнозелёная (люди всегда будут интересоваться)
✅ Есть "боль" которую можно решить
✅ Средний чек продукта > $50
✅ Комиссия партнёрки > 20%
✅ Можно создавать контент без экспертизы (через исследования)
✅ Не требует показа лица

КРАСНЫЕ ФЛАГИ:
❌ Высокая конкуренция от крупных брендов
❌ Нужны сертификаты/лицензии (медицина, финансовые советы)
❌ Сезонный спрос (только Новый год и т.д.)
❌ Низкий средний чек (< $20)
❌ Нет партнёрских программ

Всегда отвечай структурированно и конкретно. Используй реальные данные где возможно.
"""

CONTENT_STRATEGIST_PROMPT = """
Ты — Head of Content с 10-летним опытом в построении контент-империй.
Специализация: вирусный контент, контент-планирование, адаптация под алгоритмы платформ.

ЗНАНИЕ АЛГОРИТМОВ:
- TikTok: 15-60 сек, hook в первые 3 секунды, тренды важны
- YouTube Shorts: 30-45 сек, retention > 70%
- Twitter: threads работают лучше, первый твит = hook
- LinkedIn: storytelling, 1300+ символов, публикация вт-чт 8:00-10:00
- Telegram: информативный контент, 3-5 постов в день

КОНТЕНТ-МАТРИЦА:
- 70% развлекательный/полезный (охват, рост)
- 20% образовательный (доверие)
- 10% продающий (конверсия)

Создавай контент который цепляет с первой секунды и удерживает до конца.
"""

COPYWRITER_PROMPT = """
Ты — Senior Copywriter с опытом написания контента, который сгенерировал $10M+ в продажах.
Специализация: продающие тексты, сценарии для видео, адаптация под tone of voice.

ПРИНЦИПЫ:
1. Hook в первые 2 секунды ОБЯЗАТЕЛЕН
2. Говори на языке аудитории
3. Используй storytelling
4. Один CTA на единицу контента
5. Эмоции важнее логики

ФОРМУЛЫ HOOK-ОВ:
- "Я потратил [X] чтобы вы не потратили"
- "Почему [авторитет] делает [неожиданное]"
- "[Число]% людей не знают этого о [тема]"
- "Хватит делать [ошибка]. Вот почему..."

Пиши живым языком, без канцеляризмов. Каждое слово должно работать.
"""

VIDEO_PRODUCER_PROMPT = """
Ты — Video Production Director с опытом создания viral-контента.
Специализация: короткие видео (shorts, reels, TikTok), AI-генерация видео.

ТЕХНИЧЕСКИЕ СПЕЦИФИКАЦИИ:
- Все платформы: 1080x1920 (вертикаль)
- TikTok/YT Shorts: до 60 сек
- Retention правило: смена кадра каждые 3-5 сек

СТРУКТУРА ВИДЕО (30 сек):
- 0-2 сек: HOOK (визуал + текст)
- 2-10 сек: ПРОБЛЕМА
- 10-25 сек: РЕШЕНИЕ
- 25-30 сек: CTA

Создавай чёткие ТЗ для генерации видео через AI (HeyGen, Runway, etc).
"""

JARVIS_PROMPT = """
Ты — JARVIS, персональный AI-ассистент системы автоматического контента.
У тебя есть доступ ко всем данным системы: аккаунты, контент, аналитика, финансы.

СТИЛЬ ОБЩЕНИЯ:
- Дружелюбный, но профессиональный
- Краткий и информативный
- Проактивный — сам предлагай идеи
- Говори на языке пользователя

ВОЗМОЖНОСТИ:
- Отвечать на вопросы о состоянии бизнеса
- Давать рекомендации на основе аналитики
- Помогать с планированием контента
- Предупреждать о проблемах

Если нет точных данных — честно скажи и предложи как их получить.
Всегда старайся быть максимально полезным.
"""
