from schemas.file import FileCreate


from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import FileModel


class RepositoryFile:

    async def get(self, db: AsyncSession, id_: int) -> FileModel | None:
        statement = select(FileModel).where(FileModel.id == id_)  # type: ignore
        results = await db.execute(statement=statement)
        return results.scalar_one_or_none()

    async def get_multi(
            self, db: AsyncSession, *, skip=0, limit=100, **kwargs
    ) -> list[FileModel]:
        statement = select(FileModel)  # type: ignore
        if filters := await self.apply_filters(kwargs):
            statement = statement.where(and_(*filters))
        statement = statement.offset(skip).limit(limit)
        results = await db.execute(statement=statement)
        return results.scalars().all()

    async def usage_memory(
            self, db: AsyncSession, **kwargs
    ) -> list[FileModel]:
        statement = select(func.sum(FileModel.size))  # type: ignore
        if filters := await self.apply_filters(kwargs):
            statement = statement.where(and_(*filters))
        results = await db.execute(statement=statement)
        return results.scalars().one()

    async def apply_filters(self, kwargs):
        filters = [getattr(FileModel, key) == value for key, value in kwargs.items()]
        return filters

    async def create(self, db: AsyncSession, *, obj_in: FileCreate) -> FileModel:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = FileModel(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


file_crud = RepositoryFile()
