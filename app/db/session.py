from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

_engine = create_async_engine(
    url=settings.async_database_url,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=_engine,
    autoflush=False,
    # autocommit=False,
    expire_on_commit=False
)
