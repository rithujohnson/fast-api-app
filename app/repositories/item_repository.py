"""Item repository"""

from sqlalchemy import func
from sqlalchemy.orm import Session

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


def _get_category_orm(db: Session, category_name: str) -> CategoryORM:
    category_orm = (
        db.query(CategoryORM)
        .filter(func.lower(CategoryORM.name) == category_name.lower())
        .first()
    )
    if not category_orm:
        raise InvalidCategoryError(category_name)
    return category_orm


def get_all(
    db: Session,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> list[Item]:
    query = db.query(ItemORM)
    if category is not None:
        query = query.join(ItemORM.category).filter(
            func.lower(CategoryORM.name) == category.lower()
        )
    if min_price is not None:
        query = query.filter(ItemORM.price >= min_price)
    if max_price is not None:
        query = query.filter(ItemORM.price <= max_price)
    if sort_by == "name":
        col = ItemORM.name
    elif sort_by == "price":
        col = ItemORM.price
    else:
        col = ItemORM.id
    query = query.order_by(col.desc() if order == "desc" else col.asc())
    return [_to_domain(item) for item in query.offset(skip).limit(limit).all()]


def get_by_id(db: Session, item_id: int) -> Item:
    orm_item = db.get(ItemORM, item_id)
    if not orm_item:
        raise ItemNotFoundError(item_id)
    return _to_domain(orm_item)


def create(db: Session, name: str, price: float, category: str, description: str | None) -> Item:
    if db.query(ItemORM).filter(func.lower(ItemORM.name) == name.lower()).first():
        raise DuplicateItemNameError(name)
    category_orm = _get_category_orm(db, category)
    orm_item = ItemORM(
        name=name,
        price=price,
        category_id=category_orm.id,
        description=description,
    )
    db.add(orm_item)
    db.commit()
    db.refresh(orm_item)
    return _to_domain(orm_item)


def update(db: Session, item_id: int, name: str, price: float, category: str, description: str | None) -> Item:
    orm_item = db.get(ItemORM, item_id)
    if not orm_item:
        raise ItemNotFoundError(item_id)
    if db.query(ItemORM).filter(func.lower(ItemORM.name) == name.lower(), ItemORM.id != item_id).first():
        raise DuplicateItemNameError(name)
    category_orm = _get_category_orm(db, category)
    orm_item.name = name
    orm_item.price = price
    orm_item.category_id = category_orm.id
    orm_item.description = description
    db.commit()
    db.refresh(orm_item)
    return _to_domain(orm_item)


def patch(db: Session, item_id: int, name: str | None, price: float | None, category: str | None, description: str | None) -> Item:
    orm_item = db.get(ItemORM, item_id)
    if not orm_item:
        raise ItemNotFoundError(item_id)
    if name is not None:
        if db.query(ItemORM).filter(func.lower(ItemORM.name) == name.lower(), ItemORM.id != item_id).first():
            raise DuplicateItemNameError(name)
        orm_item.name = name
    if price is not None:
        orm_item.price = price
    if category is not None:
        category_orm = _get_category_orm(db, category)
        orm_item.category_id = category_orm.id
    if description is not None:
        orm_item.description = description
    db.commit()
    db.refresh(orm_item)
    return _to_domain(orm_item)


def delete(db: Session, item_id: int) -> None:
    orm_item = db.get(ItemORM, item_id)
    if not orm_item:
        raise ItemNotFoundError(item_id)
    db.delete(orm_item)
    db.commit()


def get_all_categories(db: Session) -> set[Category]:
    return {Category(c.name) for c in db.query(CategoryORM).all()}