from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.orm_models import UserORM
from app.exceptions import UserAlreadyExistsError
from app.models.user import User


def _to_domain(orm_user: UserORM) -> User:
    return User(
        id=orm_user.id,
        username=orm_user.username,
        hashed_password=orm_user.hashed_password,
        role=orm_user.role,
    )


def get_by_username(db: Session, username: str) -> User | None:
    orm_user = (
        db.query(UserORM)
        .filter(func.lower(UserORM.username) == username.lower())
        .first()
    )
    return _to_domain(orm_user) if orm_user else None


def create(db: Session, username: str, hashed_password: str, role: str) -> User:
    if get_by_username(db, username):
        raise UserAlreadyExistsError(username)
    orm_user = UserORM(username=username, hashed_password=hashed_password, role=role)
    db.add(orm_user)
    db.commit()
    db.refresh(orm_user)
    return _to_domain(orm_user)