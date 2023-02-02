import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import base
from config.config import settings
from config.logger import logger
# from middleware.blocked_host import BlockedHostMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    default_response_class=ORJSONResponse,
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
