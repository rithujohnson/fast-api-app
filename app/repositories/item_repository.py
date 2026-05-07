"""Item repository"""

from app.exceptions import DuplicateItemNameError, ItemNotFoundError
from app.models.category import Category
from app.models.item import Item


_items: dict[int, Item] = {
    1: Item(id=1, name="Apple", price=1.50, category=Category("Fruit"), description="A juicy red apple"),
    2: Item(id=2, name="Banana", price=0.75, category=Category("Fruit"), description="A sweet yellow banana"),
}


def get_all(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    order: str = "asc",
    skip: int = 0,
    limit: int = 10,
) -> list[Item]:
    items = list(_items.values())

    if category is not None:
        items = [item for item in items if str(item.category).lower() == category.lower()]
    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]

    if sort_by is not None:
        items = sorted(items, key=lambda item: getattr(item, sort_by), reverse=(order == "desc"))

    return items[skip : skip + limit]


def get_by_id(item_id: int) -> Item:
    if item_id not in _items:
        raise ItemNotFoundError(item_id)
    return _items[item_id]


def create(name: str, price: float, category: str, description: str | None) -> Item:
    if any(item.name.lower() == name.lower() for item in _items.values()):
        raise DuplicateItemNameError(name)
    new_id = max(_items.keys(), default=0) + 1
    new_item = Item(id=new_id, name=name, price=price, category=Category.from_string(category), description=description)
    _items[new_id] = new_item
    return new_item


def update(item_id: int, name: str, price: float, category: str, description: str | None) -> Item:
    if item_id not in _items:
        raise ItemNotFoundError(item_id)
    updated_item = Item(id=item_id, name=name, price=price, category=Category.from_string(category), description=description)
    _items[item_id] = updated_item
    return updated_item


def patch(item_id: int, name: str | None, price: float | None, category: str | None, description: str | None) -> Item:
    if item_id not in _items:
        raise ItemNotFoundError(item_id)
    existing_item = _items[item_id]
    patched_item = Item(
        id=item_id,
        name=name if name is not None else existing_item.name,
        price=price if price is not None else existing_item.price,
        category=Category.from_string(category) if category is not None else existing_item.category,
        description=description if description is not None else existing_item.description,
    )
    _items[item_id] = patched_item
    return patched_item


def delete(item_id: int) -> None:
    if item_id not in _items:
        raise ItemNotFoundError(item_id)
    del _items[item_id]


def get_all_categories() -> set[Category]:
    return {item.category for item in _items.values()}
