from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.orm_models import CategoryORM, ItemORM
from app.exceptions import DuplicateItemNameError, InvalidCategoryError, ItemNotFoundError
from app.models.category import Category
from app.models.item import Item


def _to_domain(orm_item: ItemORM) -> Item:
    return Item(
        id=orm_item.id,
        name=orm_item.name,
        price=orm_item.price,
        category=Category(orm_item.category.name),
        description=orm_item.description,
    )


async def _get_category_orm(db: AsyncSession, category_name: str) -> CategoryORM:
    result = await db.execute(
        select(CategoryORM).where(func.lower(CategoryORM.name) == category_name.lower())
    )
    category_orm = result.scalar_one_or_none()
    if not category_orm:
        raise InvalidCategoryError(category_name)
    return category_orm


async def get_all(
    db: AsyncSession,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> list[Item]:
    query = select(ItemORM).options(selectinload(ItemORM.category))
    if category is not None:
        query = query.join(ItemORM.category).where(
            func.lower(CategoryORM.name) == category.lower()
        )
    if min_price is not None:
        query = query.where(ItemORM.price >= min_price)
    if max_price is not None:
        query = query.where(ItemORM.price <= max_price)
    if sort_by == "name":
        col = ItemORM.name
    elif sort_by == "price":
        col = ItemORM.price
    else:
        col = ItemORM.id
    query = query.order_by(col.desc() if order == "desc" else col.asc())
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return [_to_domain(item) for item in result.scalars().all()]


async def get_by_id(db: AsyncSession, item_id: int) -> Item:
    result = await db.execute(
        select(ItemORM).options(selectinload(ItemORM.category)).where(ItemORM.id == item_id)
    )
    orm_item = result.scalar_one_or_none()
    if not orm_item:
        raise ItemNotFoundError(item_id)
    return _to_domain(orm_item)


async def create(db: AsyncSession, name: str, price: float, category: str, description: str | None) -> Item:
    existing = await db.execute(
        select(ItemORM).where(func.lower(ItemORM.name) == name.lower())
    )
    if existing.scalar_one_or_none():
        raise DuplicateItemNameError(name)
    category_orm = await _get_category_orm(db, category)
    orm_item = ItemORM(name=name, price=price, category_id=category_orm.id, description=description)
    db.add(orm_item)
    await db.commit()
    await db.refresh(orm_item)
    result = await db.execute(
        select(ItemORM).options(selectinload(ItemORM.category)).where(ItemORM.id == orm_item.id)
    )
    return _to_domain(result.scalar_one())


async def update(db: AsyncSession, item_id: int, name: str, price: float, category: str, description: str | None) -> Item:
    result = await db.execute(
        select(ItemORM).where(ItemORM.id == item_id)
    )
    orm_item = result.scalar_one_or_none()
    if not orm_item:
        raise ItemNotFoundError(item_id)
    duplicate = await db.execute(
        select(ItemORM).where(func.lower(ItemORM.name) == name.lower(), ItemORM.id != item_id)
    )
    if duplicate.scalar_one_or_none():
        raise DuplicateItemNameError(name)
    category_orm = await _get_category_orm(db, category)
    orm_item.name = name
    orm_item.price = price
    orm_item.category_id = category_orm.id
    orm_item.description = description
    await db.commit()
    result = await db.execute(
        select(ItemORM).options(selectinload(ItemORM.category)).where(ItemORM.id == item_id)
    )
    return _to_domain(result.scalar_one())


async def patch(db: AsyncSession, item_id: int, name: str | None, price: float | None, category: str | None, description: str | None) -> Item:
    result = await db.execute(
        select(ItemORM).where(ItemORM.id == item_id)
    )
    orm_item = result.scalar_one_or_none()
    if not orm_item:
        raise ItemNotFoundError(item_id)
    if name is not None:
        duplicate = await db.execute(
            select(ItemORM).where(func.lower(ItemORM.name) == name.lower(), ItemORM.id != item_id)
        )
        if duplicate.scalar_one_or_none():
            raise DuplicateItemNameError(name)
        orm_item.name = name
    if price is not None:
        orm_item.price = price
    if category is not None:
        category_orm = await _get_category_orm(db, category)
        orm_item.category_id = category_orm.id
    if description is not None:
        orm_item.description = description
    await db.commit()
    result = await db.execute(
        select(ItemORM).options(selectinload(ItemORM.category)).where(ItemORM.id == item_id)
    )
    return _to_domain(result.scalar_one())


async def delete(db: AsyncSession, item_id: int) -> None:
    result = await db.execute(
        select(ItemORM).where(ItemORM.id == item_id)
    )
    orm_item = result.scalar_one_or_none()
    if not orm_item:
        raise ItemNotFoundError(item_id)
    await db.delete(orm_item)
    await db.commit()


async def get_all_categories(db: AsyncSession) -> set[Category]:
    result = await db.execute(select(CategoryORM))
    return {Category(c.name) for c in result.scalars().all()}