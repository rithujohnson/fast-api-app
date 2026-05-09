from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(
        select(UserORM).where(func.lower(UserORM.username) == username.lower())
    )
    orm_user = result.scalar_one_or_none()
    return _to_domain(orm_user) if orm_user else None


async def create(db: AsyncSession, username: str, hashed_password: str, role: str) -> User:
    if await get_by_username(db, username):
        raise UserAlreadyExistsError(username)
    orm_user = UserORM(username=username, hashed_password=hashed_password, role=role)
    db.add(orm_user)
    await db.commit()
    await db.refresh(orm_user)
    return _to_domain(orm_user)