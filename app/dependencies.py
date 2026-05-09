from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.exceptions import InvalidCredentialsError, InsufficientPermissionsError
from app.models.user import User
from app.repositories import user_repository
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    username: str | None = payload.get("username")
    if not username:
        raise InvalidCredentialsError()
    user = user_repository.get_by_username(db, username)
    if not user:
        raise InvalidCredentialsError()
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin():
        raise InsufficientPermissionsError()
    return current_user