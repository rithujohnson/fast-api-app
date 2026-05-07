"""Unit tests for item repository get_all filtering, sorting, and pagination"""

import pytest
import app.repositories.item_repository as item_repository
from app.models.item import Item
from app.exceptions import DuplicateItemNameError, ItemNotFoundError


pytestmark = pytest.mark.unit


VARIED_ITEMS = {
    1: Item(id=1, name="Apple",    price=1.50, category="Fruit",     description=None),
    2: Item(id=2, name="Banana",   price=0.75, category="Fruit",     description=None),
    3: Item(id=3, name="Carrot",   price=0.50, category="Vegetable", description=None),
    4: Item(id=4, name="Broccoli", price=1.20, category="Vegetable", description=None),
    5: Item(id=5, name="Mango",    price=2.50, category="Fruit",     description=None),
}


@pytest.fixture(autouse=True)
def reset_items():
    item_repository._items = dict(VARIED_ITEMS)
    yield
    item_repository._items = dict(VARIED_ITEMS)


# --- get_by_id ---

def test_get_by_id_raises_when_not_found():
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.get_by_id(99)
    assert exc_info.value.item_id == 99


# --- create ---

def test_create_raises_on_duplicate_name():
    with pytest.raises(DuplicateItemNameError) as exc_info:
        item_repository.create(name="Apple", price=2.00, category="Fruit", description=None)
    assert exc_info.value.name == "Apple"


# --- update ---

def test_update_raises_when_not_found():
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.update(item_id=99, name="Ghost", price=1.00, category="Other", description=None)
    assert exc_info.value.item_id == 99


# --- patch ---

def test_patch_raises_when_not_found():
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.patch(item_id=99, name="Ghost", price=None, category=None, description=None)
    assert exc_info.value.item_id == 99


# --- delete ---

def test_delete_raises_when_not_found():
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.delete(99)
    assert exc_info.value.item_id == 99
    

# --- no filters ---

def test_get_all_no_params_returns_all_items():
    result = item_repository.get_all()
    assert len(result) == 5


# --- filtering ---

def test_get_all_filter_by_category_returns_matching_items():
    result = item_repository.get_all(category="Fruit")
    assert len(result) == 3
    assert all(item.category == "Fruit" for item in result)


def test_get_all_filter_by_category_vegetable():
    result = item_repository.get_all(category="Vegetable")
    assert len(result) == 2
    assert all(item.category == "Vegetable" for item in result)


def test_get_all_filter_by_category_no_match_returns_empty():
    result = item_repository.get_all(category="Dairy")
    assert result == []


def test_get_all_filter_by_min_price():
    result = item_repository.get_all(min_price=1.20)
    prices = [item.price for item in result]
    assert all(p >= 1.20 for p in prices)
    assert len(result) == 3  # Broccoli(1.20), Apple(1.50), Mango(2.50)


def test_get_all_filter_by_max_price():
    result = item_repository.get_all(max_price=0.75)
    prices = [item.price for item in result]
    assert all(p <= 0.75 for p in prices)
    assert len(result) == 2  # Carrot(0.50), Banana(0.75)


def test_get_all_filter_by_price_range():
    result = item_repository.get_all(min_price=0.75, max_price=1.50)
    prices = [item.price for item in result]
    assert all(0.75 <= p <= 1.50 for p in prices)
    assert len(result) == 3  # Banana(0.75), Broccoli(1.20), Apple(1.50)


def test_get_all_filter_category_and_min_price():
    result = item_repository.get_all(category="Fruit", min_price=1.00)
    assert len(result) == 2  # Apple(1.50), Mango(2.50)
    assert all(item.category == "Fruit" for item in result)
    assert all(item.price >= 1.00 for item in result)


def test_get_all_filter_category_and_max_price():
    result = item_repository.get_all(category="Fruit", max_price=1.00)
    assert len(result) == 1  # Banana(0.75)
    assert result[0].name == "Banana"


# --- sorting ---

def test_get_all_sort_by_name_asc():
    result = item_repository.get_all(sort_by="name", order="asc")
    names = [item.name for item in result]
    assert names == sorted(names)


def test_get_all_sort_by_name_desc():
    result = item_repository.get_all(sort_by="name", order="desc")
    names = [item.name for item in result]
    assert names == sorted(names, reverse=True)


def test_get_all_sort_by_price_asc():
    result = item_repository.get_all(sort_by="price", order="asc")
    prices = [item.price for item in result]
    assert prices == sorted(prices)


def test_get_all_sort_by_price_desc():
    result = item_repository.get_all(sort_by="price", order="desc")
    prices = [item.price for item in result]
    assert prices == sorted(prices, reverse=True)


def test_get_all_no_sort_by_preserves_insertion_order():
    result = item_repository.get_all()
    ids = [item.id for item in result]
    assert ids == [1, 2, 3, 4, 5]


# --- pagination ---

def test_get_all_limit_restricts_result_count():
    result = item_repository.get_all(limit=2)
    assert len(result) == 2


def test_get_all_skip_offsets_start():
    all_items = item_repository.get_all(limit=100)
    skipped = item_repository.get_all(skip=2, limit=100)
    assert skipped == all_items[2:]


def test_get_all_skip_and_limit_together():
    result = item_repository.get_all(skip=1, limit=2)
    assert len(result) == 2


def test_get_all_skip_beyond_count_returns_empty():
    result = item_repository.get_all(skip=100)
    assert result == []


def test_get_all_limit_larger_than_count_returns_all():
    result = item_repository.get_all(limit=100)
    assert len(result) == 5


# --- combined ---

def test_get_all_filter_sort_paginate_combined():
    # Fruit items sorted by price desc, second page of 1
    result = item_repository.get_all(
        category="Fruit",
        sort_by="price",
        order="desc",
        skip=1,
        limit=1,
    )
    # Fruit by price desc: Mango(2.50), Apple(1.50), Banana(0.75)
    # skip=1 → Apple
    assert len(result) == 1
    assert result[0].name == "Apple"