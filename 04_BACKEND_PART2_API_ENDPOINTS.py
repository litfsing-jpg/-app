# =============================================
# BACKEND API — ЧАСТЬ 2: API ЭНДПОИНТЫ
# =============================================

# ============================================
# ФАЙЛ: backend/app/main.py
# ============================================

"""
Главная точка входа FastAPI приложения.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import router as api_v1_router
from app.db.session import engine, Base

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle события приложения"""
    # Startup
    logger.info("🚀 Starting Content Automation System...")
    
    # Создаём таблицы если их нет (в продакшене использовать Alembic)
    # Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down...")


# Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Система автоматической генерации и публикации контента",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    """Детальная проверка здоровья системы"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "version": settings.APP_VERSION
    }


# ============================================
# ФАЙЛ: backend/app/api/v1/__init__.py
# ============================================

"""
API v1 роутер - объединяет все эндпоинты.
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    niches,
    affiliates,
    accounts,
    content,
    publications,
    analytics,
    leads,
    voice,
    webhooks
)

router = APIRouter()

# Подключаем все роутеры
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(niches.router, prefix="/niches", tags=["Niches"])
router.include_router(affiliates.router, prefix="/affiliates", tags=["Affiliates"])
router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
router.include_router(content.router, prefix="/content", tags=["Content"])
router.include_router(publications.router, prefix="/publications", tags=["Publications"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(leads.router, prefix="/leads", tags=["Leads"])
router.include_router(voice.router, prefix="/voice", tags=["Voice Assistant"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])


# ============================================
# ФАЙЛ: backend/app/api/deps.py
# ============================================

"""
Зависимости для API эндпоинтов.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import SessionLocal
from app.config import settings
from app.models.user import User

# Security схема
security = HTTPBearer()


def get_db() -> Generator:
    """Получение сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из JWT токена"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка что пользователь - админ"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# ============================================
# ФАЙЛ: backend/app/api/v1/auth.py
# ============================================

"""
Эндпоинты аутентификации.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from app.api.deps import get_db
from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

router = APIRouter()

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    
    # Проверяем что email не занят
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаём пользователя
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Вход в систему"""
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return Token(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id))
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Обновление access token"""
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")
        
        return Token(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id))
        )
        
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ============================================
# ФАЙЛ: backend/app/api/v1/users.py
# ============================================

"""
Эндпоинты пользователей.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить информацию текущего пользователя"""
    
    if user_data.name is not None:
        current_user.name = user_data.name
    
    if user_data.settings is not None:
        current_user.settings = {**current_user.settings, **user_data.settings}
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ============================================
# ФАЙЛ: backend/app/api/v1/niches.py
# ============================================

"""
Эндпоинты для работы с нишами.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.niche import Niche
from app.schemas.niche import NicheCreate, NicheUpdate, NicheResponse, NicheAnalysis
from app.services.ai.niche_analyzer import NicheAnalyzerService

router = APIRouter()


@router.get("/", response_model=List[NicheResponse])
async def get_niches(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список ниш"""
    
    query = db.query(Niche)
    
    if status:
        query = query.filter(Niche.status == status)
    
    niches = query.offset(skip).limit(limit).all()
    return niches


