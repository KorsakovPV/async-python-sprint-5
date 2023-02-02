import uuid

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from fastapi_users_db_sqlalchemy.generics import GUID, TIMESTAMPAware, now_utc
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func, sql
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base  # type: ignore

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
    __tablename__ = "files"
    name = Column(String(100), nullable=False)
    path = Column(String(255), nullable=False)
    size = Column(Integer(), nullable=False)
    is_downloadable = Column(Boolean(), default=True, nullable=False)


class User(Base):  # type: ignore
    __tablename__ = "user"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc)


class AccessToken(Base):  # type: ignore
    __tablename__ = "accesstoken"
    token = Column(String(length=43), primary_key=True)
    created_at = Column(TIMESTAMPAware(timezone=True), index=True, nullable=False, default=now_utc)
    user_id = Column(GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False)


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
        session: AsyncSession = Depends(get_session),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
