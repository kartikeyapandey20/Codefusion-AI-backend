from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.config import settings

DB_HOST = settings.DB_HOST
DB_USER = settings.DB_USER
DB_NAME = settings.DB_NAME
DB_PASS = settings.DB_PASS

# Sync URL
SYNC_DB_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

# Async URL
ASYNC_DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

# Sync engine + session
sync_engine = create_engine(SYNC_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async engine + session
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Shared base
Base = declarative_base()
