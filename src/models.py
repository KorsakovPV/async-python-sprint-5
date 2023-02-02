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

from db.db import get_session, Base


# Base = declarative_base()


class BaseModel(Base):  # type: ignore
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    created_by = Column(String(255), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())
    updated_by = Column(String(255), nullable=True)


class FileModel(BaseModel):
    __tablename__ = "file_model"
    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    path = Column(String(255), nullable=False)
    # created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())

    # user_id = Column(UUID, ForeignKey("user.id"))


class User(SQLAlchemyBaseUserTableUUID, Base):
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    pass
    # files = relationship("FileModel", backref="file_model")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    created_at = Column(TIMESTAMP(timezone=True), server_default=sql.func.current_timestamp())
    pass


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
        session: AsyncSession = Depends(get_session),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
