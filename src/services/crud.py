from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base
from services.base import Repository

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(Repository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self._model = model

    async def get(self, db: AsyncSession, id_: int) -> Optional[ModelType]:
        statement = select(self._model).where(self._model.id == id_)
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip=0, limit=100, **kwargs
    ) -> List[ModelType]:
        statement = select(self._model)
        filters = [getattr(self._model, key) == value for key, value in kwargs.items()]
        if filters:
            statement = statement.where(and_(*filters))
        statement = statement.offset(skip).limit(limit)
        # statement = select(self._model).filter().offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self._model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:

        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data_without_none = {k: v for k, v in obj_in_data.items() if v is not None}

        await db.execute(
            update(self._model).
            where(self._model.id == db_obj.id).
            values(obj_in_data_without_none)
        )
        await db.commit()
        return db_obj
