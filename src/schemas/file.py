from fastapi import UploadFile
from pydantic import BaseModel
from pydantic.types import UUID


# Shared properties
class FileBase(BaseModel):
    path: str
    user_id: UUID


# Properties to receive on entity creation
class FileCreate(FileBase):
    name: str | None


# Properties to receive on entity update
class FileUpdate(FileBase):
    name: str | None


# Properties shared by models stored in DB
class FileInDBBase(FileBase):
    id: int
    name: str | None
    file: UploadFile

    class Config:
        orm_mode = True


# Properties to return to client
class File(FileInDBBase):
    pass


# Properties stored in DB
class FileInDB(FileInDBBase):
    pass
