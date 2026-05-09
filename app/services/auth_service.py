import logging

from sqlalchemy.orm import Session

from app.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth_schema import UserRegisterRequest
from app.security import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)


def register_user(db: Session, request: UserRegisterRequest) -> User:
    try:
        user = user_repository.create(
            db=db,
            username=request.username,
            hashed_password=hash_password(request.password),
            role=request.role,
        )
    except UserAlreadyExistsError:
        logger.warning("Registration failed, username taken: username=%s", request.username)
        raise
    logger.info("User registered: id=%s username=%s role=%s", user.id, user.username, user.role)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Failed login attempt: username=%s", username)
        raise InvalidCredentialsError()
    token = create_access_token({"username": user.username, "role": user.role})
    logger.info("User logged in: username=%s", user.username)
    return token
