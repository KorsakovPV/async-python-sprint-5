from typing import Any

from pydantic import BaseSettings, PostgresDsn, validator

SENTRY_DSN_TEST = ''


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Async python sprint-5'

    DB_HOST: str = 'localhost'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'postgres'
    DB_NAME: str = 'async_python_sprint_5'
    DB_PORT: int = 5432
    DB_URL: PostgresDsn | str = ''

    TEST_DB_HOST: str = 'localhost'
    TEST_DB_USER: str = 'postgres'
    TEST_DB_PASSWORD: str = 'postgres'
    TEST_DB_NAME: str = 'test_async_python_sprint_5'
    TEST_DB_PORT: int = 5432
    TEST_DB_URL: PostgresDsn | str = ''

    API_HOST: str = '0.0.0.0'
    API_PORT: int = 8000

    FILE_FOLDER: str = 'files/'

    @validator('DB_URL', pre=True)
    def assemble_db_connection(cls, value: str | None, values: dict[str, Any]) -> Any:
        if isinstance(value, str) and value != '':
            return value
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('DB_USER'),
            password=values.get('DB_PASSWORD'),
            host=values.get('DB_HOST'),
            port=str(values.get('DB_PORT')),
            path=f'/{values.get("DB_NAME") or ""}',
        )

    @validator('TEST_DB_URL', pre=True)
    def assemble_test_db_connection(cls, value: str | None, values: dict[str, Any]) -> Any:
        if isinstance(value, str) and value != '':
            return value
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values.get('TEST_DB_USER'),
            password=values.get('TEST_DB_PASSWORD'),
            host=values.get('TEST_DB_HOST'),
            port=str(values.get('TEST_DB_PORT')),
            path=f'/{values.get("TEST_DB_NAME") or ""}',
        )


settings = Settings()
