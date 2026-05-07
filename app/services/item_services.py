"""Item service"""

import logging
from sqlalchemy.orm import Session
from app.exceptions import DuplicateItemNameError, InvalidCategoryError, InvalidPriceRangeError, ItemNotFoundError
from app.models.category import Category
from app.models.item import Item
from app.schemas.item_schema import ItemCreateRequest, ItemUpdateRequest, ItemPatchRequest
from app.repositories import item_repository

logger = logging.getLogger(__name__)


def get_all_items(
    db: Session,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> list[Item]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise InvalidPriceRangeError(min_price, max_price)
    return item_repository.get_all(
        db=db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )


def get_item(db: Session, item_id: int) -> Item:
    try:
        return item_repository.get_by_id(db, item_id)
    except ItemNotFoundError:
        logger.warning("Item not found: id=%s", item_id)
        raise


def create_item(db: Session, request: ItemCreateRequest) -> Item:
    try:
        item = item_repository.create(
            db=db,
            name=request.name, price=request.price,
            category=request.category, description=request.description,
        )
    except DuplicateItemNameError:
        logger.warning("Duplicate item name: name=%s", request.name)
        raise
    except InvalidCategoryError:
        logger.warning("Invalid category: category=%s", request.category)
        raise
    logger.info("Item created: id=%s name=%s", item.id, item.name)
    return item


def update_item(db: Session, item_id: int, request: ItemUpdateRequest) -> Item:
    try:
        item = item_repository.update(
            db=db,
            item_id=item_id, name=request.name, price=request.price,
            category=request.category, description=request.description,
        )
    except ItemNotFoundError:
        logger.warning("Item not found for update: id=%s", item_id)
        raise
    except InvalidCategoryError:
        logger.warning("Invalid category: category=%s", request.category)
        raise
    logger.info("Item updated: id=%s name=%s", item.id, item.name)
    return item


def patch_item(db: Session, item_id: int, request: ItemPatchRequest) -> Item:
    try:
        item = item_repository.patch(
            db=db,
            item_id=item_id, name=request.name, price=request.price,
            category=request.category, description=request.description,
        )
    except ItemNotFoundError:
        logger.warning("Item not found for patch: id=%s", item_id)
        raise
    except InvalidCategoryError:
        logger.warning("Invalid category: category=%s", request.category)
        raise
    logger.info("Item patched: id=%s name=%s", item.id, item.name)
    return item


def delete_item(db: Session, item_id: int) -> None:
    try:
        item_repository.delete(db, item_id)
    except ItemNotFoundError:
        logger.warning("Item not found for deletion: id=%s", item_id)
        raise
    logger.info("Item deleted: id=%s", item_id)


def get_all_categories(db: Session) -> set[Category]:
    return item_repository.get_all_categories(db)