# import shutil
#
# from fastapi import APIRouter, Depends, UploadFile
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette.responses import FileResponse
#
# from src.config.config import settings
# from src.db.db import get_session
# from src.helpers.raising_http_excp import RaiseHttpException
# from src.helpers.utils import calculate_file_size
# from src.models.user import User
# from src.schemas.file import FileCreate
# from src.services.file import file_crud
# from src.services.user_manager import current_active_user
#
# storage_router = APIRouter(prefix='/file', tags=['File storage'])
#
#
# @storage_router.post('', status_code=201, response_model=FileCreate)
# async def save_file(
#         file: UploadFile,
#         name: str,
#         db: AsyncSession = Depends(get_session),
#         user: User = Depends(current_active_user)
# ) -> FileCreate:
#     file_path = f'{app_settings.FILE_FOLDER}{file.filename}'
#     with open(file_path, "wb") as f:
#         shutil.copyfileobj(file.file, f)
#
#     obj_in = FileCreate(path=file_path, name=name, user_id=user.id)
#     await file_crud.create(db=db, obj_in=obj_in)
#     return obj_in
#
#
# @storage_router.get('/list', status_code=200)
# async def get_files(
#         db: AsyncSession = Depends(get_session),
#         user: User = Depends(current_active_user)
# ):
#
#     query = await file_crud.get_multi(db=db, user_id=str(user.id))
#     RaiseHttpException.check_is_exist(query)
#
#     return query
#
#
# @storage_router.get('/download', status_code=200)
# async def download_file(
#         file_id: int | None = None,
#         file_name: str | None = None,
#         db: AsyncSession = Depends(get_session),
#         user: User = Depends(current_active_user)
# ):
#     RaiseHttpException.check_params_isnt_none(file_id=file_id, file_name=file_name)
#
#     if file_id:
#         file_model = await file_crud.get(db=db, id_=file_id)
#         RaiseHttpException.check_is_exist(file_model)
#     else:
#         query = await file_crud.get_multi(db=db, name=file_name)
#         RaiseHttpException.check_is_one(query)
#         file_model = query[0]
#
#     return FileResponse(file_model.path, media_type='application/octet-stream', filename=file_model.name)
#
#
# @storage_router.get('/usage_memory', status_code=200)
# async def usage_memory(
#         db: AsyncSession = Depends(get_session),
#         user: User = Depends(current_active_user)
# ):
#
#     query = await file_crud.get_multi(db=db, user_id=str(user.id))
#     RaiseHttpException.check_is_exist(query)
#
#     return {'files': calculate_file_size(query)}
#
