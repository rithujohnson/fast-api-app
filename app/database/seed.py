from sqlalchemy.orm import Session

from app.database.orm_models import CategoryORM, ItemORM

CATEGORY_NAMES = ["Fruit", "Vegetable", "Dairy", "Grain", "Protein"]

INITIAL_ITEMS = [
    {"name": "Apple", "price": 1.50, "category_name": "Fruit", "description": "A juicy red apple"},
    {"name": "Banana", "price": 0.75, "category_name": "Fruit", "description": "A sweet yellow banana"},
]


def seed(db: Session) -> None:
    if db.query(CategoryORM).first():
        return

    categories = {name: CategoryORM(name=name) for name in CATEGORY_NAMES}
    db.add_all(categories.values())
    db.flush()

    for item_data in INITIAL_ITEMS:
        db.add(ItemORM(
            name=item_data["name"],
            price=item_data["price"],
            description=item_data["description"],
            category_id=categories[item_data["category_name"]].id,
        ))

    db.commit()