"""Integration test configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.item import Item
import app.repositories.item_repository as item_repository


INITIAL_ITEMS = {
    1: Item(id=1, name="Apple", price=1.50, category="Fruit", description="A juicy red apple"),
    2: Item(id=2, name="Banana", price=0.75, category="Fruit", description="A sweet yellow banana"),
}


VARIED_ITEMS = {
    1: Item(id=1, name="Apple",    price=1.50, category="Fruit",     description=None),
    2: Item(id=2, name="Banana",   price=0.75, category="Fruit",     description=None),
    3: Item(id=3, name="Carrot",   price=0.50, category="Vegetable", description=None),
    4: Item(id=4, name="Broccoli", price=1.20, category="Vegetable", description=None),
    5: Item(id=5, name="Mango",    price=2.50, category="Fruit",     description=None),
}


@pytest.fixture
def client():
    item_repository._items = dict(INITIAL_ITEMS)
    return TestClient(app)


@pytest.fixture
def rich_client():
    item_repository._items = dict(VARIED_ITEMS)
    return TestClient(app)
