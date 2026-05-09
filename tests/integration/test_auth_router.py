"""Integration tests for auth router"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base
from app.database.orm_models import CategoryORM, ItemORM
from app.database.session import get_db
from app.main import app

pytestmark = pytest.mark.integration

CATEGORY_NAMES = ["Fruit", "Vegetable", "Dairy", "Grain", "Protein"]


@pytest.fixture
async def auth_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        categories = {name: CategoryORM(name=name) for name in CATEGORY_NAMES}
        db.add_all(categories.values())
        await db.flush()
        db.add(ItemORM(
            id=1, name="Apple", price=1.50,
            description="A juicy red apple",
            category_id=categories["Fruit"].id,
        ))
        await db.commit()

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


async def _register(client: AsyncClient, username: str, password: str, role: str = "viewer") -> dict:
    response = await client.post("/auth/register", json={
        "username": username,
        "password": password,
        "role": role,
    })
    return response


async def _login(client: AsyncClient, username: str, password: str) -> str:
    response = await client.post("/auth/login", data={
        "username": username,
        "password": password,
    })
    return response.json()["access_token"]


# --- POST /auth/register ---

async def test_register_returns_201(auth_client: AsyncClient):
    response = await _register(auth_client, "rithu", "securepass")
    assert response.status_code == 201


async def test_register_response_has_correct_fields(auth_client: AsyncClient):
    response = await _register(auth_client, "rithu", "securepass")
    data = response.json()
    assert "id" in data
    assert data["username"] == "rithu"
    assert data["role"] == "viewer"


async def test_register_does_not_expose_password(auth_client: AsyncClient):
    response = await _register(auth_client, "rithu", "securepass")
    assert "hashed_password" not in response.json()
    assert "password" not in response.json()


async def test_register_defaults_role_to_viewer(auth_client: AsyncClient):
    response = await auth_client.post("/auth/register", json={
        "username": "rithu",
        "password": "securepass",
    })
    assert response.json()["role"] == "viewer"


async def test_register_with_admin_role(auth_client: AsyncClient):
    response = await _register(auth_client, "adminuser", "securepass", role="admin")
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


async def test_register_duplicate_username_returns_409(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass")
    response = await _register(auth_client, "rithu", "differentpass")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "USER_ALREADY_EXISTS"


async def test_register_username_too_short_returns_422(auth_client: AsyncClient):
    response = await _register(auth_client, "ab", "securepass")
    assert response.status_code == 422


async def test_register_password_too_short_returns_422(auth_client: AsyncClient):
    response = await _register(auth_client, "rithu", "short")
    assert response.status_code == 422


async def test_register_invalid_role_returns_422(auth_client: AsyncClient):
    response = await auth_client.post("/auth/register", json={
        "username": "rithu",
        "password": "securepass",
        "role": "superuser",
    })
    assert response.status_code == 422


async def test_register_missing_username_returns_422(auth_client: AsyncClient):
    response = await auth_client.post("/auth/register", json={"password": "securepass"})
    assert response.status_code == 422


async def test_register_missing_password_returns_422(auth_client: AsyncClient):
    response = await auth_client.post("/auth/register", json={"username": "rithu"})
    assert response.status_code == 422


# --- POST /auth/login ---

async def test_login_returns_200(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass")
    response = await auth_client.post("/auth/login", data={"username": "rithu", "password": "securepass"})
    assert response.status_code == 200


async def test_login_returns_access_token(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass")
    response = await auth_client.post("/auth/login", data={"username": "rithu", "password": "securepass"})
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass")
    response = await auth_client.post("/auth/login", data={"username": "rithu", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


async def test_login_unknown_username_returns_401(auth_client: AsyncClient):
    response = await auth_client.post("/auth/login", data={"username": "ghost", "password": "securepass"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


async def test_login_missing_username_returns_422(auth_client: AsyncClient):
    response = await auth_client.post("/auth/login", data={"password": "securepass"})
    assert response.status_code == 422


async def test_login_missing_password_returns_422(auth_client: AsyncClient):
    response = await auth_client.post("/auth/login", data={"username": "rithu"})
    assert response.status_code == 422


# --- Protected endpoints with real JWT ---

async def test_create_item_without_token_returns_401(auth_client: AsyncClient):
    response = await auth_client.post("/items/", json={"name": "Mango", "price": 2.00, "category": "Fruit"})
    assert response.status_code == 401


async def test_create_item_with_invalid_token_returns_401(auth_client: AsyncClient):
    response = await auth_client.post(
        "/items/",
        json={"name": "Mango", "price": 2.00, "category": "Fruit"},
        headers={"Authorization": "Bearer this.is.not.a.valid.token"},
    )
    assert response.status_code == 401


async def test_create_item_with_viewer_token_returns_201(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass", role="viewer")
    token = await _login(auth_client, "rithu", "securepass")
    response = await auth_client.post(
        "/items/",
        json={"name": "Mango", "price": 2.00, "category": "Fruit"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


async def test_delete_item_with_viewer_token_returns_403(auth_client: AsyncClient):
    await _register(auth_client, "rithu", "securepass", role="viewer")
    token = await _login(auth_client, "rithu", "securepass")
    response = await auth_client.delete(
        "/items/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


async def test_delete_item_with_admin_token_returns_204(auth_client: AsyncClient):
    await _register(auth_client, "adminuser", "securepass", role="admin")
    token = await _login(auth_client, "adminuser", "securepass")
    response = await auth_client.delete(
        "/items/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
