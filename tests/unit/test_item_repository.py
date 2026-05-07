"""Unit tests for item repository get_all filtering, sorting, and pagination"""

import pytest
import app.repositories.item_repository as item_repository
from app.models.category import Category
from app.exceptions import DuplicateItemNameError, InvalidCategoryError, ItemNotFoundError

pytestmark = pytest.mark.unit


# --- get_by_id ---

def test_get_by_id_raises_when_not_found(db):
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.get_by_id(db, 99)
    assert exc_info.value.item_id == 99


# --- create ---

def test_create_raises_on_duplicate_name(db):
    with pytest.raises(DuplicateItemNameError) as exc_info:
        item_repository.create(db, name="Apple", price=2.00, category="Fruit", description=None)
    assert exc_info.value.name == "Apple"


def test_create_raises_on_invalid_category(db):
    with pytest.raises(InvalidCategoryError) as exc_info:
        item_repository.create(db, name="Candy Bar", price=1.00, category="Candy", description=None)
    assert exc_info.value.name == "Candy"


# --- update ---

def test_update_raises_when_not_found(db):
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.update(db, item_id=99, name="Ghost", price=1.00, category="Fruit", description=None)
    assert exc_info.value.item_id == 99


def test_update_raises_on_duplicate_name(db):
    with pytest.raises(DuplicateItemNameError) as exc_info:
        item_repository.update(db, item_id=1, name="Banana", price=1.50, category="Fruit", description=None)
    assert exc_info.value.name == "Banana"


def test_update_raises_on_invalid_category(db):
    with pytest.raises(InvalidCategoryError) as exc_info:
        item_repository.update(db, item_id=1, name="Apple", price=1.50, category="Invalid", description=None)
    assert exc_info.value.name == "Invalid"


# --- patch ---

def test_patch_raises_when_not_found(db):
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.patch(db, item_id=99, name="Ghost", price=None, category=None, description=None)
    assert exc_info.value.item_id == 99


def test_patch_raises_on_invalid_category(db):
    with pytest.raises(InvalidCategoryError) as exc_info:
        item_repository.patch(db, item_id=1, name=None, price=None, category="Invalid", description=None)
    assert exc_info.value.name == "Invalid"


# --- delete ---

def test_delete_raises_when_not_found(db):
    with pytest.raises(ItemNotFoundError) as exc_info:
        item_repository.delete(db, 99)
    assert exc_info.value.item_id == 99


# --- get_all_categories ---

def test_get_all_categories_returns_unique_set(db):
    result = item_repository.get_all_categories(db)
    assert isinstance(result, set)
    assert Category("Fruit") in result
    assert Category("Vegetable") in result
    assert len(result) == 5  # all seeded categories, not just in-use ones


# --- no filters ---

def test_get_all_no_params_returns_all_items(db):
    result = item_repository.get_all(db)
    assert len(result) == 5


# --- filtering ---

def test_get_all_filter_by_category_returns_matching_items(db):
    result = item_repository.get_all(db, category="Fruit")
    assert len(result) == 3
    assert all(str(item.category) == "Fruit" for item in result)


def test_get_all_filter_by_category_vegetable(db):
    result = item_repository.get_all(db, category="Vegetable")
    assert len(result) == 2
    assert all(str(item.category) == "Vegetable" for item in result)


def test_get_all_filter_by_category_no_match_returns_empty(db):
    result = item_repository.get_all(db, category="Dairy")
    assert result == []


def test_get_all_filter_by_min_price(db):
    result = item_repository.get_all(db, min_price=1.20)
    prices = [item.price for item in result]
    assert all(p >= 1.20 for p in prices)
    assert len(result) == 3  # Broccoli(1.20), Apple(1.50), Mango(2.50)


def test_get_all_filter_by_max_price(db):
    result = item_repository.get_all(db, max_price=0.75)
    prices = [item.price for item in result]
    assert all(p <= 0.75 for p in prices)
    assert len(result) == 2  # Carrot(0.50), Banana(0.75)


def test_get_all_filter_by_price_range(db):
    result = item_repository.get_all(db, min_price=0.75, max_price=1.50)
    prices = [item.price for item in result]
    assert all(0.75 <= p <= 1.50 for p in prices)
    assert len(result) == 3  # Banana(0.75), Broccoli(1.20), Apple(1.50)


def test_get_all_filter_category_and_min_price(db):
    result = item_repository.get_all(db, category="Fruit", min_price=1.00)
    assert len(result) == 2  # Apple(1.50), Mango(2.50)
    assert all(str(item.category) == "Fruit" for item in result)
    assert all(item.price >= 1.00 for item in result)


def test_get_all_filter_category_and_max_price(db):
    result = item_repository.get_all(db, category="Fruit", max_price=1.00)
    assert len(result) == 1  # Banana(0.75)
    assert result[0].name == "Banana"


# --- sorting ---

def test_get_all_sort_by_name_asc(db):
    result = item_repository.get_all(db, sort_by="name", order="asc")
    names = [item.name for item in result]
    assert names == sorted(names)


def test_get_all_sort_by_name_desc(db):
    result = item_repository.get_all(db, sort_by="name", order="desc")
    names = [item.name for item in result]
    assert names == sorted(names, reverse=True)


def test_get_all_sort_by_price_asc(db):
    result = item_repository.get_all(db, sort_by="price", order="asc")
    prices = [item.price for item in result]
    assert prices == sorted(prices)


def test_get_all_sort_by_price_desc(db):
    result = item_repository.get_all(db, sort_by="price", order="desc")
    prices = [item.price for item in result]
    assert prices == sorted(prices, reverse=True)


def test_get_all_no_sort_by_preserves_insertion_order(db):
    result = item_repository.get_all(db)
    ids = [item.id for item in result]
    assert ids == [1, 2, 3, 4, 5]


# --- pagination ---

def test_get_all_limit_restricts_result_count(db):
    result = item_repository.get_all(db, limit=2)
    assert len(result) == 2


def test_get_all_skip_offsets_start(db):
    all_items = item_repository.get_all(db, limit=100)
    skipped = item_repository.get_all(db, skip=2, limit=100)
    assert skipped == all_items[2:]


def test_get_all_skip_and_limit_together(db):
    result = item_repository.get_all(db, skip=1, limit=2)
    assert len(result) == 2


def test_get_all_skip_beyond_count_returns_empty(db):
    result = item_repository.get_all(db, skip=100)
    assert result == []


def test_get_all_limit_larger_than_count_returns_all(db):
    result = item_repository.get_all(db, limit=100)
    assert len(result) == 5


# --- combined ---

def test_get_all_filter_sort_paginate_combined(db):
    result = item_repository.get_all(
        db,
        category="Fruit",
        sort_by="price",
        order="desc",
        skip=1,
        limit=1,
    )
    # Fruit by price desc: Mango(2.50), Apple(1.50), Banana(0.75) → skip 1 → Apple
    assert len(result) == 1
    assert result[0].name == "Apple"
