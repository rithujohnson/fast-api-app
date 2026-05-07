"""Integration tests for item router"""

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.integration

# --- GET all ---
def test_get_all_items_returns_200(client: TestClient):
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


# --- GET by id ---
def test_get_item_by_id_returns_200(client: TestClient):
    response = client.get("/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Apple"
    assert data["price"] == 1.50
    assert data["category"] == "Fruit"
    assert data["description"] == "A juicy red apple"


def test_get_item_not_found_returns_404(client: TestClient):
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "item not found"


# --- POST ---
def test_create_item_returns_201(client: TestClient):
    response = client.post("/items/", json={"name": "Mango", "price": 2.00, "category": "Fruit"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mango"
    assert data["price"] == 2.00
    assert data["category"] == "Fruit"
    assert data["description"] is None
    assert "id" in data


def test_create_item_with_description_returns_201(client: TestClient):
    response = client.post(
        "/items/",
        json={"name": "Mango", "price": 2.00, "category": "Fruit", "description": "A tropical fruit"}
    )
    assert response.status_code == 201
    assert response.json()["description"] == "A tropical fruit"


def test_create_item_does_not_affect_other_tests(client: TestClient):
    client.post("/items/", json={"name": "Mango", "price": 2.00, "category": "Fruit"})
    response = client.get("/items/")
    assert len(response.json()) == 3


def test_create_item_empty_name_returns_422(client: TestClient):
    response = client.post("/items/", json={"name": "", "price": 2.00, "category": "Fruit"})
    assert response.status_code == 422


def test_create_item_negative_price_returns_422(client: TestClient):
    response = client.post("/items/", json={"name": "Mango", "price": -1.00, "category": "Fruit"})
    assert response.status_code == 422


def test_create_item_missing_category_returns_422(client: TestClient):
    response = client.post("/items/", json={"name": "Mango", "price": 2.00})
    assert response.status_code == 422


def test_create_item_missing_fields_returns_422(client: TestClient):
    response = client.post("/items/", json={})
    assert response.status_code == 422


# --- PUT ---

def test_update_item_returns_200(client: TestClient):
    response = client.put(
        "/items/1",
        json={"name": "Green Apple", "price": 2.00, "category": "Fruit", "description": "A tart green apple"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Green Apple"
    assert data["price"] == 2.00
    assert data["description"] == "A tart green apple"


def test_update_item_clears_description_when_omitted(client: TestClient):
    # PUT replaces the whole item — description not sent means it becomes None
    response = client.put(
        "/items/1",
        json={"name": "Green Apple", "price": 2.00, "category": "Fruit"}
    )
    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_item_not_found_returns_404(client: TestClient):
    response = client.put(
        "/items/99",
        json={"name": "Ghost", "price": 1.00, "category": "Other"}
    )
    assert response.status_code == 404


def test_update_item_missing_required_field_returns_422(client: TestClient):
    response = client.put("/items/1", json={"name": "Green Apple"})
    assert response.status_code == 422


def test_update_item_negative_price_returns_422(client: TestClient):
    response = client.put(
        "/items/1",
        json={"name": "Apple", "price": -1.00, "category": "Fruit"}
    )
    assert response.status_code == 422


# --- PATCH ---

def test_patch_item_single_field_returns_200(client: TestClient):
    response = client.patch("/items/1", json={"price": 3.00})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 3.00
    assert data["name"] == "Apple"        # unchanged
    assert data["category"] == "Fruit"    # unchanged


def test_patch_item_multiple_fields_returns_200(client: TestClient):
    response = client.patch("/items/1", json={"name": "Red Apple", "category": "Produce"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Red Apple"
    assert data["category"] == "Produce"
    assert data["price"] == 1.50          # unchanged


def test_patch_item_not_found_returns_404(client: TestClient):
    response = client.patch("/items/99", json={"price": 3.00})
    assert response.status_code == 404


def test_patch_item_empty_name_returns_422(client: TestClient):
    response = client.patch("/items/1", json={"name": ""})
    assert response.status_code == 422


def test_patch_item_negative_price_returns_422(client: TestClient):
    response = client.patch("/items/1", json={"price": -5.00})
    assert response.status_code == 422


# --- DELETE ---

def test_delete_item_returns_204(client: TestClient):
    response = client.delete("/items/1")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_item_not_found_returns_404(client: TestClient):
    response = client.delete("/items/99")
    assert response.status_code == 404


def test_deleted_item_cannot_be_retrieved(client: TestClient):
    client.delete("/items/1")
    response = client.get("/items/1")
    assert response.status_code == 404


def test_delete_reduces_item_count(client: TestClient):
    client.delete("/items/1")
    response = client.get("/items/")
    assert len(response.json()) == 1


# --- GET all: filtering ---

def test_get_items_filter_by_category(rich_client: TestClient):
    response = rich_client.get("/items/?category=Fruit")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["category"] == "Fruit" for item in data)


def test_get_items_filter_by_category_vegetable(rich_client: TestClient):
    response = rich_client.get("/items/?category=Vegetable")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(item["category"] == "Vegetable" for item in data)


def test_get_items_filter_by_category_no_match_returns_empty(rich_client: TestClient):
    response = rich_client.get("/items/?category=Dairy")
    assert response.status_code == 200
    assert response.json() == []


def test_get_items_filter_by_min_price(rich_client: TestClient):
    response = rich_client.get("/items/?min_price=1.20")
    assert response.status_code == 200
    data = response.json()
    assert all(item["price"] >= 1.20 for item in data)
    assert len(data) == 3  # Broccoli(1.20), Apple(1.50), Mango(2.50)


def test_get_items_filter_by_max_price(rich_client: TestClient):
    response = rich_client.get("/items/?max_price=0.75")
    assert response.status_code == 200
    data = response.json()
    assert all(item["price"] <= 0.75 for item in data)
    assert len(data) == 2  # Carrot(0.50), Banana(0.75)


def test_get_items_filter_by_price_range(rich_client: TestClient):
    response = rich_client.get("/items/?min_price=0.75&max_price=1.50")
    assert response.status_code == 200
    data = response.json()
    assert all(0.75 <= item["price"] <= 1.50 for item in data)
    assert len(data) == 3  # Banana(0.75), Broccoli(1.20), Apple(1.50)


def test_get_items_filter_category_and_min_price(rich_client: TestClient):
    response = rich_client.get("/items/?category=Fruit&min_price=1.00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Apple(1.50), Mango(2.50)
    assert all(item["category"] == "Fruit" for item in data)


# --- GET all: sorting  ---

def test_get_items_sort_by_name_asc(rich_client: TestClient):
    response = rich_client.get("/items/?sort_by=name&order=asc")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == sorted(names)


def test_get_items_sort_by_name_desc(rich_client: TestClient):
    response = rich_client.get("/items/?sort_by=name&order=desc")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == sorted(names, reverse=True)


def test_get_items_sort_by_price_asc(rich_client: TestClient):
    response = rich_client.get("/items/?sort_by=price&order=asc")
    assert response.status_code == 200
    prices = [item["price"] for item in response.json()]
    assert prices == sorted(prices)


def test_get_items_sort_by_price_desc(rich_client: TestClient):
    response = rich_client.get("/items/?sort_by=price&order=desc")
    assert response.status_code == 200
    prices = [item["price"] for item in response.json()]
    assert prices == sorted(prices, reverse=True)


# --- GET all: pagination  ---

def test_get_items_limit_restricts_count(rich_client: TestClient):
    response = rich_client.get("/items/?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_items_skip_offsets_results(rich_client: TestClient):
    all_items = rich_client.get("/items/?limit=100").json()
    skipped = rich_client.get("/items/?skip=2&limit=100").json()
    assert skipped == all_items[2:]


def test_get_items_skip_and_limit_together(rich_client: TestClient):
    response = rich_client.get("/items/?skip=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_items_skip_beyond_count_returns_empty(rich_client: TestClient):
    response = rich_client.get("/items/?skip=100")
    assert response.status_code == 200
    assert response.json() == []


# --- GET all: validation ---

def test_get_items_invalid_sort_by_returns_422(rich_client: TestClient):
    response = rich_client.get("/items/?sort_by=banana")
    assert response.status_code == 422


def test_get_items_invalid_order_returns_422(rich_client: TestClient):
    response = rich_client.get("/items/?order=random")
    assert response.status_code == 422


def test_get_items_negative_skip_returns_422(rich_client: TestClient):
    response = rich_client.get("/items/?skip=-1")
    assert response.status_code == 422


def test_get_items_zero_limit_returns_422(rich_client: TestClient):
    response = rich_client.get("/items/?limit=0")
    assert response.status_code == 422


def test_get_items_negative_min_price_returns_422(rich_client: TestClient):
    response = rich_client.get("/items/?min_price=-1.0")
    assert response.status_code == 422


def test_get_items_min_price_greater_than_max_price_returns_400(rich_client: TestClient):
    response = rich_client.get("/items/?min_price=5.0&max_price=1.0")
    assert response.status_code == 400


# --- GET all: combined ---

def test_get_items_filter_sort_paginate_combined(rich_client: TestClient):
    # Fruit items, sorted by price desc, take 1 item starting from position 1
    response = rich_client.get("/items/?category=Fruit&sort_by=price&order=desc&skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    # Fruit by price desc: Mango(2.50), Apple(1.50), Banana(0.75) → skip 1 → Apple
    assert len(data) == 1
    assert data[0]["name"] == "Apple"