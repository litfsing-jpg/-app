# =============================================
# BACKEND API — ЧАСТЬ 2: ЭНДПОИНТЫ И РОУТЫ
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
    logger.info("🚀 Запуск Content Automation System...")
    
    # Создаём таблицы (в продакшене использовать Alembic миграции)
    # Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Система готова к работе")
    
    yield
    
    # Shutdown
    logger.info("👋 Остановка системы...")


# Создаём приложение
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API для автоматической генерации и публикации контента",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты API v1
app.include_router(api_v1_router, prefix="/api/v1")


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
async def root():
    return {
        "message": "Content Automation System API",
        "docs": "/docs",
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

# Подключаем все роуты
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(niches.router, prefix="/niches", tags=["Niches"])
router.include_router(affiliates.router, prefix="/affiliates", tags=["Affiliates"])
router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
router.include_router(content.router, prefix="/content", tags=["Content"])
router.include_router(publications.router, prefix="/publications", tags=["Publications"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(leads.router, prefix="/leads", tags=["Leads"])
router.include_router(voice.router, prefix="/voice", tags=["Voice/Jarvis"])
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
from app.models import User

# Security схема
security = HTTPBearer()


def get_db() -> Generator:
    """Получение сессии базы данных"""
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
        detail="Невалидный токен",
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
            detail="Пользователь деактивирован"
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка что пользователь - администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


# ============================================
# ФАЙЛ: backend/app/core/security.py
# ============================================

"""
Функции безопасности: хеширование паролей, JWT токены.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt
from passlib.context import CryptContext

from app.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Создание JWT access токена"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Создание JWT refresh токена"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# ============================================
# ФАЙЛ: backend/app/api/v1/auth.py
# ============================================

"""
Эндпоинты аутентификации.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.deps import get_db
from app.core.security import (
    verify_password, 
    get_password_hash,
    create_access_token,
    create_refresh_token
)
from app.models import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.config import settings

router = APIRouter()


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
            detail="Email уже зарегистрирован"
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
            detail="Неверный email или пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    # Создаём токены
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Обновление токенов"""
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена"
            )
        
        user_id = payload.get("sub")
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    # Создаём новые токены
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )


# ============================================
# ФАЙЛ: backend/app/api/v1/users.py
# ============================================

"""
Эндпоинты пользователей.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user, get_current_admin
from app.models import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля текущего пользователя"""
    
    if user_update.name is not None:
        current_user.name = user_update.name
    
    if user_update.settings is not None:
        current_user.settings = {**current_user.settings, **user_update.settings}
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Получение списка всех пользователей (только для админов)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ============================================
# ФАЙЛ: backend/app/api/v1/niches.py
# ============================================

"""
Эндпоинты для работы с нишами.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import User, Niche
from app.schemas.niche import NicheCreate, NicheUpdate, NicheResponse, NicheAnalysis

router = APIRouter()


@router.get("/", response_model=List[NicheResponse])
async def get_niches(
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка ниш"""
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
    """Создание новой ниши"""
    
    # Проверяем уникальность slug
    existing = db.query(Niche).filter(Niche.slug == niche_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ниша с таким slug уже существует"
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
    """Получение ниши по ID"""
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ниша не найдена"
        )
    
    return niche


@router.patch("/{niche_id}", response_model=NicheResponse)
async def update_niche(
    niche_id: UUID,
    niche_update: NicheUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление ниши"""
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ниша не найдена"
        )
    
    update_data = niche_update.model_dump(exclude_unset=True)
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
    """Удаление ниши"""
    niche = db.query(Niche).filter(Niche.id == niche_id).first()
    
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ниша не найдена"
        )
    
    db.delete(niche)
    db.commit()
    
    return {"message": "Ниша удалена"}


@router.post("/analyze", response_model=NicheAnalysis)
async def analyze_niche(
    niche_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Анализ ниши с помощью AI"""
    from app.services.ai.niche_analyzer import NicheAnalyzerService
    
    analyzer = NicheAnalyzerService()
    analysis = await analyzer.analyze_niche(niche_name)
    
    return analysis


# ============================================
# ФАЙЛ: backend/app/api/v1/accounts.py
# ============================================

"""
Эндпоинты для работы с аккаунтами социальных сетей.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import User, Account, Niche, Proxy
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse, AccountStats

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    platform: str = None,
    status: str = None,
    niche_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка аккаунтов с фильтрацией"""
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
    """Добавление нового аккаунта"""
    
    # Проверяем уникальность
    existing = db.query(Account).filter(
        Account.platform == account_data.platform,
        Account.username == account_data.username
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт уже существует"
        )
    
    # Проверяем существование ниши
    if account_data.niche_id:
        niche = db.query(Niche).filter(Niche.id == account_data.niche_id).first()
        if not niche:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ниша не найдена"
            )
    
    # Проверяем существование прокси
    if account_data.proxy_id:
        proxy = db.query(Proxy).filter(Proxy.id == account_data.proxy_id).first()
        if not proxy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Прокси не найден"
            )
    
    account = Account(**account_data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account


@router.get("/stats", response_model=List[AccountStats])
async def get_accounts_stats(
    platform: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение статистики по всем аккаунтам"""
    from sqlalchemy import func
    from app.models import Publication, Metrics
    
    query = db.query(
        Account.id,
        Account.platform,
        Account.username,
        Account.followers,
        Account.health_score,
        Account.status,
        func.count(Publication.id).label('publications_count'),
        func.coalesce(func.sum(Metrics.views), 0).label('total_views'),
        func.coalesce(func.sum(Metrics.likes), 0).label('total_likes'),
        func.coalesce(func.avg(Metrics.engagement_rate), 0).label('avg_engagement')
    ).outerjoin(
        Publication, Publication.account_id == Account.id
    ).outerjoin(
        Metrics, Metrics.publication_id == Publication.id
    ).group_by(Account.id)
    
    if platform:
        query = query.filter(Account.platform == platform)
    
    results = query.all()
    
    return [
        AccountStats(
            id=r.id,
            platform=r.platform,
            username=r.username,
            followers=r.followers,
            total_views=r.total_views,
            total_likes=r.total_likes,
            avg_engagement=r.avg_engagement or 0,
            publications_count=r.publications_count,
            health_score=r.health_score,
            status=r.status
        )
        for r in results
    ]


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение аккаунта по ID"""
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    return account


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_update: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление аккаунта"""
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    update_data = account_update.model_dump(exclude_unset=True)
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
    """Удаление аккаунта"""
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Аккаунт удалён"}


@router.post("/{account_id}/warmup")
async def start_warmup(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запуск прогрева аккаунта"""
    from datetime import datetime
    
    account = db.query(Account).filter(Account.id == account_id).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт не найден"
        )
    
    account.status = "warming_up"
    account.warmup_started_at = datetime.utcnow()
    
    db.commit()
    
    # TODO: Запустить Celery задачу для прогрева
    
    return {"message": "Прогрев аккаунта запущен", "account_id": str(account_id)}


# ============================================
# ФАЙЛ: backend/app/api/v1/content.py
# ============================================

"""
Эндпоинты для работы с контентом.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models import User, Content, Niche, Affiliate
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse, 
    ContentGenerate, ContentBatchGenerate
)

router = APIRouter()


@router.get("/", response_model=List[ContentResponse])
async def get_content_list(
    type: str = None,
    platform: str = None,
    status: str = None,
    niche_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка контента с фильтрацией"""
    query = db.query(Content)
    
    if type:
        query = query.filter(Content.type == type)
    if platform:
        query = query.filter(Content.target_platform == platform)
    if status:
        query = query.filter(Content.status == status)
    if niche_id:
        query = query.filter(Content.niche_id == niche_id)
    
    # Сортировка по дате создания (новые первыми)
    query = query.order_by(Content.created_at.desc())
    
    content = query.offset(skip).limit(limit).all()
    return content


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание контента вручную"""
    content = Content(**content_data.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    generate_request: ContentGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Генерация контента с помощью AI"""
    from app.services.ai.content_generator import ContentGeneratorService
    
    # Проверяем существование ниши
    niche = db.query(Niche).filter(Niche.id == generate_request.niche_id).first()
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ниша не найдена"
        )
    
    # Получаем партнёрку если указана
    affiliate = None
    if generate_request.affiliate_id:
        affiliate = db.query(Affiliate).filter(
            Affiliate.id == generate_request.affiliate_id
        ).first()
    
    # Создаём запись контента со статусом "generating"
    content = Content(
        niche_id=niche.id,
        affiliate_id=affiliate.id if affiliate else None,
        type=generate_request.type,
        target_platform=generate_request.target_platform,
        status="generating"
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    # Запускаем генерацию в фоне
    background_tasks.add_task(
        _generate_content_task,
        content_id=str(content.id),
        niche_name=niche.name,
        niche_keywords=niche.keywords,
        content_type=generate_request.type,
        platform=generate_request.target_platform,
        topic=generate_request.topic,
        tone=generate_request.tone,
        affiliate_link=affiliate.affiliate_link if affiliate else None,
        include_cta=generate_request.include_cta
    )
    
    return content


async def _generate_content_task(
    content_id: str,
    niche_name: str,
    niche_keywords: list,
    content_type: str,
    platform: str,
    topic: str,
    tone: str,
    affiliate_link: str,
    include_cta: bool
):
    """Фоновая задача генерации контента"""
    from app.db.session import SessionLocal
    from app.services.ai.content_generator import ContentGeneratorService
    
    db = SessionLocal()
    try:
        generator = ContentGeneratorService()
        
        # Генерируем контент
        generated = await generator.generate(
            niche_name=niche_name,
            niche_keywords=niche_keywords,
            content_type=content_type,
            platform=platform,
            topic=topic,
            tone=tone,
            affiliate_link=affiliate_link,
            include_cta=include_cta
        )
        
        # Обновляем запись
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.title = generated.get("title")
            content.hook = generated.get("hook")
            content.script = generated.get("script")
            content.caption = generated.get("caption")
            content.hashtags = generated.get("hashtags", [])
            content.call_to_action = generated.get("call_to_action")
            content.link_url = affiliate_link
            content.status = "ready"
            content.ai_model = generated.get("model", "claude-3")
            
            db.commit()
            
    except Exception as e:
        # Помечаем как failed
        content = db.query(Content).filter(Content.id == content_id).first()
        if content:
            content.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()


@router.post("/generate/batch")
async def generate_content_batch(
    batch_request: ContentBatchGenerate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Пакетная генерация контента"""
    
    # Проверяем нишу
    niche = db.query(Niche).filter(Niche.id == batch_request.niche_id).first()
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ниша не найдена"
        )
    
    created_content_ids = []
    
    # Создаём записи для каждой комбинации тип + платформа
    for content_type in batch_request.types:
        for platform in batch_request.platforms:
            for i in range(batch_request.count_per_type):
                content = Content(
                    niche_id=niche.id,
                    affiliate_id=batch_request.affiliate_id,
                    type=content_type,
                    target_platform=platform,
                    status="generating"
                )
                db.add(content)
                db.commit()
                db.refresh(content)
                created_content_ids.append(str(content.id))
                
                # Запускаем генерацию в фоне
                background_tasks.add_task(
                    _generate_content_task,
                    content_id=str(content.id),
                    niche_name=niche.name,
                    niche_keywords=niche.keywords,
                    content_type=content_type,
                    platform=platform,
                    topic=None,
                    tone="engaging",
                    affiliate_link=None,
                    include_cta=True
                )
    
    return {
        "message": f"Запущена генерация {len(created_content_ids)} единиц контента",
        "content_ids": created_content_ids
    }


@router.get("/queue")
async def get_content_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение очереди контента на публикацию"""
    scheduled_content = db.query(Content).filter(
        Content.status == "scheduled",
        Content.scheduled_for.isnot(None)
    ).order_by(Content.scheduled_for.asc()).all()
    
    ready_content = db.query(Content).filter(
        Content.status == "ready"
    ).order_by(Content.created_at.desc()).all()
    
    return {
        "scheduled": [ContentResponse.model_validate(c) for c in scheduled_content],
        "ready": [ContentResponse.model_validate(c) for c in ready_content]
    }


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение контента по ID"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )
    
    return content


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление контента"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )
    
    update_data = content_update.model_dump(exclude_unset=True)
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
    """Удаление контента"""
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )
    
    db.delete(content)
    db.commit()
    
    return {"message": "Контент удалён"}


@router.post("/{content_id}/schedule")
async def schedule_content(
    content_id: UUID,
    scheduled_for: datetime,
    account_ids: List[UUID],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Планирование публикации контента"""
    from app.models import Publication, ScheduledTask
    
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контент не найден"
        )
    
    if content.status not in ["ready", "scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контент не готов к публикации"
        )
    
    publications = []
    
    for account_id in account_ids:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            continue
        
        # Создаём публикацию
        publication = Publication(
            content_id=content.id,
            account_id=account.id,
            status="pending",
            scheduled_at=scheduled_for
        )
        db.add(publication)
        
        # Создаём задачу
        task = ScheduledTask(
            task_type="publish_content",
            content_id=content.id,
            account_id=account.id,
            scheduled_at=scheduled_for,
            payload={
                "publication_id": str(publication.id)
            }
        )
        db.add(task)
        
        publications.append(publication)
    
    content.status = "scheduled"
    content.scheduled_for = scheduled_for
    
    db.commit()
    
    return {
        "message": f"Контент запланирован на {scheduled_for}",
        "publications_count": len(publications)
    }


# ============================================
# ФАЙЛ: backend/app/api/v1/publications.py
# ============================================

"""
Эндпоинты для работы с публикациями.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models import User, Publication, Content, Account

router = APIRouter()


@router.get("/")
async def get_publications(
    account_id: UUID = None,
    content_id: UUID = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка публикаций"""
    query = db.query(Publication)
    
    if account_id:
        query = query.filter(Publication.account_id == account_id)
    if content_id:
        query = query.filter(Publication.content_id == content_id)
    if status:
        query = query.filter(Publication.status == status)
    
    query = query.order_by(Publication.created_at.desc())
    
    publications = query.offset(skip).limit(limit).all()
    
    return publications


@router.post("/{publication_id}/publish")
async def publish_now(
    publication_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Немедленная публикация"""
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Публикация не найдена"
        )
    
    if publication.status not in ["pending", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Публикация в статусе {publication.status}, нельзя опубликовать"
        )
    
    publication.status = "publishing"
    db.commit()
    
    # Запускаем публикацию в фоне
    background_tasks.add_task(
        _publish_task,
        publication_id=str(publication.id)
    )
    
    return {"message": "Публикация запущена", "publication_id": str(publication_id)}


async def _publish_task(publication_id: str):
    """Фоновая задача публикации"""
    from app.db.session import SessionLocal
    from app.services.social.publisher import SocialPublisher
    from datetime import datetime
    
    db = SessionLocal()
    try:
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if not publication:
            return
        
        content = publication.content
        account = publication.account
        
        publisher = SocialPublisher()
        
        result = await publisher.publish(
            platform=account.platform,
            account_credentials=account.credentials,
            content={
                "type": content.type,
                "caption": content.caption,
                "script": content.script,
                "media_url": content.media_url,
                "hashtags": content.hashtags,
                "link_url": content.link_url
            },
            proxy=account.proxy
        )
        
        if result["success"]:
            publication.status = "published"
            publication.platform_post_id = result.get("post_id")
            publication.platform_url = result.get("url")
            publication.published_at = datetime.utcnow()
            
            # Обновляем счётчик постов аккаунта
            account.posts_today += 1
            account.total_posts += 1
            account.last_posted_at = datetime.utcnow()
        else:
            publication.status = "failed"
            publication.error_message = result.get("error")
            publication.retry_count += 1
        
        db.commit()
        
    except Exception as e:
        publication = db.query(Publication).filter(Publication.id == publication_id).first()
        if publication:
            publication.status = "failed"
            publication.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.delete("/{publication_id}")
async def delete_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление публикации"""
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Публикация не найдена"
        )
    
    db.delete(publication)
    db.commit()
    
    return {"message": "Публикация удалена"}


# ============================================
# ФАЙЛ: backend/app/api/v1/affiliates.py
# ============================================

"""
Эндпоинты для работы с партнёрскими программами.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

router = APIRouter()

# Pydantic схемы для партнёрок
class AffiliateCreate(BaseModel):
    niche_id: Optional[UUID] = None
    name: str
    platform: str
    url: str
    affiliate_link: Optional[str] = None
    commission_type: str
    commission_rate: Decimal
    avg_order_value: Optional[Decimal] = None
    cookie_duration_days: Optional[int] = 30

class AffiliateResponse(BaseModel):
    id: UUID
    niche_id: Optional[UUID]
    name: str
    platform: str
    url: str
    affiliate_link: Optional[str]
    commission_type: str
    commission_rate: Decimal
    avg_order_value: Optional[Decimal]
    epc: Optional[Decimal]
    cookie_duration_days: int
    status: str
    
    class Config:
        from_attributes = True


from app.api.deps import get_db, get_current_user
from app.models import User, Affiliate


@router.get("/", response_model=List[AffiliateResponse])
async def get_affiliates(
    niche_id: UUID = None,
    platform: str = None,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка партнёрок"""
    query = db.query(Affiliate)
    
    if niche_id:
        query = query.filter(Affiliate.niche_id == niche_id)
    if platform:
        query = query.filter(Affiliate.platform == platform)
    if status:
        query = query.filter(Affiliate.status == status)
    
    return query.all()


@router.post("/", response_model=AffiliateResponse)
async def create_affiliate(
    affiliate_data: AffiliateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Добавление партнёрской программы"""
    affiliate = Affiliate(**affiliate_data.model_dump())
    db.add(affiliate)
    db.commit()
    db.refresh(affiliate)
    
    return affiliate


@router.get("/{affiliate_id}", response_model=AffiliateResponse)
async def get_affiliate(
    affiliate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение партнёрки по ID"""
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    
    if not affiliate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Партнёрка не найдена"
        )
    
    return affiliate


@router.delete("/{affiliate_id}")
async def delete_affiliate(
    affiliate_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление партнёрки"""
    affiliate = db.query(Affiliate).filter(Affiliate.id == affiliate_id).first()
    
    if not affiliate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Партнёрка не найдена"
        )
    
    db.delete(affiliate)
    db.commit()
    
    return {"message": "Партнёрка удалена"}


# ============================================
# ФАЙЛ: backend/app/api/v1/leads.py
# ============================================

"""
Эндпоинты для работы с лидами.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class LeadResponse(BaseModel):
    id: UUID
    telegram_user_id: Optional[int]
    telegram_username: Optional[str]
    email: Optional[str]
    name: Optional[str]
    funnel_stage: str
    lead_score: int
    source_platform: Optional[str]
    last_interaction_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


from app.api.deps import get_db, get_current_user
from app.models import User, Lead


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    funnel_stage: str = None,
    source_platform: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка лидов"""
    query = db.query(Lead)
    
    if funnel_stage:
        query = query.filter(Lead.funnel_stage == funnel_stage)
    if source_platform:
        query = query.filter(Lead.source_platform == source_platform)
    
    query = query.order_by(Lead.created_at.desc())
    
    return query.offset(skip).limit(limit).all()


@router.get("/funnel-stats")
async def get_funnel_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Статистика воронки"""
    from sqlalchemy import func
    
    stats = db.query(
        Lead.funnel_stage,
        func.count(Lead.id).label('count')
    ).group_by(Lead.funnel_stage).all()
    
    result = {stage.value: 0 for stage in Lead.funnel_stage.type.enums}
    for stage, count in stats:
        result[stage] = count
    
    total = sum(result.values())
    conversion_rate = (result.get('converted', 0) / total * 100) if total > 0 else 0
    
    return {
        "stages": result,
        "total": total,
        "conversion_rate": round(conversion_rate, 2)
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение лида по ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Лид не найден"
        )
    
    return lead


@router.patch("/{lead_id}/stage")
async def update_lead_stage(
    lead_id: UUID,
    new_stage: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Изменение стадии воронки"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Лид не найден"
        )
    
    lead.funnel_stage = new_stage
    db.commit()
    
    return {"message": "Стадия обновлена", "new_stage": new_stage}
