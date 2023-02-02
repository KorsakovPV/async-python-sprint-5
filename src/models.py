import uuid

from sqlalchemy import (TIMESTAMP, VARCHAR, Boolean, Column, Enum, ForeignKey,
                        String, func, sql, text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base  # type: ignore
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID, \
    SQLAlchemyAccessTokenDatabase
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from datetime import datetime
from fastapi_users_db_sqlalchemy.generics import GUID, TIMESTAMPAware, now_utc

from db.db import get_session

Base = declarative_base()


class BaseModel(Base):  # type: ignore
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at = Column(TIMESTAMPAware(timezone=True), server_default=sql.func.current_timestamp())
    created_by = Column(String(255), nullable=True)
    updated_at = Column(TIMESTAMPAware(timezone=True), onupdate=func.current_timestamp())
    updated_by = Column(String(255), nullable=True)


class FileModel(BaseModel):
    __tablename__ = "file_model"
    name = Column(String(100), nullable=False)
    path = Column(String(255), nullable=False)
    size = Column(Integer(), nullable=False)
    is_downloadable = Column(Boolean(), default=True, nullable=False)

from fastapi_users_db_sqlalchemy.generics import GUID

UUID_ID = uuid.UUID


class User(Base):
    __tablename__ = "user"
    id: UUID_ID = Column(GUID, primary_key=True, default=uuid.uuid4)
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    created_at: datetime = Column(
        TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc
    )


class AccessToken(Base):
    __tablename__ = "accesstoken"
    token: str = Column(String(length=43), primary_key=True)
    created_at: datetime = Column(
        TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc
    )
    user_id = Column(GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False)


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
        session: AsyncSession = Depends(get_session),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
