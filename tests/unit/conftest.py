import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        categories = {name: CategoryORM(name=name) for name in CATEGORY_NAMES}
        session.add_all(categories.values())
        await session.flush()
        for item in VARIED_ITEMS_DATA:
            session.add(ItemORM(
                id=item["id"],
                name=item["name"],
                price=item["price"],
                description=item["description"],
                category_id=categories[item["category_name"]].id,
            ))
        await session.commit()
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
