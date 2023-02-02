from api.v1 import base, auth
from config.config import settings
from config.logger import logger

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    default_response_class=ORJSONResponse,
)

app.include_router(auth.api_auth_router)
app.include_router(base.api_router, prefix='/api/v1')

if __name__ == '__main__':
    logger.info('Server started.')
    uvicorn.run(
        'main:app',
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
