from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.config import settings


def create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DB_URL,
        echo=True,
        future=True
    )


def create_sessionmaker(bind_engine: AsyncEngine | AsyncConnection) -> sessionmaker:
    return sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


engine = create_engine()
async_session = create_sessionmaker(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
