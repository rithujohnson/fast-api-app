import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.orm_models import CategoryORM, ItemORM

CATEGORY_NAMES = ["Fruit", "Vegetable", "Dairy", "Grain", "Protein"]

VARIED_ITEMS_DATA = [
    {"id": 1, "name": "Apple",    "price": 1.50, "category_name": "Fruit",     "description": None},
    {"id": 2, "name": "Banana",   "price": 0.75, "category_name": "Fruit",     "description": None},
    {"id": 3, "name": "Carrot",   "price": 0.50, "category_name": "Vegetable", "description": None},
    {"id": 4, "name": "Broccoli", "price": 1.20, "category_name": "Vegetable", "description": None},
    {"id": 5, "name": "Mango",    "price": 2.50, "category_name": "Fruit",     "description": None},
]


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()

    categories = {name: CategoryORM(name=name) for name in CATEGORY_NAMES}
    session.add_all(categories.values())
    session.flush()

    for item in VARIED_ITEMS_DATA:
        session.add(ItemORM(
            id=item["id"],
            name=item["name"],
            price=item["price"],
            description=item["description"],
            category_id=categories[item["category_name"]].id,
        ))
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
