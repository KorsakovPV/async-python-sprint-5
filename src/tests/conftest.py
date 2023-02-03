import asyncio
from dataclasses import dataclass
from functools import cached_property
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeMeta

from config.config import settings
from db.db import create_sessionmaker, get_session
from main import app
from models import Base, get_user_db, FileModel

import contextlib

from schemas.user import UserCreate
from services.user_manager import get_user_manager, auth_backend


async def get_test_session_for_dependency_overrides() -> AsyncSession:
    engine = get_test_engine()
    async_session = create_sessionmaker(engine)
    async with async_session() as session:
        yield session


get_async_session_context = contextlib.asynccontextmanager(
    get_test_session_for_dependency_overrides)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


@pytest.fixture(scope="session")
async def user():
    email, password, is_superuser = 'test2@2test.ru', 'test_password', False
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(
                    UserCreate(
                        email=email, password=password, is_superuser=is_superuser
                    )
                )
                yield user


@pytest.fixture(scope="session")
async def token(user):
    token = await auth_backend.get_strategy().write_token(user)
    yield {
        'access_token': token,
        'token_type': 'Bearer'
    }


@pytest.fixture(scope="session")
async def headers_with_token(user):
    token = await auth_backend.get_strategy().write_token(user)
    yield {'Authorization': f'Bearer {token}'}


metadata = Base.metadata


@pytest.fixture(scope="session")
async def test_app(_create_db):
    app.dependency_overrides[get_session] = get_test_session_for_dependency_overrides
    yield app


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@dataclass
class DBUtils:
    url: str

    @cached_property
    def postgres_engine(self) -> AsyncEngine:
        url_params = self._parsed_url._asdict()
        url_params['database'] = 'postgres'
        url_with_postgres_db = URL.create(**url_params)
        return create_async_engine(url_with_postgres_db, isolation_level='AUTOCOMMIT')

    @cached_property
    def db_engine(self) -> AsyncEngine:
        return create_async_engine(
            self.url,
            isolation_level='AUTOCOMMIT',
        )

    async def create_database(self) -> None:
        query = text(f'CREATE DATABASE {self._parsed_url.database} ENCODING "utf8";')
        async with self.postgres_engine.connect() as conn:
            await conn.execute(query)

    async def create_extensions(self) -> None:
        query = text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        async with self.db_engine.begin() as conn:
            await conn.execute(query)

    async def create_tables(self, base: DeclarativeMeta) -> None:
        async with self.db_engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

    async def drop_database(self) -> None:
        query = text(f'DROP DATABASE {self._parsed_url.database} WITH (FORCE);')
        async with self.postgres_engine.begin() as conn:
            await conn.execute(query)

    async def database_exists(self) -> bool:
        query = text('SELECT 1 FROM pg_database WHERE datname = :database')
        async with self.postgres_engine.connect() as conn:
            query_result = await conn.execute(query, {'database': self._parsed_url.database})
        result = query_result.scalar()
        return bool(result)

    @cached_property
    def _parsed_url(self) -> URL:
        return make_url(self.url)


async def create_db(url: str, base: DeclarativeMeta) -> None:
    db_utils = DBUtils(url=url)

    try:
        if await db_utils.database_exists():
            await db_utils.drop_database()

        await db_utils.create_database()
        await db_utils.create_extensions()
        await db_utils.create_tables(base)
    finally:
        await db_utils.postgres_engine.dispose()
        await db_utils.db_engine.dispose()


async def drop_db(url: str, base: DeclarativeMeta) -> None:
    db_utils = DBUtils(url=url)

    await db_utils.drop_database()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def _create_db() -> None:
    yield await create_db(url=settings.TEST_DB_URL, base=Base)
    await drop_db(url=settings.TEST_DB_URL, base=Base)


@pytest.fixture(scope="session")
def engine():
    return get_test_engine()


def get_test_engine() -> AsyncEngine:
    db_utils = DBUtils(url=settings.TEST_DB_URL)

    return db_utils.db_engine


@pytest_asyncio.fixture(scope="session")
async def get_test_session(engine) -> AsyncSession:
    async_session = create_sessionmaker(engine)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope='session')
async def file(get_test_session, user) -> AsyncGenerator[FileModel, None]:
    file_ = FileModel(
        name='name.jpg',
        path='path_folder',
        size=100,
        is_downloadable=True,
        created_by=str(user.id)
    )
    get_test_session.add(file_)

    statement = select(FileModel)
    await get_test_session.execute(statement=statement)

    yield file_

#############################################################
# @pytest_asyncio.fixture(scope='session')
# async def url_items(get_test_session) -> AsyncGenerator[UrlModel, None]:
#     url1 = UrlModel(
#         url='http://httpbin.org/uuid',
#         is_delete=False,
#     )
#     url2 = UrlModel(
#         url='https://www.google.ru/',
#         is_delete=True,
#     )
#     get_test_session.add_all([url1, url2])
#
#     statement = select(UrlModel)
#     await get_test_session.execute(statement=statement)
#
#     yield [url1, url2]
#
#
# @pytest_asyncio.fixture(scope='session')
# async def history_items(url_items, get_test_session) -> AsyncGenerator[HistoryModel, None]:
#     url_obj, _ = url_items
#     history = HistoryModel(
#         url_id=url_obj.id,
#         method='GET',
#         domen='',
#     )
#     get_test_session.add(history)
#
#     statement = select(HistoryModel)
#     await get_test_session.execute(statement=statement)
#
#     yield history
#
#
# @pytest_asyncio.fixture()
# def new_test_url_schema():
#     return urls_scheme.UrlCreateSchema(
#         url=f'www.google.com/{str(uuid.uuid4())}'
#     )
