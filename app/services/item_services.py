"""Item service"""

import logging
from app.models.item import Item
from app.schemas.item_schema import ItemCreateRequest, ItemUpdateRequest, ItemPatchRequest
from app.repositories import item_repository

logger = logging.getLogger(__name__)


def get_all_items(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> list[Item]:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValueError("min_price cannot be greater than max_price")
    return item_repository.get_all(
        category=category,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )


def get_item(item_id: int) -> Item | None:
    item = item_repository.get_by_id(item_id)
    if item is None:
        logger.warning("Item not found: id=%s", item_id)
    return item


def create_item(request: ItemCreateRequest) -> Item:
    item = item_repository.create(name=request.name, price=request.price, category=request.category, description=request.description)
    logger.info("Item created: id=%s name=%s", item.id, item.name)
    return item

def update_item(item_id: int, request: ItemUpdateRequest) -> Item | None:
    item = item_repository.update(item_id=item_id, name=request.name, price=request.price, category=request.category, description=request.description)
    if item is None:
        logger.warning("Item not found for update: id=%s", item_id)
    else:
        logger.info("Item updated: id=%s name=%s", item.id, item.name)
    return item 

def patch_item(item_id: int, request: ItemPatchRequest) -> Item | None:
    item = item_repository.patch(item_id=item_id, name=request.name, price=request.price, category=request.category, description=request.description)
    if item is None:
        logger.warning("Item not found for patch: id=%s", item_id)
    else:
        logger.info("Item patched: id=%s name=%s", item.id, item.name)
    return item

def delete_item(item_id: int) -> bool:
    success = item_repository.delete(item_id)
    if success:
        logger.info("Item deleted: id=%s", item_id)
    else:
        logger.warning("Item not found for deletion: id=%s", item_id)
    return success 
