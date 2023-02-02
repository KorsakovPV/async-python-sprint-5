import datetime
from pathlib import PurePath

from fastapi import UploadFile
from pydantic import BaseModel
from pydantic.types import UUID


# Shared properties
class FileBase(BaseModel):
    id: UUID
    name: str
    path: str
    size: int
    is_downloadable: bool
    # created_at: int | None
    # created_by: UUID
    # updated_at: int | None
    # updated_by: UUID | None


# Properties to receive on entity creation
class FileCreate(FileBase):
    # created_at: int | None
    created_by: UUID
    # updated_at: int | None
    # updated_by: UUID | None
    pass


# Properties to receive on entity update
class FileUpdate(FileBase):
    # created_at: int | None
    # created_by: UUID
    # updated_at: datetime.datetime | None
    updated_by: UUID | None


# Properties shared by models stored in DB
class FileInDBBase(FileBase):
    # id: UUID
    # name: str
    # path: str
    # size: int
    # is_downloadable: bool

    created_at: datetime.datetime | None
    created_by: UUID
    updated_at: datetime.datetime | None
    updated_by: UUID | None

    class Config:
        orm_mode = True


# # Properties to return to client
# class File(FileInDBBase):
#     pass
#
#
# # Properties stored in DB
# class FileInDB(FileInDBBase):
#     pass
