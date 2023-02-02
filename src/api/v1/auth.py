from fastapi import APIRouter, Depends
from schemas.user import UserRead, UserCreate, UserUpdate
from services.user_manager import fastapi_users_router, auth_backend

api_auth_router = APIRouter()

api_auth_router.include_router(
    fastapi_users_router.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
api_auth_router.include_router(
    fastapi_users_router.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
api_auth_router.include_router(
    fastapi_users_router.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
api_auth_router.include_router(
    fastapi_users_router.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
api_auth_router.include_router(
    fastapi_users_router.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)