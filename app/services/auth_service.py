import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth_schema import UserRegisterRequest
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)


async def register_user(db: AsyncSession, request: UserRegisterRequest) -> User:
    try:
        user = await user_repository.create(
            db=db,
            username=request.username,
            hashed_password=await asyncio.to_thread(hash_password, request.password),
            role=request.role,
        )
    except UserAlreadyExistsError:
        logger.warning("Registration failed, username taken: username=%s", request.username)
        raise
    logger.info("User registered: id=%s username=%s role=%s", user.id, user.username, user.role)
    return user


async def login_user(db: AsyncSession, username: str, password: str) -> str:
    user = await user_repository.get_by_username(db, username)
    if not user or not await asyncio.to_thread(verify_password, password, user.hashed_password):
        logger.warning("Failed login attempt: username=%s", username)
        raise InvalidCredentialsError()
    token = create_access_token({"username": user.username, "role": user.role})
    logger.info("User logged in: username=%s", user.username)
    return token