@router.post("/", response_model=NicheResponse)
async def create_niche(
    niche_data: NicheCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать новую нишу"""
    
    # Проверяем уникальность slug
    existing = db.query(Niche).filter(Niche.slug == niche_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niche with this slug already exists"
        )
    
    niche = Niche(**niche_data.model_dump())
    db.add(niche)
    db.commit()
    db.refresh(niche)
    
    return niche


@router.get("/{niche_id}", response_model=NicheResponse)
async def get_niche(
    niche_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить нишу по ID"""
    
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    return niche


@router.patch("/{niche_id}", response_model=NicheResponse)
async def update_niche(
    niche_id: UUID,
    niche_data: NicheUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить нишу"""
    
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    update_data = niche_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(niche, field, value)
    
    db.commit()
    db.refresh(niche)
    
    return niche


@router.delete("/{niche_id}")
async def delete_niche(
    niche_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить нишу"""
    
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    db.delete(niche)
    db.commit()
    
    return {"status": "deleted"}


@router.post("/analyze", response_model=NicheAnalysis)
async def analyze_niche(
    niche_name: str,
    current_user: User = Depends(get_current_user)
):
    """Проанализировать нишу с помощью AI"""
    
    analyzer = NicheAnalyzerService()
    analysis = await analyzer.analyze_niche(niche_name)
    
    return analysis


@router.post("/suggest")
async def suggest_niches(
    category: Optional[str] = None,
    count: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Получить предложения прибыльных ниш от AI"""
    
    analyzer = NicheAnalyzerService()
    suggestions = await analyzer.suggest_niches(category=category, count=count)
    
    return {"suggestions": suggestions}


# ============================================
# ФАЙЛ: backend/app/api/v1/accounts.py
# ============================================

"""
Эндпоинты для работы с аккаунтами соцсетей.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountStats

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    niche_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список аккаунтов с фильтрацией"""
    
    query = db.query(Account)
    
    if platform:
        query = query.filter(Account.platform == platform)
    if status:
        query = query.filter(Account.status == status)
    if niche_id:
        query = query.filter(Account.niche_id == niche_id)
    
    accounts = query.offset(skip).limit(limit).all()
    return accounts


@router.post("/", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавить новый аккаунт"""
    
    # Проверяем уникальность username на платформе
    existing = db.query(Account).filter(
        Account.platform == account_data.platform,
        Account.username == account_data.username
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this username already exists on this platform"
        )
    
    account = Account(**account_data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить аккаунт по ID"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить аккаунт"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить аккаунт"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db.delete(account)
    db.commit()
    
    return {"status": "deleted"}


@router.get("/{account_id}/stats", response_model=AccountStats)
async def get_account_stats(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику аккаунта"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Подсчитываем метрики из публикаций
    from app.models.publication import Publication
    from app.models.metrics import Metrics
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Publication.id).label('publications_count'),
        func.coalesce(func.sum(Metrics.views), 0).label('total_views'),
        func.coalesce(func.sum(Metrics.likes), 0).label('total_likes'),
        func.coalesce(func.avg(Metrics.engagement_rate), 0).label('avg_engagement')
    ).join(
        Metrics, Metrics.publication_id == Publication.id, isouter=True
    ).filter(
        Publication.account_id == account_id
    ).first()
    
    return AccountStats(
        id=account.id,
        platform=account.platform.value,
        username=account.username,
        followers=account.followers,
        total_views=int(stats.total_views or 0),
        total_likes=int(stats.total_likes or 0),
        avg_engagement=stats.avg_engagement or 0,
        publications_count=stats.publications_count or 0,
        health_score=account.health_score,
        status=account.status.value
    )


@router.post("/{account_id}/refresh-token")
async def refresh_account_token(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить токен аккаунта (для OAuth платформ)"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # TODO: Реализовать обновление токена для каждой платформы
    # Это зависит от конкретной платформы (Twitter, LinkedIn и т.д.)
    
    return {"status": "token_refreshed"}


@router.post("/{account_id}/check-health")
async def check_account_health(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Проверить здоровье аккаунта"""
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # TODO: Реализовать проверку здоровья
    # - Проверить валидность токена
    # - Проверить ограничения платформы
    # - Проверить shadowban
    
    return {
        "account_id": str(account_id),
        "health_score": account.health_score,
        "status": account.status.value,
        "issues": []
    }


# ============================================
# ФАЙЛ: backend/app/api/v1/content.py
# ============================================

"""
Эндпоинты для работы с контентом.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.content import Content, ContentStatus
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse,
    ContentGenerate, ContentBatchGenerate
)
from app.services.ai.content_generator import ContentGeneratorService

router = APIRouter()


@router.get("/", response_model=List[ContentResponse])
async def get_content_list(
    status: Optional[str] = None,
    type: Optional[str] = None,
    platform: Optional[str] = None,
    niche_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список контента с фильтрацией"""
    
    query = db.query(Content)
    
    if status:
        query = query.filter(Content.status == status)
    if type:
        query = query.filter(Content.type == type)
    if platform:
        query = query.filter(Content.target_platform == platform)
    if niche_id:
        query = query.filter(Content.niche_id == niche_id)
    
    # Сортировка: сначала новые
    query = query.order_by(Content.created_at.desc())
    
    content_list = query.offset(skip).limit(limit).all()
    return content_list


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создать контент вручную"""
    
    content = Content(**content_data.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить контент по ID"""
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_data: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновить контент"""
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    update_data = content_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    
    return content


@router.delete("/{content_id}")
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить контент"""
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"status": "deleted"}


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Сгенерировать контент с помощью AI"""
    
    # Создаём запись со статусом "generating"
    content = Content(
        niche_id=request.niche_id,
        affiliate_id=request.affiliate_id,
        type=request.type,
        target_platform=request.target_platform,
        status=ContentStatus.GENERATING
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    # Запускаем генерацию в фоне
    background_tasks.add_task(
        generate_content_task,
        content_id=content.id,
        request=request,
        db=db
    )
    
    return content


async def generate_content_task(content_id: UUID, request: ContentGenerate, db: Session):
    """Фоновая задача генерации контента"""
    
    try:
        generator = ContentGeneratorService()
        
        # Генерируем контент
        generated = await generator.generate(
            niche_id=str(request.niche_id),
            content_type=request.type,
            platform=request.target_platform,
            topic=request.topic,
            tone=request.tone,
            include_cta=request.include_cta
        )
        
        # Обновляем запись
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.title = generated.get("title")
            content.hook = generated.get("hook")
            content.script = generated.get("script")
            content.caption = generated.get("caption")
            content.hashtags = generated.get("hashtags", [])
            content.call_to_action = generated.get("cta")
            content.ai_model = generated.get("model")
            content.status = ContentStatus.READY
            
            db.commit()
            
    except Exception as e:
        # В случае ошибки помечаем как failed
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.status = ContentStatus.FAILED
            db.commit()
        raise e


@router.post("/generate-batch")
async def generate_content_batch(
    request: ContentBatchGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пакетная генерация контента"""
    
    created_content_ids = []
    
    for content_type in request.types:
        for platform in request.platforms:
            for _ in range(request.count_per_type):
                # Создаём записи
                content = Content(
                    niche_id=request.niche_id,
                    affiliate_id=request.affiliate_id,
                    type=content_type,
                    target_platform=platform,
                    status=ContentStatus.GENERATING
                )
                db.add(content)
                db.commit()
                db.refresh(content)
                
                created_content_ids.append(str(content.id))
                
                # Добавляем задачу генерации
                gen_request = ContentGenerate(
                    niche_id=request.niche_id,
                    type=content_type,
                    target_platform=platform,
                    affiliate_id=request.affiliate_id
                )
                background_tasks.add_task(
                    generate_content_task,
                    content_id=content.id,
                    request=gen_request,
                    db=db
                )
    
    return {
        "status": "generation_started",
        "content_ids": created_content_ids,
        "total_count": len(created_content_ids)
    }


@router.post("/{content_id}/schedule")
async def schedule_content(
    content_id: UUID,
    scheduled_for: datetime,
    account_ids: List[UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запланировать публикацию контента"""
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status != ContentStatus.READY:
        raise HTTPException(
            status_code=400,
            detail="Content must be in 'ready' status to schedule"
        )
    
    content.scheduled_for = scheduled_for
    content.status = ContentStatus.SCHEDULED
    
    # Создаём публикации для каждого аккаунта
    from app.models.publication import Publication
    from app.models.account import Account
    
    publications = []
    for account_id in account_ids:
        account = db.query(Account).filter(Account.id == account_id).first()
        if account:
            pub = Publication(
                content_id=content_id,
                account_id=account_id,
                scheduled_at=scheduled_for
            )
            db.add(pub)
            publications.append(pub)
    
    db.commit()
    
    return {
        "status": "scheduled",
        "scheduled_for": scheduled_for.isoformat(),
        "publications_created": len(publications)
    }


@router.get("/queue")
async def get_content_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить очередь запланированного контента"""
    
    scheduled = db.query(Content).filter(
        Content.status == ContentStatus.SCHEDULED
    ).order_by(Content.scheduled_for).all()
    
    return {
        "queue": [ContentResponse.model_validate(c) for c in scheduled],
        "total": len(scheduled)
    }


# ============================================
# ФАЙЛ: backend/app/api/v1/publications.py
# ============================================

"""
Эндпоинты для работы с публикациями.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.publication import Publication, PublicationStatus
from app.models.content import Content
from app.models.account import Account

router = APIRouter()


@router.get("/")
async def get_publications(
    status: Optional[str] = None,
    account_id: Optional[UUID] = None,
    content_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить список публикаций"""
    
    query = db.query(Publication)
    
    if status:
        query = query.filter(Publication.status == status)
    if account_id:
        query = query.filter(Publication.account_id == account_id)
    if content_id:
        query = query.filter(Publication.content_id == content_id)
    
    query = query.order_by(Publication.created_at.desc())
    
    publications = query.offset(skip).limit(limit).all()
    
    return publications


@router.get("/{publication_id}")
async def get_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить публикацию по ID"""
    
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication


@router.post("/{publication_id}/publish")
async def publish_now(
    publication_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Опубликовать сейчас"""
    
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    if publication.status not in [PublicationStatus.PENDING, PublicationStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish from status: {publication.status}"
        )
    
    # Запускаем публикацию в фоне
    background_tasks.add_task(
        publish_content_task,
        publication_id=publication_id,
        db=db
    )
    
    publication.status = PublicationStatus.PUBLISHING
    db.commit()
    
    return {"status": "publishing", "publication_id": str(publication_id)}


async def publish_content_task(publication_id: UUID, db: Session):
    """Фоновая задача публикации"""
    from app.services.social.publisher import PublisherService
    
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        return
    
    try:
        publisher = PublisherService()
        
        content = db.query(Content).filter(Content.id == publication.content_id).first()
        account = db.query(Account).filter(Account.id == publication.account_id).first()
        
        if not content or not account:
            raise Exception("Content or Account not found")
        
        # Публикуем
        result = await publisher.publish(
            platform=account.platform.value,
            credentials=account.credentials,
            content={
                "type": content.type.value,
                "caption": content.caption,
                "media_url": content.media_url,
                "link_url": content.link_url
            }
        )
        
        # Обновляем статус
        publication.platform_post_id = result.get("post_id")
        publication.platform_url = result.get("url")
        publication.status = PublicationStatus.PUBLISHED
        publication.published_at = datetime.utcnow()
        
        # Обновляем счётчик аккаунта
        account.posts_today += 1
        account.last_posted_at = datetime.utcnow()
        account.total_posts += 1
        
        db.commit()
        
    except Exception as e:
        publication.status = PublicationStatus.FAILED
        publication.error_message = str(e)
        publication.retry_count += 1
        db.commit()


@router.post("/{publication_id}/retry")
async def retry_publication(
    publication_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Повторить неудачную публикацию"""
    
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    if publication.status != PublicationStatus.FAILED:
        raise HTTPException(status_code=400, detail="Can only retry failed publications")
    
    background_tasks.add_task(
        publish_content_task,
        publication_id=publication_id,
        db=db
    )
    
    publication.status = PublicationStatus.PUBLISHING
    db.commit()
    
    return {"status": "retrying"}


@router.delete("/{publication_id}")
async def delete_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удалить публикацию"""
    
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    db.delete(publication)
    db.commit()
    
    return {"status": "deleted"}


# ============================================
# ФАЙЛ: backend/app/api/v1/analytics.py
# ============================================

"""
Эндпоинты аналитики.
"""

from typing import Optional
from datetime import date, datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.account import Account
from app.models.content import Content
from app.models.publication import Publication
from app.models.metrics import Metrics
from app.models.lead import Lead
from app.models.conversion import Conversion
from app.schemas.analytics import (
    DashboardSummary, PlatformStats, FunnelStats, RevenueStats
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить данные для главного дашборда"""
    
    today = date.today()
    month_start = today.replace(day=1)
    
    # Статистика аккаунтов
    total_accounts = db.query(Account).count()
    active_accounts = db.query(Account).filter(Account.status == "active").count()
    total_followers = db.query(func.sum(Account.followers)).scalar() or 0
    
    # Контент
    total_content = db.query(Content).count()
    scheduled_content = db.query(Content).filter(Content.status == "scheduled").count()
    published_today = db.query(Publication).filter(
        func.date(Publication.published_at) == today
    ).count()
    
    # Лиды
    total_leads = db.query(Lead).count()
    new_leads_today = db.query(Lead).filter(
        func.date(Lead.created_at) == today
    ).count()
    
    converted_leads = db.query(Lead).filter(Lead.funnel_stage == "converted").count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Финансы
    revenue_today = db.query(func.sum(Conversion.commission_amount)).filter(
        func.date(Conversion.converted_at) == today,
        Conversion.status.in_(["approved", "paid"])
    ).scalar() or 0
    
    revenue_month = db.query(func.sum(Conversion.commission_amount)).filter(
        Conversion.converted_at >= month_start,
        Conversion.status.in_(["approved", "paid"])
    ).scalar() or 0
    
    # Проблемные аккаунты
    accounts_needing_attention = db.query(Account).filter(
        Account.health_score < 50
    ).count()
    
    failed_publications = db.query(Publication).filter(
        Publication.status == "failed"
    ).count()
    
    # Статистика по платформам
    platforms_stats = []
    for platform in ["tiktok", "youtube", "twitter", "linkedin", "telegram"]:
        platform_accounts = db.query(Account).filter(Account.platform == platform).all()
        if platform_accounts:
            stats = PlatformStats(
                platform=platform,
                accounts_count=len(platform_accounts),
                total_followers=sum(a.followers for a in platform_accounts),
                total_views=0,  # TODO: собрать из metrics
                total_engagement=0,
                avg_engagement_rate=0,
                publications_count=0
            )
            platforms_stats.append(stats)
    
    return DashboardSummary(
        total_accounts=total_accounts,
        active_accounts=active_accounts,
        total_followers=total_followers,
        followers_growth=0,  # TODO: рассчитать
        total_content=total_content,
        scheduled_content=scheduled_content,
        published_today=published_today,
        total_leads=total_leads,
        new_leads_today=new_leads_today,
        conversion_rate=conversion_rate,
        revenue_today=revenue_today,
        revenue_month=revenue_month,
        expenses_month=0,  # TODO: собрать из expenses
        profit_month=revenue_month,
        accounts_needing_attention=accounts_needing_attention,
        failed_publications=failed_publications,
        top_content=[],
        platforms_stats=platforms_stats
    )


@router.get("/funnel", response_model=FunnelStats)
async def get_funnel_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику воронки"""
    
    query = db.query(Lead)
    
    if start_date:
        query = query.filter(Lead.created_at >= start_date)
    if end_date:
        query = query.filter(Lead.created_at <= end_date)
    
    total = query.count()
    new = query.filter(Lead.funnel_stage == "new").count()
    engaged = query.filter(Lead.funnel_stage == "engaged").count()
    interested = query.filter(Lead.funnel_stage == "interested").count()
    ready = query.filter(Lead.funnel_stage == "ready_to_buy").count()
    converted = query.filter(Lead.funnel_stage == "converted").count()
    lost = query.filter(Lead.funnel_stage == "lost").count()
    
    return FunnelStats(
        total_leads=total,
        new_leads=new,
        engaged_leads=engaged,
        interested_leads=interested,
        ready_to_buy=ready,
        converted=converted,
        lost=lost,
        conversion_rate=(converted / total * 100) if total > 0 else 0
    )


@router.get("/revenue", response_model=RevenueStats)
async def get_revenue_stats(
    period: str = "month",  # day, week, month
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику доходов"""
    
    today = date.today()
    
    if period == "day":
        start_date = today
    elif period == "week":
        start_date = today - timedelta(days=7)
    else:  # month
        start_date = today.replace(day=1)
    
    conversions = db.query(Conversion).filter(
        Conversion.converted_at >= start_date,
        Conversion.status.in_(["approved", "paid"])
    ).all()
    
    total_revenue = sum(c.order_amount for c in conversions)
    total_commission = sum(c.commission_amount for c in conversions)
    
    # TODO: получить расходы из таблицы expenses
    total_expenses = 0
    
    return RevenueStats(
        period=period,
        total_revenue=total_revenue,
        total_commission=total_commission,
        total_expenses=total_expenses,
        net_profit=total_commission - total_expenses,
        roi=((total_commission - total_expenses) / total_expenses * 100) if total_expenses > 0 else 0,
        conversions_count=len(conversions),
        avg_order_value=(total_revenue / len(conversions)) if conversions else 0
    )


@router.get("/content-performance")
async def get_content_performance(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить топ контента по производительности"""
    
    # Используем view v_top_content
    from sqlalchemy import text
    
    result = db.execute(text("""
        SELECT * FROM v_top_content
        ORDER BY total_views DESC
        LIMIT :limit
    """), {"limit": limit})
    
    return [dict(row._mapping) for row in result]


@router.get("/platforms")
async def get_platforms_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получить статистику по платформам"""
    
    platforms = db.query(
        Account.platform,
        func.count(Account.id).label("accounts"),
        func.sum(Account.followers).label("followers"),
        func.avg(Account.engagement_rate).label("avg_engagement")
    ).group_by(Account.platform).all()
    
    return [
        {
            "platform": p.platform.value if hasattr(p.platform, 'value') else p.platform,
            "accounts": p.accounts,
            "followers": p.followers or 0,
            "avg_engagement": float(p.avg_engagement or 0)
        }
        for p in platforms
    ]
