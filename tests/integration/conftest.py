"""Integration test configuration and fixtures"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base
from app.database.orm_models import CategoryORM, ItemORM
from app.database.session import get_db
from app.dependencies import get_current_user, require_admin
from app.main import app
from app.models.user import User

CATEGORY_NAMES = ["Fruit", "Vegetable", "Dairy", "Grain", "Protein"]

INITIAL_ITEMS_DATA = [
    {"id": 1, "name": "Apple",  "price": 1.50, "category_name": "Fruit", "description": "A juicy red apple"},
    {"id": 2, "name": "Banana", "price": 0.75, "category_name": "Fruit", "description": "A sweet yellow banana"},
]

VARIED_ITEMS_DATA = [
    {"id": 1, "name": "Apple",    "price": 1.50, "category_name": "Fruit",     "description": None},
    {"id": 2, "name": "Banana",   "price": 0.75, "category_name": "Fruit",     "description": None},
    {"id": 3, "name": "Carrot",   "price": 0.50, "category_name": "Vegetable", "description": None},
    {"id": 4, "name": "Broccoli", "price": 1.20, "category_name": "Vegetable", "description": None},
    {"id": 5, "name": "Mango",    "price": 2.50, "category_name": "Fruit",     "description": None},
]

TEST_VIEWER = User(id=1, username="testuser", hashed_password="hashed", role="viewer")
TEST_ADMIN = User(id=2, username="admin", hashed_password="hashed", role="admin")


async def _make_test_client(items_data: list[dict]) -> tuple[AsyncClient, object]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        categories = {name: CategoryORM(name=name) for name in CATEGORY_NAMES}
        db.add_all(categories.values())
        await db.flush()
        for item in items_data:
            db.add(ItemORM(
                id=item["id"],
                name=item["name"],
                price=item["price"],
                description=item["description"],
                category_id=categories[item["category_name"]].id,
            ))
        await db.commit()

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: TEST_VIEWER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test"), engine


@pytest.fixture
async def client():
    test_client, engine = await _make_test_client(INITIAL_ITEMS_DATA)
    async with test_client as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def rich_client():
    test_client, engine = await _make_test_client(VARIED_ITEMS_DATA)
    async with test_client as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()
