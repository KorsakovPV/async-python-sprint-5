import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from config.config import settings
from config.logger import logger
from db.db import get_session
from models import User
from schemas.file import FileCreate, FileInDBBase
from services.file import file_crud
from services.user_manager import current_active_user
from argparse import ArgumentParser
from pathlib import Path
import aiofiles
from fastapi import HTTPException
from starlette import status

from config.constants import APIAnswers

parser = ArgumentParser(
    description="Copying files using asynchronous io API"
)
parser.add_argument("source", type=Path)
parser.add_argument("dest", type=Path)
parser.add_argument("--chunk-size", type=int, default=65535)

storage_router = APIRouter(prefix='/file', tags=['File storage'])


@storage_router.post('', status_code=status.HTTP_201_CREATED, response_model=FileInDBBase)
async def save_file(
        in_file: UploadFile,
        path: str,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
) -> FileCreate:
    """
    Create an item with all the information:

    - **in_file**: File for save
    - **path**: Additional information about the file. Path
    """
    logger.info('Save file.')
    id_ = uuid.uuid4()
    filename = in_file.filename
    out_file_path = rf'{settings.FILE_FOLDER}{id_}'
    file_path = rf'{path}/{filename}'
    size = 0

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        while content := await in_file.read(2 ** 16):
            size += len(content)  # async read chunk
            await out_file.write(content)  # async write chunk

    obj_in = FileCreate(
        id=id_,
        path=file_path,
        name=in_file.filename,
        size=size,
        created_by=user.id,
        is_downloadable=True
    )
    db_obj = await file_crud.create(db=db, obj_in=obj_in)
    return db_obj


@storage_router.get('/list', status_code=status.HTTP_200_OK, response_model=list[FileInDBBase])
async def get_files(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    """
    Get items with all the information:
    """
    logger.info('Get file.')
    query = await file_crud.get_multi(db=db, created_by=str(user.id))
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=APIAnswers.NOT_FOUND
        )

    return query


@storage_router.get('/download', status_code=status.HTTP_200_OK)
async def download_file(
        id_: uuid.UUID,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    """
    Download file:

    - **id_**: uuid item
    """
    logger.info(f'Download file {id_}.')
    query = await file_crud.get_multi(db=db, id=id_, is_downloadable=True)

    if isinstance(query, list) and len(query) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=APIAnswers.MANY_MATCHES
        )

    file_model = query[0]

    return FileResponse(
        rf'{settings.FILE_FOLDER}{id_}',
        media_type='application/octet-stream',
        filename=file_model.name
    )


@storage_router.get('/usage_memory', status_code=status.HTTP_200_OK)
async def usage_memory(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    """
    Get usage memory by files:
    """
    logger.info('Get usage memory.')
    return await file_crud.usage_memory(db=db, created_by=str(user.id))
