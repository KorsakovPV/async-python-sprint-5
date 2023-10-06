import datetime
from pydantic import BaseModel
from pydantic.types import UUID


class FileBase(BaseModel):
    id: UUID
    name: str
    path: str
    size: int
    is_downloadable: bool


class FileCreate(FileBase):
    created_by: UUID


class FileUpdate(FileBase):
    updated_by: UUID


class FileInDBBase(FileBase):
    created_at: datetime.datetime | None
    created_by: UUID
    updated_at: datetime.datetime | None
    updated_by: UUID | None

    class Config:
        orm_mode = True
