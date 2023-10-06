import datetime
import sys
import asyncpg  # type: ignore

from fastapi import APIRouter, Depends
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from starlette import status

from api.v1 import file_storage
from config.logger import logger
from db.db import get_session

api_router = APIRouter()
api_router.include_router(file_storage.storage_router)


@api_router.get('/', status_code=status.HTTP_200_OK)
async def root_handler():
    return {'version': 'v1'}


@api_router.get('/ping', status_code=status.HTTP_200_OK)
async def ping(db: Session = Depends(get_session)):
    logger.info('Test ping.')
    db_response_time = await ping_db(db)
    return {
        'api': 'v1',
        'python': sys.version_info,
        'db': db_response_time
    }


async def ping_db(db):
    logger.info('Test ping dependent services.')
    statement = text('SELECT version();')
    start = datetime.datetime.now()
    try:
        await db.execute(statement)
        ping_db_time = datetime.datetime.now() - start
        return ping_db_time
    except (exc.SQLAlchemyError, asyncpg.PostgresError) as err:
        return err.message
