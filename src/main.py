import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import base
from config.config import settings
from config.logger import logger
# from middleware.blocked_host import BlockedHostMiddleware


import logging
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

# from src.api.v1.file_storage import storage_router
# from src.api.v1.ping import ping_router
# from src.core.config import app_settings
# from src.core.logger import LOGGING
from schemas.user import UserRead, UserCreate, UserUpdate
from services.user_manager import fastapi_users_router, auth_backend

app = FastAPI(
    title=settings.PROJECT_NAME,
    default_response_class=ORJSONResponse,
)

app.include_router(
    fastapi_users_router.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users_router.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_router.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_router.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users_router.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(base.api_router, prefix='/api/v1')

# app.add_middleware(
#     BlockedHostMiddleware, blocked_hosts=settings.blocked_hosts
# )

if __name__ == '__main__':
    logger.info('Server started.')
    uvicorn.run(
        'main:app',
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
