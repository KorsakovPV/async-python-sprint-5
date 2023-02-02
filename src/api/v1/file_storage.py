import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from config.config import settings
from db.db import get_session
from helpers.raising_http_excp import RaiseHttpException
from helpers.utils import calculate_file_size
from models import User
from schemas.file import FileCreate, FileInDBBase
from services.file import file_crud
from services.user_manager import current_active_user

storage_router = APIRouter(prefix='/file', tags=['File storage'])


@storage_router.post('', status_code=201, response_model=FileInDBBase)
async def save_file(
        file: UploadFile,
        path: str,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
) -> FileCreate:
    id = uuid.uuid4()
    filename = file.filename
    file_path = rf'{path}/{filename}'
    with open(rf'{settings.FILE_FOLDER}{id}', "wb") as f:
        shutil.copyfileobj(file.file, f)
    size = os.path.getsize(rf'{settings.FILE_FOLDER}{id}')

    obj_in = FileCreate(
        id=id,
        path=file_path,
        name=file.filename,
        size=size,
        created_by=user.id,
        is_downloadable=True
    )
    db_obj = await file_crud.create(db=db, obj_in=obj_in)
    return db_obj


@storage_router.get('/list', status_code=200, response_model=List[FileInDBBase])
async def get_files(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    query = await file_crud.get_multi(db=db, created_by=str(user.id))
    RaiseHttpException.check_is_exist(query)

    return query


@storage_router.get('/download', status_code=200)
async def download_file(
        id: uuid.UUID,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    query = await file_crud.get_multi(db=db, id=id, is_downloadable=True)
    RaiseHttpException.check_is_one(query)
    file_model = query[0]

    return FileResponse(
        rf'{settings.FILE_FOLDER}{id}',
        media_type='application/octet-stream',
        filename=file_model.name
    )


@storage_router.get('/usage_memory', status_code=200)
async def usage_memory(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    query = await file_crud.get_multi(db=db, created_by=str(user.id))
    RaiseHttpException.check_is_exist(query)

    return {'files': calculate_file_size(query)}
